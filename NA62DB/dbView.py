#!/usr/bin/env python

'''
Created on Nov 5, 2014

@author: ncl
'''
import sys

from database import DBConnector
from tabulate import tabulate
from DBConfig import DBConfig as DB


def getColName(myconn, table):
    res = myconn.executeGet("SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_NAME`='%s'" % (table))
    return [x[0] for x in res]

def record2Table(sqlRec):
    table = []
    for r in sqlRec:
        row = []
        for el in r:
            row.append(el)
        table.append(row)
    return table
    
    
def printTable(myconn, table, order="", where=""):
    headers = getColName(myconn, table)
    if order!="":
        strOrder = "ORDER BY " + order
    else:
        strOrder = ""
    if where!="":
        strWhere = "WHERE " + where
    else:
        strWhere = ""
    
    print "SELECT * FROM %s %s %s" % (table, strOrder, strWhere)
    sqlres = myconn.executeGet("SELECT * FROM %s %s %s" % (table, strOrder, strWhere))
    
    #table = [headers]
    #table = record2Table(sqlres)
    
    #print PrettyPrint(table, justify, colwdth)
    print tabulate(record2Table(sqlres), headers, tablefmt="orgtbl")
    print ""

if __name__ == '__main__':
    myconn = DBConnector()
    myconn.connectDB(passwd=sys.argv[1], host=DB.host, db=DB.dbName, user=DB.userName, port=DB.port)
    
    
    res = myconn.executeGet("SELECT table_name FROM information_schema.tables WHERE table_schema='testRC' AND table_type='BASE TABLE'")
    tableList = record2Table(res)
    res = myconn.executeGet("SELECT table_name FROM information_schema.tables WHERE table_schema='testRC' AND table_type='VIEW'")
    viewList = record2Table(res)
    
    while True:
        req = raw_input("Select (T)able or (V)iew: ")
        if req.lower() == "t":
            print "### Tables"
            for i,t in enumerate(tableList):
                print "---> (%i) %s" % (i,t[0])
            req = int(raw_input("Select a number: "))
            if req>=0 and req<len(tableList):
                printTable(myconn, tableList[req][0])
        elif req.lower() == "v":
            print "### Views"
            for i,t in enumerate(viewList):
                print "---> (%i) %s" % (i,t[0])
            req = int(raw_input("Select a number: "))
            if req>=0 and req<len(viewList):
                printTable(myconn, viewList[req][0])
            
