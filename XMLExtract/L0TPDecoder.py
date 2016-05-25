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

class ControlInfo(TriggerInfo):
    def __init__(self):
        self.Mask = None
        self.Detector = None
    
    def __str__(self):
        return self.Mask + "(" + str(self.Detector) + "):" + str(self.Downscaling)    
        
def readValue(node):
    if hasattr(node,"hex"):
        return str(node.hex)
    elif hasattr(node, "readable_string"):
        return str(node.readable_string)
    else:
        return str(node)
        
class Global(object):
    
    def __init__(self, xml):
        self.bit_finetime = None
        self.calibLatency = None
        self.calibLatencyDirection = None
        self.calibTriggerWord = None
        self.chokeErrorMask = None
        self.controlDetector = None
        self.controlDownscaling = None
        self.deltaPacket = None
        self.downscalMask = []
        self.enableMask = None
        self.fixLatency = None
        self.maskControlTrigger = None
        self.max_delay_detector = None
        self.nimCalib_triggerword = None
        self.numEvtMEP = None
        self.offsetDet = []
        self.periodicEndTime = None
        self.periodicEndTime1 = None
        self.periodicStartTime = None
        self.periodicStartTime1 = None
        self.periodicTrgPrimitive = None
        self.periodicTrgPrimitive1 = None
        self.periodicTrgTime = None
        self.periodicTrgTime1 = None
        self.primitiveDT = None
        self.randomEndTime = None
        self.randomPeriod = None
        self.randomStartTime = None
        self.randomTriggerWord = None
        self.referenceDet = None
        self.timeCut = []
        
        self._decode(xml)
        
    def _decode(self, xml):
        if hasattr(xml, "bit_finetime"):
            self.bit_finetime = tryint(xml.bit_finetime.hex)
        if hasattr(xml, "calibLatency"):
            self.calibLatency = tryint(xml.calibLatency.hex)
        if hasattr(xml, "calibLatencyDirection"):
            self.calibLatencyDirection = tryint(xml.calibLatencyDirection.hex)
        if hasattr(xml, "CalibTriggerWord"):
            self.calibTriggerWord = tryint(xml.CalibTriggerWord.hex)
        if hasattr(xml, "ChokeErrorMask"):
            self.chokeErrorMask = tryint(xml.ChokeErrorMask.hex)
        if hasattr(xml, "ControlDetector"):
            self.controlDetector = tryint(xml.ControlDetector.hex)
        if hasattr(xml, "ControlDownscaling"):
            self.controlDownscaling = tryint(xml.ControlDownscaling.hex)
        if hasattr(xml, "DeltaPacket"):
            self.DeltaPacket = tryint(xml.DeltaPacket.hex)
        if hasattr(xml, "downScal_mask"):
                lDownMaskList = xmlDocument.getTagRefsStatic("item", xml.downScal_mask)
                for el in lDownMaskList:
                    self.downscalMask.append(tryint(el.hex))
        if hasattr(xml, "enableMask"):
            self.enableMask = tryint(xml.enableMask.hex)
        if hasattr(xml, "fixLatency"):
            self.fixLatency = tryint(xml.fixLatency.hex)
        if hasattr(xml, "MaskControltrigger"):
            self.maskControltrigger = tryint(xml.MaskControltrigger.hex)
        if hasattr(xml, "max_delay_detector"):
            self.max_delay_detector = tryint(xml.max_delay_detector.hex)
        if hasattr(xml, "nimCalib_triggerword"):
            self.nimCalib_triggerword = tryint(xml.nimCalib_triggerword.hex)
        if hasattr(xml, "numEvtMEP"):
            self.numEvtMEP = tryint(xml.numEvtMEP.hex)
        for letter in ["A", "B", "C", "D", "E", "F", "G"]:
            if hasattr(xml, "offset_det{0}".format(letter)):
                lOffset = xmlDocument.getTagRefsStatic("offset_det{0}".format(letter), xml)
                self.offsetDet.append(tryint(lOffset[0].hex))
        if hasattr(xml, "PeriodicEndTime"):
            self.periodicEndTime = tryint(xml.PeriodicEndTime.hex)
        if hasattr(xml, "PeriodicEndTime1"):
            self.periodicEndTime1 = tryint(xml.PeriodicEndTime1.hex)
        if hasattr(xml, "PeriodicStartTime"):
            self.periodicStartTime = tryint(xml.PeriodicStartTime.hex)
        if hasattr(xml, "PeriodicStartTime1"):
            self.periodicStartTime1 = tryint(xml.PeriodicStartTime1.hex)
        if hasattr(xml, "periodicTrgPrimitive"):
            self.periodicTrgPrimitive = tryint(xml.periodicTrgPrimitive.hex)
        if hasattr(xml, "periodicTrgPrimitive1"):
            self.periodicTrgPrimitive1 = tryint(xml.periodicTrgPrimitive1.hex)
        if hasattr(xml, "periodicTrgTime"):
            self.periodicTrgTime = tryint(xml.periodicTrgTime.hex)
        if hasattr(xml, "periodicTrgTime1"):
            self.periodicTrgTime1 = tryint(xml.periodicTrgTime1.hex)
        if hasattr(xml, "primitiveDT"):
            self.primitiveDT = tryint(xml.primitiveDT.hex)
        if hasattr(xml, "RandomEndTime"):
            self.randomEndTime = tryint(xml.RandomEndTime.hex)
        if hasattr(xml, "RandomPeriod"):
            self.randomPeriod = tryint(xml.RandomPeriod.hex)
        if hasattr(xml, "RandomStartTime"):
            self.randomStartTime = tryint(xml.RandomStartTime.hex)
        if hasattr(xml, "RandomTriggerWord"):
            self.randomTriggerWord = tryint(xml.RandomTriggerWord.hex)
        if hasattr(xml, "referenceDet"):
            self.referenceDet = tryint(xml.referenceDet.hex)
        for i in range(0, 7):
            if hasattr(xml, "timeCut{0}".format(i)):
                el = xmlDocument.getTagRefsStatic("timeCut{0}".format(i), xml)
                self.timeCut.append(tryint(el[0].hex))

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
    
    def __init__(self, xml):
        self.masks = []
        
        self._decode(xml)

    
    def _decode(self, xml):
        listMask = xmlDocument.getTagRefsStatic("item", xml)
        for el in listMask:
            if hasattr(el,"hex"): 
                self.masks.append(tryint(el.hex))

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
       
        if not self._bad:
            self._decode()
    
    def _decode(self):
        self.globalParam = Global(self._xml.global_parameters)
        
        for letter in ["A", "B", "C", "D", "E", "F", "G"]:
            if hasattr(self._xml.LUT_parameters, "lut_det{0}mask".format(letter)):
                lLUT = xmlDocument.getTagRefsStatic("lut_det{0}mask".format(letter), self._xml)
                self.lutParam.append(LUT(lLUT[0]))

    def getPeriodicPeriod(self):
        return int(readValue(self._xml.global_parameters.periodicTrgTime), 0)
    
    def getPeriodic1Period(self):
        return int(readValue(self._xml.global_parameters.periodicTrgTime1), 0)
    
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
            for i in range(0, 8):
                if (primEnabled & (1<<i)) != 0:
                    prim = PrimitiveInfo()
                    prim.Downscaling = int(readValue(self._xml.global_parameters.downScal_mask.item[i]), 0)
                    prim.MaskNumber = i
                    
                    prim.detA = readValue(self._xml.LUT_parameters.lut_detAmask.item[i]).lower()
                    prim.detB = readValue(self._xml.LUT_parameters.lut_detBmask.item[i]).lower()
                    prim.detC = readValue(self._xml.LUT_parameters.lut_detCmask.item[i]).lower()
                    prim.detD = readValue(self._xml.LUT_parameters.lut_detDmask.item[i]).lower()
                    prim.detE = readValue(self._xml.LUT_parameters.lut_detEmask.item[i]).lower()
                    prim.detF = readValue(self._xml.LUT_parameters.lut_detFmask.item[i]).lower()
                    prim.detG = readValue(self._xml.LUT_parameters.lut_detGmask.item[i]).lower()
                    
                    masksList.append(prim)
        return masksList
    
    def getControlMask(self):
        if self._runNumber > 4800:
            control = ControlInfo()
            control.Downscaling = int(readValue(self._xml.global_parameters.controlDownscaling), 0)
            control.Mask = readValue(self._xml.global_parameters.maskControlTrigger)
            control.Detector = int(readValue(self._xml.global_parameters.controlDetector), 0)
            return control
        return None
            
    
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
        
        if detector == "E":
            if mask == "0x6fff7fff":
                meaning = "IRC"
        if detector == "G":
            if mask == "0x7fef7fff":
                meaning = "LKr"
            
        return meaning
    
    def getPrimitiveRefDetector(self):
        if readValue(self._xml.global_parameters.referenceDet)=="":
            return -1
        value = -1
        try:
            value = int(readValue(self._xml.global_parameters.referenceDet), 0)
        except:
            pass
        return value
    
    def __str__(self):
        PrimTriggerS = self.globalParam.getPrimGlobalString()
        lutList = ["{0:>#11x}".format(i) for i in range(0, 16)]
        detList = []
        for det in self.lutParam:
            detList.append(["{0:>#11x}".format(mask) for mask in det.masks])
        nElem = 5
        lutAddress = ["     ".join(lutList[i:i+nElem]) for i in range(0,len(lutList),nElem)]
        lutDetA = ["     ".join(detList[0][i:i+nElem]) for i in range(0,len(detList[0]),nElem)]
        lutDetB = ["     ".join(detList[1][i:i+nElem]) for i in range(0,len(detList[1]),nElem)]
        lutDetC = ["     ".join(detList[2][i:i+nElem]) for i in range(0,len(detList[2]),nElem)]
        lutDetD = ["     ".join(detList[3][i:i+nElem]) for i in range(0,len(detList[3]),nElem)]
        lutDetE = ["     ".join(detList[4][i:i+nElem]) for i in range(0,len(detList[4]),nElem)]
        lutDetF = ["     ".join(detList[5][i:i+nElem]) for i in range(0,len(detList[5]),nElem)]
        lutDetG = ["     ".join(detList[6][i:i+nElem]) for i in range(0,len(detList[6]),nElem)]
        lutDownscaling = self.globalParam.getPrimDownscalingString()
        print lutDownscaling
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
                          PrimTriggerS=PrimTriggerS,
                          **self.__dict__)
