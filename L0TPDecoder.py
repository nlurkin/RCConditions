'''
Created on Jul 16, 2015

@author: nlurkin
'''
from string import replace
from lxml import objectify, etree

class TriggerInfo(object):
    def __init__(self):
        self.Downscaling = None
        
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)
        
class PrimitiveInfo(TriggerInfo):
    def __init__(self):
        self.detA = None
        self.detB = None
        self.detC = None
        self.detD = None
        self.detE = None
        self.detF = None
        self.detG = None
    
    def __str__(self):
        return self.detA + "," + self.detB + "," + self.detB + \
            "," + self.detB + "," + self.detB + "," + self.detB + \
            "," + self.detB + ":" + str(self.Downscaling)
#     def __eq__(self, other):
#         if self.Downscaling==other.Downscaling and \
#             self.detA==other.detA and \
#             self.detB==other.detB and \
#             self.detC==other.detC and \
#             self.detD==other.detD and \
#             self.detE==other.detE and \
#             self.detF==other.detF and \
#             self.detG==other.detG:
#             return True
#         return False

class NIMInfo(TriggerInfo):
    def __init__(self):
        self.Mask = None
    
    def __str__(self):
        return self.Mask + ":" + str(self.Downscaling)    
#     def __eq__(self, other):
#         if self.Downscaling==other.Downscaling and \
#             self.Mask==other.Mask:
#             return True
#         return False
        
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
            nimEnabled = int(readValue(self._xml.global_parameters.enableMask_NIM), 0)
            for i in range(0, 7):
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
        masksList = []
        if self._runNumber > 1307:
            primEnabled = int(readValue(self._xml.global_parameters.enableMask), 0)
            for i in range(0, 7):
                if (primEnabled & (1<<i)) != 0:
                    prim = PrimitiveInfo()
                    prim.Downscaling = int(readValue(self._xml.global_parameters.downScal_mask.item[i]), 0)
                    
                    prim.detA = readValue(self._xml.LUT_parameters.item[i].lut_detAmask).lower()
                    prim.detB = readValue(self._xml.LUT_parameters.item[i].lut_detBmask).lower()
                    prim.detC = readValue(self._xml.LUT_parameters.item[i].lut_detCmask).lower()
                    if hasattr(self._xml.LUT_parameters.item[i], "lut_detDmask"):
                        prim.detD = readValue(self._xml.LUT_parameters.item[i].lut_detDmask).lower()
                    else:
                        prim.detD = "0x7fff7fff"
                    if hasattr(self._xml.LUT_parameters.item[i], "lut_detDmask"):
                        prim.detE = readValue(self._xml.LUT_parameters.item[i].lut_detEmask).lower()
                    else:
                        prim.detD = "0x7fff7fff"
                    if hasattr(self._xml.LUT_parameters.item[i], "lut_detDmask"):
                        prim.detF = readValue(self._xml.LUT_parameters.item[i].lut_detFmask).lower()
                    else:
                        prim.detD = "0x7fff7fff"
                    if hasattr(self._xml.LUT_parameters.item[i], "lut_detDmask"):
                        prim.detG = readValue(self._xml.LUT_parameters.item[i].lut_detGmask).lower()
                    else:
                        prim.detD = "0x7fff7fff"
                    
                    masksList.append(prim)
        return masksList
    
    def getPrimitiveMeaning(self, detector, mask):
        '''
        Message to Dario: FILL ME!
        I need a string that tells me what that mask means for that detector
        '''
        meaning = ""
        if detector=="A":
            if mask == "0x7FFF6FFF":
                meaning = "LAV blah blah blah"
        if detector=="B":
            if mask == "0x7FFF456F":
                meaning = "!MUV(Loose)"
        #etc, etc
        return meaning
    
    def getPrimitiveRefDetector(self):
        if readValue(self._xml.global_parameters.referenceDet)=="":
			  return -1
        return int(readValue(self._xml.global_parameters.referenceDet), 0)
