'''List of imported modules'''
import zlib
import socket

# Constants
PORT = 5555
CRC32_SIZE = 4
HEADER_SIZE = 2
CONTENT_LENGTH_SIZE = 2

def calculate_crc32(data: bytes) -> int:
    """
    Description: Calculate the CRC32 checksum of the provided data.

    Parameters:
        data (bytes): The data for which to compute the checksum.

    Returns:
        int: The computed CRC32 checksum as an unsigned 32-bit integer.
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

def send_message(sock, addr, header, content):
    """
    Description:
        Send a message as a complete data packet to a specified address using a socket.
    
    Parameters:
        sock (socket.socket): The socket object used for sending the packet.
        addr (tuple): The address (IP, port) to which the packet will be sent.
        header (bytes): The header to identify the type of packet.
        content (bytes): The payload content to be included in the packet.
    
    Returns:
        None: This function does not return a value. It sends the packet over the network.
    
    Note:
        The packet is created by calling the `create_packet` function, which appends
        the necessary header, size, content, and checksum before sending it through the socket.
    """
    packet = create_packet(header, content)
    sock.sendto(packet, addr)

def receive_message(sock):
    """
    Description:
        Receive a message from a socket and extract its components, including 
        header, content, and checksum verification.
    
    Parameters:
        sock (socket.socket): The socket object used to receive the packet.
    
    Returns:
        tuple: A tuple containing the header (bytes), content (str), and the 
               address (tuple) from which the packet was received. If there is a 
               checksum mismatch, returns (None, None, addr).
    
    Note:
        The function reads data from the socket, extracts the header and content, 
        and checks the integrity of the message using a CRC32 checksum. If the 
        checksum does not match, an error message is printed and (None, None, addr)
        is returned.
    """
    data, addr = sock.recvfrom(2048)
    header = data[:HEADER_SIZE]
    content = data[HEADER_SIZE + CONTENT_LENGTH_SIZE:-4]
    crc32 = data[-4:]

    if calculate_crc32(data[:-4]) != int.from_bytes(crc32, byteorder='big'):
        print("Checksum mismatch")
        return None, None, addr  # Return None for header and content, but include addr

    return header, content.decode('utf-8'), addr

def discover_headers():
    """
    Description:
        Discover valid headers by sending specific request messages to a server 
        and checking the responses for each header type. This function iterates 
        through all possible 2-byte headers and identifies headers for Connect, 
        Command, and Disconnect requests.

    Parameters:
        None

    Returns:
        None: The function prints the valid headers found and notifies if all 
        headers are identified or if some are missing.

    Note:
        The function uses a UDP socket to communicate with a server located at 
        a specified address. It sends predefined messages (CONNECT, DISCONNECT, 
        and a command) for each header and expects a response. The header is 
        considered valid if a specific response is received.
    """
    server_address = ('cr47.cr', PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    valid_headers = {}
    connect_content = b"CONNECT"
    disconnect_content = b"DISCONNECT"

    # Iterate through all possible 2-byte headers
    for i in range(0x10000):
        header = i.to_bytes(2, byteorder='big')

        # Check for ConnectRequest
        if 'ConnectRequest' not in valid_headers:
            send_message(sock, server_address, header, connect_content)
            header_response, response, _ = receive_message(sock)
            if response and header_response == b'\x17\x72':
                valid_headers['ConnectRequest'] = header.hex()
                print(f"Valid header for ConnectRequest: {header.hex()}")
                continue  # Go to the next iteration

        # Check for CommandRequest
        if 'CommandRequest' not in valid_headers:
            command_content = b"ls"  # Replace with a valid command if needed
            send_message(sock, server_address, header, command_content)
            header_response, response, _ = receive_message(sock)
            if response and header_response == b'\x17\x72':
                valid_headers['CommandRequest'] = header.hex()
                print(f"Valid header for CommandRequest: {header.hex()}")
                continue  # Go to the next iteration

        # Check for DisconnectRequest
        if 'DisconnectRequest' not in valid_headers:
            send_message(sock, server_address, header, disconnect_content)
            header_response, response, _ = receive_message(sock)
            if response and header_response == b'\x17\x72':
                valid_headers['DisconnectRequest'] = header.hex()
                print(f"Valid header for DisconnectRequest: {header.hex()}")
                continue  # Go to the next iteration

        # Stop if all headers are found
        if len(valid_headers) == 3:
            break

    if len(valid_headers) < 3:
        print("Not all valid headers found.")
    else:
        print("All valid headers found:", valid_headers)

if __name__ == "__main__":
    discover_headers()
