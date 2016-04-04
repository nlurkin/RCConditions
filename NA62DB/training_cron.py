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

def next_weekday(d, weekday):
   days_ahead = weekday - d.weekday()
   if days_ahead <= 0: # Target day already happened this week
      days_ahead += 7
   return d + datetime.timedelta(days_ahead)

if __name__ == '__main__':
    myconn = DBConnector()
    myconn.connectDB(passwd=sys.argv[1])
    
    first_date = datetime.datetime.now()
    if first_date < datetime.datetime(2016,04,15):
        first_date = datetime.datetime(2016,04,15)
    nextTraining = next_weekday(first_date, 1)
    res = myconn.executeGet("SELECT * FROM shifter_training WHERE Date BETWEEN '{0}' AND '{1}'".format(nextTraining.strftime("%Y-%m-%dT00:00:00.000"), nextTraining.strftime("%Y-%m-%dT23:59:59.000")))
    shifter_list = []
    for r in res:
        shifter_list.append("{0} {1}".format(r[1],r[2]))
    
    nextNextTraining = next_weekday(first_date+datetime.timedelta(7), 1)
    res = myconn.executeGet("SELECT COUNT(*) FROM shifter_training WHERE Date BETWEEN '{0}' AND '{1}'".format(nextTraining.strftime("%Y-%m-%dT00:00:00.000"), nextTraining.strftime("%Y-%m-%dT23:59:59.000")))
    next_number = 0
    if len(res)>0:
        next_number = res[0][0]
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

