# Main imports
import logging
import logging.config
import logging.handlers
from multiprocessing import Process, Queue
import random
import threading
import time

# Noted:
# self.levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

# Had to reimplement logging queues myself reather than using the queuehandler modules

class Logger(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.log_level = {
            'debug': logging.DEBUG, 
            'info': logging.INFO, 
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }

        self.log_q = Queue(-1)

        self.log_dict = {
            'version': 1,
            'formatters': {
                'detailed': {
                    'class': 'logging.Formatter',
                    'format': '[%(asctime)s-%(name)-15s %(levelname)-8s  %(message)s'
                }
            },
            'handlers': {
                'server': {
                    'class': 'logging.FileHandler',
                    'filename': 'log/server-msg.log',
                    'mode': 'a',                            # Append; Keep logs from previous sessions
                    'formatter': 'detailed',
                },
                'connection': {
                    'class': 'logging.FileHandler',
                    'filename':  'log/connection.log',
                    'mode': 'a',
                    'formatter': 'detailed',
                },
                'uptime': {
                    'class': 'logging.FileHandler',
                    'filename': 'log/uptime.log',
                    'mode': 'a',
                    'formatter': 'detailed',
                },
                'history': {
                    'class': 'logging.FileHandler',
                    'filename': 'log/.history',
                    'mode': 'a',
                    'formatter': 'detailed',
                }
            },
            'loggers': {
                'serv': {
                    'handlers': ['server']
                },
                'conn': {
                    'handlers': ['connection']
                },
                'up': {
                    'handlers': ['uptime']
                },
                'hist': {
                    'handlers': ['history']
                }
            },
            'root': {
                'level': 'DEBUG',
                #'handlers': ['server', 'connection','uptime', 'history']
            }
        }

        logging.config.dictConfig(self.log_dict)
        # print('logging-running')

        lp = threading.Thread(target=self.logger_thread, args=(self.log_q,))
        lp.start()



    # def run(self):

    def logger_thread(self, q):


        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        # Monitor for record additions
        while True:

            # print(f'Queue before .get(): {str(q)}')
            record = q.get()
            # print(f'Queue after .get(): {str(q)}')

            # print(f'Record: {str(record)}')                 # Currently this is not engaging < Before moving chunk of preq-code to q_log
                                                            # Now, we are getting a continuously loop of the same message, spawned from one call to q_log in Server
                                                            # This is the current suspect of the recursion.

            # print(f"Record msg: {str(record['msg'])}") 

            if record is None:
                break

            # print("Calling handle : record")

            logger = logging.getLogger(record['log'])        
            # print("Calling log from function q_log")            # Executed once
            logger.log(self.log_level.get(record['lvl'], logging.DEBUG), record['msg'])

    # Function simply creates a template-dict object and stores the information to be logged inside of it. Then throws it in the queue to be handled.
    def q_log(self, lg, lvl, msg):

        
        temp_dict = {
            'log': lg,
            'lvl': lvl,
            'msg': msg
        }
        self.log_q.put(temp_dict)


    

