'''
Created on Aug 10, 2015

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

CREAMTemplate = """
CREAM Configuration file decoding
-----------------------------------------

Version            : {version:>5}
Zero Supp. Thresh. : {zsThreshold:>5}
Acqisition Mode    : {acqMode:>5}
ADC Mode           : {adcMode:>5}
Latency            : {latency:>5}
# Samples          : {nSamp:>5}
{tslS}
{NetworkConfigS}
{MaskConfigS}
"""

TSLTemplate = """
TSL Configuration
  Active SC       : {activeSC:>10}
  Active Channels : {activeChannel[0]:>#10x}   {activeChannel[1]:>#10x}
  Global Offset   : {globalOffset[0]:>#10x}   {globalOffset[1]:>#10x}
"""

NetworkTemplate = """
Network configuration:
  Max PL Size      : {maxPLSize:>11}
  MRP Listen Port  : {mrpLstPort:>11}
  Ethernet Length  : {ethLength:>11}
  Base Multicast   : {baseMCastAddrS:>15}
  Source: 
    SDE Port       : {sdeSrcPort:>11}
    Base MAC       : {baseMACAddrS:>15}
    Base IP        : {baseIPAddrS:>15}
  Destination:
    Mode:        IP:{ipDestMode:>2}   MAC:{macDestMode:>2}
    SDE Port       : {sdeDstPort:>11}
    Base MAC       : {baseMACDestAddrS:>15}
    IP             : {ipDestAddrS:>15}
"""

class TSL(object):
    
    def __init__(self, xml):
        self.activeSC = None
        self.activeChannel = []
        self.globalOffset = []
        
        self.decode(xml)

    def decode(self, xml):
        self.activeSC = tryint(xml.ActiveSC.hex)
        
        listAC = xmlDocument.getTagRefsStatic("item", xml.ActiveChannel)
        for el in listAC:
            self.activeChannel.append(tryint(el.hex))

        listGO = xmlDocument.getTagRefsStatic("item", xml.GlobalOffset)
        for el in listGO:
            self.globalOffset.append(tryint(el.hex))
    
    def __str__(self):
        return fmt.format(TSLTemplate, 
                          **self.__dict__)
        
class Network(object):
    
    def __init__(self, xml):
        self.maxPLSize = None 
        self.ipDestMode = None
        self.macDestMode = None
        self.baseMCastAddr = None
        self.baseMACAddr = None
        self.baseIPAddr = None
        self.BaseMACDestAddr = None
        self.ipDestAddr = None
        self.sdeSrcPort = None
        self.sdeDstPort = None
        self.mrpLstPort = None
        self.ethLength = None

        self.decode(xml)
    
    def decode(self, xml):
        self.maxPLSize = tryint(xml.MaxPLSize) 
        self.ipDestMode = tryint(xml.IPDestMode)
        self.macDestMode = tryint(xml.MACDestMode)
        self.baseMCastAddr = tryint(xml.BaseMCastAddr.hex)
        self.baseMACAddr = tryint(xml.BaseMACAddr.hex)
        self.baseIPAddr = tryint(xml.BaseIPAddr.hex)
        self.baseMACDestAddr = tryint(xml.BaseMACDestAddr.hex)
        self.ipDestAddr = tryint(xml.IPDestAddr.hex)
        self.sdeSrcPort = tryint(xml.SDESrcPort)
        self.sdeDstPort = tryint(xml.SDEDstPort)
        self.mrpLstPort = tryint(xml.MRPLstPort)
        self.ethLength = tryint(xml.EthLength)

    def __str__(self):
        return fmt.format(NetworkTemplate,
                          baseMCastAddrS = formatIP(self.baseMCastAddr),
                          baseMACAddrS = formatMAC(self.baseMACAddr),
                          baseIPAddrS = formatIP(self.baseIPAddr),
                          baseMACDestAddrS = formatMAC(self.baseMACDestAddr),
                          ipDestAddrS = formatIP(self.ipDestAddr),
                          **self.__dict__)
    
class CREAMDecoder(xmlDocument):
    '''
    Class representing a CREAM configuration
    '''


    def __init__(self, xml):
        '''
        Constructor
        '''
        
        super(CREAMDecoder, self).__init__(xml)
        
        self.version = None
        self.creamMask = {}
        self.zsThreshold = None
        self.acqMode = None
        self.adcMode = None
        self.latency = None
        self.nSamp = None
        self.tsl = None
        self.network = None
        
        if not self._bad:
            self._decode()

    def __str__(self):
        """
        Build pretty string printing of the class following the template
        """
        nElem = 5
        masksList = [["  Mask {0:>2} ".format(k), "{0:>#10x}".format(elem)] for k,elem in self.creamMask.items()]
        maskHeaderS = ["    ".join(x for [x,_] in masksList[i:i+nElem]) for i in range(0,len(masksList),nElem)]
        maskValueS = ["    ".join(x for [_,x] in masksList[i:i+nElem]) for i in range(0,len(masksList),nElem)]
        maskS = "\n\n".join("{0}\n{1}".format(h,v) for h,v in zip(maskHeaderS, maskValueS))
        
        return fmt.format(CREAMTemplate,  
                          tslS=str(self.tsl),
                          NetworkConfigS=str(self.network),
                          MaskConfigS = maskS,
                          **self.__dict__)
        
    def _decode(self):
        """
        XML decoding method. Fill the class with
        available information from XML.
        """
        
        self.version = tryint(self._xml.version)
        self.zsThreshold = tryint(self._xml.ZSThreshold)
        self.acqMode = tryint(self._xml.AcqMode.hex)
        self.adcMode = tryint(self._xml.AdcMode.hex)
        self.latency = tryint(self._xml.Latency)
        self.nSamp = tryint(self._xml.NSamp)
        
        lmasks = self.getTagRefs("item", self._xml.CreamMask)
        for i, el in enumerate(lmasks):
            self.creamMask[i] = tryint(el.hex)
            
        self.tsl = TSL(self._xml.tsl)
        self.network = Network(self._xml.network)

