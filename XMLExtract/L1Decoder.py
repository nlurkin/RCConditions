'''
Created on June 13, 2016

@author: nlurkin
'''

from lxml import objectify, etree
from BufferPrint import PartialFormatter
from XMLDoc import xmlDocument, tryint

fmt = PartialFormatter()

def formatIP(ipInteger):
    splitIP = [int("{0:x}".format(ipInteger)[i:i+2],16) for i in range(0,8,2)]
    return ".".join("{0:>3}".format(x) for x in splitIP)

def formatMAC(macInteger):
    splitMAC = [int("{0:x}".format(macInteger)[i:i+2],16) for i in range(0,8,2)]
    return ":".join("{0:0>2x}".format(x) for x in splitMAC)

HLTTemplate = """
HTL Configuration file decoding
-----------------------------------------

L1 Trigger
----------
{l1}
{l2}
"""

TriggerTemplate = """
{globalConf}
{masks}
"""
L1GlobalTemplate = """
  Bypass Probability   : {l1BypassProbability:>5}
  Reduction factor     : {l1ReductionFactor:>5}
  Doswcaleing          : {l1DownscaleFactor:>5}
  Flagging mode        : {l1FlagMode:>5}
  Autoflagging factor  : {l1AutoFlagFactor:>5}
  Reference source     : {l1ReferenceTimeSourceID:>5}
"""

L2GlobalTemplate = """
  Bypass Probability   : {l2BypassProbability:>5}
  Reduction factor     : {l2ReductionFactor:>5}
  Doswcaleing          : {l2DownscaleFactor:>5}
  Flagging mode        : {l2FlagMode:>5}
  Autoflagging factor  : {l2AutoFlagFactor:>5}
  Reference source     : {l2ReferenceTimeSourceID:>5}
"""

L1MaskTemplate = """
    Mask{maskNumber}
    ------
    Enabled algos     : {numberOfEnabledAlgos:>5}
    Flagged algos     : {numberOfFlaggedAlgos:>5}
    Reduction factor  : {maskReductionFactor:>5}

{algos}
"""

L2MaskTemplate = """
    Mask{maskNumber}
    ------
{algos}
"""

L1AlgoTemplate = """
    {algoName}
    - Process ID            : {l1TrigProcessID:>5}
    - Mask ID               : {l1TrigMaskID:>5}
    - Enable                : {l1TrigEnable:>5}
    - Logic                 : {l1TrigLogic:>5}
    - Flagging              : {l1TrigFlag:>5}
    - Downscaling           : {l1TrigDownScale:>5}
    - Downscaling Factor    : {l1TrigDSFactor:>5}
    - Reference source      : {l1TrigRefTimeSourceID:>5}
    - Time window           : {l1TrigOnlineTimeWindow:>5}"""

L2AlgoTemplate = """
    {algoName}
    - Process ID            : {l2TrigProcessID:>5}
    - Enable                : {l2TrigEnable:>5}
    - Logic                 : {l2TrigLogic:>5}
    - Flagging              : {l2TrigFlag:>5}
    - Downscaling           : {l2TrigDownScale:>5}
    - Downscaling Factor    : {l2TrigDSFactor:>5}
    - Reference source      : {l2TrigRefTimeSourceID:>5}
    - Time window           : {l2TrigOnlineTimeWindow:>5}"""
    
class L1Algo(object):
    def __init__(self, xml):
        self.algoName = None
        self.l1TrigProcessID = None
        self.l1TrigMaskID = None
        self.l1TrigEnable = None
        self.l1TrigLogic = None
        self.l1TrigFlag = None
        self.l1TrigDownScale = None
        self.l1TrigDSFactor = None
        self.l1TrigRefTimeSourceID = None
        self.l1TrigOnlineTimeWindow = None

        self.decode(xml)
    
    def decode(self, xml):
        self.algoName = xml.tag
        subNode = xml.getchildren()[0]
        self.l1TrigProcessID = tryint(subNode.l1TrigProcessID)
        self.l1TrigMaskID = tryint(subNode.l1TrigMaskID)
        self.l1TrigEnable = tryint(subNode.l1TrigEnable)
        self.l1TrigLogic = tryint(subNode.l1TrigLogic)
        self.l1TrigFlag = tryint(subNode.l1TrigFlag)
        self.l1TrigDownScale = tryint(subNode.l1TrigDownScale)
        self.l1TrigDSFactor = tryint(subNode.l1TrigDSFactor)
        self.l1TrigRefTimeSourceID = tryint(subNode.l1TrigRefTimeSourceID)
        self.l1TrigOnlineTimeWindow = tryint(subNode.l1TrigOnlineTimeWindow)

    def __str__(self):
        return fmt.format(L1AlgoTemplate,
                          **self.__dict__)

class L2Algo(object):
    def __init__(self, xml):
        self.algoName = None
        self.l2TrigProcessID = None
        self.l2TrigEnable = None
        self.l2TrigLogic = None
        self.l2TrigFlag = None
        self.l2TrigDownScale = None
        self.l2TrigDSFactor = None
        self.l2TrigRefTimeSourceID = None
        self.l2TrigOnlineTimeWindow = None

        self.decode(xml)
    
    def decode(self, xml):
        self.algoName = xml.tag
        subNode = xml.getchildren()[0]
        self.l2TrigProcessID = tryint(subNode.l2TrigProcessID)
        self.l2TrigEnable = tryint(subNode.l2TrigEnable)
        self.l2TrigLogic = tryint(subNode.l2TrigLogic)
        self.l2TrigFlag = tryint(subNode.l2TrigFlag)
        self.l2TrigDownScale = tryint(subNode.l2TrigDownScale)
        self.l2TrigDSFactor = tryint(subNode.l2TrigDSFactor)
        self.l2TrigRefTimeSourceID = tryint(subNode.l2TrigRefTimeSourceID)
        self.l2TrigOnlineTimeWindow = tryint(subNode.l2TrigOnlineTimeWindow)

    def __str__(self):
        return fmt.format(L2AlgoTemplate,
                          **self.__dict__)

class L1Mask(object):
    def __init__(self, xml, maskID):
        self.numberOfEnabledAlgos = None
        self.numberOfFlaggedAlgos = None
        self.maskReductionFactor = None
        self.ktag = None
        self.chod = None
        self.rich = None
        self.lav = None
        self.ircsac = None
        self.straw = None
        self.muv = None
        self.maskID = maskID

        self.decode(xml)
    
    def decode(self, xml):
        self.numberOfEnabledAlgos = tryint(xml.numberOfEnabledAlgos)
        self.numberOfFlaggedAlgos = tryint(xml.numberOfFlaggedAlgos)
        self.maskReductionFactor = tryint(xml.maskReductionFactor)
        self.ktag = L1Algo(xml.ktag)
        self.chod = L1Algo(xml.chod)
        self.rich = L1Algo(xml.rich)
        self.lav = L1Algo(xml.lav)
        self.ircsac = L1Algo(xml.ircsac)
        self.straw = L1Algo(xml.straw)
        self.muv = L1Algo(xml.muv)

    def __str__(self):
        listAlgos = [str(self.ktag), str(self.chod), str(self.rich), str(self.lav), str(self.ircsac), str(self.straw), str(self.muv)]
        return fmt.format(L1MaskTemplate,
                          algos="  ".join(listAlgos),
                          maskNumber=self.maskID,
                          **self.__dict__)
    
    def getEnabledAlgos(self):
        enList = {"id":self.maskID}
        
        currAlgo = self.ktag
        if currAlgo.l1TrigEnable and not currAlgo.l1TrigFlag:
            enList["KTAG"] = {"Downscaling": (currAlgo.l1TrigDSFactor if currAlgo.l1TrigDownScale else 1), "Logic":currAlgo.l1TrigLogic}

        currAlgo = self.chod
        if currAlgo.l1TrigEnable and not currAlgo.l1TrigFlag:
            enList["CHOD"] = {"Downscaling": (currAlgo.l1TrigDSFactor if currAlgo.l1TrigDownScale else 1), "Logic":currAlgo.l1TrigLogic}

        currAlgo = self.rich
        if currAlgo.l1TrigEnable and not currAlgo.l1TrigFlag:
            enList["RICH"] = {"Downscaling": (currAlgo.l1TrigDSFactor if currAlgo.l1TrigDownScale else 1), "Logic":currAlgo.l1TrigLogic}

        currAlgo = self.lav
        if currAlgo.l1TrigEnable and not currAlgo.l1TrigFlag:
            enList["LAV"] = {"Downscaling": (currAlgo.l1TrigDSFactor if currAlgo.l1TrigDownScale else 1), "Logic":currAlgo.l1TrigLogic}

        currAlgo = self.ircsac
        if currAlgo.l1TrigEnable and not currAlgo.l1TrigFlag:
            enList["IRCSAC"] = {"Downscaling": (currAlgo.l1TrigDSFactor if currAlgo.l1TrigDownScale else 1), "Logic":currAlgo.l1TrigLogic}

        currAlgo = self.straw
        if currAlgo.l1TrigEnable and not currAlgo.l1TrigFlag:
            enList["STRAW"] = {"Downscaling": (currAlgo.l1TrigDSFactor if currAlgo.l1TrigDownScale else 1), "Logic":currAlgo.l1TrigLogic}

        currAlgo = self.muv
        if currAlgo.l1TrigEnable and not currAlgo.l1TrigFlag:
            enList["MUV"] = {"Downscaling": (currAlgo.l1TrigDSFactor if currAlgo.l1TrigDownScale else 1), "Logic":currAlgo.l1TrigLogic}
        
        return enList

class L2Mask(object):
    def __init__(self, xml, maskID):
        self.lkr = None
        self.maskID = maskID

        self.decode(xml)
    
    def decode(self, xml):
        self.lkr = L2Algo(xml.lkr)

    def __str__(self):
        listAlgos = [str(self.lkr)]
        return fmt.format(L2MaskTemplate,
                          algos="  ".join(listAlgos),
                          maskNumber=self.maskID,
                          **self.__dict__)
        
class L1Global(object):
    
    def __init__(self, xml):
        self.l1BypassProbability = None 
        self.l1ReductionFactor = None
        self.l1DownscaleFactor = None
        self.l1FlagMode = None
        self.l1AutoFlagFactor = None
        self.l1ReferenceTimeSourceID = None

        self.decode(xml)
    
    def decode(self, xml):
        self.l1BypassProbability = tryint(xml.l1BypassProbability)
        self.l1ReductionFactor = tryint(xml.l1ReductionFactor)
        self.l1DownscaleFactor = tryint(xml.l1DownscaleFactor)
        self.l1FlagMode = tryint(xml.l1FlagMode)
        self.l1AutoFlagFactor = tryint(xml.l1AutoFlagFactor)
        self.l1ReferenceTimeSourceID = tryint(xml.l1ReferenceTimeSourceID)

    def __str__(self):
        return fmt.format(L1GlobalTemplate,
                          **self.__dict__)

class L2Global(object):
    
    def __init__(self, xml):
        self.l2BypassProbability = None 
        self.l2ReductionFactor = None
        self.l2DownscaleFactor = None
        self.l2FlagMode = None
        self.l2AutoFlagFactor = None
        self.l2ReferenceTimeSourceID = None

        self.decode(xml)
    
    def decode(self, xml):
        self.l2BypassProbability = tryint(xml.l2BypassProbability)
        self.l2ReductionFactor = tryint(xml.l2ReductionFactor)
        self.l2DownscaleFactor = tryint(xml.l2DownscaleFactor)
        self.l2FlagMode = tryint(xml.l2FlagMode)
        self.l2AutoFlagFactor = tryint(xml.l2AutoFlagFactor)
        self.l2ReferenceTimeSourceID = tryint(xml.l2ReferenceTimeSourceID)

    def __str__(self):
        return fmt.format(L2GlobalTemplate,
                          **self.__dict__)
        
class L1Trigger(object):
    
    def __init__(self, xml):
        self.globalParams = None 
        self.masksList = []

        self.decode(xml)
    
    def decode(self, xml):
        self.globalParams = L1Global(xml.l1Global)
        listMasks = xmlDocument.getTagRefsStatic("l1Mask", xml)
        for el in listMasks:
            self.masksList.append(L1Mask(el, int(el.attrib["id"])))

    def __str__(self):
        listMasks = [str(masks) for masks in self.masksList]
        return fmt.format(TriggerTemplate,
                          globalConf=str(self.globalParams),
                          masks="   ".join(listMasks),
                          **self.__dict__)
    
    def getEnabledMasks(self):
        if self.globalParams.l1FlagMode==1:
            return []
        else:
            enList = []
            for mask in self.masksList:
                if (mask.numberOfEnabledAlgos-mask.numberOfFlaggedAlgos)>0:
                    enList.append(mask)
            return enList

class L2Trigger(object):
    
    def __init__(self, xml):
        self.globalParams = None 
        self.masksList = []

        self.decode(xml)
    
    def decode(self, xml):
        self.globalParams = L2Global(xml.l2Global)
        listMasks = xmlDocument.getTagRefsStatic("l2Mask", xml)
        for el in listMasks:
            self.masksList.append(L2Mask(el, el.attrib["id"]))

    def __str__(self):
        listMasks = [str(masks) for masks in self.masksList]
        return fmt.format(TriggerTemplate,
                          globalConf=str(self.globalParams),
                          masks="   ".join(listMasks),
                          **self.__dict__)

class HLTDecoder(xmlDocument):
    '''
    Class representing a HLT trigger configuration
    '''


    def __init__(self, xml):
        '''
        Constructor
        '''
        
        super(HLTDecoder, self).__init__(xml)
        
        self.l1 = None
        self.l2 = None
        
        if not self._bad:
            self._decode()

    def __str__(self):
        """
        Build pretty string printing of the class following the template
        """
        return fmt.format(HLTTemplate,
                          **self.__dict__)
        
    def _decode(self):
        """
        XML decoding method. Fill the class with
        available information from XML.
        """
        
        self.l1 = L1Trigger(self._xml.l1)
        self.l2 = L2Trigger(self._xml.l2)

    def getL1EnabledMasks(self):
        return self.l1.getEnabledMasks()
    