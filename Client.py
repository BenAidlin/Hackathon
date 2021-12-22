import socket
import struct

class Client:
    def __init__(self):
        self.udp_port = 13117
        self.tcp_port = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(("",self.udp_port))
        #Message format
        self.udp_format = 'IbH'
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.team_name = "Ben@Shahar"


    def find_server(self):
        print("shahar")
        while True:
            try:
                data, address = self.udp_socket.recvfrom(1024)
                message = struct.unpack(self.udp_format, data)
                print(data)
                print(address)
            except struct.error:
                print("except")
            if message[0] == self.magic_cookie and message[1] == self.message_type:
                print(f"Received offer from {address[0]}, attempting to connect...")
                break
        self.tcp_connect_to_game(address[0], int(message[2]))

    def tcp_connect_to_game(self, ip_server, port_server):
        try:
            self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn_tcp.connect((ip_server, port_server))
        except Exception as e:
            print(f" connection failed , reconnecting ...")
            # if connection is failed changes the variable is_playing
            self.is_palying = False
            return
        # send client name's team for the game
        self.conn_tcp.send(self.team_name.encode('utf-8'))
        # self.is_palying = True













client = Client()
client.find_server()