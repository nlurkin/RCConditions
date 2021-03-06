'''
Created on Jul 16, 2015

@author: nlurkin
'''
from BufferPrint import PartialFormatter
from XMLDoc import xmlDocument
from XMLDoc import tryint


L0TPTemplate = """
L0TP (Torino) Configuration file decoding
-----------------------------------------

{globalParamS}
{lutParamS}
{lutNIMParamS}
"""

GlobalTemplate = """
  # of events/MEP: {numEvtMEP:>5}
"""

fmt = PartialFormatter()

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
        super(PrimitiveInfo, self).__init__()
        self.detA = None
        self.detB = None
        self.detC = None
        self.detD = None
        self.detE = None
        self.detF = None
        self.detG = None
        self.MaskNumber = None
    
    def __str__(self):
        return self.MaskNumber + ")" + self.detA + "," + self.detB + "," + self.detC + \
            "," + self.detD + "," + self.detE + "," + self.detF + \
            "," + self.detG + ":" + str(self.Downscaling)

class NIMInfo(TriggerInfo):
    def __init__(self):
        self.Mask = None
    
    def __str__(self):
        return self.Mask + ":" + str(self.Downscaling)    
        
def readValue(node):
    if hasattr(node,"hex"):
        return str(node.hex)
    elif hasattr(node, "readable_string"):
        return str(node.readable_string)
    else:
        return str(node)
        
class Global(object):
    
    def __init__(self, xml):
        self.numEvtMEP = None
        self.fixLatency = None
        self.periodicTrgPrimitive = None
        self.periodicTrgTime = None
        self.calibLatency = None
        self.calibLatencyDirection = None
        self.referenceDet = None
        self.referenceDetNIM = None
        self.enableMask = None
        self.enableMaskNIM = None
        self.primitiveDT = None
        self.nimDT = None
        self.shiftReg = None
        self.calibTriggerWord = None
        self.downscalMask = []
        self.downscalNIMMask = []
        self.offsetDet = []
        self.maxDelayDetector = None
        
        self._decode(xml)
        
    def _decode(self, xml):
        if hasattr(xml, "numEvtMEP"):
            self.numEvtMEP = tryint(xml.numEvtMEP.hex)
        if hasattr(xml, "fixLatency"):
            self.fixLatency = tryint(xml.fixLatency.hex)
        if hasattr(xml, "periodicTrgPrimitive"):
            self.periodicTrgPrimitive = tryint(xml.periodicTrgPrimitive.hex)
        if hasattr(xml, "periodicTrgTime"):
            self.periodicTrgTime = tryint(xml.periodicTrgTime.hex)
        if hasattr(xml, "calibLatency"):
            self.calibLatency = tryint(xml.calibLatency.hex)
        if hasattr(xml, "calibLatencyDirection"):
            self.calibLatencyDirection = tryint(xml.calibLatencyDirection.hex)
        if hasattr(xml, "referenceDet"):
            self.referenceDet = tryint(xml.referenceDet.hex)
        if hasattr(xml, "referenceDet_NIM"):
            self.referenceDetNIM = tryint(xml.referenceDet_NIM.hex)
        if hasattr(xml, "enableMask"):
            self.enableMask = tryint(xml.enableMask.hex)
        if hasattr(xml, "enableMask_NIM"):
            self.enableMaskNIM = tryint(xml.enableMask_NIM.hex)
        if hasattr(xml, "primitiveDT"):
            self.primitiveDT = tryint(xml.primitiveDT.hex)
        if hasattr(xml, "nimDT"):
            self.nimDT = tryint(xml.nimDT.hex)
        if hasattr(xml, "shift_reg"):
            self.shiftReg = tryint(xml.shift_reg.hex)
        if hasattr(xml, "calib_triggerword"):
            self.calibTriggerWord = tryint(xml.calib_triggerword.hex)
        if hasattr(xml, "bit_finetime"):
            self.bitFineTime = tryint(xml.bit_finetime.hex)
        
        if hasattr(xml, "downScal_mask"):
            lDownMask = xmlDocument.getTagRefsStatic("item", xml.downScal_mask)
            for el in lDownMask:
                self.downscalMask.append(el.hex)
        if hasattr(xml, "downScal_NIM_mask"):
            lDownMask = xmlDocument.getTagRefsStatic("item", xml.downScal_NIM_mask)
            for el in lDownMask:
                self.downscalNIMMask.append(el.hex)
        if hasattr(xml, "offset_det"):
            lOffset = xmlDocument.getTagRefsStatic("item", xml.offset_det)
            for el in lOffset:
                self.offsetDet.append(el.hex)
        
        if hasattr(xml, "maxDelayDetector"):
            self.maxDelayDetector = tryint(xml.maxDelayDetector.hex)
    
    def __str__(self):
        return fmt.format(GlobalTemplate, 
                          **self.__dict__)

class LUT(object):
    
    def __init__(self, xml):
        self.id = None
        self.addressLUT = None
        self.lut_detAmask = None
        self.lut_detBmask = None
        self.lut_detCmask = None
        self.lut_detDmask = None
        self.lut_detEmask = None
        self.lut_detFmask = None
        self.lut_detGmask = None
        
        self._decode(xml)

    
    def _decode(self, xml):
        pass
    
    def __str__(self):
        return ""

class LUTNIM(object):
    
    def __init__(self, xml):
        self.id = None
        self.addressLUT = None
        self.lut_detAmask = None
        self.lut_detBmask = None
        self.lut_detCmask = None
        self.lut_detDmask = None
        self.lut_detEmask = None
        
        self._decode(xml)
    
    def _decode(self, xml):
        pass
    
    def __str__(self):
        return ""

class L0TPDecoder(xmlDocument):
    '''
    classdocs
    '''

    def __init__(self, xml, runNumber=None):
        '''
        Constructor
        '''
        
        super(L0TPDecoder, self).__init__(xml)
        self._runNumber = runNumber
        self.globalParam = None
        self.lutParam = None
        self.lutNIMParam = None
        
        self._decode()
    
    def _decode(self):
        self.globalParam = Global(self._xml.global_parameters)
    
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
                    prim.MaskNumber = i
                    
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
    
    @staticmethod
    def getPrimitiveMeaning(detector, mask):
        '''
        Message to Dario: FILL ME!
        I need a string that tells me what that mask means for that detector
        Dont specify don't cares (not displayed)
        '''
        meaning = ""
        if detector=="A":
            if mask == "0x00000000" or mask == "0x0":
                meaning = "!CHOD"
#             if mask == "0x7fff7fff":
#                 meaning = "CHOD don't care"
            if mask == "0x6fff7fff":
                meaning = "CHOD"
                
        if detector=="B":
            if mask == "0x00000000" or mask == "0x0":
                meaning = "!RICH"
#             if mask == "0x7fff7fff":
#                 meaning = "RICH don't care"
            if mask == "0x6fff7fff":
                meaning = "RICH"
            if mask == "0x00001001":
                meaning = "R1"
            if mask == "0x00001002":
                meaning = "R2"
            if mask == "0x00001004":
                meaning = "R3"
             
        if detector=="C":
            if mask == "0x00000000" or mask == "0x0":
                meaning = "!LAV"
#             if mask == "0x7fff7fff":
#                 meaning = "LAV don't care"
            if mask == "0x6fff7fff":
                meaning = "LAV"
            if mask=="0x00001001":
                meaning="LMIP"
            if mask=="0x00001002":
                meaning="LES"
            if mask=="0x00001004":
                meaning="LM"
                
        if detector=="D":
            if mask == "0x00000000" or mask == "0x0":
                meaning = "!MUV"
#             if mask == "0x7fff7fff":
#                 meaning = "MUV don't care"
            if mask == "0x3fff7fff":
                meaning = "MUV"
            if mask == "0x1fff7fff":
                meaning = "M2"
            if mask == "0x00004001":
                meaning = "ML1"
            if mask == "0x00004002":
                meaning = "MT1"
            if mask == "0x00004004":
                meaning = "MLO1"
            if mask == "0x00004008":
                meaning = "MTO1"
            if mask == "0x00004010":
                meaning = "MLO2"
            if mask == "0x00004020":
                meaning = "MTO2"
            if mask == "0x00004040":
                meaning = "MMO2"
            if mask == "0x00004080":
                meaning = "ML2"
            if mask == "0x00004100":
                meaning = "MT2"
            if mask == "0x00004200":
                meaning = "MM2"
            if mask == "0x00004400":
                meaning = "MO1"
            if mask == "0x00004800":
                meaning = "M1"
            if mask == "0x00005000":
                meaning = "MO2"
            if mask == "0x00006000":
                meaning = "M2" 
            
            
        return meaning
    
    def getPrimitiveRefDetector(self):
        if readValue(self._xml.global_parameters.referenceDet)=="":
            return -1
        return int(readValue(self._xml.global_parameters.referenceDet), 0)
    
    def __str__(self):
        return fmt.format(L0TPTemplate,
                          globalParamS = str(self.globalParam), 
                          **self.__dict__)
