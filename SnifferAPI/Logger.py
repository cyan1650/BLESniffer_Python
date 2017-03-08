import time, os, logging, traceback, threading
import logging.handlers as logHandlers

#################################################################
# This file contains the logger. To log a line, simply write     #
# 'logging.[level]("whatever you want to log")'                    #
# [level] is one of {info, debug, warning, error, critical,        #
#     exception}                                                    #
# See python logging documentation                                #
# As long as Logger.initLogger has been called beforehand, this    #
# will result in the line being appended to the log file        #
#################################################################

#try:
#      logFilePath=os.path.join(os.getenv('appdata'), 'Nordic Semiconductor', 'Sniffer', 'logs')
#except:
logFilePath="logs"

logFileName = os.path.join(logFilePath, 'log.txt')

# Ensure that the directory we are writing the log file to exists.
# Create our logfile, and write the timestamp in the first line.
def initLogger():
    try:
        # First, make sure that the directory exists
        if not os.path.isdir(logFilePath):
            os.makedirs(logFilePath)

        logHandler = logging.FileHandler(logFileName)
        logFormatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%d-%b-%Y %H:%M:%S (%z)')
        logHandler.setFormatter(logFormatter)
        logger = logging.getLogger()
        logger.addHandler(logHandler)
        logger.setLevel(logging.INFO)
    except:
        print("LOGGING FAILED")
        print(traceback.format_exc())
        raise

def shutdownLogger():
    pass

# Clear the log (typically after it has been sent on email)
def clearLog():
    try:
        pass
    except:
        print("LOGGING FAILED")
        raise
