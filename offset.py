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
        
def parseCorrections(xml, filePath):
    with open(filePath, "r") as fd:
        for line in fd:
            splitArray = line.split()
            if len(splitArray)==2:
                tdcb = splitArray[0]
                commonValue = splitArray[1]
                for tdc in xml.tdcb[tdcb].tdc:
                    for channel in xml.tdcb[tdcb].tdc[tdc].channels:
                        xml.tdcb[tdcb].tdc[tdc].replaceChannelOffset(channel, commonValue)
                        
            if len(splitArray)==3:
                tdcb = splitArray[0]
                tdc = splitArray[1]
                commonValue = splitArray[2]
                for channel in xml.tdcb[tdcb].tdc[tdc].channels:
                    xml.tdcb[tdcb].tdc[tdc].replaceChannelOffset(channel, commonValue)
            if len(splitArray)==4:
                tdcb = splitArray[0]
                tdc = splitArray[1]
                channel = splitArray[2]
                commonValue = splitArray[3]
                xml.tdcb[tdcb].tdc[tdc].replaceChannelOffset(channel, commonValue)
    
    channelsAverage = sum(xml.tdcb[tdcb].tdc[tdc].channels.values())/len(xml.tdcb[tdcb].tdc[tdc].channels)
    xml.tdcb[tdcb].tdc[tdc].replaceOffset(commonValue)
    
    with open("outfile.xml", "w") as fd:
        fd.write(etree.tostring(xml, pretty_print=True))
        
