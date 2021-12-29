import socket
import struct
from threading import *
from multiprocessing import Process
try: # hackathon lab
    import getch as gc
except: #private machine
    import msvcrt as gc


class Client:
    def __init__(self):
        self.udp_port = 13119
        self.tcp_port = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(("",self.udp_port))
        #Message format
        self.udp_format = 'IbH'
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.conn_tcp = None
        self.team_name = "Client 2"
        self.is_playing = False


    def find_server(self):
        while True:
            try:
                data, address = self.udp_socket.recvfrom(1024)
                message = struct.unpack(self.udp_format, data)
            except struct.error:
                return 
            if message[0] == self.magic_cookie and message[1] == self.message_type:
                print(f"Received offer from {address[0]}, attempting to connect...")
                break
        return address, message

    def tcp_connect_to_game(self, ip_server, port_server):
        try:
            self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn_tcp.connect((ip_server, port_server))
        except Exception as e:
            print(f"Connection failed , reconnecting ...")
            # if connection is failed changes the variable is_playing
            self.is_playing = False
            return
        self.is_playing = True
        return

    def game_mode(self):        
        # question = self.conn_tcp.recv(1024).decode()
        # print(question)        
        while True:
            try:
                input = str(gc.getch().decode()) #sys.stdin.read(1)
                if input=='c':
                    print("Stop recieving input")
                    return
                self.conn_tcp.send((input).encode('utf-8'))
            except:
                print("No connection to server")
        

    def recv_msgs(self):
        while self.is_playing:
            try:
                message = self.conn_tcp.recv(1024)
            except:
                print("Server disconnected, listening for offer requestes...")
                self.is_playing = False
                return
            if not message:
                print("Server disconnected, listening for offer requestes...")
                self.is_playing = False
                return
            print(message.decode())
         
    def finish_game(self):
        self.conn_tcp.close()
        self.conn_tcp = None

    def activate_client(self):
     
        while True:
            tup = client.find_server()
            if not tup:
                continue
            address, message = tup
            self.tcp_connect_to_game(address[0], int(message[2]))
            if self.is_playing:
                # send client name's team for the game
                self.conn_tcp.send(self.team_name.encode('utf-8'))
                t1 = Thread(target=self.recv_msgs, daemon=True)
                t2 = Process(target=self.game_mode, daemon=True)
                t2.start()   
                t1.start()
                
                t1.join()
                #t2.join(5)

        client.finish_game()


client = Client()
client.activate_client()