import sys
import socket
import threading

from handle_client import handle_client

# Define constants for the server
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 1337  # Random port
BUFFER_LEN = 1024


# Function to start the server
def start_server():
    server_name = sys.argv[1]
    port = int(sys.argv[2])

    print("start server...")
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Bind the socket to the host and port
        # server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.bind((server_name, port))
        
        # Listen for incoming connections
        print(f"[*] Listening on {server_name}:{port}")
        
        try:
            while True:
                # Receive UDP packet for stage_a
                message, client_address = server_socket.recvfrom(BUFFER_LEN)  # This function won't create a new socket for client, since it's a UDP connection
                print(f"[*] Received stage a packet from {client_address[0]}:{client_address[1]}")
                
                # Create a new thread to handle the client
                client_thread = threading.Thread(target=handle_client, args=(message, client_address))
                client_thread.start()
        except KeyboardInterrupt:
            print("\n[*] Server shutting down...")
    finally:
        # Close the server socket even under interruption
        server_socket.close()

if __name__ == "__main__":
    start_server()
