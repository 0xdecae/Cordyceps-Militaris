# Main imports
import logging
import logging.config
import logging.handlers
from multiprocessing import Process, Queue
import random
import threading
import time

class Logger(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
            q = Queue()

            log_dict = {
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
                        'mode': 'w',
                        'formatter': 'detailed',
                    },
                    'connection': {
                        'class': 'logging.FileHandler',
                        'filename':  'log/connection.log',
                        'mode': 'w',
                        'formatter': 'detailed',
                    },
                    'uptime': {
                        'class': 'logging.FileHandler',
                        'filename': 'log/uptime.log',
                        'mode': 'w',
                        'formatter': 'detailed',
                    },
                    'history': {
                        'class': 'logging.FileHandler',
                        'filename': 'log/.history',
                        'mode': 'w',
                        'formatter': 'detailed',
                    }
                },
                'loggers': {
                    'serv': {
                        'handlers': ['server']
                    }
                    'conn': {
                        'handlers': ['connection']
                    }
                    'up': {
                        'handlers': ['uptime']
                    }
                    'hist': {
                        'handlers': ['history']
                    }
                },
                'root': {
                    'level': 'DEBUG',
                    'handlers': ['server', 'handler','uptime']
                },
            }
            workers = []
            for i in range(4):
                wp = Process(target=worker_process, name='CM-LOGGER %d' % (i + 1), args=(q,))
                workers.append(wp)
                wp.start()
            logging.config.dictConfig(log_dict)
            lp = threading.Thread(target=logger_thread, args=(q,))
            lp.start()
            # At this point, the main process could do some useful work of its own
            # Once it's done that, it can wait for the workers to terminate...
            # for wp in workers:
            #     wp.join()
            # And now tell the logging thread to finish up, too
            # q.put(None)
            # lp.join()

    def logger_thread(self, q):
        while True:
            record = q.get()
            if record is None:
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)

    # Change to log()?
    def worker_process(self, q):
        qh = logging.handlers.QueueHandler(q)
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.addHandler(qh)
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR,
                logging.CRITICAL]
        loggers = ['foo', 'foo.bar', 'foo.bar.baz',
                'spam', 'spam.ham', 'spam.ham.eggs']
        for i in range(100):
            lvl = random.choice(levels)
            logger = logging.getLogger(random.choice(loggers))
            logger.log(lvl, 'Message no. %d', i)

    def log(self, type, msg):


    

