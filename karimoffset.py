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
                   

if __name__ == '__main__':
    inputXMLFile = sys.argv[2]
    
    m = re.search(".*KTAG([0-9]+).*\.xml", inputXMLFile)
    if m:
        currentTEL62 = int(m.group(1))
    else:
        print "TEL62 number cannot be extracted"
        sys.exit(0)
        
    xml = TEL62Decoder(inputXMLFile)
    parseCorrections(xml, sys.argv[1], currentTEL62)
    with open(inputXMLFile, "w") as fd:
        fd.write(etree.tostring(xml._xml, pretty_print=True))
