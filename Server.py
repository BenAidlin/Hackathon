import socket
from datetime import datetime
import threading
from scapy.arch import get_if_addr
import time
from threading import * #Thread, acquire
import struct

class Server:
    link_proto = 'eth1'
    buff_size = 1024
    def __init__(self, tcp_port):
        self.udp_port = 13117
        self.tcp_port = tcp_port

        #Message format
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.udp_format = 'IbH'
        #Create a new UDP server socket
        #family - IVP4 addresses, type - UDP protocol
        self.broad_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broad_socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        self.ip =  socket.gethostbyname(socket.gethostname()) #get_if_addr("eth1") 
        self.keep_broadcasting = True
        #self.broad_socket.bind(('', self.udp_port))
        self.welcome_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.welcome_tcp_socket.bind((self.ip, self.tcp_port))
        self.lock_team_dict = threading.Lock()
        self.teams_details = {}


    def send_broadcast(self):
        now = datetime.now()
        print("Server started, listening on IP address " + self.ip)
        message = struct.pack(self.udp_format, self.magic_cookie, self.message_type, self.tcp_port)
        while self.keep_broadcasting:
            self.broad_socket.sendto(message, ('<broadcast>', self.udp_port))
            time.sleep(1)

    def welcome_clients(self):
        self.welcome_tcp_socket.settimeout(1000)
        self.welcome_tcp_socket.listen()
        lst = []
        while len(self.teams_details.keys()) < 2:
            try:
                (client_socket,(client_ip, client_port)) = self.welcome_tcp_socket.accept()
                t = Thread(target=self.handle_client, args=(client_socket,client_ip, client_port), daemon=True)
                t.start()
                lst.append(t)
            except socket.timeout:
                self.keep_broadcasting = False
                break
        for t in lst:
            t.join()
        
        

    def handle_client(self,client_socket,client_ip, client_port):
        team_name = client_socket.recv(Server.buff_size).decode()
        print(team_name)
        self.lock_team_dict.acquire()
        if len(self.teams_details.keys()) < 2:
            self.teams_details[team_name] = [client_socket,client_ip, client_port]
        self.lock_team_dict.release()
    
    def init_server(self):
        while True:
            t1 = Thread(target=self.send_broadcast, daemon=True)
            t2 = Thread(target=self.welcome_clients, daemon=True)

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            # self.game_mode()

            # time.sleep(10)
            # self.is_palying = False

            # self.finish_game()





server = Server(18121)
server.init_server()
        



