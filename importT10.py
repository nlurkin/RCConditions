#!/usr/bin/python

'''
Created on Nov 4, 2014

@author: ncl
'''

import os
import re
import sys
#from  datetime import datetime
#import time
from NA62DB import DBConnector
from NA62DB.DBConfig import DBConfig as DB
from XMLExtract import tryint

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def exportFile(myconn, filePath):
    
    intensities = []
    with open(filePath, "r") as fd:
        for line in fd:
            dateVal, val = line.split(";")
            TS = int(dateVal) #time.mktime(datetime.strptime(dateVal, "%Y-%m-%d %H:%M:%S").timetuple()))
            intensities.append([TS, float(val)])
    
    if myconn is None:
        #Print everything
        print intensities
        return False
    else:
        ## Insert runinfo into DB
        myconn.setTVList("T10_intensity", intensities)
        return True

if __name__ == '__main__':
    if hasattr(DB, 'passwd'):
        password = DB.passwd
    elif len(sys.argv)<3:
        print "Please provide path and database password"
        sys.exit()
    else:
        password = sys.argv[-1:][0]
    
    #myconn = None
    myconn = DBConnector(False)
    myconn.initConnection(passwd=password, db=DB.dbName, user=DB.userName, host=DB.host, port=DB.port)
    myconn.openConnection()
    myconn.setSilent(True)

    filePath = sys.argv[1:]
    
    fileList = []
    for path in filePath:
            fileList.append(path)
    
    fileList.sort(key=alphanum_key)
    for f in fileList:
        if os.path.isfile(f):
            print "\nImport " + f + "\n---------------------"
            if exportFile(myconn, f):
                os.remove(f)
    if not myconn is None:
        myconn.close()
