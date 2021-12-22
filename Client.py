import socket
class Client:
    def __init__(self):
        self.udp_port = 13117
        self.tcp_port = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(("",self.udp_port))
        #Message format
        self.magicCookie = 0xabcddcba
        self.message_type = 0x2
    def find_server(self):
        print("shahar")
        while True:
            try:
                data, address = self.udp_socket.recvfrom(1024)
                print(data)
                print(address)
            except:
                print("except")

client = Client()
client.find_server()