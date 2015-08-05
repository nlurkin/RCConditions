'''
Created on Aug 5, 2015

@author: nlurkin
'''

import sys

from XMLDoc import xmlDocument, tryint

def xxx(l):
    return " ".join(l)

tel62Template = """
TEL62 Configuration file decoding
---------------------------------
File Version {version} for detector "{subdetectorName}" (subid: {subID})

Enabled (TDS): {triggerEnabled:d}{dataEnabled:d}{spyEnabled:d}
{TDCBList}
"""

tdcbTemplate = """
  TDCB id:     {id:>5}
  Rate Monitor:{tdccRateMon:>5}
  TDCC Debug:  {tdccDebug:>5}
{TDCList}
"""

tdcTemplate = """
    TDC id:  {id:>10} 
    Enabled: {enabled:>10}   TDC_ID:{tdcId:>5}
    Use (LT):{useLeading:>9d}{useTrailing:d}
    Offset:  {Offset:>10}
    Channels:{channelEnabled:>10x}
    Channel Offset: 
      {channelOffsetS}
"""


class TDC(object):
    '''
    classdocs
    '''
    
    def __init__(self, xml):
        self.id = None
        self.enabled = None
        self.tdcId = None
        self.useLeading = None
        self.useTrailing = None
        self.Offset = None
        self.channelOffset = {}
        self.channelEnabled = None
        
        self._decode(xml)

    def _decode(self, xml):
        self.id = tryint(xml.attrib["id"])
        self.enabled = bool(xml.enable)
        self.tdcId = tryint(xml.id) 
        self.useLeading = bool(xml.useleading)
        self.useTrailing = bool(xml.usetrailing)
        self.Offset = tryint(xml.tdcoff)
        
        lOffset = xmlDocument.getTagRefsStatic("choff", xml)
        for el in lOffset:
            self.channelOffset[tryint(el.attrib["id"])] = el
        self.channelEnabled = tryint(xml.chena)   
    
    def __str__(self):
        stringChoff = ['{:>2}: {:}  '.format(*k) for k in self.channelOffset.items()]
        stringChoff = zip(*[iter(stringChoff)]*8)
        stringChoff = map(xxx, stringChoff)
        stringChoff = "\n      ".join(stringChoff)
        return tdcTemplate.format(channelOffsetS=stringChoff, **self.__dict__)
    
class TDCB(object):
    '''
    classdocs
    '''
    
    
    def __init__(self, xmlNode):
        self.id = None
        self.tdccRateMon = None
        self.tdccDebug = None
        self.tdc = {}
        
        self._decode(xmlNode)
        
    def _decode(self, xml):
        self.id = tryint(xml.attrib["id"])
        self.tdccRateMon = tryint(xml.tdcc.ratemon)
        self.tdccDebug = tryint(xml.tdcc.debug)
        
        lTDC = xmlDocument.getTagRefsStatic("tdc", xml)
        for el in lTDC:
            self.tdc[tryint(el.attrib["id"])] = TDC(el)
    
    def __str__(self):
        return tdcbTemplate.format(TDCList=self.tdc[0], **self.__dict__)

class PP(object):
    '''
    classdocs
    '''
    
    def __init__(self, xml):
        self.id = None
        self.enabled = None
        self.logEnabled = None
        self.logLevel = None
        self.logMask = None
        self.debug = None
        self.tdccPhase = None
        self.trigrxPhase = None
        self.chokeMask = None
        self.errorMask = None
        self.nSlots = None
        self.lastSlot = None
        self.countMode = None
        
        self._decode(xml)
    
    def _decode(self, xml):
        self.id = tryint(xml.attrib["id"])
        self.enabled = bool(xml.enable)
        self.logEnabled = bool(xml.logena)
        self.logLevel = bool(xml.loglevel)
        self.logMask = tryint(xml.logmask)
        self.debug = tryint(xml.debug)
        self.tdccPhase = tryint(xml.tdccphase)
        self.trigrxPhase = tryint(xml.trigrxphase)
        self.chokeMask = tryint(xml.chokemask)
        self.errorMask = tryint(xml.errormask)
        self.nSlots = tryint(xml.nslots)
        self.lastSlot = tryint(xml.lastslot)
        self.countMode = tryint(xml.countmode)
    
    def __str__(self):
        return str(self.__dict__)
    
class GBEPort(object):
    '''
    classdocs
    '''
    
    def __init__(self, xml):
        self.id = None
        self.enable = None
        self.dataNotTrig = None
        self.srcMac = None
        self.srcIP = None
        self.srcUDP = None
        self.dstMac = None
        self.dstIP = None
        self.dstUDP = None
        self.dynMac = {}
        self.dynIP = {}
        
        self._decode(xml)
    
    def _decode(self, xml):
        self.id = tryint(xml.attrib["id"])
        self.enable = bool(xml.enable)
        self.dataNotTrig = bool(xml.datanottrig)
        self.srcMac = xml.srcmac_s
        self.srcIP = xml.srcip_s
        self.srcUDP = xml.srcudp_s
        self.dstMac = xml.dstmac_s
        self.dstIP = xml.dstip_s
        self.dstUDP = xml.dstudp_s
        
        lDynMac = xmlDocument.getTagRefsStatic("dynmac_s", xml)
        for el in lDynMac:
            self.dynMac[tryint(el.attrib["id"])] = el
        lDynIP = xmlDocument.getTagRefsStatic("dynip_s", xml)
        for el in lDynIP:
            self.dynIP[tryint(el.attrib["id"])] = el
    
    def __str__(self):
        return str(self.__dict__)
    
class SL(object):
    '''
    classdocs
    '''
    
    def __init__(self, xml):
        self.logEnabled = None
        self.logLevel = None
        self.logMask = None
        self.ppPhases = {}
        self.chokeMask = None
        self.errorMask = None
        self.latency = None
        self.mtpPeriod = None
        self.mtpFactor = None
        self.mepFactor = None
        self.jumboFrame = None
        self.mepPort = None
        self.nDynadd = None
        self.mepAddr = None
        self.gbePort = {}
        
        self._decode(xml)

    def _decode(self, xml):
        self.logEnabled = bool(xml.logena)
        self.logLevel = tryint(xml.loglevel)
        self.logMask = tryint(xml.logmask)
        
        lPPPhases = xmlDocument.getTagRefsStatic("ppphase", xml)
        for el in lPPPhases:
            self.ppPhases[tryint(el.attrib["id"])] = tryint(el)
        
        self.chokeMask = tryint(xml.chokemask)
        self.errorMask = tryint(xml.errormask)
        self.latency = tryint(xml.latency)
        self.mtpPeriod = tryint(xml.mtpperiod)
        self.mtpFactor = tryint(xml.mtpfactor)
        self.mepFactor = tryint(xml.mepfactor)
        self.jumboFrame = bool(xml.jumbo)
        self.mepPort = tryint(xml.mepport)
        self.nDynadd = tryint(xml.ndynadd)
        self.mepAddr = tryint(xml.mepaddr)
        
        lPort = xmlDocument.getTagRefsStatic("port", xml)
        for el in lPort:
            self.gbePort[tryint(el.attrib["id"])] = GBEPort(el)
    
    def __str__(self):
        return str(self.__dict__) + "\n" + str(self.gbePort[0])
    
class TEL62Decoder(xmlDocument):
    '''
    classdocs
    '''


    def __init__(self, xml):
        '''
        Constructor
        '''
        super(TEL62Decoder, self).__init__(xml)
        
        self.version = None
        self.subdetectorName = None
        self.subdetectorID = None
        self.subID = None
        self.triggerEnabled = None
        self.dataEnabled = None
        self.spyEnabled = None
        self.tdcb = {}
        self.pp = {}
        self.sl = None
        
        if not self._bad:
            self._decode()
    
    def __str__(self):
        return tel62Template.format(TDCBList=str(self.tdcb[0]), **self.__dict__)
        
    def _decode(self):
        self.version = tryint(self._xml.version)
        self.subdetectorName = self._xml.subdetector_name
        self.subdetectorID = tryint(self._xml.subdetector_id)
        self.subID = tryint(self._xml.subid)
        self.triggerEnabled = bool(self._xml.trig_enable)
        self.dataEnabled = bool(self._xml.data_enable)
        self.spyEnabled = bool(self._xml.spy_enable)
        
        
        lTDCB = self.getTagRefs("tdcb")
        for el in lTDCB:
            self.tdcb[tryint(el.attrib["id"])] = TDCB(el)
            
        lPP = self.getTagRefs("pp")
        for el in lPP:
            self.pp[tryint(el.attrib["id"])] = PP(el)        

        self.sl = SL(self._xml.sl)
    

if __name__ == "__main__":
    xmldoc = TEL62Decoder(sys.argv[1])
    print xmldoc