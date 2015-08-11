#!/usr/bin/python
'''
Created on Aug 10, 2015

@author: nlurkin
'''

from XMLExtract import TEL62Decoder
import sys
from lxml import etree


if __name__ == '__main__':

    inputXMLFile = sys.argv[1]
    
    xml = TEL62Decoder(inputXMLFile)
    parseCorrections(xml, sys.argv[2])

    with open(filePath, "r") as fd:
        for line in fd:

            splitArray = line.split()

            if len(splitArray)==2:
                tdcb = splitArray[0]
                commonValue = splitArray[1]
                for tdc in xml.tdcb[tdcb].tdc:
                    for channel in xml.tdcb[tdcb].tdc[tdc].channels:
                        xml.tdcb[tdcb].tdc[tdc].addToOffsetNS(channel, -commonValue)
                        
            if len(splitArray)==3:
                tdcb = splitArray[0]
                tdc = splitArray[1]
                commonValue = splitArray[2]
                for channel in xml.tdcb[tdcb].tdc[tdc].channels:
                    xml.tdcb[tdcb].tdc[tdc].addToOffsetNS(channel, -commonValue)

            if len(splitArray)==4:
                tdcb = splitArray[0]
                tdc = splitArray[1]
                channel = splitArray[2]
                commonValue = splitArray[3]
                xml.tdcb[tdcb].tdc[tdc].addToOffsetNS(channel, -commonValue)


        slotBin = 24.951059536
        fineBin = slot_bin/256

        for tdcb in xml.tdcb:

            for tdc in xml.tdcb[tdcb]:
                tdcOffsetNS = xml.tdcb[tdcb].tdc[tdc].OffsetNS
                minOffsetNS = 9999999

                for channel in xml.tdcb[tdcb].tdc[tdc].channels:
                    chOffsetNS = xml.tdcb[tdcb].tdc[tdc].channelOffsetNS[channel]
                    offsetNS = tdcOffsetNS + chOffsetNS
                    if offsetNS < minOffsetNS:
                        minOffsetNS = offsetNS

                slotOffset = int(minOffsetNS/slotBin)
                        
                xlm.tdcb[tdcb].tdc[tdc].replaceOffset(slotOffset)
                for channel in xml.tdcb[tdcb].tdc[tdc].channels:
                    chOffsetNS = xml.tdcb[tdcb].tdc[tdc].channelOffsetNS[channel]
                    offsetNS = tdcOffsetNS + chOffsetNS - slotOffset*slotBin
                    xml.tdcb[tdcb].tdc[tdc].replaceChannelOffsetNS[channel](offsetNS)
    

    with open("outfile.xml", "w") as fd:
        fd.write(etree.tostring(xml, pretty_print=True))
        
        
