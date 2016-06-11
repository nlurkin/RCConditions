#!/usr/bin/python

'''
Created on May 10, 2016

@author: ncl
'''
import datetime
import sys
import smtplib
from email.mime.text import MIMEText

from database import DBConnector
from DBConfig import DBConfig as DB

body_normal="""
Dear {name} {surname},

This is a kind reminder that you have a shift assignment tomorrow (on {date}). 
Your shift is starting in {in} hours. If you are covering the night shift, 
be well aware that it concerns the night from the {prev} to the {curr}.
We thank you for your attention.

Best regards,
The shift database. 
"""

body_shadow="""
Dear {name} {surname},

This is a kind reminder that you have booked a shadow shift tomorrow (on {date}). 
Your shift is starting in {in} hours.
We thank you in advance for attending.

Best regards,
The shift database. 
"""

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
    
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(1)
    
    #Get list of shifters for tomorrow
    res = myconn.executeGet("SELECT * FROM shifters.shifts_display WHERE date=%s", [tomorrow])
    normal_shifter = []
    shadow_shifter = []
    for r in res:
        if r["canceled"]:
            continue
        d = {}
        shift_date = datetime.datetime.combine(tomorrow, datetime.time(r["slot"]*8, 0, 0))
        d["date"] = shift_date.strftime("%d-%m-%Y at %H:%M:%S")
	t_delta = (shift_date-datetime.datetime.now())
        d["in"] = int((t_delta.seconds + t_delta.days * 24 * 3600)/(60*60))
        d["prev"] = today.strftime("%d-%m")
        d["curr"] = shift_date.strftime("%d-%m")
        d["name"] = r["name"]
        d["surname"] = r["surname"]
        d["emails"] = []
        if not r["email_cern"] is None and not r["email_cern"].strip()=="":
            d["emails"].append(r["email_cern"])
        if not r["email_priv"] is None and not r["email_priv"].strip()=="":
            d["emails"].append(r["email_priv"])
        
        if r["shift_type"]==3:
            shadow_shifter.append(d)
        else:
            normal_shifter.append(d)
    
    
    for shifter in normal_shifter:
        print shifter
        if len(shifter["emails"])==0:
            continue
        msg_body =  body_normal.format(**shifter)
    
        msg = MIMEText(msg_body)
        #shifter["emails"] = ["nicolas.lurkin@cern.ch", "nicolas.lurkin@gmail.com"]
        msg['Subject'] = "Your shift tomorrow"
        msg['From'] = "na62-shiftertraining@cern.ch"
        msg['To'] = ", ".join(shifter["emails"])
     
        print "Ready to send shifter message"
        server = smtplib.SMTP("localhost")
        server.sendmail("na62-shiftertraining@cern.ch", shifter["emails"], msg.as_string())
        server.quit()
        print "Message sent"
    
    sys.exit(0)
    for shifter in shadow_shifter:
        print shifter
        if len(shifter["emails"])==0:
            continue
        msg_body =  body_shadow.format(**shifter)
    
        msg = MIMEText(msg_body)
        #shifter["emails"] = ["nicolas.lurkin@cern.ch", "nicolas.lurkin@gmail.com"]
        msg['Subject'] = "Your shift tomorrow"
        msg['From'] = "na62-shiftertraining@cern.ch"
        msg['To'] = ", ".join(shifter["emails"])
     
        print "Ready to send shifter message"
        server = smtplib.SMTP("localhost")
        server.sendmail("na62-shiftertraining@cern.ch", shifter["emails"], msg.as_string())
        server.quit()
        print "Message sent"
      
