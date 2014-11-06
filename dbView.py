#!/usr/bin/env python

'''
Created on Nov 5, 2014

@author: ncl
'''
import sys

from database import DBConnector
from tabulate import tabulate


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
    
    
def printTable(myconn, table, order="", colwdth=0):
    headers = getColName(myconn, table)
    if order!="":
        strOrder = "ORDER BY " + order
    else:
        strOrder = ""
    sqlres = myconn.executeGet("SELECT * FROM %s %s" % (table, strOrder))
    
    #table = [headers]
    #table = record2Table(sqlres)
    
    #print PrettyPrint(table, justify, colwdth)
    print tabulate(record2Table(sqlres), headers, tablefmt="orgtbl")
    print ""

if __name__ == '__main__':
    myconn = DBConnector()
    myconn.connectDB()
    
    print "#################################  Run Info  ################################"
    printTable(myconn, sys.argv[1])
