#!/bin/env python

'''
Created on Apr 27, 2016

@author: nlurkin
'''

import sys
from database import DBConnector
from DBConfig import DBConfig as DB

import re

if __name__ == '__main__':
    myconn = DBConnector(True)
    myconn.connectDB(passwd=sys.argv[1], host=DB.host, db="shifters", user=DB.userName, port=DB.port)
    
    list = myconn.executeGet("SELECT id, surname FROM shifter", [])
    
    for user in list:
        m = re.findall("([A-Z])(.*)", user["surname"])
        if len(m)==1 and m[0][1]=="":
            print user["surname"]
            myconn.executeInsert("DELETE FROM shifter WHERE id=%s", [user["id"]])
            continue
        if len(m)>=1:
            name = ""
            for hit in m:
                name = name + " {0}{1}".format(hit[0], hit[1].lower())
        else:
            name = user["surname"]
        print "{0} -> {1}".format(user["surname"], name.strip())
        myconn.executeInsert("UPDATE shifter SET surname=%s WHERE id=%s", [name.strip(),user["id"]]) 