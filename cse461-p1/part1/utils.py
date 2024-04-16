import socket
import struct
from config import *


# Utility functions for sending and receiving messages

def create_udp_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Wrap the payload with the header and send the message
def send_udp_message(sock, host, port, message, psecret=0, step=1, student_no=490):
    print(f"Sending message to {host}:{port}")
    if isinstance(message, str):
        payload = message.encode('utf-8')
        payload += b'\0'  # Adding string terminator as per the protocol
    else:
        payload = message

    # Padding to align to 4-byte boundary
    while len(payload) % 4 != 0:
        payload += b'\0'

    header = struct.pack(HEADER_FORMAT, len(payload), psecret, step, student_no)
    packet = header + payload
    decode_packet(packet) # decode packet for debugging, remove this line in production
    sock.sendto(packet, (host, port))

def receive_udp_message(sock):
    data, _ = sock.recvfrom(BUFFER_SIZE)
    return data

def parse_udp_response(data, response_format):
    return struct.unpack(response_format, data)

# function to create a packet for stage b
def create_packet(packet_id, length):
    packet_id = struct.pack('!I', packet_id)
    payload = length * b'\x00'
    packet = packet_id + payload
    return packet


# =================================================================================================
# Utility functions for decoding packets
def decode_packet(data):
    payload_len, psecret, step, student_no = struct.unpack(HEADER_FORMAT, data[:12])
    payload = data[12:12+payload_len]
    print(payload_len, psecret, step, student_no,) 
    print(payload)
        
