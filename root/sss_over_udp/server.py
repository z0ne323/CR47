'''List of imported modules'''
import sys
import time
import zlib
import signal
import socket
import logging
import subprocess
from enum import Enum
from logging import handlers
from typing import Tuple, Optional

# Server configuration
PORT = 5555
CLIENT_TIMEOUT = 300

# Packet configuration
CRC32_SIZE = 4
HEADER_SIZE = 2
MAX_PACKET_SIZE = 2048
CONTENT_LENGTH_SIZE = 2

# Define message constants
ERROR_HEADER = b'\x17\x73'
CONNECT_REQUEST = b'\x0b\xb9'
COMMAND_REQUEST = b'\x0b\xba'
RESPONSE_HEADER = b'\x17\x72'
DISCONNECT_REQUEST = b'\x0b\xbb'
VALID_HEADERS = {CONNECT_REQUEST, COMMAND_REQUEST, DISCONNECT_REQUEST}

# Enum for client states
class ClientState(Enum):
    """
    Enum representing the connection states of a client.
    
    Attributes:
        DISCONNECTED: The client is not connected to the server.
        CONNECTED: The client is connected to the server.
    """
    DISCONNECTED = 'DISCONNECTED'
    CONNECTED = 'CONNECTED'

# Create and configure logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

rotating_handler = handlers.RotatingFileHandler(
    'server.log', maxBytes=10 * 1024 * 1024, backupCount=5
)
rotating_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
rotating_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(rotating_handler)

# Dictionary to track client connections
client_connections: dict[Tuple[str, int], Tuple[ClientState, float]] = {}

def log_error(message: str, error: Exception) -> None:
    """
    Description: Log an error message with the associated exception.

    Parameters:
        message (str): The error message to log.
        error (Exception): The exception to log.

    Returns:
        None
    """
    logger.error("%s: %s", message, error)

def calculate_crc32(data: bytes) -> int:
    """
    Description: Calculate the CRC32 checksum of the provided data.

    Parameters:
        data (bytes): The data for which to compute the checksum.

    Returns:
        int: The computed CRC32 checksum as an unsigned 32-bit integer.
    """
    return zlib.crc32(data) & 0xffffffff

def execute_command(command: str) -> bytes:
    """
    Description: Execute a shell command and return its output.

    Parameters:
        command (str): The command to be executed.

    Returns:
        bytes: The combined output and error messages from the command.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            check=False,
            shell=True,
            text=True,
            timeout=10
        )
        return (result.stdout + result.stderr).encode('utf-8')
    except subprocess.TimeoutExpired as e:
        log_error("Command timed out", e)
        return str(e).encode('utf-8')
    except OSError as e:
        log_error("OS error occurred", e)
        return str(e).encode('utf-8')

def is_valid_size(data: bytes) -> bool:
    """
    Description: Check if the packet size is within valid limits.

    Parameters:
        data (bytes): The raw data packet received from a client.

    Returns:
        bool: True if the size is valid; False otherwise.
    """
    return HEADER_SIZE + CONTENT_LENGTH_SIZE + CRC32_SIZE <= len(data) <= MAX_PACKET_SIZE

def is_valid_checksum(data: bytes, crc32: bytes) -> bool:
    """
    Description: Check if the packet checksum matches the calculated value.

    Parameters:
        data (bytes): The data to calculate the checksum for.
        crc32 (bytes): The received CRC32 checksum from the packet.

    Returns:
        bool: True if the checksum is valid; False otherwise.
    """
    return calculate_crc32(data) == int.from_bytes(crc32, byteorder='big')

def is_valid_header(header: bytes) -> bool:
    """
    Description: Check if the packet header is valid.

    Parameters:
        header (bytes): The header of the packet received from a client.

    Returns:
        bool: True if the header is valid; False otherwise.
    """
    return header in VALID_HEADERS

def process_message(data: bytes, addr: Tuple[str, int]) -> bytes:
    """
    Description: Process a message received from a client and respond accordingly.

    Parameters:
        data (bytes): The received data packet.
        addr (tuple): The address of the client that sent the packet.

    Returns:
        bytes: The response to be sent back to the client.
    """
    cleanup_clients()

    validation_error = validate_packet(data)
    if validation_error:
        return validation_error

    header, content = extract_header_and_content(data)
    client_state, _ = client_connections.get(addr, (ClientState.DISCONNECTED, time.time()))

    if header == CONNECT_REQUEST:
        return handle_connect_request(content, addr)
    elif header == COMMAND_REQUEST:
        return handle_command_request(content, client_state)
    elif header == DISCONNECT_REQUEST:
        return handle_disconnect_request(content, client_state, addr)

    return create_error_message("[-] Unknown message ID")

def cleanup_clients() -> None:
    """
    Description: Remove clients that have been disconnected for a certain timeout period.

    Returns:
        None
    """
    current_time = time.time()
    for addr in list(client_connections.keys()):
        state, last_active_time = client_connections[addr]
        if state == ClientState.DISCONNECTED and (current_time - last_active_time) > CLIENT_TIMEOUT:
            del client_connections[addr]
            logger.info("Removed client %s due to inactivity.", addr)

def validate_packet(data: bytes) -> Optional[bytes]:
    """
    Description: Validate the received packet for size, checksum, and header.

    Parameters:
        data (bytes): The raw data packet to be validated.

    Returns:
        Optional[bytes]: An error message if validation fails; None otherwise.
    """
    if not is_valid_size(data):
        return create_error_message("[-] Invalid packet size")

    header = data[:HEADER_SIZE]
    size = data[HEADER_SIZE:HEADER_SIZE + CONTENT_LENGTH_SIZE]
    content = data[HEADER_SIZE + CONTENT_LENGTH_SIZE:-CRC32_SIZE]
    crc32 = data[-CRC32_SIZE:]

    if not is_valid_checksum(header + size + content, crc32):
        return create_error_message("[-] Checksum mismatch")

    if not is_valid_header(header):
        return create_error_message("[-] Unknown message ID")

    return None

def extract_header_and_content(data: bytes) -> Tuple[bytes, bytes]:
    """
    Description: Extract the header and content from the received data.

    Parameters:
        data (bytes): The raw data packet received from a client.

    Returns:
        tuple: A tuple containing the header (bytes) and content (bytes).
    """
    header = data[:HEADER_SIZE]
    content = data[HEADER_SIZE + CONTENT_LENGTH_SIZE:-CRC32_SIZE]
    return header, content

def handle_connect_request(content: bytes, addr: Tuple[str, int]) -> bytes:
    """
    Description: Handle connection requests from the client.

    Parameters:
        content (bytes): The content of the connect request.
        addr (tuple): The address of the client.

    Returns:
        bytes: A response message indicating the connection status.
    """
    decoded_content = decode_content(content)
    if not decoded_content:
        return create_error_message("[-] Invalid content format")

    if decoded_content == "CONNECT":
        client_connections[addr] = (ClientState.CONNECTED, time.time())
        logger.info("Client %s connected.", addr)
        return create_response_message(b'[+] Connection established')

    return create_error_message("[-] Unknown Content")

def handle_command_request(content: bytes, state: ClientState) -> bytes:
    """
    Description: Handle command requests from the client.

    Parameters:
        content (bytes): The content of the command request.
        state (ClientState): The current state of the client.

    Returns:
        bytes: A response message containing the command output or error.
    """
    if state == ClientState.CONNECTED:
        decoded_command = decode_content(content)
        if not decoded_command:
            return create_error_message("[-] Invalid command format")

        logger.info("Executing command: %s", decoded_command)
        output = execute_command(decoded_command)

        if len(output) > 2040:
            return create_error_message("[*] Output too large (max 2040 bytes allowed)")
        return create_response_message(output)

    return create_error_message("[-] Client not connected")

def handle_disconnect_request(content: bytes, state: ClientState, addr: Tuple[str, int]) -> bytes:
    """
    Description: Handle disconnection requests from the client.

    Parameters:
        content (bytes): The content of the disconnect request.
        state (ClientState): The current state of the client.
        addr (tuple): The address of the client.

    Returns:
        bytes: A response message indicating the disconnection status.
    """
    if state == ClientState.CONNECTED:
        decoded_content = decode_content(content)
        if not decoded_content:
            return create_error_message("[-] Invalid content format")

        if decoded_content == "DISCONNECT":
            client_connections[addr] = (ClientState.DISCONNECTED, time.time())
            logger.info("Client %s disconnected.", addr)
            return create_response_message(b'[+] Disconnected')

        return create_error_message("[-] Unknown Content")
    return create_error_message("[-] Client not connected")

def decode_content(content: bytes) -> Optional[str]:
    """
    Description: Decode content from bytes to a string.

    Parameters:
        content (bytes): The content to decode.

    Returns:
        Optional[str]: The decoded string, or None if decoding fails.
    """
    try:
        return content.decode('utf-8')
    except UnicodeDecodeError:
        return None

def create_response_message(content: bytes) -> bytes:
    """
    Description: Create a response message packet with the specified content.

    Parameters:
        content (bytes): The content to include in the response.

    Returns:
        bytes: The complete response message packet.
    """
    header = RESPONSE_HEADER
    return create_packet(header, content)

def create_error_message(error_message: str) -> bytes:
    """
    Description: Create an error message packet with the specified error message.

    Parameters:
        error_message (str): The error message to include.

    Returns:
        bytes: The complete error message packet.
    """
    header = ERROR_HEADER
    return create_packet(header, error_message.encode('utf-8'))

def create_packet(header: bytes, content: bytes) -> bytes:
    """
    Description: Create a complete data packet consisting of a header, size, content, and checksum.

    Parameters:
        header (bytes): The packet header.
        content (bytes): The content of the packet.

    Returns:
        bytes: The complete data packet.
    """
    size = len(content).to_bytes(CONTENT_LENGTH_SIZE, byteorder='big')
    packet = header + size + content
    crc32 = calculate_crc32(packet).to_bytes(CRC32_SIZE, byteorder='big')
    return packet + crc32

def server() -> None:
    """
    Description: Start a UDP server that listens for incoming messages on a specified port.

    Returns:
        None
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server_socket.bind(('0.0.0.0', PORT))
        server_socket.settimeout(5)
        logger.info("Server listening on port %s", PORT)

        def signal_handler(_sig: int, _frame: None) -> None:
            """
            Description: Handle the signal for graceful shutdown of the server.

            Parameters:
                _sig (int): The signal number.
                _frame (None): The current stack frame (not used).

            Returns:
                None
            """
            logger.info("Shutting down server...")
            server_socket.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        while True:
            try:
                data, addr = server_socket.recvfrom(MAX_PACKET_SIZE)
                logger.info("Received message from %s", addr)
                response = process_message(data, addr)
                server_socket.sendto(response, addr)
            except socket.timeout:
                continue
            except (socket.error, OSError) as e:
                log_error("Socket error occurred", e)
                continue
    finally:
        server_socket.close()

if __name__ == "__main__":
    server()
