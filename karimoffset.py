#!/bin/env python
'''
Created on Aug 10, 2015

@author: nlurkin
'''

from math import copysign, fabs
import re
import sys

from lxml import etree

from XMLExtract import TEL62Decoder

clockPeriod = 24./961.883 * 1000.
def parseCorrections(xml, filePath, currentTEL62):
    with open(filePath, "r") as fd:
        for line in fd:
            if line[0] =="#":
                continue
            splitArray = line.split()
            channelNr = int(splitArray[0], 0)
            value = (float(splitArray[2])/clockPeriod * 256)
            value = int(-1*copysign(fabs(value)+0.5, value))
            
            TEL62 = int(channelNr/512)
            TDCB = (channelNr % 512)/128
            TDC = (channelNr % 128)/32
            CH = (channelNr % 32)
            
            if TEL62 == int(currentTEL62):
                print splitArray, TEL62, TDCB, TDC, CH, value
                xml.tdcb[TDCB].tdc[TDC].addToChannelOffset(CH, value)
                   
def parseGlobal(xml, filePath, currentTEL62):
    with open(filePath, "r") as fd:
        for line in fd:
            if line[0] =="#":
                continue
            splitArray = line.split()
            value = (float(splitArray[currentTEL62+4])/clockPeriod * 256)
            value = int(-1*copysign(fabs(value)+0.5, value))
            
            print splitArray, currentTEL62, value
            for tdcb in xml.tdcb:
                for tdc in xml.tdcb[tdcb].tdc:
                    for ch in xml.tdcb[tdcb].tdc[tdc].channelOffset:
                        if ch % 8 ==0:
                            xml.tdcb[tdcb].tdc[tdc].addToChannelOffset(ch, value)
def addToMap(myMap, tel62, tdcb, tdc, ch, val):
    if not tel62 in myMap:
        myMap[tel62] = {}
    if not tdcb in myMap[tel62]:
        myMap[tel62][tdcb] = {}
    if not tdc in myMap[tel62][tdcb]:
        myMap[tel62][tdcb][tdc] = {}
    if not ch in myMap[tel62][tdcb][tdc]:
        myMap[tel62][tdcb][tdc][ch] = 0
    
    myMap[tel62][tdcb][tdc][ch] += val
        
def readFineT0(filePath, channelMap):
    with open(filePath, "r") as fd:
        for line in fd:
            if line[0] == "#":
                continue
            splitArray = line.split()

            channelNr = int(splitArray[0], 0)
            value = float(splitArray[2])
#             value = (float(splitArray[2])/clockPeriod * 256)
#             value = int(-1*copysign(fabs(value)+0.5, value))
            
            TEL62 = int(channelNr/512)
            TDCB = (channelNr % 512)/128
            TDC = (channelNr % 128)/32
            CH = (channelNr % 32)
            
            addToMap(channelMap, TEL62, TDCB, TDC, CH, value)
            

def readMezzanineT0(filePath, channelMap):
    with open(filePath, "r") as fd:
        for line in fd:
            if line[0] == "#":
                continue
            splitArray = line.split()
            lNumber = int(splitArray[0][-3:-1])
            for i,offset in enumerate(splitArray[1:]):
                channelStart = lNumber*16*128 + i*128
                channelEnd = channelStart+128
                TEL62 = lNumber*4 + int(i/4)
                TDCB = lNumber*4 + i % 4
                for channel in range(channelStart, channelEnd):
                    TDC = (channel % 128)/32
                    CH = (channel % 32)
                    value = float(offset)
#                     value = (float(offset)/clockPeriod * 256)
#                     value = int(-1*copysign(fabs(value)+0.5, value))
                    addToMap(channelMap, TEL62, TDCB, TDC, CH, value)

def readStationT0(filePath, channelMap):
    with open(filePath, "r") as fd:
        for line in fd:
            if line[0] == "#":
                continue
            splitArray = line.split()

            value = float(splitArray[1])
#             value = (float(splitArray[1])/clockPeriod * 256)
#             value = int(-1*copysign(fabs(value)+0.5, value))
            
            for tel62 in channelMap:
                for tdcb in channelMap[tel62]:
                    for tdc in channelMap[tel62][tdcb]:
                        for ch in channelMap[tel62][tdcb][tdc]:
                            channelMap[tel62][tdcb][tdc][ch] += value

def applyMap(xml, channelMap, currentTEL62):
    for TDCB in channelMap[currentTEL62]:
        for TDC in channelMap[currentTEL62][TDCB]:
            for CH in channelMap[currentTEL62][TDCB][TDC]:
                value = (channelMap[currentTEL62][TDCB][TDC][CH]/clockPeriod * 256)
                value = int(-1*copysign(fabs(value)+0.5, value))
                
                xml.tdcb[TDCB].tdc[TDC].addToChannelOffset(CH, value)

if __name__ == '__main__':
    if len(sys.argv)<6 or "-h" in sys.argv:
        print "Wrong number of arguments. Expecting: inputXML StationT0 MezzanineT0 FineT0 outputXML"
        sys.exit(0)
        
    inputXMLFile = sys.argv[1]
    outputXMLFile = sys.argv[5]
    
    m = re.search(".*KTAG([0-9]+).*\.xml", inputXMLFile)
    if m:
        currentTEL62 = int(m.group(1))
    else:
        print "TEL62 number cannot be extracted"
        sys.exit(0)
    
    xml = TEL62Decoder(inputXMLFile)
    
    channelMap = {}
    readFineT0(sys.argv[4], channelMap)
    readMezzanineT0(sys.argv[3], channelMap)
    readStationT0(sys.argv[2], channelMap)
    
    applyMap(xml, channelMap, currentTEL62)
    
    xml.fixT0Offset()
    
    #parseCorrections(xml, sys.argv[1], currentTEL62)
    #parseGlobal(xml, sys.argv[1], currentTEL62)
    with open(outputXMLFile, "w") as fd:
        fd.write(etree.tostring(xml._xml, pretty_print=True))
