'''
Created on Aug 5, 2015

@author: nlurkin
'''

from __builtin__ import True
import copy
import datetime
import re

from lxml import objectify, etree

from BufferPrint import PartialFormatter
from XMLDoc import xmlDocument, tryint


fmt = PartialFormatter()

def getArrayIndex(el):
    """
    Read a string and extract the eventual array index
    Format is name[index]
    
    Args:
        string
    
    Returns:
        index, name
        If no [index] pattern is found returns 
        -1, el
    """
    m = re.search("(.*)\[([0-9])\]", el)
    if m is None:
        return -1,el
    else:
        return int(m.group(2)), m.group(1)
    
def saveElement(el):
    parent = el.getparent()
    cpy = copy.deepcopy(el)
    cpy.attrib["date"] = str(datetime.datetime.now())
    cmt = etree.Comment(etree.tostring(cpy))
    parent.append(cmt)

def toLine(l):
    """
    Transforms a list in a whitespace separated string
    
    Args:
        l: List
    
    Returns:
        String
    """
    return " ".join(l)

def formatIP(l):
    """
    Returns original list whose last element has been 
    interpreted as an IP address (last 2 fields only)
    and reformatted as an aligned string (xxx.xxx).
    
    Args:
        l: list whose last element is a 2 elements list
        [x,x,[123, 45]]
    
    Returns:
        Input list with last elements formatted as a 
        string [x,x,"123. 45"]
    """
    ret = l[:-1]
    if len(l[-1])==1:
        ret.append("")
    else:
        ret.append("{:>3}.{:>3}".format(*l[-1]))
    return ret

# ------------------------------------
# String templates for each TEL62 class
# ------------------------------------
tel62Template = """
TEL62 Configuration file decoding
---------------------------------
File Version {version} for detector "{subdetectorName}" (subid: {subID})

Enabled (TDS): {triggerEnabled:d}{dataEnabled:d}{spyEnabled:d}
# of TDCB: {nTDCB:>5}
{TDCBList}

# of PP:   {nPP:>5}
{PPList}

{SLConfig}
"""

tdcbTemplate = """
  TDCB id:     {id:>5}
  Rate Monitor:{tdccRateMon:>5}
  TDCC Debug:  {tdccDebug:>5}
  # of TDC:    {nTDC:>5} 
{TDCList}
"""

tdcTemplate = """
    TDC id:  {id:>10} 
    Enabled: {enabled:>10}   TDC_ID:{tdcId:>5}
    Use (LT):{useLeading:>9d}{useTrailing:d}
    Offset:  {Offset:>10}
    Channels:{channelEnabled:>#10x}
    Channel Offset: 
      {channelOffsetS}
"""

ppTemplate = """
  PP id:   {id:>15}
  Enabled (BLD):{enabled:>8d}{logEnabled:d}{debug:d}
  Log level:  {logLevel:>12}   Mask:  {logMask:>#11x}
  Phases TDCC:{tdccPhase:>12}   Trigrx:{trigrxPhase:>11}
  Masks  Error:{errorMask:>#11x}   Choke: {chokeMask:>#11x}
  Slots: #:   {nSlots:>12}   Last:  {lastSlot:>11}
  Count Mode: {countMode:>12}
"""

slTemplate = """
  Log: Enabled: {logEnabled:>5}   Level: {logLevel:>6}   Mask: {logMask:>#5x}
  PP Phases:    {ppPhasesS}
  Masks: Error: {errorMask:>#5x}   Choke: {chokeMask:>#6x}
  Latency:      {latency:>5}
  MTP: Period:  {mtpPeriod:>5}   Factor:{mtpFactor:>6}
  MEP: Factor:  {mepFactor:>5}   Port:  {mepPort:>6}   Addr:{mepAddr:>5}
  Network configuration:
  Jumbo:        {jumboFrame:>5}   # of Dst:{nDynAdd:>4}
  # of GBE Ports:{nGBE:>4}
{GBEList}
"""

gbeTemplate = """
    GBE Port id:{id:>5}
    Enabled:    {enable:>5}   Data: {dataNotTrig:>5}
    Source      MAC: {srcMac:>18}   IP: {srcIPSplit[0]:>3}.{srcIPSplit[1]:>3}.{srcIPSplit[2]:>3}.{srcIPSplit[3]:>3}   UDP: {srcUDP:>5}
    Destination MAC: {dstMac:>18}   IP: {dstIPSplit[0]:>3}.{dstIPSplit[1]:>3}.{dstIPSplit[2]:>3}.{dstIPSplit[3]:>3}   UDP: {dstUDP:>5}
    Destination addresses:
    {dstList}
"""

class TDC(object):
    '''
    Class representing a TDC configuration
    '''
    
    def __init__(self, xml):
        """
        Constructor
        """
        self.id = None
        self.enabled = None
        self.tdcId = None
        self.useLeading = None
        self.useTrailing = None
        self.Offset = None
        self.channelOffset = {}
        self.channelEnabled = 0
        
        self._xml = xml
        
        self._decode(xml)

    def _decode(self, xml):
        """
        XML decoding method. Fill the class with
        available information from XML.
        
        Args:
            xml: xml node of the TDC
        """
        self.id = tryint(xml.attrib["id"])
        
        if hasattr(xml, "enable"):
            self.enabled = bool(xml.enable)
        if hasattr(xml, "id"):
            self.tdcId = tryint(xml.id)
        if hasattr(xml, "useleading"): 
            self.useLeading = bool(xml.useleading)
        if hasattr(xml, "usetrailing"):
            self.useTrailing = bool(xml.usetrailing)
        if hasattr(xml, "tdcoff"):
            self.Offset = tryint(xml.tdcoff)
        
        lOffset = xmlDocument.getTagRefsStatic("choff", xml)
        for el in lOffset:
            self.channelOffset[tryint(el.attrib["id"])] = el
        if hasattr(xml, "chena"):
            self.channelEnabled = tryint(xml.chena)   
    
    def __str__(self):
        """
        Build pretty string printing of the class following the template
        """
        stringChoff = ['{:>2}: {:}  '.format(*k) for k in self.channelOffset.items()]
        stringChoff = zip(*[iter(stringChoff)]*8)
        stringChoff = map(toLine, stringChoff)
        stringChoff = "\n      ".join(stringChoff)
        return fmt.format(tdcTemplate, channelOffsetS=stringChoff, 
                                  **self.__dict__)
        
    def replaceOffset(self, value):
        self.Offset = value
        if hasattr(self._xml, "tdcoff"):
            saveElement(self._xml.tdcoff)
        self._xml.tdcoff = self.Offset
        objectify.deannotate(self._xml.tdcoff, xsi_nil=True, cleanup_namespaces=True)
    
    def addToOffset(self, value):
        prevValue = 0
        if hasattr(self._xml, "tdcoff"):
            prevValue = tryint(self._xml.tdcoff)
        
        self.replaceOffset(prevValue+value)
    
    def getChannelOffsetIndex(self, channel):
        if hasattr(self._xml, "choff"):
            for i, choff in enumerate(self._xml.choff):
                if int(choff.attrib["id"])==channel:
                    return i
        return -1
        
    def replaceChannelOffset(self, channel, value):
        self.channelOffset[channel] = value
        
        index = self.getChannelOffsetIndex(channel)
        if index==-1:
            objectify.SubElement(self._xml, "choff", id=str(channel))
        else:
            saveElement(self._xml.choff[index])
            
        self._xml.choff[index] = value
        self._xml.choff[index].attrib["id"] = str(channel)
        
        objectify.deannotate(self._xml.choff[index], xsi_nil=True, cleanup_namespaces=True)
    
    def addToChannelOffset(self, channel, value):
        index = self.getChannelOffsetIndex(channel)
        
        prevValue = 0
        if index>=0:
            prevValue = tryint(self._xml.choff[index])
        
        self.replaceChannelOffset(channel, prevValue+value)
                
class TDCB(object):
    '''
    Class representing a TDCB configuration
    '''
    
    
    def __init__(self, xmlNode):
        """
        Constructor
        """
        self.id = None
        self.tdccRateMon = None
        self.tdccDebug = None
        self.tdc = {}
        
        self._decode(xmlNode)
        
    def _decode(self, xml):
        """
        XML decoding method. Fill the class with
        available information from XML.
        
        Args:
            xml: xml node of the TDCB
        """

        self.id = tryint(xml.attrib["id"])
        
        if hasattr(xml, "tdcc"):
            if hasattr(xml.tdcc, "ratemon"):
                self.tdccRateMon = tryint(xml.tdcc.ratemon)
            if hasattr(xml.tdcc, "debug"):
                self.tdccDebug = tryint(xml.tdcc.debug)
        
        lTDC = xmlDocument.getTagRefsStatic("tdc", xml)
        for el in lTDC:
            self.tdc[tryint(el.attrib["id"])] = TDC(el)
    
    def __str__(self):
        """
        Build pretty string printing of the class following the template
        """
        TDCLListS = "\n".join([str(tdc) for _,tdc in sorted(self.tdc.items())])
        return fmt.format(tdcbTemplate, nTDC=len(self.tdc), 
                                   TDCList=TDCLListS, 
                                   **self.__dict__)

class PP(object):
    '''
    Class representing a PP configuration
    '''
    
    def __init__(self, xml):
        """
        Constructor
        """
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
        
        self._xml = xml
        
        self._decode(xml)
    
    def _decode(self, xml):
        """
        XML decoding method. Fill the class with
        available information from XML.
        
        Args:
            xml: xml node of the PP
        """

        self.id = tryint(xml.attrib["id"])
        
        if hasattr(xml, "enable"):
            self.enabled = bool(xml.enable)
        if hasattr(xml, "logena"):
            self.logEnabled = bool(xml.logena)
        if hasattr(xml, "loglevel"):
            self.logLevel = tryint(xml.loglevel)
        if hasattr(xml, "logmask"):
            self.logMask = tryint(xml.logmask)
        if hasattr(xml, "debug"):
            self.debug = tryint(xml.debug)
        if hasattr(xml, "tdccphase"):
            self.tdccPhase = tryint(xml.tdccphase)
        if hasattr(xml, "trigrxphase"):
            self.trigrxPhase = tryint(xml.trigrxphase)
        if hasattr(xml, "chokemask"):
            self.chokeMask = tryint(xml.chokemask)
        if hasattr(xml, "errormask"):
            self.errorMask = tryint(xml.errormask)
        if hasattr(xml, "nslots"):
            self.nSlots = tryint(xml.nslots)
        if hasattr(xml, "lastslot"):
            self.lastSlot = tryint(xml.lastslot)
        if hasattr(xml, "countmode"):
            self.countMode = tryint(xml.countmode)
    
    def __str__(self):
        """
        Build pretty string printing of the class following the template
        """
        return fmt.format(ppTemplate, **self.__dict__)
    
    def replaceTDCCPhase(self, value):
        self.tdccPhase = value
        if hasattr(self._xml, "tdccphase"):
            saveElement(self._xml.tdccphase)
        self._xml.tdccphase = "{:#x}".format(self.tdccPhase)
        objectify.deannotate(self._xml.tdccphase, xsi_nil=True, cleanup_namespaces=True)
    
    def addToTDCCPhase(self, value):
        prevValue = 0
        if hasattr(self._xml, "tdccphase")>=0:
            prevValue = tryint(self._xml.tdccphase)
        
        self.replaceTDCCPhase(prevValue+value)
        
    def replaceTrigrXPhase(self, value):
        self.trigrxPhase = value
        if hasattr(self._xml, "trigrxphase"):
            saveElement(self._xml.trigrxphase)
        self._xml.trigrxphase = "{:#x}".format(self.trigrxPhase)
        objectify.deannotate(self._xml.trigrxphase, xsi_nil=True, cleanup_namespaces=True)

    def addToTrigrXPhase(self, value):
        prevValue = 0
        if hasattr(self._xml, "trigrxphase")>=0:
            prevValue = tryint(self._xml.trigrxphase)
        
        self.replaceTrigrXPhase(prevValue+value)
        
class GBEPort(object):
    '''
    Class representing a Gigabit Ethernet port configuration
    '''
    
    def __init__(self, xml):
        """
        Constructor
        """
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
        """
        XML decoding method. Fill the class with
        available information from XML.
        
        Args:
            xml: xml node of the GBE port
        """

        self.id = tryint(xml.attrib["id"])
        if hasattr(xml, "enable"):
            self.enable = bool(xml.enable)
        if hasattr(xml, "datanottrig"):
            self.dataNotTrig = bool(xml.datanottrig)
        if hasattr(xml, "srcmac_s"):
            self.srcMac = str(xml.srcmac_s)
        if hasattr(xml, "srcip_s"):
            self.srcIP = str(xml.srcip_s)
        if hasattr(xml, "srcudp_s"):
            self.srcUDP = tryint(xml.srcudp_s)
        if hasattr(xml, "dstmac_s"):
            self.dstMac = str(xml.dstmac_s)
        if hasattr(xml, "dstip_s"):
            self.dstIP = str(xml.dstip_s)
        if hasattr(xml, "dstudp_s"):
            self.dstUDP = tryint(xml.dstudp_s)
        
        lDynMac = xmlDocument.getTagRefsStatic("dynmac_s", xml)
        for el in lDynMac:
            self.dynMac[tryint(el.attrib["id"])] = str(el)
        lDynIP = xmlDocument.getTagRefsStatic("dynip_s", xml)
        for el in lDynIP:
            self.dynIP[tryint(el.attrib["id"])] = str(el)
    
    def __str__(self):
        """
        Build pretty string printing of the class following the template
        """
        dstDict = {key:(mac, "".join([ip for ipkey,ip in self.dynIP.items() if ipkey==key])) for key,mac in self.dynMac.items()}
        dstList = [[key, mac, ip.split(".")] for key,(mac,ip) in dstDict.items()]
        dstList = map(formatIP, dstList)
        dstList = ["  [{0:2}]  Mac: {1}   IP: {2}".format(*x) for x in dstList]
        dstListS = "\n    ".join(dstList)
        
        if not self.srcIP is None:
            srcIPS = self.srcIP.split(".")
        else:
            srcIPS = "....".split(".")
        if not self.dstIP is None:
            dstIPS = self.dstIP.split(".")
        else:
            dstIPS = "....".split(".")
            
        print self.__dict__
        return fmt.format(gbeTemplate, srcIPSplit=srcIPS,
                                  dstIPSplit=dstIPS,
                                  dstList=dstListS,
                                  **self.__dict__)
    
class SL(object):
    '''
    Class representing a SL configuration
    '''
    
    def __init__(self, xml):
        """
        Constructor
        """
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
        self.nDynAdd = None
        self.mepAddr = None
        self.gbePort = {}
        
        self._decode(xml)

    def _decode(self, xml):
        """
        XML decoding method. Fill the class with
        available information from XML.
        
        Args:
            xml: xml node of the SL
        """

        if hasattr(xml, "logena"):
            self.logEnabled = bool(xml.logena)
        if hasattr(xml, "loglevel"):
            self.logLevel = tryint(xml.loglevel)
        if hasattr(xml, "logmask"):
            self.logMask = tryint(xml.logmask)
        
        lPPPhases = xmlDocument.getTagRefsStatic("ppphase", xml)
        for el in lPPPhases:
            self.ppPhases[tryint(el.attrib["id"])] = tryint(el)
        
        if hasattr(xml, "chokemask"):
            self.chokeMask = tryint(xml.chokemask)
        if hasattr(xml, "errormask"):
            self.errorMask = tryint(xml.errormask)
        if hasattr(xml, "latency"):
            self.latency = tryint(xml.latency)
        if hasattr(xml, "mtpperiod"):
            self.mtpPeriod = tryint(xml.mtpperiod)
        if hasattr(xml, "mtpfactor"):
            self.mtpFactor = tryint(xml.mtpfactor)
        if hasattr(xml, "mepfactor"):
            self.mepFactor = tryint(xml.mepfactor)
        if hasattr(xml, "jumbo"):
            self.jumboFrame = bool(xml.jumbo)
        if hasattr(xml, "mepport"):
            self.mepPort = tryint(xml.mepport)
        if hasattr(xml, "ndynadd"):
            self.nDynAdd = tryint(xml.ndynadd)
        if hasattr(xml, "mepaddr"):
            self.mepAddr = tryint(xml.mepaddr)
        
        lPort = xmlDocument.getTagRefsStatic("port", xml)
        for el in lPort:
            self.gbePort[tryint(el.attrib["id"])] = GBEPort(el)
    
    def __str__(self):
        """
        Build pretty string printing of the class following the template
        """
        ppPhasesS = "   ".join(["{0}:{1:>3}".format(i, str(x)) for i,x in self.ppPhases.items()])
        gbeListS = "\n".join([str(gbe) for _,gbe in sorted(self.gbePort.items())])
        return fmt.format(slTemplate, ppPhasesS=ppPhasesS,
                                 nGBE=len(self.gbePort),
                                 GBEList=gbeListS,
                                 **self.__dict__)
    
    def getPPIndex(self, pp):
        if hasattr(self._xml, "ppphase"):
            for i, ppphase in enumerate(self._xml.pphase):
                if ppphase.attrib["id"]==pp:
                    return i
        return -1
        
    def replacePPPhase(self, pp, value):
        self.ppPhases[pp] = value
        
        index = self.getPPPhaseIndex(pp)
        if index==-1:
            objectify.SubElement(self._xml, "ppphase", id=str(pp))
        else:
            saveElement(self._xml.ppphase[index])
            
        self._xml.ppphase[index] = "{:#x}".format(value)
        objectify.deannotate(self._xml.ppphase[index], xsi_nil=True, cleanup_namespaces=True)
        
    def addToPPPhase(self, pp, value):
        index = self.getPPIndex(pp)
        
        prevValue = 0
        if index>=0:
            prevValue = tryint(self._xml.ppphase[index])
        
        self.replacePPPhase(pp, prevValue+value)
        
class TEL62Decoder(xmlDocument):
    '''
    Class representing a TEL62 configuration
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
        """
        Build pretty string printing of the class following the template
        """
        TDCBListS = "\n".join([str(tdcb) for _,tdcb in sorted(self.tdcb.items())])
        PPListS = "\n".join([str(pp) for _,pp in sorted(self.pp.items())])
        return fmt.format(tel62Template, nTDCB=len(self.tdcb), 
                    TDCBList=TDCBListS,
                    nPP=len(self.pp), 
                    PPList=PPListS,
                    SLConfig=str(self.sl), 
                    **self.__dict__)
        
    def _decode(self):
        """
        XML decoding method. Fill the class with
        available information from XML.
        """
        
        if hasattr(self._xml, "version"):
            self.version = tryint(self._xml.version)
        if hasattr(self._xml, "subdetector_name"):
            self.subdetectorName = self._xml.subdetector_name
        if hasattr(self._xml, "subdetector_id"):
            self.subdetectorID = tryint(self._xml.subdetector_id)
        if hasattr(self._xml, "subid"):
            self.subID = tryint(self._xml.subid)
        if hasattr(self._xml, "trig_enable"):
            self.triggerEnabled = bool(self._xml.trig_enable)
        if hasattr(self._xml, "data_enable"):
            self.dataEnabled = bool(self._xml.data_enable)
        if hasattr(self._xml, "spy_enable"):
            self.spyEnabled = bool(self._xml.spy_enable)
        
        
        lTDCB = self.getTagRefs("tdcb")
        for el in lTDCB:
            self.tdcb[tryint(el.attrib["id"])] = TDCB(el)
            
        lPP = self.getTagRefs("pp")
        for el in lPP:
            self.pp[tryint(el.attrib["id"])] = PP(el)        

        if hasattr(self._xml, "sl"):
            self.sl = SL(self._xml.sl)
        
        self._xml.pp[1].rcphase = 56

    def navigate(self, path):
        listPath = path.split(".")
        
        currentXMLEl = self._xml
        parentName = "root"
        for el in listPath:
            index,el = getArrayIndex(el)
            
            if index == -1:
                currentXMLEl = currentXMLEl.find(el)
            else:
                elList = currentXMLEl.findall(el)
                currentXMLEl = None
                for xmlel in elList:
                    if int(xmlel.attrib["id"]) == index:
                        currentXMLEl = xmlel
                        break
            if currentXMLEl is None:
                print "Element {} not found under {}".format(el, parentName)
                return
            parentName = el
        
        return currentXMLEl

    def replacePath(self, path, value):
        xmlEl = self.navigate(path)
        if xmlEl is None:
            print "{} not found. Ignoring".format(path)
        else:
            xmlEl._setText(value)
    