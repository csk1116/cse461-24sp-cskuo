from utils import *

def stage_c(tcp_socket):
    print("Stage C: Receiving package via TCP")
    data = receive_tcp_message(tcp_socket)
    # data would be 28 bytes because of the padding
    # c char is the fourth-to-the-last byte
    num2, len2, secret_c, char_c = parse_tcp_response(data[12:-3], '!IIIc')
    return num2, len2, secret_c, char_c
