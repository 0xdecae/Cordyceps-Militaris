# Main imports
import sys
import os
import threading
import queue
import time
import random

## NOT IN USE : USING PYTHON3 BUILT-IN LOGGER ##



class Logger(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.serverLogPath = "./log/server.log"
        self.connLogPath = "./log/conn.log"
        self.uptimeLogPath = "./log/uptime.log"

        self.jobs = queue.Queue()
        
    def run(self):
        initLogs()
        monitorQueue()

    def initLogs():
        # Check if log Directory exists
        # if not create ./log/
        try:
            if not os.path.exists('./log') or not os.path.isdir('./log'):
                os.makedirs('log')
        except Exception as ex:
            print(f"Could not create log dir because of {ex}")

        # Check if server.log file exists
        # if not create ./log/server.log
        try:
            if not os.path.exists('./log/server.log') or not os.path.isfile('./log/server.log'):
                os.mknod('./log/server.log')
        except Exception as ex:
            print(f"Could not create server.log file because of {ex}")

        # Check if uptime.log file exists
        # if not create ./log/uptime.log
        try:
            if not os.path.exists('./log/uptime.log') or not os.path.isfile('./log/uptime.log'):
                os.mknod('./log/uptime.log')
        except Exception as ex:
            print(f"Could not create uptime.log file because of {ex}")

        # Check if uptime.log file exists
        # if not create ./log/conn.log
        try:
            if not os.path.exists('./log/uptime.log') or not os.path.isfile('./log/uptime.log'):
                os.mknod('./log/conn.log')
        except Exception as ex:
            print(f"Could not create conn.log file because of {ex}")

    def monitorQueue(self):

        while True:
            obj = self.jobs.get()
            print(obj)
            print(obj[0])
            print(obj[1])

            log = obj[0]
            msg = obj[1]

            self.log(log, msg)

    def log(self, log, msg):

        # Log msg in appropriate file
        





