import socket
import threading
import sys
import datetime

class ClientHandler(threading.Thread):
    def __init__(self, client_conn):
        threading.Thread.__init__(self)
        self.client_conn = client_conn

    def run(self):
        try:
            data = self.client_conn.recv(8192)
            if not data:
                return

            strings = data.decode(errors='ignore')
            http_version_idx = strings.find('HTTP/1.1')
            connection_idx = strings.find('keep-alive')
            second_connection_idx = strings.find('keep-alive', connection_idx + 10)

            forward_request = strings[0:http_version_idx + 7] + '0' + strings[http_version_idx + 8:connection_idx] + 'close'

            if second_connection_idx == -1:
                forward_request = forward_request + strings[connection_idx + 10:]
            else:
                forward_request = forward_request + strings[connection_idx + 10:second_connection_idx] + 'close' + strings[second_connection_idx + 10:]

            request, headers = strings.split('\r\n', 1)
            forward_port = 80
            forward_host = ""
            list_headers = headers.split('\r\n')
            for header in list_headers:
                if header.lower().startswith('host:'):
                    host_port = header.split(':')
                    if len(host_port) == 3:
                        forward_port = int(host_port[2])
                    forward_host = host_port[1].strip()

            request_word = request.split(' ')[0]
        except Exception as e:
            print("Error parsing request:", e)
            return

        print(datetime.datetime.now().strftime("%d %b %X"), '- >>>', request_word, forward_host, ':', forward_port)
        if request_word == 'CONNECT':
            self.connect_to_server(forward_port, forward_host)
        else:
            self.nonconnect_to_server(forward_port, forward_host, forward_request.encode())

    def connect_to_server(self, forward_port, forward_host):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            forward_ip = socket.gethostbyname(forward_host)
            sock.connect((forward_ip, forward_port))
            self.client_conn.send(b"HTTP/1.0 200 OK\r\n\r\n")
        except Exception as e:
            self.client_conn.send(b"HTTP/1.0 502 Bad Gateway\r\n\r\n")
            print("Failed to connect:", e)
            sock.close()
            return

        self.transfer_data(sock)

    def nonconnect_to_server(self, forward_port, forward_host, forward_request):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            forward_ip = socket.gethostbyname(forward_host)
            sock.connect((forward_ip, forward_port))
            sock.send(forward_request)

            while True:
                result = sock.recv(8192)
                if len(result) > 0:
                    self.client_conn.send(result)
                else:
                    break
        except Exception as e:
            print("Error in non-connect request:", e)
        finally:
            sock.close()

    def transfer_data(self, sock):
        self.client_conn.settimeout(0.5)
        sock.settimeout(0.5)
        while True:
            try:
                data = self.client_conn.recv(8192)
                if not data:
                    break
                sock.sendall(data)
            except socket.timeout:
                continue
            except Exception as e:
                print("Error in data transfer from client to server:", e)
                break

            try:
                data = sock.recv(8192)
                if not data:
                    break
                self.client_conn.sendall(data)
            except socket.timeout:
                continue
            except Exception as e:
                print("Error in data transfer from server to client:", e)
                break
        sock.close()
        self.client_conn.close()

if __name__ == '__main__':
    tcp_port = int(sys.argv[1])
    
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind(("127.0.0.1", tcp_port))
    proxy_socket.listen(200)
    print(datetime.datetime.now().strftime("%d %b %X"), '- Proxy listening on 127.0.0.1:', tcp_port)

    while True:
        try:
            client_conn, client_addr = proxy_socket.accept()
            handler = ClientHandler(client_conn)
            handler.daemon = True
            handler.start()
        except (KeyboardInterrupt, SystemExit):
            proxy_socket.close()
            sys.exit()
    proxy_socket.close()

