'''
Created on Jul 29, 2015

@author: nlurkin
'''

from string import replace
import os
import re
from lxml import objectify, etree

def tryint(s):
    if "lxml.objectify" in str(type(s)):
        s = str(s)
    try:
        return int(s, 0)
    except:
        return s
    
def getSplitElementText(el):
    """
    Returns the text stored in an ObjectifiedElement'
    Split field (SplitStore or SplitContent)
    
    Args:
        el: ObjectifiedElement
        
    Returns:
        String
    """
    if hasattr(el, "SplitStore"):
        field = "R"
        xmlstring = el.SplitStore
    elif hasattr(el, "SplitContent"):
        field = "S"
        xmlstring = el.SplitContent
    return field, str(xmlstring)

def parseSplitElementText(el):
    """
    Returns a xmlDocument from the text stored
    in an ObjectifiedElement' Split field
    (SplitStore or SplitContent)
    
    Args:
        el: ObjectifiedElement
        
    Returns:
        xmlDocument
    """
    field, text = getSplitElementText(el)
    return field, xmlDocument(text)

def checkElementsXMLValidity(listTs):
    """
    Check for each element in the dictionary if the
    Split field contains valid XML. Set the
    bad field of the secondary dictionary to True
    if the string is not valid xml. Also sets the 
    cmd field of the secondary dictionary to the 
    identified command. The type is R(eport) or 
    S(ent)
    
    Args:
        listTs: Dictionary of dictionary of ObjectifiedElement
            {TS: {"node": el}}
    
    Modifies:
        listTs: {TS: {"node": el, "cmd": cmd, "bad": bad, "type": type}}
    """
    for k, v in listTs.iteritems():
        field, test = parseSplitElementText(v["node"])
        listTs[k]["cmd"] = "-"
        listTs[k]["bad"] = test._bad
        listTs[k]["type"] = field
        
        if not test._bad:
            test.identifyFileType()
            if test._type == "TEL":
                listTs[k]["cmd"] = test._cmd



class xmlDocument(object):
    def __init__(self, xml):
        '''
        Constructor. Try to read XML file and objectify it.
        Set _bad to True if failed or False if successful
        
        Args:
            xml: File path of the xml or xml string itself
        '''
      
        if isinstance(xml, xmlDocument):
            self._copy_construct(xml)
        else:    
            #Replace all html < and > codes with the real ascii character 
            self._xmlstring = replace(replace(xml, "&gt;", ">"), "&st;", ">")
            
            #Remove eventual enclosing doubles quotes
            if self._xmlstring[0] == "\"":
                self._xmlstring = self._xmlstring[1:]
            if self._xmlstring[-1] == "\"":
                self._xmlstring = self._xmlstring[:-1]
            try:
                #Read from file or from string
                if os.path.isfile(self._xmlstring):
                    self._xml = objectify.parse(self._xmlstring).getroot()
                else:
                    self._xml = objectify.fromstring(self._xmlstring)
            except etree.XMLSyntaxError as e:
                print e
                self._bad = True
            else:
                self._bad = False
    
    def _copy_construct(self, xml):
        self.__dict__ = xml.__dict__
        
    def __str__(self):
        return etree.tostring(self._xml, pretty_print=True)
    
    def printXML(self, nFirst, nLast):
        print self._xmlstring[0:nFirst]
        print "..."
        print "..."
        print "..."
        print self._xmlstring[-nLast]    
    
    def getTagRefs(self, tagName, parent=None):
        if parent is None:
            parent = self._xml

        return xmlDocument.getTagRefsStatic(tagName, parent)
    
    @staticmethod
    def getTagRefsStatic(tagName, parent=None):
        """
        Returns a list containing the xml elements whose 
        tag name corresponding to tagName
        
        Args:
            tagName: name of the xml tags to be extracted
            parent: node under which elements are searched. 
                    Default is root
        Returns:
            A list of ObjectifiedElement elements
        """        
        listTags = []
        for el in parent.iter(tagName):
            listTags.append(el)
        
        return listTags
    
    def identifyFileType(self):
        """
        Try to identify type of XML file.
        Valid types:
            TEL        (TEL62 file)
                -> S   (Start command)
                -> I   (Initialize command)
            L0TP       (L0TP file)
                -> S   (Start command)
            CREAM      (CREAM file)
                -> I   (Initialize command)
            Other      (Undefined device)
                -> U   (Unknown command)
        """
        if self._xml.tag == "tdconf":
            self._type = "TEL"
            if len(self.getTagRefs("dynip_s"))>0:
                self._cmd = "S"
            else:
                self._cmd = "I"
        elif self._xml.tag == "conf":
            self._type = "L0TP"
            self._cmd = "S"
        else:
            self._type = "Other"
            self._cmd = "U"    

class rcXML(xmlDocument):
    def __init__(self, xml):
        '''
        Constructor. Try to create xml file with super constructor.
        
        Args:
            xml: File path of the xml or xml string itself 
        '''
        super(rcXML, self).__init__(xml)
        
        self._runNumber = None
        self._runStart = None
        self._runEnd = None
        self._devs = []
    
    def getTagsRefsWithTS(self, tagName, parent=None):
        """
        Returns a dictionary of dictionary containing the xml 
        elements whose tag name corresponding to tagName and 
        their timestamp
        
        Args:
            tagName: name of the xml tags to be extracted
            parent: node under which elements are searched. 
                    Default is root
        Returns:
            A dictionary of dictionary of ObjectifiedElement elements.
            Timestamp as key of main dictionary. Element under "node"
            key of the secondary dictionary.
            {TS: {"node": el}}
        """
        
        elList = self.getTagRefs(tagName, parent)
        listTs = {}
        for el in elList:
            event = el.getparent()
            listTs[int(event.attrib["Timestamp"])] = {"node": el}
        
        return listTs
    
    def _extractDevs(self):
        """
        Extract the list of devices present in the XML file
        and store them in an internal list.
        """
        devs = set()
        for el in self._xml.iter():
            if "Split" in el.tag:
                devs.add(el.getparent().tag)
        self._devs = list(devs)
        
    def getMatchingDevs(self, regex):
        """
        Returns a list of devices present in the XML file
        that matches the given regular expression.
        
        Args:
            regex: Regular expression for the devices
        
        Returns:
            A list of string
        """
        if len(self._devs)==0:
            self.extractDevs()
            
        correspondingDevs = []
        for el in self._devs:
            if re.search(regex, el):
                correspondingDevs.append(el)
        return correspondingDevs
    
    def _extractMetaData(self):
        """
        Extract run metadata from XML file.
        """
        self._runStart = int(self._xml.attrib["startTime"])
        self._runEnd = int(self._xml.attrib["endTime"])
        listStartRun = self.getTagsRefsWithTS("RunInfo")
        #Find the RunInfo element closest to the start run timestamp
        for ts in listStartRun:
            if abs(ts-self._runStart)<5:
                listRunNumber = self.getTagRefs("RunNumber", listStartRun[ts]["node"])
                self._runNumber = listRunNumber[0]
    
    def __str__(self):
        ret =  "RunNumber: " + str(self._runNumber) + "\n"
        ret += "Start    : " + str(self._runStart) + "\n"
        ret += "End      : " + str(self._runEnd) + "\n"
        return ret
    
    def extractInfo(self):
        self._extractMetaData()
        self._extractDevs()
    
    