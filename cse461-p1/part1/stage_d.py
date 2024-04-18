from utils import *
from config import *

def stage_d(tcp_socket, num2, len2, secretC, char_c):
    print("Stage D: Sending multiple packet and receiving packet via TCP")
    header = generate_header(len2, secretC, STEP, STUDENT_ID)
    packet = create_stage_d_packet(header, char_c, len2)
    # send num2 packet
    for i in range(num2):
        send_tcp_packet(tcp_socket, packet)
        print(f"Packet {i} was sent.")
    # receive secretD
    data = receive_tcp_message(tcp_socket)
    secret_d = parse_tcp_response(data[12:], '!I')
    return secret_d

