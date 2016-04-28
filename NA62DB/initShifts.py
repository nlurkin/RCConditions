#!/usr/bin/python2.7

'''
Created on Apr 25, 2016

@author: nlurkin
'''
import sys

from database import DBConnector
from DBConfig import DBConfig as DB
from datetime import datetime, timedelta

def getShiftID(myconn, date, slot):
    shift = myconn.executeGet("SELECT * FROM shifts WHERE date=%s AND slot=%s", [date, slot])
    if len(shift)>0:
        return shift[0]["id"]
    else:
        return -1
    
def insertShift(myconn, date, slot):
    shiftID = getShiftID(myconn, date, slot)
    if shiftID==-1:
        myconn.executeInsert("INSERT INTO shifts (date, slot) VALUES (%s,%s)", [date, slot])
        
if __name__ == '__main__':
    if len(sys.argv)<4:
        print "Please provide database password, date of first shift (%Y-%m-%d), date of last shift (%Y-%m-%d)"
        sys.exit()
    
    myconn = DBConnector(True)
    myconn.connectDB(passwd=sys.argv[1], host=DB.host, db="shifters", user=DB.userName, port=DB.port)
    
    
    firstShift = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    lastShift = datetime.strptime(sys.argv[3], "%Y-%m-%d")
    currentShift = firstShift
    
    while currentShift<=lastShift:
        for slot in range(0, 3):
            insertShift(myconn, currentShift, slot)
        currentShift = currentShift + timedelta(1)
    
    