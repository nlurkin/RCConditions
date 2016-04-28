#!/bin/env python
'''
Created on Apr 25, 2016

@author: nlurkin
'''
from datetime import datetime
import re
import sys
from database import DBConnector
from DBConfig import DBConfig as DB

from lxml import html

def getShiftID(myconn, date, slot):
    shift = myconn.executeGet("SELECT * FROM shifts WHERE date=%s AND slot=%s", [date, slot])
    if len(shift)>0:
        return shift[0]["id"]
    else:
        return -1

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

def getShiftAssignment(myconn, shifterID, shiftID, shiftType):
    r = myconn.executeGet("SELECT * FROM shifts_assignments WHERE shift_id=%s AND shifter_id=%s AND shift_type=%s", [shiftID, shifterID, shiftType])
    if len(r) > 1:
        print "Problem: more than one shift matching shift={0} shifter={1}".format(shiftID, shifterID)
        return -2
    elif len(r)==0:
        print "Shift not found shift={0} shifter={1}".format(shiftID, shifterID)
        return -1
    else:
        return r[0]["id"]
        
def addShiftAssignment(myconn, shifterID, shiftID, shiftType, institute, canceled):
    assignmentID = getShiftAssignment(myconn, shifterID, shiftID, shiftType)
    if assignmentID==-1:
        myconn.executeInsert("INSERT INTO shifts_assignments (shift_id, shifter_id, shift_type, canceled, institute) VALUES (%s,%s,%s,%s,%s)", [shiftID, shifterID, shiftType, canceled, institute])
    
def extractInfo(sh, shadow):
    canceled = False
    if "canceled" in sh:
        canceled = True
    sh = sh.replace("canceled", "").strip()
    if "_" in sh:
        [institute, name] = sh.split("_")
    elif not shadow:
        institute = sh
        name = "None"
    else:
        institute = None
        name = sh
    
    if name!=None:
        if name=="PerrinTerrin":
            name = "Perrin-Terrin"
        if name=="Cortina":
            name = "Cortina Gil"
        m = re.search("([A-Z][a-z]*)([A-Z][a-z]*)", name)
        if m:
            name = "{0} {1}".format(m.group(1), m.group(2))

    if not name is None:
        if ',' in name:
            name = name.split(",")
        else:
            name = name.split("/")

    return (institute, name, canceled)

def processLine(myconn, d, sh1, sh2, sh3, slot):
    (institute1, name1, canceled) = extractInfo(sh1, False)
    (institute2, name2, _) = extractInfo(sh2, False)
    if sh3.strip() != '' and sh3.strip()!='canceled':
        (_, name3, _) = extractInfo(sh3, True)
    else:
        name3 = []
    
    #print "{0:30}{1:30}{2:30}{3}".format(d.strftime("%Y-%m-%d {0}:00:00".format(slot*8)), "{0} ({1})".format(name1, institute1), "{0} ({1})".format(name2, institute2), canceled)
    shiftID = getShiftID(myconn, d, slot)
    if shiftID==-1:
        print "Shift not found {0} (slot {1})".format(d, slot)
        return
    
    if not name1 is None:
        for name in name1:
            name = name.strip()
            if name=="X":
                name = "None"
            userID = getUserID(myconn, "%", name)
            if userID==-1:
                print "Problem with user {0} for shift {1} slot {2} sh1".format(name, shiftID, slot)
            else:
                addShiftAssignment(myconn, userID, shiftID, 1, institute1, canceled)
                
    if not name2 is None:
        for name in name2:
            name = name.strip()
            if name=="X":
                name = "None"
            userID = getUserID(myconn, "%", name)
            if userID==-1:
                print "Problem with user {0} for shift {1} slot {2} sh2".format(name, shiftID, slot)
            else:
                addShiftAssignment(myconn, userID, shiftID, 2, institute2, canceled)

    if not name3 is None:
        for name in name3:
            name = name.strip()
            userID = getUserID(myconn, "%", name)
            if userID==-1:
                print "Problem with user {0} for shift {1} slot {2} sh3".format(name, shiftID, slot)
            else:
                addShiftAssignment(myconn, userID, shiftID, 3, "", canceled)
    
    
if __name__ == '__main__':
    tree = html.parse("/home/nlurkin/Downloads/na62_twiki.html")
    xxx = tree.xpath('//table[@class="twikiTable"]/tr[10]/td')
    dates = tree.xpath('//table[@class="twikiTable"]/tr[1]/th/font[not(contains(., "Week"))]/text()')
    night_sh1 = tree.xpath('//table[@class="twikiTable"]/tr[2]/td')
    night_sh2 = tree.xpath('//table[@class="twikiTable"]/tr[3]/td')
    night_sh3 = tree.xpath('//table[@class="twikiTable"]/tr[4]/td')
    day_sh1 = tree.xpath('//table[@class="twikiTable"]/tr[5]/td')
    day_sh2 = tree.xpath('//table[@class="twikiTable"]/tr[6]/td')
    day_sh3 = tree.xpath('//table[@class="twikiTable"]/tr[7]/td')
    eve_sh1 = tree.xpath('//table[@class="twikiTable"]/tr[8]/td')
    eve_sh2 = tree.xpath('//table[@class="twikiTable"]/tr[9]/td')
    eve_sh3 = tree.xpath('//table[@class="twikiTable"]/tr[10]/td')


    print html.tostring(xxx[0])
    print html.tostring(xxx[1])

    dateList = []
    for d in dates:
        try:
            date = datetime.strptime(d, "%A - %B %d")
        except ValueError as e:
            date = datetime.strptime(d, "%A %B %d")
        
        dateList.append(date.replace(year=2016).date())
    
    regex = re.compile("sh.?[12]+")
    
    night_sh1 = [regex.sub("", sh).strip() for sh in ["".join(sh.xpath("descendant-or-self::*/text()")) for sh in night_sh1] if sh.strip()!=""]
    night_sh2 = [regex.sub("", sh).strip() for sh in ["".join(sh.xpath("descendant-or-self::*/text()")) for sh in night_sh2] if sh.strip()!=""]
    night_sh3 = [regex.sub("", sh).strip() for sh in ["".join(sh.xpath("descendant-or-self::*/text()")) for sh in night_sh3[0::2]] if sh.strip()!="Shadow"]
    day_sh1 = [regex.sub("", sh).strip() for sh in ["".join(sh.xpath("descendant-or-self::*/text()")) for sh in day_sh1] if sh.strip()!=""]
    day_sh2 = [regex.sub("", sh).strip() for sh in ["".join(sh.xpath("descendant-or-self::*/text()")) for sh in day_sh2] if sh.strip()!=""]
    day_sh3 = [regex.sub("", sh).strip() for sh in ["".join(sh.xpath("descendant-or-self::*/text()")) for sh in day_sh3[0::2]] if sh.strip()!="Shadow"]
    eve_sh1 = [regex.sub("", sh).strip() for sh in ["".join(sh.xpath("descendant-or-self::*/text()")) for sh in eve_sh1] if sh.strip()!=""]
    eve_sh2 = [regex.sub("", sh).strip() for sh in ["".join(sh.xpath("descendant-or-self::*/text()")) for sh in eve_sh2] if sh.strip()!=""]
    eve_sh3 = [regex.sub("", sh).strip() for sh in ["".join(sh.xpath("descendant-or-self::*/text()")) for sh in eve_sh3[0::2]] if sh.strip()!="Shadow"]
    print len(dates), len(night_sh1), len(night_sh2), len(night_sh3), len(day_sh1), len(day_sh2), len(day_sh3), len(eve_sh1), len(eve_sh2), len(eve_sh3)
    eve_sh3.extend([""]*203)
    myconn = DBConnector(True)
    myconn.initConnection(passwd=sys.argv[1], host=DB.host, db="shifters", user=DB.userName, port=DB.port)
    myconn.openConnection()

    for (d, n_sh1, n_sh2, n_sh3, d_sh1, d_sh2, d_sh3, e_sh1, e_sh2, e_sh3) in zip(dateList, night_sh1, night_sh2, night_sh3, day_sh1, day_sh2, day_sh3, eve_sh1, eve_sh2, eve_sh3):
        print d
        processLine(myconn, d, n_sh1, n_sh2, n_sh3, 0)
        processLine(myconn, d, d_sh1, d_sh2, d_sh3, 1)
        processLine(myconn, d, e_sh1, e_sh2, e_sh3, 2)
