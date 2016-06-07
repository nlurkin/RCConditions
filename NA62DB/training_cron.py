#!/usr/bin/python

'''
Created on Nov 5, 2014

@author: ncl
'''
import datetime
import sys
import smtplib
from email.mime.text import MIMEText

from database import DBConnector
from DBConfig import DBConfig as DB

body="""
Dear Training Crew Members,

The next training session is foreseen on {training_date}. The following {shift_number}
shifters have booked a slot for the training:
   {shifter_list}

Already {next_number} have booked for the session the week after.

Regards,
The Cron member of the Training Crew
"""

dest_emails = ["na62-shiftertraining@cern.ch"]
#dest_emails = ["nicolas.lurkin@cern.ch"]

def getSessionID(myconn, sess_date):
    entries = myconn.executeGet("SELECT * FROM shifters.training_sessions WHERE date=%s", [sess_date])
    if len(entries) > 1:
        print "Problem: more than one sessions at the date {0}".format(sess_date)
        return -1
    elif len(entries) ==0:
        print "Problem: no session at the date {0}".format(sess_date)
        return -1        
    else:
        return entries[0]["session_id"]

def getUserID(myconn, name, surname):
    entries = myconn.executeGet("SELECT * FROM shifters.shifter WHERE name like %s and surname like %s", [name, surname])
    if len(entries) > 1:
        print "Problem: more than one user matching {0} {1}".format(name, surname)
        return -1
    elif len(entries)==0:
        print "User not found {0} {1}".format(name, surname)
        return -1
    else:
        return entries[0]["id"]

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

if __name__ == '__main__':
    if hasattr(DB, 'passwd'):
        password = DB.passwd
    elif len(sys.argv)!=2:
        print "Please provide DB password"
        sys.exit(0)
    else:
        password = sys.argv[1]

    myconn = DBConnector()
    myconn.initConnection(passwd=password, host=DB.host, db=DB.dbName, user=DB.userName, port=DB.port)
    myconn.openConnection()
    
    first_date = datetime.datetime.now()
    if first_date < datetime.datetime(2016,04,15):
        first_date = datetime.datetime(2016,04,15)
    nextTraining = next_weekday(first_date, 1)
    nextTraining = nextTraining.replace(hour=0, minute=0, second=0, microsecond=0)
    
    nextTrainingID = getSessionID(myconn, nextTraining)
    res = myconn.executeGet("SELECT * FROM shifters.shifter_booking WHERE session_id={0}".format(nextTrainingID))
    shifter_list = []
    for r in res:
        shifter_list.append("{0} {1}".format(r["name"],r["surname"]))
    
    nextNextTraining = next_weekday(first_date+datetime.timedelta(7), 1)
    nextNextTraining = nextNextTraining.replace(hour=0, minute=0, second=0, microsecond=0)
    nextNextTrainingID = getSessionID(myconn, nextNextTraining)
    
    res = myconn.executeGet("SELECT COUNT(*) as tot FROM shifters.shifter_booking WHERE session_id={0}".format(nextNextTrainingID))
    next_number = 0
    if len(res)>0:
        next_number = res[0]["tot"]
    msg_body =  body.format(training_date=nextTraining.strftime("%d-%m-%Y"), shift_number=len(shifter_list), shifter_list="\n   ".join(shifter_list), next_number=next_number)
   
    msg = MIMEText(msg_body)
    msg['Subject'] = "Next Shifter Training Session"
    msg['From'] = "na62-shiftertraining@cern.ch"
    msg['To'] = ", ".join(dest_emails)
    
    print "Ready to send shifter message"
    server = smtplib.SMTP("localhost")
    server.sendmail("na62-shiftertraining@cern.ch", dest_emails, msg.as_string())
    server.quit()
    print "Message sent"

