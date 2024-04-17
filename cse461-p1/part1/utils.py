import socket
import struct
from config import *


# Utility functions for sending and receiving messages

def create_udp_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Wrap the payload with the header and send the message
# sock: the socket to send the message
# host: the host to send the message to
# port: the port to send the message to
# message: the message to send
def send_udp_message(sock, host, port, message, psecret=0, step=1, student_no=490):
    print(f"Sending message to {host}:{port}")

    if isinstance(message, str):
        # Assume message is a string
        payload = message.encode('utf-8')
        payload += b'\0'
    else:
        # Assume message is a list of byte integers
        payload = message
        

    header = struct.pack(HEADER_FORMAT, len(payload), psecret, step, student_no)
    packet = header + payload
    while len(packet) % 4 != 0:
        packet += b'\0'
    decode_packet(packet) # decode packet for debugging, remove this line in production
    sock.sendto(packet, (host, port))

def receive_udp_message(sock):
    data, _ = sock.recvfrom(BUFFER_SIZE)
    return data

def parse_udp_response(data, response_format):
    return struct.unpack(response_format, data)

# function to create a packet for stage b
# packet_id: the id of the packet
# length: the length of the payload

def create_packet(packet_id, length):
    # Pack the packet_id as a 4-byte integer using network byte order
    packet_id = struct.pack('!I', packet_id)

    # Create a payload of the specified length, initialized to zeros
    payload = bytearray(length)

    # Combine the packet_id and the payload to create the packet
    packet = packet_id + payload

    return packet


# =================================================================================================
# Utility functions for decoding packets
def decode_packet(data):
    payload_len, psecret, step, student_no = struct.unpack(HEADER_FORMAT, data[:12])
    payload = data[12:]
    print(payload_len, psecret, step, student_no) 
    print(payload)
        
