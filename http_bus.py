from handler import Handler

class Listener_TCP(threading.Thread):
    def __init__(self, lhost, lport, agentList):
        threading.Thread.__init__(self)
        self.lhost = lhost
        self.lport = lport
        self.agentList = agentList
        # self.logger = logger

    def run(self):
        # Records Connection ID
        connRecord = 0
        while True:
            # start listening

            print(f"\n[* Listener-Msg] Connection received from {str(client_address[0])}\n")

            # BotHandler = Multiconn, a new BotHandler is spawned for each incoming connection
            newConn = Handler(client, client_address, connRecord)
            newConn.start()

            self.agentList.append(newConn)
            # print(agentList)
            connRecord += 1
    
    # def log(self, msg):
    #     # Write msg to tcp_listener.log