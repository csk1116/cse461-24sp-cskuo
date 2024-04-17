from utils import *
from config import *

def stage_b(server_host, initial_udp_port, num, length, secret):
    print("Stage B: Seding multiple package via UDP")
    with create_udp_socket() as sock:
        sock.settimeout(2.0)
        # Step b1: Send multiple packets
        for i in range(num):
            packet = create_packet(i, length)
            send_udp_message(sock, server_host, initial_udp_port, packet, psecret=secret, step=1, student_no=STUDENT_ID)

            # wait for ACK
            while True:
                try:
                    data = receive_udp_message(sock)
                    ack_id = parse_udp_response(data[12:], '!I')
                    print(f"Received from server: ack_num={ack_id[0]}")
                    break
                except socket.timeout:
                    # Send packet again
                    send_udp_message(sock, server_host, initial_udp_port, packet, psecret=secret, step=1, student_no=STUDENT_ID)
                    
                
        # Step b2: Receive the final response
        sock.settimeout(None)
        data = receive_udp_message(sock)
        tcp_port, secretB = parse_udp_response(data[12:], '!II')
        sock.close()
        return tcp_port, secretB