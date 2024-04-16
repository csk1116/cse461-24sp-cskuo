
""" Copyright 2024 Wayne Huang, Vincent Wang, and Eric Kuo
    UW CSE 461 course lab 1 
"""

import sys
import socket
import struct


SERVER_HOST1 = "attu2.cs.washington.edu"
SERVER_HOST2 = "attu3.cs.washington.edu"
SERVER_PORT = 41201

STEP = 1
STUDENT_ID = 860

def main():
    if len(sys.argv) != 3:
        print("Usage: ./run_client.sh <server name> <port>")
        return

    server_name = sys.argv[1]
    port = int(sys.argv[2])

if __name__ == "__main__":
    main()
