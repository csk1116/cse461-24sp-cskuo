
# Copyright 2024 Wayne Huang, Vincent Wang, and Eric Kuo
# UW CSE 461 course lab1-part1

import sys
from config import *
from utils import *
from stage_a import stage_a
from stage_b import stage_b
from stage_c import stage_c
from stage_d import stage_d

def main():
    server_name = sys.argv[1]
    port = int(sys.argv[2])

    # Stage A
    num, length, udp_port, secretA = stage_a(server_name, port)
    print(f"Stage A: num={num}, len={length}, udp_port={udp_port}, secretA={secretA}")

    # Stage B
    tcp_port, secretB = stage_b(server_name, udp_port, num, length, secretA)
    print(f"Stage B: tcp_port={tcp_port}, secretB={secretB}")

    # tcp socket
    with create_tcp_socket() as tcp_socket:
        tcp_socket.settimeout(5.0)
        tcp_socket.connect((server_name, tcp_port))

        # Stage C
        num2, len2, secretC, char_c = stage_c(tcp_socket)
        print(f"Stage C: num2={num2}, len2={len2}, secretC={secretC}, c={char_c}")

        # Stage D
        secretD = stage_d(tcp_socket, num2, len2, secretC, char_c)
        print(f"Stage D: secretD={secretD[0]}")

        tcp_socket.close()

if __name__ == "__main__":
    main()
