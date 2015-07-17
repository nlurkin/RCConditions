'''
Created on Jul 16, 2015

@author: nlurkin
'''
from string import replace
from lxml import objectify, etree

class PrimitiveInfo(object):
    def __init__(self):
        self.Downscaling = None
        self.detA = None
        self.detB = None
        self.detC = None
        self.detD = None
        self.detE = None
        self.detF = None
        self.detG = None
    
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return ""
    def __eq__(self, other):
        if self.Downscaling==other.Downscaling and \
            self.detA==other.detA and \
            self.detB==other.detB and \
            self.detC==other.detC and \
            self.detD==other.detD and \
            self.detE==other.detE and \
            self.detF==other.detF and \
            self.detG==other.detG:
            return True
        return False

class NIMInfo(object):
    def __init__(self):
        self.Downscaling = None
        self.Mask = None
    
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.Mask + ":" + str(self.Downscaling)
    
    def __eq__(self, other):
        if self.Downscaling==other.Downscaling and \
            self.Mask==other.Mask:
            return True
        return False
        
def readValue(node):
    if hasattr(node,"hex"):
        return str(node.hex)
    elif hasattr(node, "readable_string"):
        return str(node.readable_string)
    else:
        return str(node)
        
    
class L0TPDecoder(object):
    '''
    classdocs
    '''

    def __init__(self, xml, runNumber):
        '''
        Constructor
        '''
        self._xmlstring = replace(replace(replace(xml, "&gt;", ">"), "&st;", ">"), "\"", "")
        self._runNumber = runNumber
        try:
            self._xml = objectify.fromstring(self._xmlstring)
        except etree.XMLSyntaxError as e:
            print e
            self._bad = True
        else:
            self._bad = False
        
    
    def getPeriodicPeriod(self):
        return int(readValue(self._xml.global_parameters.periodicTrgTime), 0)
    
    def getNIMMasks(self):
        masksList = []
        if self._runNumber<1307:
            for i in range(0, 7):
                if int(self._xml.Element("lut%i_nim_detEmask" % i)) != 1:
                    trigger = NIMInfo()
                    row = []
                    row.append(self._xml.Element("lut%i_nim_detAmask" % i))
                    row.append(self._xml.Element("lut%i_nim_detBmask" % i))
                    row.append(self._xml.Element("lut%i_nim_detCmask" % i))
                    row.append(self._xml.Element("lut%i_nim_detDmask" % i))
                    row.append(self._xml.Element("lut%i_nim_detEmask" % i))
                    trigger.Downscaling = int(self._xml.Element("downScal_mask%i_nim" % i), 0)
                    trigger.Mask = ''.join(row)
                    masksList.append(trigger)
        else:
            for i in range(0, 7):
                nimEnabled = int(readValue(self._xml.global_parameters.enableMask_NIM), 0)
                if (nimEnabled & (1<<i)) != 0:
                    trigger = NIMInfo()
                    trigger.Downscaling = int(readValue(self._xml.global_parameters.downScal_NIM_mask.item[i]), 0)
                    row = []
                    row.append(readValue(self._xml.LUT_parameters_NIM.item[i].lut_detAmask))
                    row.append(readValue(self._xml.LUT_parameters_NIM.item[i].lut_detBmask))
                    row.append(readValue(self._xml.LUT_parameters_NIM.item[i].lut_detCmask))
                    row.append(readValue(self._xml.LUT_parameters_NIM.item[i].lut_detDmask))
                    row.append(readValue(self._xml.LUT_parameters_NIM.item[i].lut_detEmask))
                    trigger.Mask = ''.join(row)
                    masksList.append(trigger)
        return masksList
        
    def getNIMRefDetector(self):
        return int(readValue(self._xml.global_parameters.referenceDet_NIM), 0)
    
    def getPrimitiveMasks(self):
        '''
        Message to Dario: FILL ME!
        I need a list of fully filled PrimitiveInfo. One element for each enabled mask 
        '''
        masksList = []
        prim = PrimitiveInfo()
        prim.Downscaling = 1
        prim.ReferenceDet = 1
        #In binary
        prim.detA = "0000001001010111"
        prim.detB = "0000001001010111"
        prim.detC = "0000001001010111"
        prim.detD = "0000001001010111"
        prim.detE = "0000001001010111"
        prim.detF = "0000001001010111"
        prim.detG = "0000001001010111"
        masksList.append(prim)
        #return masksList
        return []
    
    def getPrimitiveMeaning(self, detector, mask):
        '''
        Message to Dario: FILL ME!
        I need a string that tells me what that mask means for that detector
        '''
        meaning = ""
        if detector=="A":
            if mask == "000000111010101":
                meaning = "LAV blah blah blah"
        if detector=="B":
            if mask == "0000110010101010":
                meaning = "!MUV(Loose)"
        #etc, etc
        return meaning
    
    def getPrimitiveRefDetector(self):
        return int(readValue(self._xml.global_parameters.referenceDet), 0)