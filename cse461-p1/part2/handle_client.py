import struct
import random
import time

# Define protocol-specific constants
HEADER_SIZE = 4  # Size of the packet header in bytes
TIMEOUT = 3

# Function to handle each client connection
def handle_client(client_socket):
    # Set timeout for receiving data
    client_socket.settimeout(TIMEOUT)
    