#!/usr/bin/env python

'''
Created on Nov 5, 2014

@author: ncl
'''
import matplotlib.pyplot as plt
from datetime import datetime

from database import DBConnector

if __name__ == '__main__':
    myconn = DBConnector()
    myconn.connectDB(passwd="2Kfole")
    
    
    res = myconn.executeGet("SELECT totalMerger, timestop, totalL2, totalL0, totalL1, number  FROM run WHERE timestart>'2015-06-22T00:00:00.000' ORDER BY number")
    #res = myconn.executeGet("SELECT DISTINCT totalMerger, timestop, totalL2, totalL0, totalL1, number, d1.detectorname, d2.detectorname FROM run JOIN enableddetectors as d1 JOIN enableddetectors as d2 ON d1.run_id=run.id AND d2.run_id=run.id AND run.timestart>'2015-06-22T00:00:00.000' AND (d1.detectorname='LKr' and d2.detectorname='STRAW') ORDER BY number")
    totalMerger = []
    totalL2 = []
    totalL0 = []
    totalL1 = []
    time = []
    number = []
    for r in res:
        if r[1] is None:
            continue
        totalMerger.append(r[0])
        totalL2.append(r[2])
        totalL0.append(r[3])
        totalL1.append(r[4])
        time.append(r[1])
        number.append(r[5])

    d = [x-y for x,y in zip(totalL2[1:], totalL2[:-1])]
    td = [x-y for x,y in zip(time[1:], time[:-1])]
    dd = [x/y.total_seconds() for x,y in zip(d, td)]
    #plt.plot(number, totalL0, 'ro')
    #plt.plot(number, totalMerger, 'bo')
    #plt.plot(time[:-1], dd)
    #plt.show()
    for i,t in enumerate(time):
        print "{0} {1} {2} {3} {4}".format(str(t), sum(totalMerger[:i]), sum(totalL2[:i]), sum(totalL0[:i]), sum(totalL1[:i]))
    
