#!/usr/bin/env python
'''
Created on Apr 26, 2016
@author: nlurkin
'''

import sys
import time

import pydim

import NA62DB
from NA62DB.DBConfig import DBNamedConfig


class DBDimObject(object):
    '''
    classdocs
    '''

    def __init__(self, dbName, user, passwd, service):
        '''
        Constructor
        '''
        print "creating DimObject"
        dbConf = DBNamedConfig(dbName)
        self.myconn = NA62DB.DBConnector(dry_run=False, exitOnFailure=False)
        self.myconn.initConnection(passwd=passwd, host=dbConf.host, db=dbConf.dbName, user=user, port=dbConf.port)
        
        self.serverName = dbName
        self.serviceName = service
        
        self.query_success = 0
        self.resultString = " "
        self.resultFields = " "
        self.ignoreFirstSet = True
        self.ignoreFirstGet = True
	self.error = ""
        
    def parseParameters(self, description, params):
        paramsList = params.split("$")
        transformedParams = []
        for desc_letter, param_val in zip(description, paramsList):
            if desc_letter=="s":
                transformedParams.append(param_val)
            elif desc_letter=="i":
                transformedParams.append(int(param_val))
            elif desc_letter=="f":
                transformedParams.append(float(param_val))
        
        return transformedParams
            
    ###########################
    #    Query Execution
    ###########################
    def execute_set_callback(self, *args):
        if self.ignoreFirstSet:
            self.ignoreFirstSet = False
            return
        print "set received", args
        try:
            [sql, params_desc, params] = args[0].strip('\x00').split(";")
            params = self.parseParameters(params_desc, params)
        except ValueError as e:
            self.error = str(e)
        
        self.myconn.openConnection()
        self.query_success = self.myconn.executeInsert(sql, params)
        self.myconn.close()
        pydim.dis_update_service(self.success_service)
        
    def execute_get_callback(self, *args):
        if self.ignoreFirstGet:
            self.ignoreFirstGet = False
            return
        print "get received", args
        try:
            [sql, params_desc, params] = args[0].strip('\x00').split(";")
            params = self.parseParameters(params_desc, params)
        except ValueError as e:
            self.error = str(e)
            
        self.myconn.openConnection()
        rows = self.myconn.executeGet(sql, params)
        self.myconn.close()

        if rows==-1:
            self.query_success = -1
        else:
            rows[:] = ["$".join(str(row[val]) for val in row) for row in rows]
            self.resultString = "|".join(rows)
            self.resultFields = "|".join(row)
            pydim.dis_update_service(self.result_service)
            pydim.dis_update_service(self.fields_service)
        
        pydim.dis_update_service(self.success_service)

    ###########################
    #    Services callbacks
    ###########################    
    def send_success_callback(self, tag):
        return (self.query_success, "{0}|{1}\x00".format(self.myconn.getLastError(), self.error))
        self.error = ""
    
    def send_result_callback(self, tag):
        print self.resultString
        return [self.resultString + "\x00"]
    
    def send_fields_callback(self, tag):
        print self.resultFields
        return [self.resultFields + "\x00"]
    
    ###########################
    #    DIM execution
    ###########################
    def start(self):
        print "Adding service {serverName}/sql_success L:1;C".format(**self.__dict__)
        self.success_service = pydim.dis_add_service("{serverName}/sql_success".format(**self.__dict__), "L:1;C", self.send_success_callback, 1)
        print "Adding service {serverName}/sql_result C".format(**self.__dict__)
        self.result_service = pydim.dis_add_service("{serverName}/sql_result".format(**self.__dict__), "C", self.send_result_callback, 1)
        print "Adding service {serverName}/sql_fields C".format(**self.__dict__)
        self.fields_service = pydim.dis_add_service("{serverName}/sql_fields".format(**self.__dict__), "C", self.send_fields_callback, 1)
        
        pydim.dis_update_service(self.success_service)
        pydim.dis_update_service(self.result_service)
        pydim.dis_update_service(self.fields_service)
        
        print "Connecting to service {serviceName}/sql_set C".format(**self.__dict__)
        self.set_command = pydim.dic_info_service("{serviceName}/sql_set".format(**self.__dict__), "C", self.execute_set_callback)
        print "Connecting to service {serviceName}/sql_get C".format(**self.__dict__)
        self.get_command = pydim.dic_info_service("{serviceName}/sql_get".format(**self.__dict__), "C", self.execute_get_callback)
        pydim.dis_start_serving()
        print ""
        
    def stop(self):
        pydim.dis_remove_service(self.result_service)
        pydim.dis_remove_service(self.fields_service)
        pydim.dis_remove_service(self.success_service)
        pydim.dic_release_service(self.set_command)
        pydim.dic_release_service(self.get_command)
        print "Connector {serverName} terminated".format(**self.__dict__)


add_connector_service = None
list_connectors = {}
def add_connector_callback(cmd, tag):
    '''
    Callback for the add_connector command.
    Expected string to add a new connector is: dbName;userName;password;client_service_prefix
    Expected string to remove an existing connector is: dbName;;;
    '''
    global list_connectors
    print "add_connector receiving ", cmd
    [dbName, user, passwd, service] = cmd[0].strip('\x00').split(";")
    if(list_connectors.has_key(dbName)):
        if(service==""):
            print "Removing connector {0}".format(dbName)
            list_connectors[dbName].stop()
            del list_connectors[dbName]
            return
        else:
            print "{0} connector already exists ... Aborting".format(dbName)
            return
    
    list_connectors[dbName] = DBDimObject(dbName, user, passwd, service)
    list_connectors[dbName].start()
    

def start(serverName):
    global add_connector_service
    add_connector_service = pydim.dis_add_cmnd("{0}/add_connector".format(serverName), "C", add_connector_callback, 1)
    
    pydim.dis_start_serving(serverName)
    while True:
        time.sleep(1)

if __name__ == '__main__':
    start(sys.argv[1])
