
""" Copyright 2024 Wayne Huang, Vincent Wang, and Eric Kuo
    UW CSE 461 course lab 1 
"""

import sys
import socket
import struct
from stage_a import stage_a
from stage_b import stage_b
from config import *
from utils import *

def main():
    if len(sys.argv) != 3:
        print("Usage: ./run_client.sh <server name> <port>")
        return

    server_name = sys.argv[1]
    port = int(sys.argv[2])

    # Stage A
    num, length, udp_port, secretA = stage_a(server_name, port)
    print(f"Stage A: num={num}, len={length}, udp_port={udp_port}, secretA={secretA}")

    # Stage B
    tcp_port, secretB = stage_b(server_name, udp_port, num, length)
    print(f"Stage B: tcp_port={tcp_port}, secretB={secretB}")


if __name__ == "__main__":
    main()
