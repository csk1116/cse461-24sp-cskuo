from utils import *
from config import *
import sys

def stage_a(server_host, initial_udp_port):
    print("Stage A: Sending 'hello world' via UDP")
    with create_udp_socket() as sock:
        # Step a1: Send "hello world"
        send_udp_message(sock, server_host, initial_udp_port, "hello world", psecret=0, step=1, student_no=STUDENT_ID)
        
        # Step a2: Receive server response
        data = receive_udp_message(sock)
        num, len, udp_port, secretA = parse_udp_response(data[12:], '!IIII')  # Skipping header which is first 12 bytes
        sock.close()
        return num, len, udp_port, secretA

