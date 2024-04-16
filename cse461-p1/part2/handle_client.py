import struct
import random
import socket
import time

# Define protocol-specific constants
TIMEOUT = 3
HEADER_SIZE = 12


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
    response = pack('>iihhiiii', 12, presecret, server_step, sid, num, ln, udp_port, secretA)
    server_step += 1

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

    # Stage A completed
    print("Stage A done!")

    # Stage B
    print("Stage B start")
    
