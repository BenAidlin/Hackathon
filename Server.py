import socket
from datetime import datetime
import threading
from scapy.arch import get_if_addr,get_if_list
import time
from threading import * #Thread, acquire
import struct
from Extensions import Colors, MathProblems

class Server:
    link_proto = 'eth1'
    buff_size = 1024
    def __init__(self):
        self.udp_port = 13117

        #Message format
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.udp_format = 'IbH'
        self.ip = None
        try: # hackathon lab
            self.ip = get_if_addr("eth1")
        except: # private machine
            self.ip = socket.gethostbyname(socket.gethostname())
        self.keep_broadcasting = True
        self.lock_team_dict = threading.Lock()
        self.teams_details = {}
        self.lock_answer = threading.Lock()
        self.team_win = None
        self.game_started = False

        #Create a new UDP server socket
        self.broad_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broad_socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        split_ip = self.ip.split('.')
        split_ip[len(split_ip)-1] = '255'
        split_ip[len(split_ip)-2] = '255'
        self.subnet_broadcast_ip = '.'.join(split_ip)
        
        #Create a new TCP server socket
        self.welcome_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.welcome_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.welcome_tcp_socket.bind((self.ip, 0))
        self.tcp_port = self.welcome_tcp_socket.getsockname()[1]

    def send_broadcast(self):
        print(Colors.OKBLUE + "Server started, listening on IP address " + self.ip)
        message = struct.pack(self.udp_format, self.magic_cookie, self.message_type, self.tcp_port)
        while self.keep_broadcasting:
            self.broad_socket.sendto(message, (self.subnet_broadcast_ip, self.udp_port))
            time.sleep(1)

    def welcome_clients(self):
        self.welcome_tcp_socket.settimeout(10)
        timeout = time.time() + 10.0
        self.welcome_tcp_socket.listen()
        lst = []
        while True:
            try:    
                if(time.time()>timeout):
                    raise socket.timeout()            
                (client_socket,(client_ip, client_port)) = self.welcome_tcp_socket.accept()
                t = Thread(target=self.handle_client, args=(client_socket,client_ip, client_port), daemon=True)
                lst.append(t)   
                t.start()
            except socket.timeout:
                for t in lst:
                    t.join()
                self.game_started = True
                if len(self.teams_details.keys()) < 2:
                    for team_name, details in self.teams_details.items():
                        details[0].shutdown(socket.SHUT_RD)
                        details[0].close()
                        print(team_name + " was close")
                    self.game_started = False
                    self.teams_details = {}
                print(Colors.WARNING + 'Temporarily not acceptig clients')
                break
        self.keep_broadcasting = False
        print("------------")
        

    def handle_client(self,client_socket,client_ip, client_port):
        team_name = client_socket.recv(Server.buff_size).decode()
        self.lock_team_dict.acquire()
        if len(self.teams_details.keys()) < 2:
            self.teams_details[team_name] = [client_socket,client_ip, client_port]
        else:
            sorry_string = Colors.WARNING + 'Sorry '+team_name+', too many players'
            client_socket.send(sorry_string.encode('utf-8'))
            client_socket.shutdown(socket.SHUT_RD)
            client_socket.close()
        self.lock_team_dict.release()
    
    def start_game(self):
        if not self.game_started: # TODO: handle with 1 good connection
            print(Colors.WARNING + "Not enough players.. Cant start game. Disconnecting...")
            return
        lst = []
        problem, solution = MathProblems.generate_problem()
        for team_name, details in self.teams_details.items():
            t = Thread(target=self.send_question, daemon=True,args=[team_name,details,problem,solution])
            t.start()
            lst.append(t)
        for t in lst:
            t.join()

    def send_question(self,team_name, details, problem, solution):
        details[0].settimeout(10)
        try:
            welcome_string = Colors.OKCYAN + "Welcome to Quick Maths.\nPlayer 1: " + list(self.teams_details.keys())[0] \
                + "\nPlayer 2: " + list(self.teams_details.keys())[1] \
                    + "\n==\nPlease asnwer the following question as fast as you can:\n" \
                        + "How mush is " + problem + "?" 
            details[0].send(welcome_string.encode('utf-8'))
            answer = details[0].recv(Server.buff_size).decode('utf-8')
            self.lock_answer.acquire()
            if(self.team_win is None):
                # I answered first
                if(str(answer) == solution):
                    self.team_win = team_name
                else:
                    self.team_win = [i for i in self.teams_details.keys() if i!=team_name][0]
                over_string = Colors.OKGREEN + "Game over!\nThe correct answer was " \
                    + solution + "!\n\nCongratulations to the winner: " \
                    + str(self.team_win)
                for team_name, conn in self.teams_details.items():
                    conn[0].send(over_string.encode('utf-8'))
            self.lock_answer.release()
        except socket.timeout:
            print(Colors.WARNING+'timeout')
        except: 
            pass
    def finish_game(self):
        for team_name, conn in self.teams_details.items():
            try:
                conn[0].shutdown(socket.SHUT_RD)
                conn[0].close()
            except:
                pass
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.udp_format = 'IbH'
        self.keep_broadcasting = True
        self.lock_team_dict = threading.Lock()
        self.teams_details = {}
        self.lock_answer = threading.Lock()
        self.team_win = None
        self.game_started = False

        #Create a new UDP server socket
        self.broad_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broad_socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        

    def activate_server(self):
        while True:
            t1 = Thread(target=self.send_broadcast, daemon=True)
            t2 = Thread(target=self.welcome_clients, daemon=True)

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            self.start_game()
            self.finish_game()
            


server = Server()
server.activate_server()
        



