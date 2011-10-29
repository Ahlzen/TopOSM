#!/usr/bin/python

"""common.py: Common utility functions for TopOSM"""

import os, time, sys
from os import path
from threading import Lock

from env import *

__author__      = "Lars Ahlzen"
__copyright__   = "(c) Lars Ahlzen 2008-2011"
__license__     = "GPLv2"


class ConsoleManager:
    lock = Lock()
    def printMessage(self, message):
        ConsoleManager.lock.acquire()
        print message
        ConsoleManager.lock.release()
    def debugMessage(self, message):
        if TOPOSM_DEBUG:
            self.printMessage(message)

class ErrorLog:
    lock = Lock()
    def log(self, message, exception = None):
        timestr = time.strftime('[%Y-%m-%d %H:%M:%S]')
        ErrorLog.lock.acquire()
        try:
            file = open(ERRORLOG, 'a')
            file.write("%s %s (%s)\n" % (timestr, message, str(exception)))
            file.close()
        except:
            print "Failed to write to the error log:"
            print "%s %s" % (sys.exc_info()[0], sys.exc_info()[1])
        finally:
            ErrorLog.lock.release()        

console = ConsoleManager()
errorLog = ErrorLog()


# global locking object for file system ops (e.g. creating directories)
fslock = Lock()

def ensureDirExists(path):
    fslock.acquire()
    try:
        if not os.path.isdir(path):
            os.makedirs(path)
    finally:
        fslock.release()

def tryRemove(filename):
    fslock.acquire()
    try:
        if path.isfile(filename):
            os.remove(filename)
    finally:
        fslock.release()

def writeEmpty(filename):
    "Overwrites the specified filename with a new empty file."
    fslock.acquire()
    try:
        open(filename, 'w').close();
    finally:
        fslock.release()

def runSql(sql):
    command = "psql -d %s -q -c \"%s\"" % (DATABASE, sql)
    print command
    os.system(command)

