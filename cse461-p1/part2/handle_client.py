import struct
import random
import socket
from struct import pack, unpack
import time

# Define protocol-specific constants
TIMEOUT = 3
HEADER_SIZE = 12
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 1337  # Random port
BUFFER_LEN = 1024
SERVER_STEP = 2


def handle_client(message, client_ip):
    # Stage A
    print("Stage A start")
    server_step = 1
    expected_payload = "hello world" + '\0'
    expected_message_len = HEADER_SIZE + len(expected_payload)
    
    # Unpack header fields (12-bytes)
    # >: Big-endian (most significant byte first)
    # 1. payload length (4 bytes): Signed integer "i" (4 bytes)
    # 2. psecret (4 bytes): Signed integer "i" (4 bytes)
    # 3. step (2 bytes): Short integer "h" (2 bytes)
    # 4. sid (2 bytes): Short integer "h" (2 bytes) 
    payload_len, psecret, step, sid = unpack('>iihh', message[:HEADER_SIZE])
    payload = message[HEADER_SIZE:]
    
    # Verify payload and header
    if (payload != expected_payload.encode('utf-8') or
            len(payload) != len(expected_payload) or
            expected_message_len != len(message)):
        print("Payload or header verification failed. Closing connection.")
        return
    
    # Pass test, generate random numbers for response
    num = random.randint(1, 16)
    ln = random.randint(8, 256)
    udp_port = random.randint(10000, 20000)
    secretA = random.randint(1, 1024)
    
    # Pack response
    # >: Big-endian (most significant byte first)
    # 1. Headers: iihh, same as packet received
    # 2. num, len, udp_port, secretA: all 4 bytes, Signed integer "i" (4 bytes)
    response = pack('>iihhiiii', 12, psecret, SERVER_STEP, sid, num, ln, udp_port, secretA)

    # Send response
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    try:
        sock.sendto(response, client_ip)
        print("Stage A response sent.")
    except socket.timeout:
        print("Timeout while sending response. Closing connection.")
    finally:
        sock.close()
    print("Stage A done!")

    # Stage B
    print("Stage B start")
    payload_of_length_len = ln + 4
    while (payload_of_length_len % 4 != 0):
        payload_of_length_len += 1

    expected_message_len = HEADER_SIZE + payload_of_length_len
    num_received = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create socket before sending the response or after? 
    sock.bind((SERVER_HOST, udp_port))
    sock.settimeout(TIMEOUT)

    try:
        while num_received < num:
            message, client_address = sock.recvfrom(BUFFER_LEN)
            payload_len, psecret, step, sid, pid = unpack('>iihhi', message[:HEADER_SIZE+4])
            payload = message[HEADER_SIZE+4:]
            
            # Verification
            if psecret != secretA:
                print("Secret verification failed. Closing connection.")
                return
            # if payload_len != ln + 4 or len(payload) != ln:    # TODO: Test failed -> discuss
            #     print("Payload length verification failed. Closing connection.")
            #     return
            if len(message) != expected_message_len:
                print("Packet length verification failed. Closing connection.")
                return
            if step != 1:
                print("Step count verification failed. Closing connection.")
                return
            all_zeros = all(byte == 0 for byte in payload)
            if not all_zeros:
                print("Payload contents verification failed. Closing connection.")
                return

            # Send acknowledgment
            if random.random() < 0.95:  # 95% chance of sending an ack
                response = pack('>iihhi', 4, psecret, SERVER_STEP, sid, num_received)
                sock.sendto(response, client_ip)
                num_received += 1
    
        # Send TCP port number and secretB
        tcp_port = random.randint(10000, 20000)
        secretB = random.randint(1, 1024)
        response = pack('>iihhii', 8, psecret, SERVER_STEP, sid, tcp_port, secretB)
        sock.sendto(response, client_ip)
        print("Stage B response sent.")
    except socket.timeout:
        print("Timeout while waiting for packets.")
    finally:
        sock.close()
        print("Stage B done!")

    # Stage C
    print("Stage C start")
