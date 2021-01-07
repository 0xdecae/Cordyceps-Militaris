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

interpreters = []               # Literally only here to access outside of MAIN

listeners = []                  # Handles all listeneing threads (TCP, HTTP, DNS, etc...)
                                # Ensuring that information can be passed between them and allowing for easier management

# -------------------------------------------------------------------------------------------

# TODO
#      - Test Kill function


# Catch CTRL-C
def catchSIGINT(signum, frame):

    print(f"\n[* Server-Msg] Please exit gracefully!")
    print(f"[* Server-Msg] Either use the EXIT command or EXIT whatever mode you are interacting in.")
    print(f"[* Server-Msg] Ungraceful exit behavior causes shells and connections to break...")

    try:
        signal.signal(signal.SIGINT, original_sigint)

        check = input(f"[* Server-Msg] Would you like to proceed and kill the program? (Y/n): ")

        if check.casefold() == 'y':
            print(f"[* Server-Msg] HEATHEN!!!\n")
            if(interpreters):
                interpreters[0].exit()
            else:
                os._exit(0)
    except KeyboardInterrupt:
        print(f"[* Server-Msg] HEATHEN!!!\n")

    signal.signal(signal.SIGINT, catchSIGINT)
        
def logger()

def main():

    if (len(sys.argv) < 3):
        print(f"[* Server-Msg] Usage:\n  [+] python3 {sys.argv[0]} <LHOST> <LPORT>\n  [+] Eg.: python3 {sys.argv[0]} 0.0.0.0 1337\n")
    else:
        try:
            lhost = sys.argv[1]
            lport = int(sys.argv[2])

            TCP_Thread = Listener_TCP(lhost, lport, agentList)
            TCP_Thread.start()
            listeners.append(TCP_Thread)

            time.sleep(1)

            InterpreterThread = Interpreter(agentList, listeners)          # Handles interface, queue is for commands
            InterpreterThread.start()
            interpreters.append(InterpreterThread)
        except Exception as ex:
            print(f"[* Server-Msg] Unable to establish the Handler. Error: {str(ex)}\n")

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, catchSIGINT)
    main()
