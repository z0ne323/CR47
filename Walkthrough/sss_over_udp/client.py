'''List of imported modules'''
import zlib
import socket

# Configuration
PORT = 5555
CRC32_SIZE = 4
HEADER_SIZE = 2
CONTENT_LENGTH_SIZE = 2

def calculate_crc32(data: bytes) -> int:
    """
    Calculate the CRC32 checksum of the provided data.

    Parameters:
        data (bytes): The input data for which to calculate the CRC32 checksum.

    Returns:
        int: The CRC32 checksum of the input data, represented as an unsigned 32-bit integer.
    """
    return zlib.crc32(data) & 0xffffffff

def create_packet(header: bytes, content: bytes) -> bytes:
    """
    Create a complete data packet consisting of a header, size, content, and checksum.

    Parameters:
        header (bytes): The header to identify the type of packet.
        content (bytes): The payload content to be included in the packet.

    Returns:
        bytes: A complete packet with header, size, content, and CRC32 checksum appended.
    """
    size = len(content).to_bytes(CONTENT_LENGTH_SIZE, byteorder='big')
    packet = header + size + content
    crc32 = calculate_crc32(packet).to_bytes(CRC32_SIZE, byteorder='big')
    return packet + crc32

def send_message(sock: socket.socket, addr: tuple, header: bytes, content: bytes) -> None:
    """
    Send a message as a complete data packet to a specified address using a socket.

    Parameters:
        sock (socket.socket): The socket object used for sending the packet.
        addr (tuple): The address (IP, port) to which the packet will be sent.
        header (bytes): The header to identify the type of packet.
        content (bytes): The payload content to be included in the packet.
    """
    packet = create_packet(header, content)
    sock.sendto(packet, addr)

def receive_message(sock: socket.socket) -> tuple:
    """
    Receive a message from a socket and extract its components, 
    including header, content, and checksum verification.

    Parameters:
        sock (socket.socket): The socket object used to receive the packet.

    Returns:
        tuple: A tuple containing the header (bytes), content (str), 
        and the address (tuple) from which the packet was received.
    """
    data, addr = sock.recvfrom(2048)
    header = data[:HEADER_SIZE]
    content = data[HEADER_SIZE + CONTENT_LENGTH_SIZE:-CRC32_SIZE]
    crc32 = data[-CRC32_SIZE:]

    if calculate_crc32(data[:-CRC32_SIZE]) != int.from_bytes(crc32, byteorder='big'):
        print("Checksum mismatch")
        return None, None, addr

    return header, content.decode('utf-8'), addr

def decode_content(content: bytes) -> str:
    """
    Decode content from bytes to a string.

    Parameters:
        content (bytes): The content to decode.

    Returns:
        str: The decoded string, or an error message if decoding fails.
    """
    return content.decode('utf-8')

def client():
    """
    Implements a UDP client that connects to a server, sends a connection request, 
    executes a command based on user input, and handles disconnection.
    """
    server_address = ('cr47.cr', PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Connect to the server
    connect_header = b'\x0b\xb9'
    send_message(sock, server_address, connect_header, b'CONNECT')
    header, response, addr = receive_message(sock)

    if response is not None:
        print(f"[*] Received from server: `{response}` from {addr}")
    else:
        print("No response received.")

    # Execute command on the server
    if header == b'\x17\x72':
        while True:
            command = input("[*] Enter command to execute (or 'exit' to disconnect): ")
            if command.lower() == 'exit':
                break
            command_header = b'\x0b\xba'
            send_message(sock, server_address, command_header, command.encode('utf-8'))
            header, response, addr = receive_message(sock)
            if response is not None:
                print(f"[+] Command response from {addr}: ")
                for line in response.splitlines():
                    print(f"{line}")
            else:
                print("[-] No response received for command.")

    # Disconnect from server
    disconnect_header = b'\x0b\xbb'
    send_message(sock, server_address, disconnect_header, b'DISCONNECT')
    header, response, addr = receive_message(sock)
    if response is not None:
        print(f"[*] Received from server: `{response}` from {addr}")
    else:
        print("[-] No response received for disconnection.")

if __name__ == "__main__":
    client()
