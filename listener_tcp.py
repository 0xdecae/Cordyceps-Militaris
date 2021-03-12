# Main imports
import socket
import sys
import os
import signal
import threading
import queue
import time

from handler import Handler

class Listener_TCP(threading.Thread):
    def __init__(self, lhost, lport, agentList, loggers):
        threading.Thread.__init__(self)
        self.lhost = lhost
        self.lport = lport
        self.agentList = agentList
        self.loggers = loggers

        self.max_connections = 1000

    def run(self):

        # Initial socket setup
        try:
            print(f"[* Listener-Msg] Initializing TCP socket on tcp://{self.lhost}:{self.lport}")
            loggers[0].q_log('serv','info',f"[* Listener-Msg] Initializing TCP socket on tcp://{self.lhost}:{self.lport}")

            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_address = (self.lhost, self.lport)

            print(f"[* Listener-Msg] Binding tcp://{self.lhost}:{self.lport} to socket")
            loggers[0].q_log('serv','info',f"[* Listener-Msg] Binding tcp://{self.lhost}:{self.lport} to socket")
            server.bind(server_address)

            print(f"[* Listener-Msg] Listening for {self.max_connections} connections")
            loggers[0].q_log('serv','info',f"[* Listener-Msg] Listening for {self.max_connections} connections")            
            server.listen(self.max_connections)

        except Exception as ex:
            print("[* Listener-Msg] Fatal error with socket initialization")
            loggers[0].q_log('serv','critical','[* Listener-Msg] Fatal error with socket initialization')
            print(f"[* Listener-Msg] Error: {ex}")
            loggers[0].q_log('serv','critical',f'[* Listener-Msg] Error: {str(ex)}')
            os._exit(0)

        print(f"[* Listener-Msg] TCP listener initialized on tcp://{self.lhost}:{str(self.lport)}")
        loggers[0].q_log('serv','info',f"[* Listener-Msg] TCP listener successfully initialized on tcp://{self.lhost}:{str(self.lport)}")            

        loggers[0].q_log('serv','info',f"[* Listener-Msg] Initializing TCP connection record")            
        connRecord = 0                                         # Records Connection ID

        while True:

            (client, client_address) = server.accept()

            print(f"\n[* Listener-Msg] Connection received from {str(client_address[0])}\n")
            loggers[0].q_log('serv','info',f"[* Listener-Msg] Connection received from {str(client_address[0])}")            

            loggers[0].q_log('serv','info',f"[* Listener-Msg] Creating a new Handler thread for {str(client_address[0])}")            
            newConn = Handler(client, client_address, connRecord, self.loggers)
            newConn.start()

            self.agentList.append(newConn)
            connRecord += 1