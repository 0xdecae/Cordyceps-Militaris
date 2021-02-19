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
# from listener_http import Listener_HTTP


agentList = []                  # Stores client_address[] info (IP, Port): IP is stored in string format, port is not

                                # [Handler-ID]-[client_address]-[ IP ]
                                #            |                L-[Port]
                                #            L-[CMD_Queue]

interpreters = []               # Literally only here to access outside of MAIN

listeners = []                  # Handles all listening threads (TCP, HTTP, DNS, etc...)
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
        if(interpreters):
            interpreters[0].exit()
            os._exit(0)
        else:
            os._exit(0)
    
    except KeyboardInterrupt:
        if(interpreters):
            interpreters[0].exit()
            os._exit(0)
        else:
            os._exit(0)
        print(f"[* Server-Msg] HEATHEN!!!\n")

    signal.signal(signal.SIGINT, catchSIGINT)
        
def main():

    # if (len(sys.argv) < 3):
    #     print(f"[* Server-Msg] Usage:\n  [+] python3 {sys.argv[0]} <LHOST> <LPORT>\n  [+] Eg.: python3 {sys.argv[0]} 0.0.0.0 1337\n")
    # else:

    print('''
/\______________________________________________________________________/\\
|                                                                        |
|       CORDYCEPS MILITARIS                                              |
|                             /\       .    /\\                           |
|                            / /       \\\\  / /      /\                   |
|                        /\  \ \    /\  \\\\/ /      / /                   |
|                       / /   \ \.==\ \==\ (==/\=./ /   /\               |
|               /\      \ \.==*\ \###\ \##\ \#\ \/ /*=. \ \              | 
|               \ \  /\  \//###/ /###{_/@@@\_}#\  /###\\\\ \ \  /\         |
|                \ \/ /  //###{_/#@@######@@@@@/ /#####\\\\ \ \/ /         |
|                 \  /  //#####@___________##@/ /@######\\\\/ / /          | 
|                  \ \  (|####@[  __       ]##\ \@@######/  _/           | 
|                  / /  (|##__@[ /  \ |\/| ]@##\ \_@####/ /)             |
|   /\   /\        \ \  (|#/  }[ |    |  | ]@@##\  }###/ /|)             | 
|   ||   ||         \ \_(|/  /@[ \__/ |  | ]@###@\_}##{ /#|)             | 
|  (XX) (XX)         \______/#@[___________]####@@@###{/##//             |
|   \ \  \ \      _______(\########@@__/ /####@@@@#######//              |
|    \ \--\ \----/        (\########{___/####@@@@#######//               |
|     \ (..\....           (\.=._.=._.=-=..__.=..=._.=.//_               |
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

        # lhost = sys.argv[1]
        # lport = int(sys.argv[2])

    print("\n\n\n\t[Welcome to the Cordyceps-Militaris command and control framework]\n")



#### ADDRESS ENTRY ####

    address_entry_success = False
    while not address_entry_success:
        try:
            print("[* Server-Msg] Please enter the address you would like to start the listeners on, e.g. 0.0.0.0")
            address_entry = input('[* Address-Entry]% ')
        # Input error
        except Exception as ex:
            print(f"[* Server-Msg] Unable to process address entered...")
            print(f"[* Server-Msg] Error: {ex}")
            continue

        # No input
        if not address_entry:
            print("[* Server-Msg] No input received. Please retry...\n")
        else:
            # Test if valid address
            try:
                socket.inet_aton(address_entry)
            # Invalid format
            except socket.error:
                print("[* Server-Msg] Invalid address received. Please retry...\n")
                continue
            
            # Confirm
            print(f"[* Server-Msg] Is the address entered correct [Y/n]: {address_entry}")
            try:
                confirm_entry = input('[* Confirm]% ')
            # Input error
            except Exception as ex:
                print(f"[* Server-Msg] Unable to process confirmation..")
                print(f"[* Server-Msg] Error: {ex}")
                continue
            else:
                # Yes?
                if confirm_entry.casefold().strip(" ") == 'y' or confirm_entry.casefold().strip(" ") == '':
                    lhost = address_entry
                    print(f"[* Server-Msg] Address set to {address_entry}...")
                    address_entry_success = True

                # Anything else?
                else: 
                    continue


#### LISTENER SELECTION ####

    print("[* Server-Msg] Select which type of listeners you would like to use. You may choose more than one.")

    listener_entry_success = False

    while not listener_entry_success:
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

            if(not listener_entry_list):
                print("[* Server-Msg] No input received. Please retry...\n")
                listener_entry_success = False
                continue

            if("quit" in listener_entry_list):
                print("[* Server-Msg] Exiting...")
                os._exit(0)

            try:
                # TCP
                if("0" in listener_entry_list):

                    # Port entry and verification
                    port_entry_success = False
                    while not port_entry_success:
                        try:
                            print("[* Server-Msg] Please enter the port you would like to start the TCP listeners on, e.g. 31337")
                            port_entry = int(input('[* Port-Entry]% '))
                        # Input error
                        except Exception as ex:
                            print(f"[* Server-Msg] Unable to process port entered...")
                            print(f"[* Server-Msg] Error: {ex}")
                            continue

                        # No input
                        if not port_entry:
                            print("[* Server-Msg] No input received. Please retry...\n")
                        else:
                            
                            # Confirm
                            print(f"[* Server-Msg] Is the port entered correct [Y/n]: {port_entry}")
                            try:
                                confirm_entry = input('[* Confirm]% ')
                            # Input error
                            except Exception as ex:
                                print(f"[* Server-Msg] Unable to process confirmation..")
                                print(f"[* Server-Msg] Error: {ex}")
                                continue
                            else:
                                # Yes?
                                if confirm_entry.casefold().strip(" ") == 'y' or confirm_entry.casefold().strip(" ") == '':
                                    lport = port_entry
                                    print(f"[* Server-Msg] Port set to {port_entry}...")
                                    port_entry_success = True
                                # Anything else?
                                else: 
                                    continue
                    
                    try:
                        TCP_Thread = Listener_TCP(lhost, lport, agentList)
                        TCP_Thread.start()
                        listeners.append(TCP_Thread)
                        listener_entry_success = True
                    except Exception as ex:
                        print("[* Server-Msg] Fatal error with listener selection and initialization. Exiting...")
                        print(f"[* Server-Msg] Error: {ex}")
                        os._exit(0)

                if("1" in listener_entry_list):
                    # HTTP_Thread = Listener_HTTP(lhost, lport, agentList)
                    # HTTP_Thread.start()
                    # listeners.append(HTTP_Thread)
                    print("[* Server-Msg] Function yet to be included")
                    # entry_success = False

                if("2" in listener_entry_list):
                    # DNS_Thread = Listener_DNS(lhost, lport, agentList)
                    # DNS_Thread.start()
                    # listeners.append(DNS_Thread)
                    print("[* Server-Msg] Function yet to be included")
                    # entry_success = False

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
        print(f"[* Server-Msg] Unable to initialize Interpreter Session. Error: {str(ex)}\n")
        os._exit(0)

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, catchSIGINT)
    main()
