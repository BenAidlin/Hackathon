import socket
from datetime import datetime
import threading
from scapy.arch import get_if_addr,get_if_list
import time
from threading import * #Thread, acquire
import struct

class Server:
    link_proto = 'eth1'
    buff_size = 1024
    def __init__(self):
        self.udp_port = 13117

        #Message format
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.udp_format = 'IbH'
        #Create a new UDP server socket
        #family - IVP4 addresses, type - UDP protocol
        self.broad_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broad_socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
<<<<<<< HEAD
        self.ip = get_if_addr("eth1") # socket.gethostbyname(socket.gethostname()) #get_if_addr("eth1") 
=======
        self.ip = socket.gethostbyname(socket.gethostname()) #get_if_addr("eth1") # TODO
        # interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        # self.ip = [ip[-1][0] for ip in interfaces][1]

>>>>>>> 9043dc1bc4c1b77f65e661d9b914c8fa05d16f4f
        self.keep_broadcasting = True
        #self.broad_socket.bind(('', self.udp_port))
        self.welcome_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.welcome_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.welcome_tcp_socket.bind((self.ip, self.tcp_port))
        self.welcome_tcp_socket.bind((self.ip, 0))
        self.tcp_port = self.welcome_tcp_socket.getsockname()[1]
        self.lock_team_dict = threading.Lock()
        self.teams_details = {}
        split_ip = self.ip.split('.')
        split_ip[len(split_ip)-1] = '255'
        self.subnet_broadcast_ip = '.'.join(split_ip)
        self.lock_answer = threading.Lock()
        self.team_win = None

    def send_broadcast(self):
        print("Server started, listening on IP address " + self.ip)
        message = struct.pack(self.udp_format, self.magic_cookie, self.message_type, self.tcp_port)
        while self.keep_broadcasting:
            self.broad_socket.sendto(message, (self.subnet_broadcast_ip, self.udp_port))
            time.sleep(1)

    def welcome_clients(self):
        self.welcome_tcp_socket.settimeout(10)
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
        #print(team_name)
        self.lock_team_dict.acquire()
        if len(self.teams_details.keys()) < 2:
            self.teams_details[team_name] = [client_socket,client_ip, client_port]
        self.lock_team_dict.release()
    
    def start_game(self):
        if len(self.teams_details.keys()) < 1: # TODO: handle with 1 good connection
            print("walla meztaer ach sheli")
            return
        for team_name, details in self.teams_details.items():
            Thread(target=self.send_question, daemon=True,args=[team_name,details]).start()

    def send_question(self,team_name, details):
        details[0].settimeout(10)
        try:
            welcome_string = "Welcome to Quick Maths.\nPlayer 1: " + list(self.teams_details.keys())[0] \
                + "\nPlayer 2: " + list(self.teams_details.keys())[1] \
                    + "\n==\nPlease asnwer the following question as fast as you can:\n" \
                        + "How mush is " + "2+2" + "?" 
            details[0].send(welcome_string.encode('utf-8'))
            answer = details[0].recv(Server.buff_size).decode()
            self.lock_answer.acquire()

            if(self.team_win is None):
                # i answered first
                if(answer == "4"):
                    self.team_win = team_name
                else:
                    self.team_win = [i for i in self.teams_details.keys() if i!=team_name][0]
            self.lock_answer.release()
        except socket.timeout:
            pass
        over_string = "Game over!\nThe correct answer was " + "4" + "!\n\nCongratulations to the winner: " \
            + self.team_win 
        details[0].send(over_string.encode('utf-8'))
    

    def activate_server(self):
        while True:
            t1 = Thread(target=self.send_broadcast, daemon=True)
            t2 = Thread(target=self.welcome_clients, daemon=True)

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            self.start_game()

            # time.sleep(10)
            # self.is_palying = False

            # self.finish_game()





server = Server()
server.activate_server()
        



