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
                os._exit(0)
            else:
                os._exit(0)
    except KeyboardInterrupt:
        print(f"[* Server-Msg] HEATHEN!!!\n")

    signal.signal(signal.SIGINT, catchSIGINT)
        
def main():

    if (len(sys.argv) < 3):
        print(f"[* Server-Msg] Usage:\n  [+] python3 {sys.argv[0]} <LHOST> <LPORT>\n  [+] Eg.: python3 {sys.argv[0]} 0.0.0.0 1337\n")
    else:

        print('''
/\______________________________________________________________________/\\
|                                                                        |
|       CORDYCEPS MILITARIS                                              |
|                          ___         _    /\\                           |
|                         {__ \        \\\\  / /                           |
|                            \ \  ____--\\\\/ /____      ____              |
|                 _____       \ \-       \ (    --__  {___ \\             |
|                / ___ \   _---\ \  0     \ \ 0  __---_   \ }  ____      | 
|                \ (  \y  /    / /         \_}  / /    \  | } / __ \\     |
|                 \ \    / 0  {_/     0        / / 0    \ | |/ /  \y     |
|                  \ \  /       ___________   / {       0\/ / /          | 
|                   ) ) |      [  __       ]  \  \   0   / __/           | 
|                  /  / |0  __ [ /  \ |\/| ]// \  \     / /|             |
|   /\   /\        \  \ |  /  }[ |    |  | ]/ 0 \  }0  / / |             | 
|   ||   ||         \  \__/  / [ \__/ |  | ]     \_}  { /  |             | 
|  (XX) (XX)         \______/0 [___________]          {/ 0 /             |
|   \ \  \ \      _______)        0  __/ /     0          /              |
|    \ \--\ \----/        )0        {___/ 0        0     /               |
|     \ (..\....           \--__--__----____---_---___--/_               |
|     (___________________________________________________)              |
|                                                                        |
|                                                                        |
|========================================================================|
|   Produced by:                                                         |
|                                                                        |      
|          Josh Robertson    Andrew Linscott     Dalton Brown            |
| ______________________________________________________________________ |
\/                                                                      \/
        ''') 

        lhost = sys.argv[1]
        lport = int(sys.argv[2])

        print("\n\n\n\t[Welcome to the Cordyceps-Militaris command and control framework]\n")

        print("[* Server-Msg] Select which type of listeners you would like to use. You may choose more than one.")

        entry_success = False

        while not entry_success:
            print("[* Server-Msg] Please type them in as a space-seperated list, ie. '0 1 2', without apostrophes.") 
            print("[* Server-Msg] Or, type 'quit' to exit.\n")
            print("\t\t[0] Standard TCP")
            print("\t\t[1] HTTP")
            print("\t\t[2] DNS\n")
            
            try:
                listener_entry_list = input('[* Select Listeners]% ').split()
            except Exception as ex:
                print("[* Server-Msg] Fatal error with input. Exiting...")
                print(f"[* Server-Msg] Error: {ex}")
                # entry_success = False
                os._exit(0)
            else:
                if("quit" in listener_entry_list):
                    print("[* Server-Msg] Exiting...")
                    os._exit(0)

                try:
                    if("0" in listener_entry_list):
                        TCP_Thread = Listener_TCP(lhost, lport, agentList)
                        TCP_Thread.start()
                        listeners.append(TCP_Thread)
                        entry_success = True

                    if("1" in listener_entry_list):
                        # HTTP_Thread = Listener_HTTP(lhost, lport, agentList)
                        # HTTP_Thread.start()
                        # listeners.append(HTTP_Thread)
                        print("[* Server-Msg] Function yet to be included. Choose another...")
                        entry_success = False

                    if("2" in listener_entry_list):
                        # DNS_Thread = Listener_DNS(lhost, lport, agentList)
                        # DNS_Thread.start()
                        # listeners.append(DNS_Thread)
                        print("[* Server-Msg] Function yet to be included. Choose another...")
                        entry_success = False

                except Exception as ex:
                    print("[* Server-Msg] Fatal error with listener selection and initialization. Exiting...")
                    print(f"[* Server-Msg] Error: {ex}")
                    os._exit(0)

        time.sleep(2)
        print("[* Server-Msg] Initializing Interpreter session...")

        try:
            InterpreterThread = Interpreter(agentList, listeners)          # Handles interface, queue is for commands
            InterpreterThread.start()
            interpreters.append(InterpreterThread)
            # print("[* Server-Msg] Interpreter initialization complete...")

        except Exception as ex:
            print(f"[* Server-Msg] Unable to initialize Intrepeter Session. Error: {str(ex)}\n")
            os._exit(0)

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, catchSIGINT)
    main()
