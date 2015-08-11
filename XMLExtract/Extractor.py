#!/bin/env python

'''
XMLExtract.extractor -- Extract device xml configuration file from run xml

XMLExtract.extractor is a description

@author:     Nicolas Lurkin

@contact:    nicolas.lurkin@cern.ch
@deffield    updated: Updated
'''

from string import replace
import sys
from lxml import etree
import XMLDoc
from XMLExtract import BufferPrint
from XMLExtract import TEL62Decoder, L0TPDecoder, CREAMDecoder

def generateSystemSpecificDecoder(xmlDoc):
    if xmlDoc._type==None:
        xmlDoc.identifyFileType()
    if xmlDoc._type=="TEL":
        return TEL62Decoder(xmlDoc)
    elif xmlDoc._type=="L0TP":
        return L0TPDecoder(xmlDoc)
    elif xmlDoc._type=="CREAM":
        return CREAMDecoder(xmlDoc)
    else:
        return xmlDoc

class abortException(Exception):
    """
    Used to go back directly to top function
    """
    def __init__(self):
        pass
    
def requestInput(text):
    """
    Request a raw input and test special values.
        -1: Raise abortException
        .q: Exit
        
    Args:
        text: Text to display
    """
    uInput = raw_input("{0}:".format(text))
    if uInput == "":
        uInput = "*"
    if uInput == "-1":
        raise abortException()
    if uInput==".q":
        sys.exit(0)
    
    return uInput 

def generateRange(value):
    """
    Takes a string values and generate a range from it.
    "1,4,6-9" generates [1,4,6,7,8,9]
    
    Args:
        value: String representing ranges
    
    Returns:
        List of integers
    """
    valuesList = []
    disjointList = [x.strip() for x in value.split(",")]
    for r in disjointList:
        rLimits = r.split("-")
        if len(rLimits)>1:
            valuesList.extend(range(XMLDoc.tryint(rLimits[0]), XMLDoc.tryint(rLimits[-1])+1))
        else:
            valuesList.append(XMLDoc.tryint(rLimits[0]))
    
    return valuesList
        
def selectDevice(xml):
    """
    Requests a wildcard expression for the devices to search and
    then displays the list of matching devices. User is requested
    to select one of the displayed devices.
    
    Args:
        xml: Good rcXML instance
    
    Returns:
        String: Name of the selected device 
    """
    expr = requestInput("Please enter a device expression")
        
    devList = xml.getMatchingDevs(replace(expr, "*", ".*"))

    print "List of available devices"
    printArray = [[]]
    for i, dev in enumerate(devList):
        if len(printArray[-1])>=3:
            printArray.append([])

        printArray[-1].append("  [{index}] {dev}".format(index = i, dev=dev))
    
    while len(printArray[-1])<3:
        printArray[-1].append("")
        
    for line in printArray:
        print "{0: <30} {1: <30} {2: <30}".format(*line)
    
    value = requestInput("Select one entry")
    selected = XMLDoc.tryint(value)
    if selected < len(devList):
        return devList[selected]
        
def selectTimeStamp(xml, selectedDevice):
    """
    Extracts all the elements for the requested device
    and displays their timestamp (with some additional
    information). User is requested to select one or more
    of the timestamp.
    
    Args:
        xml: Good rcXML instance
        selectedDevice: Name of the device to extract
        
    Returns:
        List of selected timestamp Tuple [(Timestamp, {"node":node, "bad":bad, "cmd":cmd})]
    """
    listTs = xml.getTagsRefsWithTS(selectedDevice)
    XMLDoc.checkElementsXMLValidity(listTs)

    printStart = False
    printEnd = False
    print "Found element at following timestamps:"
    print "  [i]TC Timestamp*"
    print "  (i: index; T: R(eport) or S(ent); C: I(NITIALIZE) or S(TART_RUN); *: Invalid XML file)"
    print ""
    
    for i, ts in enumerate(sorted(listTs)):
        if ts>xml._runStart and printStart==False:
            print "--->start"
            printStart = True
        if ts>xml._runEnd and printEnd==False:
            print "--->end"
            printEnd = True
        
        print "  [{index}]{type}{cmd} {ts}{corrupt}".format(index= i, 
                                                      ts = ts, 
                                                      corrupt = "*" if listTs[ts]["bad"] else "",
                                                      cmd = listTs[ts]["cmd"], 
                                                      type = listTs[ts]["type"])
    
    if len(listTs)>0:
        value = requestInput("Select entries")
        valueList = generateRange(value)
        retList = []
        for selected in valueList:
            if selected < len(listTs):
                retList.append(sorted(listTs.items())[selected])
        return retList

def printRaw(xmlNode, path, TS):
    _, text = XMLDoc.getSplitElementText(xmlNode)
    if text == "\"\"":
        print "This file is empty"
    else:
        ret = BufferPrint.displayBuffer(text)
        if ret==BufferPrint.OperationType.WRITE:
            with open("{devName}_{ts}.corrupt.xml".format(devName=path, ts=TS), "w") as fd:
                fd.write(text)    

def printGenericXML(xmlDoc, path, TS):
    generateSystemSpecificDecoder(xmlDoc)
    ret = BufferPrint.displayBuffer(str(xmlDoc))
    if ret==BufferPrint.OperationType.WRITE:
        with open("{devName}_{ts}.xml".format(devName=path, ts=TS), "w") as fd:
            fd.write(etree.tostring(xmlDoc._xml, pretty_print=True))
            
            
def writeFile(elementDict, TS):
    """
    Write node text content in file. Either as XML if possible
    else as plain text.
    The file has a name device_timestamp(.corrupt).xml with 
    corrupt if XML is not possible.
    
    Args:
        elementDict: Element dictionary  {"node":node, "bad":bad, "cmd":cmd}
        TS: element timestamp
    """
    path = elementDict["node"].tag
    if elementDict["bad"]:
        printRaw(elementDict["node"], path, TS)
    else:
        _, xmlDoc = XMLDoc.parseSplitElementText(elementDict["node"])
        printGenericXML(xmlDoc, path, TS)

def startReading(filePath):
    """
    Read a RunControl xml and interactively allows user 
    to retrieve configuration files from it.
    Selection of a device pattern, then selection of
    a device in a list of devices matching the pattern.
    Finally selection of one or more of the timestamp for this
    device. The information written at this timestamp for
    this device is written in a file.
    
    Args:
        filePath: Path to a RunControl file
    """
    xml = XMLDoc.rcXML(filePath)
    if not xml._bad:
        xml.extractInfo()
        while True:
            try:
                print ""
                print str(xml)
                selDev = selectDevice(xml)
                selElement = selectTimeStamp(xml, selDev)
                for selection in selElement:
                    writeFile(selection[1], selection[0])
            except abortException:
                pass

