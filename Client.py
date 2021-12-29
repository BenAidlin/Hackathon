import socket
import struct
from threading import *
from multiprocessing import Process, Value
from Extensions import GeorgianFood
try: # hackathon lab
    import getch as gc
except: #private machine
    import msvcrt as gc
import time

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
        self.team_name = GeorgianFood.get_random_georgian_dish()
        print("Player name: " + self.team_name)
        self.is_playing = False
        self.input = Value('i', -1) # shared value between processes

    def find_server(self):
        while True:
            try:
                data, address = self.udp_socket.recvfrom(1024)
                message = struct.unpack(self.udp_format, data)
            except struct.error:
                return 
            if message[0] == self.magic_cookie and message[1] == self.message_type: # found!!
                print(f"Received offer from {address[0]}, attempting to connect...")
                break
        return address, message

    def tcp_connect_to_game(self, ip_server, port_server):
        try: # connecting to the server who was broadcasting
            self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn_tcp.connect((ip_server, port_server))
        except Exception as e: # something wrong.. server disconnected?
            print(f"Connection failed , reconnecting ...")
            # if connection is failed changes the variable is_playing
            self.is_playing = False
            return
        self.is_playing = True # succeded! lets play...
        return

    def get_input(self):                 
        while True: # listen for input
            get = str(gc.getch()) 
            if get=='c': # this is mainly to allow us to break the process from terminal
                print("Stop recieving input")
                return
            try: # try converting to int. if successfull, assign to shared field self.input
                self.input.value = int(get)    
            except: 
                print("Invalid number")
                            
    def listen_to_input(self):
        # on main process, always expect users input. sleep every 0.5 sec
        while True:
            if(self.input.value==-1): # no user input
                time.sleep(0.5)
            else:
                try: # sending input to server
                    self.conn_tcp.send((str(self.input.value)).encode('utf-8'))
                    print("Sent to server")
                except: # server disconnected ?
                    print("No connection to server")
                finally: # return to no input state
                    self.input.value=-1

    def recv_msgs(self):
        # only while in game mode, be prepared to recieve messages
        while self.is_playing:
            try:
                message = self.conn_tcp.recv(1024)
            except: # in game mode but crashed - server disconnected
                print("Server disconnected, listening for offer requestes...")
                self.is_playing = False
                return
            if not message: # message not in format
                print("Server disconnected, listening for offer requestes...")
                self.is_playing = False
                return
            print(message.decode()) # shiw the message to user
         
    def finish_game(self):
        # wrap up the game - close the connection with server
        # udp - keep open, continue listening right after
        self.conn_tcp.close()
        self.conn_tcp = None

    def activate_client(self):
        # independantly from main process - allow user input and save in inter process shared field
        get_input_process = Process(target=self.get_input, daemon=True)
        get_input_process.start()
        # also, listen in main thread if the shared field is being changed
        listen_to_input_thread = Thread(target=self.listen_to_input, daemon=True)
        listen_to_input_thread.start()   
        while True:
            tup = client.find_server()
            if not tup: # couldn't find appropriate server
                continue
            address, message = tup
            self.tcp_connect_to_game(address[0], int(message[2]))
            if self.is_playing: # successfull connection
                # send user team name to the server.
                self.conn_tcp.send(self.team_name.encode('utf-8'))
                # start recieving messages!! this is game mode!!
                t1 = Thread(target=self.recv_msgs, daemon=True)
                t1.start()        
                t1.join()

            client.finish_game()


client = Client()
client.activate_client()