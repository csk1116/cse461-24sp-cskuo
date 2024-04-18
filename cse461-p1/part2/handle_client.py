import struct
import random
import socket
from struct import pack, unpack
import time
import string

# Define protocol-specific constants
TIMEOUT = 3.0
HEADER_SIZE = 12
BUFFER_LEN = 1024
SERVER_STEP = 2

def validate_header(header, p_length, psecret, sid):
    payload_len, secret, step, id = unpack('!IIHH', header)

    if (len(header) != 12 or
        payload_len != p_length or
        secret != psecret or
        step != 1 or
        id != sid):
        return False
    return True

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
            expected_message_len != len(message) or 
            step != 1 or psecret != 0):
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
    response = pack('>iihhiiii', 16, psecret, SERVER_STEP, sid, num, ln, udp_port, secretA)

    # Send response
    sender_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_sock.settimeout(TIMEOUT)

    try:
        sender_sock.sendto(response, client_ip)
        print("Stage A response sent.")
    except sender_sock.timeout:
        print("Timeout while sending response. Closing connection.")
    finally:
        sender_sock.close()
    print("Stage A done!")

    # Stage B
    # Create server socket, waiting for request
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', udp_port))
    sock.settimeout(TIMEOUT)

    print("Stage B start")
    payload_of_length_len = ln + 4
    while (payload_of_length_len % 4 != 0):
        payload_of_length_len += 1

    expected_message_len = HEADER_SIZE + payload_of_length_len
    num_received = 0

    try:
        while num_received < num:
            message, client_address = sock.recvfrom(BUFFER_LEN)
            payload_len, psecret, step, sid, pid = unpack('>iihhi', message[:HEADER_SIZE+4])
            payload = message[HEADER_SIZE+4:]
            
            # Verification
            if psecret != secretA:
                print("Secret verification failed. Closing connection.")
                return
            if payload_len != ln + 4:
                print("Payload length verification failed. Closing connection.")
                return
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
                print(f"Send ack_num = {num_received}")
                response = pack('>iihhi', 4, secretA, SERVER_STEP, sid, num_received)
                sock.sendto(response, client_address)
                num_received += 1
    
        # check if that port can be used first!!!
        # Send TCP port number and secretB
        global tcp_port
        tcp_port = random.randint(10000, 20000)
        secretB = random.randint(1, 1024)
        response = pack('>iihhii', 8, psecret, SERVER_STEP, sid, tcp_port, secretB)
        sock.sendto(response, client_address)
        print("Stage B response sent.")
    except socket.timeout:
        print("Timeout while waiting for packets.")

    finally:
        sock.close()
        print("Stage B done!")

    # Stage C
    print("Stage C start")

    # tcp
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.settimeout(3.0)
    tcp_socket.bind(('', tcp_port))
    tcp_socket.listen(1)
    stage_c_socket, addr_c = tcp_socket.accept()

    num2 = random.randint(1,20)
    length2 = random.randint(1,20)
    secret_c = random.randint(100,1000)
    char_c = random.choice(string.ascii_letters).encode('ascii')
    print(f"Stage C Sent: num2={num2}, len2={length2}, secretC={secret_c}, c={char_c}")

    try:
        header = bytearray()
        header.extend(struct.pack('!IIHH', 13, secretB, SERVER_STEP, sid))
        packet = header + struct.pack('!IIIc', num2, length2, secret_c, char_c)
        while len(packet) % 4:
            packet += b'\0'
        
        stage_c_socket.send(packet)
        print("Stage C done!")

        # Stage D
        print("Stage D start")
        expected_len = HEADER_SIZE + length2
        while expected_len % 4:
            expected_len += 1

        for i in range(num2):
            packet_d = stage_c_socket.recv(BUFFER_LEN)
            # validate packet 
            if len(packet_d) != expected_len:
                print("Packet validation failed in Stage D.")
                return
            # validate header
            if not validate_header(packet_d[:12], length2, secret_c, sid):
                print("Header validation failed in Stage D.")
                return
            # validate payload
            payload = packet_d[12:]
            for byte in payload[:length2]:
                if byte != ord(char_c):
                    print("Payload validation failed in Stage D.")
                    return
            # validate padding
            for byte in payload[length2:]:
                if byte != 0:
                    print("Padding validation failed in Stage D.")
                    return
                
            print(f"packet {i} received")
        
        # send final packet: secret D
        secret_d = random.randint(100,1000)
        print(f"Stage D sent: secretD={secret_d}")

        header = bytearray()
        header.extend(struct.pack('!IIHH', 4, secret_c, SERVER_STEP, sid))
        packet = header + struct.pack('!I', secret_d)
        stage_c_socket.send(packet)

    except socket.timeout:
        print("Timeout while waiting for packets.")

    finally:
        tcp_socket.close()
        stage_c_socket.close()
        print("Stage D done!")
