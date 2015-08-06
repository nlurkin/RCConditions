'''
Created on Aug 5, 2015

@author: nlurkin
'''

import os
import sys

from XMLDoc import xmlDocument, tryint


def toLine(l):
    return " ".join(l)

def formatIP(l):
    ret = l[:-1]
    if len(l[-1])==1:
        ret.append("")
    else:
        ret.append("{:>3}.{:>3}".format(*l[-1]))
    return ret
    
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
        stringChoff = map(toLine, stringChoff)
        stringChoff = "\n      ".join(stringChoff)
        return tdcTemplate.format(channelOffsetS=stringChoff, 
                                  **self.__dict__)
    
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
        TDCLListS = "\n".join([str(tdc) for _,tdc in sorted(self.tdc.items())])
        return tdcbTemplate.format(nTDC=len(self.tdc), 
                                   TDCList=TDCLListS, 
                                   **self.__dict__)

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
        self.logLevel = tryint(xml.loglevel)
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
        return ppTemplate.format(**self.__dict__)
    
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
        self.srcMac = str(xml.srcmac_s)
        self.srcIP = str(xml.srcip_s)
        self.srcUDP = tryint(xml.srcudp_s)
        self.dstMac = str(xml.dstmac_s)
        self.dstIP = str(xml.dstip_s)
        self.dstUDP = tryint(xml.dstudp_s)
        
        lDynMac = xmlDocument.getTagRefsStatic("dynmac_s", xml)
        for el in lDynMac:
            self.dynMac[tryint(el.attrib["id"])] = str(el)
        lDynIP = xmlDocument.getTagRefsStatic("dynip_s", xml)
        for el in lDynIP:
            self.dynIP[tryint(el.attrib["id"])] = str(el)
    
    def __str__(self):
        dstDict = {key:(mac, "".join([ip for ipkey,ip in self.dynIP.items() if ipkey==key])) for key,mac in self.dynMac.items()}
        dstList = [[key, mac, ip.split(".")] for key,(mac,ip) in dstDict.items()]
        dstList = map(formatIP, dstList)
        dstList = ["  [{0:2}]  Mac: {1}   IP: {2}".format(*x) for x in dstList]
        dstListS = "\n    ".join(dstList)
        return gbeTemplate.format(srcIPSplit=self.srcIP.split("."),
                                  dstIPSplit=self.dstIP.split("."),
                                  dstList=dstListS,
                                  **self.__dict__)
    
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
        self.nDynAdd = None
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
        self.nDynAdd = tryint(xml.ndynadd)
        self.mepAddr = tryint(xml.mepaddr)
        
        lPort = xmlDocument.getTagRefsStatic("port", xml)
        for el in lPort:
            self.gbePort[tryint(el.attrib["id"])] = GBEPort(el)
    
    def __str__(self):
        ppPhasesS = "   ".join(["{0}:{1:>3}".format(i, str(x)) for i,x in self.ppPhases.items()])
        gbeListS = "\n".join([str(gbe) for _,gbe in sorted(self.gbePort.items())])
        return slTemplate.format(ppPhasesS=ppPhasesS,
                                 nGBE=len(self.gbePort),
                                 GBEList=gbeListS,
                                 **self.__dict__)
    
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
        TDCBListS = "\n".join([str(tdcb) for _,tdcb in sorted(self.tdcb.items())])
        PPListS = "\n".join([str(pp) for _,pp in sorted(self.pp.items())])
        return tel62Template.format(nTDCB=len(self.tdcb), 
                    TDCBList=TDCBListS,
                    nPP=len(self.pp), 
                    PPList=PPListS,
                    SLConfig=str(self.sl), 
                    **self.__dict__)
        
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
    
def getch():
    import tty, termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        
if __name__ == "__main__":
    xmldoc = TEL62Decoder(sys.argv[1])
    xmlstring = str(xmldoc).split("\n")
    length = 0
    newLength = 0
    doQuit = False
    termLen = int(os.popen('stty size', 'r').read().split()[0])-3
    while not doQuit:
        length = newLength
        for line in xmlstring[length:length+termLen]:
            print line
        print ""
        print "Up/Down arrows to navigate   Space/Enter to skip 1 screen   q to exit"
        while newLength==length and not doQuit:
            ch = getch()
            if ord(ch)==13 or ord(ch)==32:
                newLength += termLen
            elif ord(ch)==27:
                if ord(getch())==91:
                    #arrow key
                    ch = getch()
                    if ord(ch)==65:
                        newLength -= 1
                    elif ord(ch)==66:
                        newLength += 1
            if newLength<0:
                newLength=0
            elif (newLength+termLen)>len(xmlstring):
                newLength = len(xmlstring)-termLen
            elif ord(ch)==113:
                doQuit = True
    
    