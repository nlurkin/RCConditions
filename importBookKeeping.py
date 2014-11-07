#!/bin/env python

'''
Created on Nov 4, 2014

@author: ncl
'''

import os
import sys

from config import ConfigFile
from database import DBConnector
from runConfig import runParam
import xml.dom.minidom as xmld


param = None
##---------------------------------------
#    Utility functions for XML
##---------------------------------------
def importFile(filePath):
    """Parse XML from file"""
    return xmld.parse(filePath)


def getAttribute(node, attributeName):
    """Return a node attribute ( <node attrA=aaa attrB=bbb></node> )"""
    attr = node.attributes
    for i in range(0, attr.length):
        if attr.item(i).name == attributeName:
            return attr.item(i).value 

def getValue(nodelist):
    """Return the text contained in a node ( <node>this text</node> )"""
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

##---------------------------------------
#    Utility functions
##---------------------------------------
def findPreviousInList(varList, val):
    """
    Find the element of the sorted varList that is just before val. Returns the index and the value of the element.
    """
    if len(varList)==0:
        return 0, False
    
    ## If val is smaller than any in the list, there is no previous element
    if varList[0]>val:
        return 0, False

    ## Val is greater than all elements in the list, return the last one
    if val>varList[-1]:
        return len(varList), varList[-1]
    
    ## Go through the list. When an element is greater than val, we just passed the one we were searching
    for i,el in enumerate(varList[1:]):
        if el>val:
            return i,varList[i] 
    

def str2bool(val):
    """
    Transform boolean string to boolean type
    """
    return val.lower() in ("true")

def removeAllAfterTS(tsDict, endTS):
    lDict = sorted(tsDict.keys())
    
    for ts in lDict:
        if ts>endTS:
            del tsDict[ts]
    
##---------------------------------------
#    Functions to for trigger processing
##---------------------------------------
def buildNIMMask(fd):
    """
    Return a list of mask with each NIM trigger LUT.
    The mask for a LUT is only build if detE != 1 (trick for 'don't use this LUT')
    
    Input:
        fd: ConfigFile instance
    """
    l = []
    for i in range(0, 7):
        if int(fd.getPropertie("lut%i_nim_detEmask" % (i))) != 1:
            row = []
            row.append(fd.getPropertie("lut%i_nim_detAmask" % (i)))
            row.append(fd.getPropertie("lut%i_nim_detBmask" % (i)))
            row.append(fd.getPropertie("lut%i_nim_detCmask" % (i)))
            row.append(fd.getPropertie("lut%i_nim_detDmask" % (i)))
            row.append(fd.getPropertie("lut%i_nim_detEmask" % (i)))
            l.append(''.join(row))

    return l

def buildPrimitiveMask(fd):
    """
    Return a list of mask with each Primitive trigger LUT.
    
    Input:
        fd: ConfigFile instance
    """
    l = []
    for i in range(0, 7):
        row = []
        row.append(fd.getPropertie("lut%i_detAmask" % (i)))
        row.append(fd.getPropertie("lut%i_detBmask" % (i)))
        row.append(fd.getPropertie("lut%i_detCmask" % (i)))
        l.append(''.join(row))

    return l

def simplifyTrigger(trigg, reject):
    """
    Simplify triggers to merge timestamps with same content.
    
    Input:
        trigg: triggers map
        reject: trigger propertie values to reject
    """
    lTrigg = sorted(trigg.keys())
    prev = [0,0]
    for t in lTrigg:
        if trigg[t]==prev:  ## if current entry is the same as the previous, delete the current
            del trigg[t]
        elif trigg[t][1]==reject:  ## if the current entry is one that should be rejected, delete it
            del trigg[t]    
        else:
            prev = trigg[t]
            
def mergeTriggers(trigg, prop, startTS, endTS):
    """
    Merge the trigger enabled and trigger propertie maps and simplify the resulting map
    
    Input:
        trigg: map of enabled trigger
        prop: map of trigger properties
        startTS: start run timestamp
        endTS: end run timestamp
    """
    lProp = sorted(prop.keys())
    lTrigg = sorted(trigg.keys())
    
    ## Go through the enabled list
    for t in lTrigg:
        if t>endTS:     ## If current timestamp is after the end of run, don't care
            continue
        
        ## Find the previous entry in the properties
        i,closest = findPreviousInList(lProp, t)
        if closest:
            ## If found, delete it because used and assign it to the current enabled
            del lProp[i]
            trigg[t][1] = prop[closest][1]

    ## Go through the remaining properties list
    for t in lProp:
        if t>endTS:     ## If current timestamp is after the end of run, don't care
            continue
        
        ## Find the previous entry in the enabled list
        i,closest = findPreviousInList(lTrigg, t)
        if closest:
            ## If found, assign the current propertie to this enabled
            trigg[closest] = [trigg[closest][0], prop[t][1]]
    
    ## Find the element just before the start run timestamp and delete all elements before that one
    i,_ = findPreviousInList(lTrigg, startTS)
    for t in lTrigg[:i]:
        del trigg[t]

    simplifyTrigger(trigg, None)

##---------------------------------------
#    Functions to retrieve batch of info from XML doc
##---------------------------------------
def retrieveAllRunInfos(nodeList, runNumber):
    """Return a map of runInfo.
    
    Input: 
        nodeList: list of <RunInfo> nodes
        runNumber: the run number for which the info should be extracted
    """
    runInfoMap = {'RunType':'', 'RunNumber':'', 'RunStartTime':'', 'RunStopTime':'', 'StartRunComment':'', 'EndRunComment':''};
    goodInfo = False
    for node in nodeList:
        runNumberNode = node.getElementsByTagName("RunNumber")
        if goodInfo==False:
            runTypeNode = node.getElementsByTagName("RunType")
            if runTypeNode.length > 0:
                runInfoMap['RunType'] = getValue(runTypeNode[0].childNodes)
        if runNumberNode.length > 0:
            rid = getValue(runNumberNode[0].childNodes)
            if int(rid)==runNumber:
                goodInfo = True
            else:
                goodInfo = False
        if goodInfo:
            for cnode in node.childNodes:
                if cnode.nodeName != 'RunType':
                    val = getValue(cnode.childNodes)
                    if val!="":
                        runInfoMap[cnode.nodeName] = val
    return runInfoMap

def getTriggerEnabled(listNodes):
    """Return a map of triggers (enabled fields only).
    
    Each map element is a map of timestamp whose element are a 2 elements list. The second is always None
    {123456:[True|False, None]}
    
    Input: 
        listNodes: list of <L0TP> nodes
    """
    events = {'Periodic':{}, 'NIM':{}, 'Primitive':{}, 'Calib':{}, 'Sync':{}}
    for node in listNodes:
        eventNode = node.parentNode
        timestamp = int(getAttribute(eventNode, "Timestamp"))
        
        triggerList = node.childNodes
        for tNode in triggerList:
            if "Activated" in tNode.nodeName:
                triggerName = tNode.nodeName.split('.')[1]
                val = getValue(tNode.childNodes)
                events[triggerName][timestamp] = [str2bool(val), None]
    return events

def getTriggerProperties(listNode):
    """Return a map of triggers (propertie fields only).
    
    Each map element is a map of timestamp whose element are a 2 elements list. 
    The first is always None, the second (triggProp) is dependent of the trigger type 
    {123456:[None, triggProp]}
    
    Input: 
        listNodes: list of <na62L0TP_Torino> nodes
    """

    events = {'Periodic':{}, 'NIM':{}, 'Primitive':{}, 'Calib':{}, 'Sync':{}}
    for node in listNode:
        fileContentNodeList = node.getElementsByTagName(param.configFileTagName)
        eventNode = node.parentNode
        timestamp = int(getAttribute(eventNode, "Timestamp"))
        if fileContentNodeList.length>0:
            fileContentNode = fileContentNodeList[0]
            val = getValue(fileContentNode.childNodes)
            fc = ConfigFile(val)
            events['Periodic'][timestamp] = [None, int(fc.getPropertie("periodicTrgTime"))]
            events['NIM'][timestamp] = [None, [x for x in buildNIMMask(fc)]]
            events['Primitive'][timestamp] = [None, buildPrimitiveMask(fc)]
    
    return events

def getDetectorID(listNode):
    for node in listNode:
        l = node.getElementsByTagName("Name")
        if len(l)>0:
            val = getValue(l[0].childNodes)
            if len(val)>0:
                return int(val[1:], 0)

def getDetectorEnabled(listNode):
    enabled = {}
    for node in listNode:
        detectorName = node.parentNode.nodeName
        timestamp = getAttribute(node.parentNode.parentNode, "Timestamp")
        val = getValue(node.childNodes)
        if not detectorName in enabled:
            enabled[detectorName] = {}
        enabled[detectorName][int(timestamp)] = [str2bool(val), None]
    
    return enabled

def setDetectorID(detList, detID):
    for el in detList:
        detList[el][1] = detID

def exportFile(myconn, filePath):
    global param
    ## Import config file
    doc = importFile(filePath)
    rootNode = doc.getElementsByTagName("Run")[0]
    
    ## Get run info
    runNumber = getAttribute(rootNode, "id")
    param = runParam(runNumber)
    startTS = int(getAttribute(rootNode, "startTime"))
    endTS = int(getAttribute(rootNode, "endTime"))
    runInfoList = doc.getElementsByTagName("RunInfo")
    
    runInfo = retrieveAllRunInfos(runInfoList, int(runNumber))
    
    ## Get Trigger info
    l0tpList = doc.getElementsByTagName("L0TP")
    triggerDict = getTriggerEnabled(l0tpList)
    
    l0tpFileList = doc.getElementsByTagName("na62L0TP_Torino")
    triggerProp = getTriggerProperties(l0tpFileList)
    
    
    ## Process triggers into a coherent timeline
    mergeTriggers(triggerDict['Periodic'], triggerProp['Periodic'], startTS, endTS)
    mergeTriggers(triggerDict['NIM'], triggerProp['NIM'], startTS, endTS)
    mergeTriggers(triggerDict['Primitive'], triggerProp['Primitive'], startTS, endTS)
    simplifyTrigger(triggerDict['Calib'], -1)
    simplifyTrigger(triggerDict['Sync'], -1)
    
    removeAllAfterTS(triggerDict['Periodic'], endTS)
    removeAllAfterTS(triggerDict['NIM'], endTS)
    removeAllAfterTS(triggerDict['Primitive'], endTS)
    removeAllAfterTS(triggerDict['Calib'], endTS)
    removeAllAfterTS(triggerDict['Sync'], endTS)
    
    ## Get detector enabled info
    enabledList = doc.getElementsByTagName("Enabled")
    detEnabled = getDetectorEnabled(enabledList)
    for det in detEnabled:
        setDetectorID(detEnabled[det], getDetectorID(doc.getElementsByTagName(det)))
        removeAllAfterTS(detEnabled[det], endTS)
        
    ## Insert runinfo into DB
    myconn.setRunInfo(runInfo)
    
    ## Insert triggers into DB
    myconn.setPeriodicTriggerList(triggerDict['Periodic'], runNumber)
    myconn.setNIMTriggerList(triggerDict['NIM'], runNumber)
    myconn.setPrimitiveTriggerList(triggerDict['Primitive'], runNumber)
    
    myconn.setSyncTriggerList(triggerDict['Sync'], runNumber)
    myconn.setCalibTriggerList(triggerDict['Calib'], runNumber)
    
    myconn.setEnabledDetectorList(detEnabled, runNumber)
    
if __name__ == '__main__':
    if len(sys.argv)<3:
        print "Please provide path and database password"
        sys.exit()


    myconn = DBConnector()
    myconn.connectDB(passwd=sys.argv[2])
    myconn.setNIMNames(1409529600, None, [[0,'Q1'], [1,'NHOD'], [2,'MUV2'], [3,'MUV3'], [4,'']])


    if len(sys.argv)>1:
        filePath = sys.argv[1]
    else:
        filePath = "/home/ncl/sampleExportConfig.xml"
    
    if os.path.isdir(filePath):
        fileList = [filePath+"/"+f for f in sorted(os.listdir(filePath))]
    else:
        fileList = [filePath]
    
    for f in fileList:
        if os.path.isfile(f):
            print "\nImport " + f + "\n---------------------"
            exportFile(myconn, f)
    
    myconn.close()
