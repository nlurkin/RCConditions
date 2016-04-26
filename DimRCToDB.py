#!/usr/bin/env python

'''
Created on Apr 26, 2016

@author: nlurkin
'''

import time

import pydim
import NA62DB
from NA62DB.DBConfig import ProcessingConfig as DBConf


class dimReceiver(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.myconn = NA62DB.DBConnector(False)
    
    def runProcess_callback(self, runNumber, revision):
        #Consistency checks
        if revision[0]!='r':
            print "Revision number not valid: {0}".format(revision)
            return
        if runNumber<0:
            print "Run number not valid: {0}".format(runNumber)
            return
        
        self.myconn.connectDB(passwd=DBConf.passwd, host=DBConf.host, db=DBConf.dbName, user=DBConf.userName, port=DBConf.port)
        res = self.myconn.executeGet("SELECT COUNT(*) FROM Run WHERE ID=%s AND Version=%s", [runNumber, revision])
        if res[0]["COUNT(*)"]==0:
            self.myconn.executeInsert("INSERT INTO Run (ID, Version, Status) VALUES (%s,%s,'OnlinePending')", [runNumber, revision])
        else:
            self.myconn.executeInsert("UPDATE Run SET Status='OnlinePending' WHERE Id=%s AND Version=%s", [runNumber, revision])
        self.myconn.close()
    
    def start(self):
        self.runProcess = pydim.dic_info_service("RunControl/StartProcessing", "L:1;C", self.runProcess_callback)
        
    def stop(self):
        pydim.dic_release_service(self.runProcess)

if __name__ == '__main__':
    b = dimReceiver();
    
    b.start()
    while True:
        time.sleep(10)
