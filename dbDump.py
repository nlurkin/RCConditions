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
    printTable(myconn, "run", "number")
    printTable(myconn, "runtype")
    
    print "#################################  Triggers  ################################"
    printTable(myconn, "runtrigger")
    print " ----> periodic"
    printTable(myconn, "triggerperiodic")
    printTable(myconn, "triggerperiodictype")
    print " ----> NIM"
    printTable(myconn, "triggernim")
    printTable(myconn, "triggernimtype")
    print " ----> Primitive"
    printTable(myconn, "triggerprimitive")
    printTable(myconn, "triggerprimitivetype")
    print " ----> Sync"
    printTable(myconn, "triggersync")
    print " ----> Calib"
    printTable(myconn, "triggercalib")
    
    print "#################################  Detectors ################################"
    printTable(myconn, "enableddetectors")
   
    printTable(myconn, "viewnim") 
    print "#################################  Website display ################################"
    
    headers = ['Run#', 'RunType', 'Start', 'Stop', 'PeriodicTrigger', 'NimTrigger', 'EnabledDetectors']
    res = myconn.executeGet("""
    SELECT run.number, runtype.runtypename, run.timestart, run.timestop, CONCAT_WS('+', T1.periodstring, GROUP_CONCAT(DISTINCT T2.nimstring SEPARATOR '+')), GROUP_CONCAT(DISTINCT enableddetectors.detectorname ORDER BY enableddetectors.detectorname SEPARATOR '+') 
    FROM run 
    LEFT JOIN runtype ON (runtype.id = run.runtype_id)
    LEFT JOIN enableddetectors ON enableddetectors.run_id = run.id
    LEFT JOIN (SELECT viewperiodic.runid AS periodrunid, CONCAT('Period:', viewperiodic.periods) AS periodstring
        FROM viewperiodic) AS T1 ON run.id = T1.periodrunid 
    LEFT JOIN (SELECT viewnim.runid AS nimrunid, viewnim.triggerstring AS nimstring
        FROM viewnim) AS T2 ON run.id = T2.nimrunid 
    GROUP BY run.id
    ORDER BY run.number
    """)
    print tabulate(record2Table(res), headers, tablefmt="orgtbl")
    print ""
    
    sys.exit()
    headers = ['run #', 'period']
    res = myconn.executeGet("""
    SELECT run.number, CONCAT('Period:', T1.periods)
    FROM run
    INNER JOIN (SELECT run.id AS runid, runtrigger.id, GROUP_CONCAT(DISTINCT triggerperiodictype.period SEPARATOR ',') as periods FROM triggerperiodictype
                INNER JOIN (triggerperiodic, runtrigger, run) ON (triggerperiodic.runtrigger_id = runtrigger.id AND run.id = runtrigger.run_id) 
                GROUP BY triggerperiodictype.period AND run.id) 
                AS T1
    ON (run.id=T1.runid)
    """)
    print tabulate(record2Table(res), headers, tablefmt="orgtbl")
    print ""
    
    headers = ['run #', 'nim']
    res = myconn.executeGet("""
    SELECT run.number, CONCAT_WS('x',T3.det_0, T3.det_1, T3.det_2, T3.det_3, T3.det_4)
    FROM run
    INNER JOIN (SELECT DISTINCT T2.runid, IF(det_0='1', D0.detname, IF(det_0=2, CONCAT('!', D0.detname), NULL)) as det_0, IF(det_1='1', D1.detname, IF(det_1=2, CONCAT('!', D1.detname), NULL)) AS det_1,
                IF(det_2='1', D2.detname, IF(det_2=2, CONCAT('!', D2.detname), NULL)) AS det_2, IF(det_3='1', D3.detname, IF(det_3=2, CONCAT('!', D3.detname), NULL)) AS det_3,
                IF(det_4='1', D4.detname, IF(det_4=2, CONCAT('!', D4.detname), NULL)) AS det_4
                FROM ((SELECT T1.runid, T1.validitystart, T1.validityend, SUBSTRING(T1.mask, 1, 1) AS det_0, SUBSTRING(T1.mask, 2, 1) as det_1, SUBSTRING(T1.mask, 3, 1) AS det_2, SUBSTRING(T1.mask, 4, 1) AS det_3, SUBSTRING(T1.mask, 5, 1) AS det_4 
                       FROM (SELECT runtrigger.run_id AS runid, runtrigger.id, runtrigger.validitystart, runtrigger.validityend, triggernimtype.mask FROM triggernimtype
                             INNER JOIN (triggernim, runtrigger) ON (triggernim.runtrigger_id = runtrigger.id) 
                             GROUP BY triggernimtype.mask)
                             AS T1)
                       AS T2)
                INNER JOIN (
                       (SELECT detnumber, detname, validitystart FROM nimdetname WHERE detnumber=0) AS D0,
                       (SELECT detnumber, detname, validitystart FROM nimdetname WHERE detnumber=1) AS D1,
                       (SELECT detnumber, detname, validitystart FROM nimdetname WHERE detnumber=2) AS D2,
                       (SELECT detnumber, detname, validitystart FROM nimdetname WHERE detnumber=3) AS D3,
                       (SELECT detnumber, detname, validitystart FROM nimdetname WHERE detnumber=4) AS D4)
                ON (D0.validitystart<T2.validitystart AND D1.validitystart<T2.validitystart AND D2.validitystart<T2.validitystart AND 
                    D3.validitystart<T2.validitystart AND D4.validitystart<T2.validitystart)
                ) AS T3
    ON (run.id=T3.runid)
    """)
    print tabulate(record2Table(res), headers, tablefmt="orgtbl")
    print ""
    
