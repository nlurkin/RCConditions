#!/bin/env python

'''
XMLExtract.extractor -- Extract device xml configuration file from run xml

XMLExtract.extractor is a description

@author:     Nicolas Lurkin

@contact:    nicolas.lurkin@cern.ch
@deffield    updated: Updated
'''

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

import bz2
import sys
import XMLDoc
import urllib2
from lxml import etree
from string import replace

__all__ = []
__version__ = 0.1
__date__ = '2015-08-05'
__updated__ = '2015-08-05'

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
        print "{: <30} {: <30} {: <30}".format(*line)
    
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
    
    for i, ts in enumerate(listTs):
        if ts>xml._runStart and printStart==False:
            print "--->start"
            printStart = True
        if ts>xml._runEnd and printEnd==False:
            print "--->end"
            printEnd = True
        
        print "  [{index}]{cmd} {ts}{corrupt}".format(index= i, 
                                                      ts = ts, 
                                                      corrupt = "*" if listTs[ts]["bad"] else "",
                                                      cmd = listTs[ts]["cmd"])
    
    if len(listTs)>0:
        value = requestInput("Select entries")
        valueList = generateRange(value)
        retList = []
        for selected in valueList:
            if selected < len(listTs):
                retList.append(listTs.items()[selected])
        return retList
        
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
        text = XMLDoc.getSplitElementText(elementDict["node"])
        if text == "\"\"":
            print "This file is empty"
        else:
            with open("{devName}_{ts}.corrupt.xml".format(devName=path, ts=TS), "w") as fd:
                fd.write(text)
    else:
        xmlDoc = XMLDoc.parseSplitElementText(elementDict["node"])
        with open("{devName}_{ts}.xml".format(devName=path, ts=TS), "w") as fd:
            fd.write(etree.tostring(xmlDoc._xml, pretty_print=True))

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

def main(argv=None):
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    
    # Setup argument parser
    parser = ArgumentParser(description=program_shortdesc, formatter_class=RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", dest="file", help="File to process")
    group.add_argument("-r", "--run", dest="run", help="Run number to extract", type=int)
    parser.add_argument('-V', '--version', action='version', version=program_version_message)

    # Process arguments
    args = parser.parse_args()

    if not args.file is None:
        startReading(args.file)
    elif not args.run is None:
        try:    
            response = urllib2.urlopen('https://na62runconditions.web.cern.ch/na62runconditions/XMLProcessed/{0}.xml.bz2'.format(args.run))
            html = response.read()
        except urllib2.HTTPError as e:
            print e
            return -1
        data = bz2.decompress(html)
        startReading(data)
    return 0

if __name__ == "__main__":
    sys.exit(main())
    