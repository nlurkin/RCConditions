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

{globalParam}
{NIMTriggerS}
{PrimTriggerS}
{lutParamS}
{lutNIMParamS}
"""

GlobalTemplate = """
  MEP factor     :  {numEvtMEP:>5}
  Latency        :  {fixLatency:>5}
  Shift register :  {shiftReg:>5}
  Max delay det. :  {maxDelayDetector:>5}
  
  Periodic trigger:
    Primitive    :  {periodicTrgPrimitive:>5}
    Period       :  {periodicTrgTime:>5} ({periodicTimeNS} ns)
  
  Calibration trigger:
    Latency      :  {calibLatency:>5}
    Direction    :  {calibLatencyDirection:>5}
    Word         :  {calibTriggerWord:>5}
"""

GlobalNIMString = """
  NIM trigger:
    Ref. Detector: {referenceDetNIM:>5}
    Mask         : {enableMaskNIM:>#5x}
    Dead time    : {nimDT:>5}
"""

NIMString = """
                  Mask0     Mask1     Mask2     Mask3     Mask4     Mask5     Mask6     Mask7
    Address     : {lutNimAddress}
    DetA        : {lutNimDetA}
    DetB        : {lutNimDetB}
    DetC        : {lutNimDetC}
    DetD        : {lutNimDetD}
    DetE        : {lutNimDetE}
    Downscaling : {lutNimDownscaling}
"""

GlobalPrimString = """
  Primitive trigger:
    Ref. Detector: {referenceDet:>5}
    Mask         : {enableMask:>#5x}
    Dead time    : {primitiveDT:>5}
"""

PrimString = """
                         Mask0           Mask1           Mask2           Mask3           Mask4
    Address     :  {lutAddress[0]}
    DetA        :  {lutDetA[0]}
    DetB        :  {lutDetB[0]}
    DetC        :  {lutDetC[0]}
    DetD        :  {lutDetD[0]}
    DetE        :  {lutDetE[0]}
    DetF        :  {lutDetF[0]}
    DetG        :  {lutDetG[0]}
    Downscaling :  {lutDownscaling[0]}
    
                         Mask5           Mask6           Mask7
    Address     :  {lutAddress[1]}
    DetA        :  {lutDetA[1]}
    DetB        :  {lutDetB[1]}
    DetC        :  {lutDetC[1]}
    DetD        :  {lutDetD[1]}
    DetE        :  {lutDetE[1]}
    DetF        :  {lutDetF[1]}
    DetG        :  {lutDetG[1]}
    Downscaling :  {lutDownscaling[1]}
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
        return str(self.MaskNumber) + ")" + self.detA + "," + self.detB + "," + self.detC + \
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
                self.downscalMask.append(tryint(el.hex))
        if hasattr(xml, "downScal_NIM_mask"):
            lDownMask = xmlDocument.getTagRefsStatic("item", xml.downScal_NIM_mask)
            for el in lDownMask:
                self.downscalNIMMask.append(tryint(el.hex))
        if hasattr(xml, "offset_det"):
            lOffset = xmlDocument.getTagRefsStatic("item", xml.offset_det)
            for el in lOffset:
                self.offsetDet.append(tryint(el.hex))
        
        if hasattr(xml, "maxDelayDetector"):
            self.maxDelayDetector = tryint(xml.maxDelayDetector.hex)
    
    def __str__(self):
        periodNS = self.periodicTrgTime*25
        return fmt.format(GlobalTemplate, 
                          periodicTimeNS=periodNS,
                          **self.__dict__)

    def getNIMGlobalString(self):
        return fmt.format(GlobalNIMString,
                          **self.__dict__)

    def getPrimGlobalString(self):
        return fmt.format(GlobalPrimString,
                          **self.__dict__)
    
    def getNIMDownscalingString(self):
        return "     ".join(["{0:>5}".format(down) for down in self.downscalNIMMask])

    def getPrimDownscalingString(self):
        listDown = ["{0:>11}".format(down) for down in self.downscalMask]
        nElem = 5
        return ["     ".join(listDown[i:i+nElem]) for i in range(0, len(listDown), nElem)]
    
class LUT(object):
    
    def __init__(self, xml, lutId):
        self.id = lutId
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
        if hasattr(xml, "addressLUT"):
            self.addressLUT = tryint(xml.addressLUT.hex)
        if hasattr(xml, "lut_detAmask"):
            self.lut_detAmask = tryint(xml.lut_detAmask.hex)
        if hasattr(xml, "lut_detBmask"):
            self.lut_detBmask = tryint(xml.lut_detBmask.hex)
        if hasattr(xml, "lut_detCmask"):
            self.lut_detCmask = tryint(xml.lut_detCmask.hex)
        if hasattr(xml, "lut_detDmask"):
            self.lut_detDmask = tryint(xml.lut_detDmask.hex)
        if hasattr(xml, "lut_detEmask"):
            self.lut_detEmask = tryint(xml.lut_detEmask.hex)
        if hasattr(xml, "lut_detFmask"):
            self.lut_detFmask = tryint(xml.lut_detFmask.hex)
        if hasattr(xml, "lut_detGmask"):
            self.lut_detGmask = tryint(xml.lut_detGmask.hex)
            print xml.lut_detGmask.hex
    
    def __str__(self):
        return ""

class LUTNIM(object):
    
    def __init__(self, xml, lutId):
        self.id = lutId
        self.addressLUT = None
        self.lut_detAmask = None
        self.lut_detBmask = None
        self.lut_detCmask = None
        self.lut_detDmask = None
        self.lut_detEmask = None
        
        self._decode(xml)
    
    def _decode(self, xml):
        if hasattr(xml, "addressLUT"):
            self.addressLUT = tryint(xml.addressLUT.hex)
        if hasattr(xml, "lut_detAmask"):
            self.lut_detAmask = tryint(xml.lut_detAmask.hex)
        if hasattr(xml, "lut_detBmask"):
            self.lut_detBmask = tryint(xml.lut_detBmask.hex)
        if hasattr(xml, "lut_detCmask"):
            self.lut_detCmask = tryint(xml.lut_detCmask.hex)
        if hasattr(xml, "lut_detDmask"):
            self.lut_detDmask = tryint(xml.lut_detDmask.hex)
        if hasattr(xml, "lut_detEmask"):
            self.lut_detEmask = tryint(xml.lut_detEmask.hex)
    
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
        self.lutParam = []
        self.lutNIMParam = []
       
        if not self._bad:
            self._decode()
    
    def _decode(self):
        self.globalParam = Global(self._xml.global_parameters)
        
        listLUT = self.getTagRefs("item", self._xml.LUT_parameters)
        for i,el in enumerate(listLUT):
            self.lutParam.append(LUT(el,i))

        listLUTNIM = self.getTagRefs("item", self._xml.LUT_parameters_NIM)
        for i,el in enumerate(listLUTNIM):
            self.lutNIMParam.append(LUTNIM(el,i))
    
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
        print "Get Primitive"
        masksList = []
        if self._runNumber > 1307:
            primEnabled = int(readValue(self._xml.global_parameters.enableMask), 0)
            for i in range(0, 7):
                print i + "\n\n\n"
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
                    if hasattr(self._xml.LUT_parameters.item[i], "lut_detEmask"):
                        prim.detE = readValue(self._xml.LUT_parameters.item[i].lut_detEmask).lower()
                    else:
                        prim.detE = "0x7fff7fff"
                    if hasattr(self._xml.LUT_parameters.item[i], "lut_detFmask"):
                        prim.detF = readValue(self._xml.LUT_parameters.item[i].lut_detFmask).lower()
                    else:
                        prim.detF = "0x7fff7fff"
                    if hasattr(self._xml.LUT_parameters.item[i], "lut_detGmask"):
                        print "has G"
                        prim.detG = readValue(self._xml.LUT_parameters.item[i].lut_detGmask).lower()
                    else:
                        print "not has G"
                        prim.detG = "0x7fff7fff"
                    
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
            
        if detector == "G":
            if mask == "0x7fef7fff":
                meaning = "LKr"
            
        return meaning
    
    def getPrimitiveRefDetector(self):
        if readValue(self._xml.global_parameters.referenceDet)=="":
            return -1
        return int(readValue(self._xml.global_parameters.referenceDet), 0)
    
    def __str__(self):
        NIMTriggerS = self.globalParam.getNIMGlobalString()
        lutNimAddress = "     ".join(["{0:>#5x}".format(mask.addressLUT) for mask in self.lutNIMParam])
        lutNimDetA = "     ".join(["{0:>#5x}".format(mask.lut_detAmask) for mask in self.lutNIMParam])
        lutNimDetB = "     ".join(["{0:>#5x}".format(mask.lut_detBmask) for mask in self.lutNIMParam])
        lutNimDetC = "     ".join(["{0:>#5x}".format(mask.lut_detCmask) for mask in self.lutNIMParam])
        lutNimDetD = "     ".join(["{0:>#5x}".format(mask.lut_detDmask) for mask in self.lutNIMParam])
        lutNimDetE = "     ".join(["{0:>#5x}".format(mask.lut_detEmask) for mask in self.lutNIMParam])
        lutNimDownscaling = self.globalParam.getNIMDownscalingString()
        NIMTriggerS += fmt.format(NIMString, 
                                  lutNimAddress=lutNimAddress,
                                  lutNimDetA=lutNimDetA,
                                  lutNimDetB=lutNimDetB,
                                  lutNimDetC=lutNimDetC,
                                  lutNimDetD=lutNimDetD,
                                  lutNimDetE=lutNimDetE, 
                                  lutNimDownscaling=lutNimDownscaling)
        PrimTriggerS = self.globalParam.getPrimGlobalString()
        lutList = ["{0:>#11x}".format(mask.addressLUT) for mask in self.lutParam]
        detAList = ["{0:>#11x}".format(mask.lut_detAmask) for mask in self.lutParam]
        detBList = ["{0:>#11x}".format(mask.lut_detBmask) for mask in self.lutParam]
        detCList = ["{0:>#11x}".format(mask.lut_detCmask) for mask in self.lutParam]
        detDList = ["{0:>#11x}".format(mask.lut_detDmask) for mask in self.lutParam]
        detEList = ["{0:>#11x}".format(mask.lut_detEmask) for mask in self.lutParam]
        detFList = ["{0:>#11x}".format(mask.lut_detFmask) for mask in self.lutParam]
        detGList = ["{0:>#11x}".format(mask.lut_detGmask) for mask in self.lutParam]
        nElem = 5
        lutAddress = ["     ".join(lutList[i:i+nElem]) for i in range(0,len(lutList),nElem)]
        lutDetA = ["     ".join(detAList[i:i+nElem]) for i in range(0,len(detAList),nElem)]
        lutDetB = ["     ".join(detBList[i:i+nElem]) for i in range(0,len(detBList),nElem)]
        lutDetC = ["     ".join(detCList[i:i+nElem]) for i in range(0,len(detCList),nElem)]
        lutDetD = ["     ".join(detDList[i:i+nElem]) for i in range(0,len(detDList),nElem)]
        lutDetE = ["     ".join(detEList[i:i+nElem]) for i in range(0,len(detEList),nElem)]
        lutDetF = ["     ".join(detFList[i:i+nElem]) for i in range(0,len(detFList),nElem)]
        lutDetG = ["     ".join(detGList[i:i+nElem]) for i in range(0,len(detGList),nElem)]
        lutDownscaling = self.globalParam.getPrimDownscalingString()
        PrimTriggerS += fmt.format(PrimString,
                                   lutAddress=lutAddress,
                                   lutDetA=lutDetA,
                                   lutDetB=lutDetB,
                                   lutDetC=lutDetC,
                                   lutDetD=lutDetD,
                                   lutDetE=lutDetE,
                                   lutDetF=lutDetF,
                                   lutDetG=lutDetG,
                                   lutDownscaling=lutDownscaling)
        return fmt.format(L0TPTemplate,
                          NIMTriggerS = NIMTriggerS, 
                          PrimTriggerS=PrimTriggerS,
                          **self.__dict__)
