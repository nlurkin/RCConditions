#!/bin/env python

'''
Created on Aug 6, 2015

@author: nlurkin
'''

from XMLExtract import BufferPrint
import sys
from XMLExtract.XMLDoc import xmlDocument
from XMLExtract import generateSystemSpecificDecoder

if __name__ == "__main__":
    xmldoc = xmlDocument(sys.argv[1])
    xmldoc = generateSystemSpecificDecoder(xmldoc)
    BufferPrint.displayBuffer(str(xmldoc))
