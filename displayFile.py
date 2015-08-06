#!/bin/env python

'''
Created on Aug 6, 2015

@author: nlurkin
'''

from XMLExtract import TEL62Decoder
from XMLExtract import BufferPrint
import sys
from XMLExtract.XMLDoc import xmlDocument
from XMLExtract import L0TPDecoder

if __name__ == "__main__":
    xmldoc = xmlDocument(sys.argv[1])
    xmldoc.identifyFileType()
    if xmldoc._type=="TEL":
        xmldoc = TEL62Decoder(xmldoc)
    elif xmldoc._type=="L0TP":
        xmldoc = L0TPDecoder(xmldoc)
    BufferPrint.displayBuffer(str(xmldoc))
