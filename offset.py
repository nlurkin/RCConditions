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

    with open(sys.argv[2], "r") as fd:
        for line in fd:

            splitArray = line.split()

            if len(splitArray)==2:
                tdcb = int(splitArray[0])
                commonValue = float(splitArray[1])
                for tdc in xml.tdcb[tdcb].tdc:
                    if xml.tdcb[tdcb].tdc[tdc].Offset != 0:
                        for channel in xml.tdcb[tdcb].tdc[tdc].channelOffset:
                            if xml.tdcb[tdcb].tdc[tdc].channelOffset > 0:
                                xml.tdcb[tdcb].tdc[tdc].addToChannelOffsetNS(channel, -commonValue)
                        
            if len(splitArray)==3:
                tdcb = int(splitArray[0])
                tdc = int(splitArray[1])
                if xml.tdcb[tdcb].tdc[tdc].Offset != 0:
                    commonValue = float(splitArray[2])
                    for channel in xml.tdcb[tdcb].tdc[tdc].channelOffset:
                        if xml.tdcb[tdcb].tdc[tdc].channelOffset > 0:
                            xml.tdcb[tdcb].tdc[tdc].addToChannelOffsetNS(channel, -commonValue)

            if len(splitArray)==4:
                tdcb = int(splitArray[0])
                tdc = int(splitArray[1])
                if xml.tdcb[tdcb].tdc[tdc].Offset != 0:
                    channel = int(splitArray[2])
                    commonValue = float(splitArray[3])
                    if xml.tdcb[tdcb].tdc[tdc].channelOffset > 0:
                        xml.tdcb[tdcb].tdc[tdc].addToChannelOffsetNS(channel, -commonValue)

        slotBin = 24.951059536
        fineBin = slotBin/256

        for tdcb in xml.tdcb:

            for tdc in xml.tdcb[tdcb].tdc:
                tdcOffsetNS = xml.tdcb[tdcb].tdc[tdc].OffsetNS
                minOffsetNS = 9999999

                modified = 0
                for channel in xml.tdcb[tdcb].tdc[tdc].channelOffset:
                    if xml.tdcb[tdcb].tdc[tdc].channelModify[channel]:
                        modified += 1
                        chOffsetNS = xml.tdcb[tdcb].tdc[tdc].channelOffsetNS[channel]
                        offsetNS = tdcOffsetNS + chOffsetNS
                        if offsetNS < minOffsetNS:
                            minOffsetNS = offsetNS

                if modified == 0:
                    continue

                slotOffset = int(minOffsetNS/slotBin)
                        
		xml.tdcb[tdcb].tdc[tdc].replaceOffset(slotOffset)
                for channel in xml.tdcb[tdcb].tdc[tdc].channelOffset:
                    if xml.tdcb[tdcb].tdc[tdc].channelModify[channel]:
                        chOffsetNS = xml.tdcb[tdcb].tdc[tdc].channelOffsetNS[channel]
                        offsetNS = tdcOffsetNS + chOffsetNS - slotOffset*slotBin
                        xml.tdcb[tdcb].tdc[tdc].replaceChannelOffsetNS(channel, offsetNS)
    

    with open("outfile.xml", "w") as fd:
        fd.write(etree.tostring(xml._xml, pretty_print=True))
        
        
