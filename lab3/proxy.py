import sys
import socket
import threading
import re

LOCAL_HOST = "127.0.0.1"
BUFF_SIZE = 256

def receive_full_header(sock):
    header = ""
    curr_line = ""
    while True:
        if header.endswith("\r\n\r\n") or header.endswith("\n\r\n"):
            break
        try:
            curr_line += sock.recv(1).decode()
        except socket.timeout:
            print("Didn't receive any data from this socket")
            sock.close()
            return None
        except socket.error:
            continue
        if curr_line.endswith("\n"):
            header += curr_line
            curr_line = ""
    return header

def parse_request(request_header):
    request_line = request_header.split('\r\n')[0]
    print(">>> " + request_line)
    request_parts = re.split(' |:', request_line)
    server_port = 80 # Default port for HTTP
    if len(request_parts) == 5:
        server_port = int(request_parts[3])
    elif len(request_parts) == 4 and request_parts[0] == "CONNECT":
        server_port = int(request_parts[2])
    elif request_parts[1].lower() == "https":
        server_port = 443 # Default port for HTTPS
    return request_line, server_port

def extract_server_details(header):
    server_name = ""
    server_port = 80 # Default port for HTTP
    for line in header.split('\r\n'):
        if "host" in line.lower():
            host_parts = re.split(' :|: |:', line)
            server_name = host_parts[1].strip()
            if len(host_parts) == 3:
                server_port = int(host_parts[2].strip())
            return server_name, server_port
    return server_name, server_port

def connect_to_server(server_name, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.connect((server_name, server_port))
    except Exception:
        print("Error connecting to server, sending 502 Bad Gateway")
        return None
    return server_socket

def handle_connect_request(client_socket, server_socket):
    client_socket.send("HTTP/1.0 200 OK\r\n\r\n".encode()) # Inform client of successful connection
    client_socket.settimeout(50)
    server_socket.settimeout(50)
    # Start threads to relay data between client and server
    send_thread = threading.Thread(target=relay_data, args=(client_socket, server_socket))
    receive_thread = threading.Thread(target=relay_data, args=(server_socket, client_socket))
    send_thread.start()
    receive_thread.start()

def relay_data(src_socket, dst_socket):
    while True:
        try:
            data = src_socket.recv(BUFF_SIZE)
        except socket.timeout:
            continue
        except (OSError, ConnectionAbortedError):
            break
        if not data:
            break
        try:
            dst_socket.send(data)
        except (OSError, ConnectionAbortedError):
            break

def forward_request(client_socket, server_socket, request, header):
    # Send the initial request and header to the server
    server_socket.send(request.encode())
    server_socket.send(header.encode())
    while True:
        try:
            data = client_socket.recv(BUFF_SIZE)
        except socket.error:
            break
        if not data:
            break
        server_socket.send(data)

def get_server_response(server_socket):
    response_header = receive_full_header(server_socket)
    if not response_header:
        return None
    return response_header

def send_response_to_client(client_socket, server_socket, response_header):
    client_socket.send(response_header.encode()) # Send the response header to the client
    while True:
        data = server_socket.recv(BUFF_SIZE)
        if not data:
            break
        client_socket.send(data) # Relay data from server to client

def handle_client(client_socket, client_address):
    header = receive_full_header(client_socket)
    if not header:
        return
    
    request, server_port = parse_request(header)
    server_name, server_port = extract_server_details(header)
    server_socket = connect_to_server(server_name, server_port)
    if not server_socket:
        client_socket.send("HTTP/1.0 502 Bad Gateway\r\n\r\n".encode())
        client_socket.close()
        return

    if "CONNECT" in request:
        handle_connect_request(client_socket, server_socket)
    else:
        forward_request(client_socket, server_socket, request, header)
        response_header = get_server_response(server_socket)
        if response_header:
            send_response_to_client(client_socket, server_socket, response_header)
        server_socket.close()
        client_socket.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 proxy.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((LOCAL_HOST, port))
    
    try:
        while True:
            server_socket.listen()
            client_socket, client_address = server_socket.accept()
            client_socket.setblocking(0) # Non-blocking mode
            # Create a new thread to handle the client connection
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
    except (KeyboardInterrupt, SystemExit):
        server_socket.close()
        sys.exit()

if __name__ == '__main__':
    main()
