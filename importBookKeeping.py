#!/usr/bin/python

'''
Created on Nov 4, 2014

@author: ncl
'''

import bz2
from contextlib import closing
import os
import re
import shutil
import sys

import xml.dom.minidom as xmld

from XMLExtract import Timeline, L0TPDecoder, tryint
from XMLExtract.Timeline import TriggerObject, DetectorObject
from NA62DB import DBConnector
from NA62DB.DBConfig import DBConfig as DB
from runConfig import runParam
from XMLExtract.L0TPDecoder import PrimitiveInfo


def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

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

def str2bool(val):
    """
    Transform boolean string to boolean type
    """
    return val.lower() in ("true")
            
def mergeTriggers(trigg, prop, startTS, endTS):
    """
    Merge the trigger enabled and trigger propertie maps and simplify the resulting map
    
    Input:
        trigg: map of enabled trigger
        prop: map of trigger properties
        startTS: start run timestamp
        endTS: end run timestamp
    """
    trigg.merge(prop, True)
    trigg.cutAfter(endTS)
    trigg.cutBefore(startTS, 1)
    trigg.simplify()

##---------------------------------------
#    Functions to retrieve batch of info from XML doc
##---------------------------------------
def retrieveAllRunInfos(nodeList, runNumber):
    """Return a map of runInfo.
    
    Input: 
        nodeList: list of <RunInfo> nodes
        runNumber: the run number for which the info should be extracted
    """
    runInfoMap = {'RunType':'', 'RunNumber':'', 'RunStartTime':None, 'RunStopTime':None, 'StartRunComment':'', 'EndRunComment':'', 'TotalBurst':'', 'totalL0':'', 'totalL1':'', 'totalL2':''};
    for node in nodeList:
        goodInfo = False
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
    
    Each map element is a map of timestamp whose element are a 3 elements list. The second and third is always None
    {123456:[True|False, None, None]}
    
    Input: 
        listNodes: list of <L0TP> nodes
    """
    events = {'Periodic':Timeline(TriggerObject), 
              'NIM':Timeline(TriggerObject), 'Primitive':Timeline(TriggerObject), 
              'Calib':Timeline(TriggerObject), 'Sync':Timeline(TriggerObject)}
    for node in listNodes:
        eventNode = node.parentNode
        timestamp = int(getAttribute(eventNode, "Timestamp"))
        
        triggerList = node.childNodes
        for tNode in triggerList:
            if "Activated" in tNode.nodeName:
                triggerName = tNode.nodeName.split('.')[1]
                val = getValue(tNode.childNodes)
                tobject = events[triggerName].addTS(timestamp)
                tobject.Enabled = str2bool(val)
    return events

def getTriggerProperties(listNode):
    """Return a map of triggers (propertie fields only).
    
    Each map element is a map of timestamp whose element are a 2 elements list. 
    The first is always None. The second (triggProp) is dependent of the trigger type 
    {123456:[None, triggProp]}. The third is the reference detector: None for periodic, calib and sync.
    
    Input: 
        listNodes: list of <na62L0TP_Torino> nodes
    """

    events = {'Periodic':Timeline(TriggerObject), 
              'NIM':Timeline(TriggerObject), 'Primitive':Timeline(TriggerObject), 
              'Calib':Timeline(TriggerObject), 'Sync':Timeline(TriggerObject)}
    for node in listNode:
        fileContentNodeList = node.getElementsByTagName(param.configFileTagName)
        eventNode = node.parentNode
        timestamp = int(getAttribute(eventNode, "Timestamp"))
        if fileContentNodeList.length>0:
            fileContentNode = fileContentNodeList[0]
            val = getValue(fileContentNode.childNodes)
            l0tpConfig = L0TPDecoder(val, param.runNumber) 
            if not l0tpConfig._bad:
                tobject = events['Periodic'].addTS(timestamp)
                tobject.Propertie = l0tpConfig.getPeriodicPeriod()
                #tobject = events['NIM'].addTS(timestamp)
                #tobject.Propertie = l0tpConfig.getNIMMasks()
                #tobject.RefDetector = l0tpConfig.getNIMRefDetector()
                tobject = events['Primitive'].addTS(timestamp)
                tobject.Propertie = l0tpConfig.getPrimitiveMasks()
                tobject.RefDetector = l0tpConfig.getPrimitiveRefDetector()
                for prim in tobject.Propertie:
                    setPrimitivesReferences(prim)
    
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
        if detectorName=="CEDAR":
            detectorName="KTAG"
        if not detectorName in enabled:
            enabled[detectorName] = Timeline(DetectorObject)
        detObj = enabled[detectorName].addTS(int(timestamp))
        detObj.Enabled = str2bool(val)
    
    return enabled

def setDetectorID(detList, detID):
    for el in detList.getList():
        el[1].Name = detID

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
    totalBurst = getAttribute(rootNode, "totalBurst")
    totalL0 = getAttribute(rootNode, "totalL0")
    totalL1 = getAttribute(rootNode, "totalL1")
    totalL2 = getAttribute(rootNode, "totalL2")
    totalMerger = getAttribute(rootNode, "totalMerger")
    runInfoList = doc.getElementsByTagName("RunInfo")

    runInfo = retrieveAllRunInfos(runInfoList, int(runNumber))
    
    runInfo['TotalBurst'] = None if totalBurst==None else int(totalBurst)
    runInfo['TotalL0'] = None if totalL0==None else int(totalL0)
    runInfo['TotalL1'] = None if totalL1==None else int(totalL1)
    runInfo['TotalL2'] = None if totalL2==None else int(totalL2)
    runInfo['TotalMerger'] = None if totalMerger==None else int(totalMerger)

    if runInfo['RunNumber']=='':
        return
    ## Get Trigger info
    l0tpList = doc.getElementsByTagName("L0TP")
    triggerDict = getTriggerEnabled(l0tpList)
    
    l0tpFileList = doc.getElementsByTagName("na62L0TP_Torino")
    triggerProp = getTriggerProperties(l0tpFileList)
    
    ## Process triggers into a coherent timeline
    refTriggerObject = TriggerObject()
    refTriggerObject.Propertie = -1;
    mergeTriggers(triggerDict['Periodic'], triggerProp['Periodic'], startTS, endTS)
    #mergeTriggers(triggerDict['NIM'], triggerProp['NIM'], startTS, endTS)
    mergeTriggers(triggerDict['Primitive'], triggerProp['Primitive'], startTS, endTS)
    triggerDict['Calib'].simplify(refTriggerObject)
    triggerDict['Sync'].simplify(refTriggerObject)
    
    triggerDict['Calib'].cutAfter(endTS)
    triggerDict['Sync'].cutAfter(endTS)

    ## Get detector enabled info
    enabledList = doc.getElementsByTagName("Enabled")
    detEnabled = getDetectorEnabled(enabledList)
    detMap = {"KTAG":4, "GTK":8, "CHANTI":12, "LAV":16, "STRAW": 20, "CHOD":24, "RICH":28, "IRC_SAC":32, "LKR":36, "MUV1":40, "MUV2":44, "MUV3":48, "SAC":52, "L0TP":64}
    for det in detEnabled:
        detID = getDetectorID(doc.getElementsByTagName(det))
        if detID==None:
            detID = detMap[det]
        setDetectorID(detEnabled[det], detID)
        detEnabled[det].cutAfter(endTS)
    
    if myconn is None:
        #Print everything
        print "Run TS: %i -> %i" % (startTS, endTS)
        print "RunInfo"
        print runInfo
        
        print "Periodic triggers"
        print triggerDict['Periodic'].getList()

        #print "NIM triggers"
        #print triggerDict['NIM'].getList()

        print "Primitive triggers"
        print triggerDict['Primitive'].getList()
        
        print "Enabled detectors"
        for det in detEnabled:
            print det
            print detEnabled[det].getList()
        
        return False
    else:
        ## Insert runinfo into DB
        myconn.setRunInfo(runInfo)
        
        ## Insert triggers into DB
        myconn.setPeriodicTriggerList(triggerDict['Periodic'], runNumber)
        #myconn.setNIMTriggerList(triggerDict['NIM'], runNumber)
        myconn.setPrimitiveTriggerList(triggerDict['Primitive'], runNumber)
        
        myconn.setSyncTriggerList(triggerDict['Sync'], runNumber)
        myconn.setCalibTriggerList(triggerDict['Calib'], runNumber)
        
        myconn.setEnabledDetectorList(detEnabled, runNumber)
        
        return True

def setPrimitivesReferences(prim):
    if myconn is None:
        return
    l0 = L0TPDecoder
    startTS = 1435701600
    
    primDef = PrimitiveInfo()
    
    primDef.detA = l0.getPrimitiveMeaning("A", prim.detA)
    primDef.detB = l0.getPrimitiveMeaning("B", prim.detB)
    primDef.detC = l0.getPrimitiveMeaning("C", prim.detC)
    primDef.detD = l0.getPrimitiveMeaning("D", prim.detD)
    primDef.detE = l0.getPrimitiveMeaning("E", prim.detE)
    primDef.detF = l0.getPrimitiveMeaning("F", prim.detF)
    primDef.detG = l0.getPrimitiveMeaning("G", prim.detG)
    
    myconn.setPrimitivesNames(startTS, None, primDef, prim)
    
if __name__ == '__main__':
    if len(sys.argv)<3:
        print "Please provide path and database password"
        sys.exit()

    
    #myconn = None
    myconn = DBConnector(False)
    myconn.initConnection(passwd=sys.argv[-1:][0], db=DB.dbName, user=DB.userName, host=DB.host, port=DB.port)
    myconn.openConnection()
    #myconn.setNIMNames(1409529600, None, [[0,'Q1'], [1,'NHOD'], [2,'MUV2'], [3,'MUV3'], [4,'']])
    #myconn.setPrimitivesNames(1409529600, None, [[0,'Q1'], [1,'NHOD'], [2,'MUV2'], [3,'MUV3'], [4,'']])

    if len(sys.argv)>1:
        filePath = sys.argv[1:]
    else:
        filePath = ["/home/ncl/sampleExportConfig.xml"]
    
    fileList = []
    for path in filePath:
        if os.path.isdir(path):
            fileList.extend([path+"/"+f for f in sorted(os.listdir(path))])
        else:
            fileList.append(path)
    
    fileList.sort(key=alphanum_key)
    for f in fileList:
        if os.path.isfile(f):
            print "\nImport " + f + "\n---------------------"
            if not exportFile(myconn, f):
                continue
            with open(f, 'rb') as inputFile:
                with closing(bz2.BZ2File('/home/lkrpn0/XMLProcessed/%s.bz2' % os.path.basename(f), 'wb', compresslevel=9)) as outputFile:
                    shutil.copyfileobj(inputFile, outputFile)
            #shutil.copyfile(f, '/home/lkrpn0/XMLProcessedDBOD/%s' % os.path.basename(f))
            os.remove(f)
            #shutil.move(f, "/home/XMLProcessed/" + os.path.basename(f))
    if not myconn is None:
        myconn.close()
