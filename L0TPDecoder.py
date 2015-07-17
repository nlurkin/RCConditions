'''
Created on Jul 16, 2015

@author: nlurkin
'''
from string import replace
from lxml import objectify, etree

class L0TPDecoder(object):
    '''
    classdocs
    '''

    def __init__(self, xml, runNumber):
        '''
        Constructor
        '''
        self._xmlstring = replace(replace(xml, "&gt;", ">"), "&st;", ">")
        self._runNumber = runNumber
        try:
            self._xml = objectify.fromstring(self._xmlstring)
        except etree.XMLSyntaxError as e:
            print e
            self._bad = True
        else:
            self._bad = False
        
    
    def getPeriodicPeriod(self):
        return int(self._xml.conf.global_parameters.periodicTrgTime.hex, 0)
    
    def getNIMMasks(self):
        masksList = []
        if self._runNumber<1307:
            for i in range(0, 7):
                if int(self._xml.conf.Element("lut%i_nim_detEmask" % i)) != 1:
                    row = []
                    row.append(self._xml.conf.Element("lut%i_nim_detAmask" % i))
                    row.append(self._xml.conf.Element("lut%i_nim_detBmask" % i))
                    row.append(self._xml.conf.Element("lut%i_nim_detCmask" % i))
                    row.append(self._xml.conf.Element("lut%i_nim_detDmask" % i))
                    row.append(self._xml.conf.Element("lut%i_nim_detEmask" % i))
                    masksList.append(''.join(row) + ":" + self._xml.conf.Element("downScal_mask%i_nim" % i))
        else:
            for i in range(0, 7):
                nimEnabled = int(self._xml.conf.global_parameters.enableMask_NIM, 0)
                if (nimEnabled & (1<<i)) != 0:
                    downscalList = self._xml.conf.global_parameters.downScal_NIM_mask.item[i]
                    row = []
                    row.append(self._xml.conf.LUT_parameters_NIM.item[i].lut_detAmask.hex)
                    row.append(self._xml.conf.LUT_parameters_NIM.item[i].lut_detBmask.hex)
                    row.append(self._xml.conf.LUT_parameters_NIM.item[i].lut_detCmask.hex)
                    row.append(self._xml.conf.LUT_parameters_NIM.item[i].lut_detDmask.hex)
                    row.append(self._xml.conf.LUT_parameters_NIM.item[i].lut_detEmask.hex)
                    masksList.append(''.join(row) + ":" + str(self.getValue(downscalList.childNodes)))
        return masksList
        
    def getNIMRefDetector(self):
        return int(self._xml.conf.global_parameters.referenceDet_NIM.hex, 0)
    
    def getPrimitiveMasks(self):
        '''
        Message to Dario: FILL ME!
        '''
        return []
    
    def getPrimitiveRefDetector(self):
        return int(self._xml.conf.global_parameters.referenceDet.hex, 0)