#!/usr/bin/python

"""JobManager: Helper class for running independent jobs in parallel,
catching and logging exceptions, and printing status messages."""


from multiprocessing import Pool

from env import *
from common import *

__author__      = "Lars Ahlzen"
__copyright__   = "(c) Lars Ahlzen 2011"
__license__     = "GPLv2"


def runJob(message, function, args):
    console.printMessage(message)
    try:
        function(*args)
    except Exception as ex:
        console.printMessage('Failed: ' + message)
        errorLog.log('Failed: ' + message, ex)

class JobManager():
    def __init__(self, processes = NUM_THREADS):
        self.pool = Pool(processes)

    def addJob(self, message, function, args):
        self.pool.apply_async(runJob, (message, function, args))
        
    def finish(self):
        self.pool.close()
        self.pool.join()

