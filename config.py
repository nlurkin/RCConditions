'''
Created on Nov 5, 2014

@author: ncl
'''

import re
import xml.dom.minidom as xmld

class BadConfigException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class ConfigFile(object):
	'''
	ConfigFile
	'''
	
	def __init__(self, string):
		self.content = string
	
	def importFile(self):
		"""Parse XML from file"""
		return xmld.parseString(self.content[1:-1])
	
	def getPropertie(self, name):
		m = re.findall("<"+name+"\>(.*)</"+name+">", self.content)
		if m:
			return m[0]
		raise BadConfigException(name);
	
	def getValue(self, nodelist):
		"""Return the text contained in a node ( <node>this text</node> )"""
		rc = []
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				rc.append(node.data)
		return ''.join(rc)
	
	
	def findNIMMask(self, address):
		try:
			doc = self.importFile()
		except:
			raise BadConfigException("Unable to parse for NIM " + str(address))
		rootNode = doc.getElementsByTagName("LUT_parameters_NIM")[0]
		itemNodes = rootNode.getElementsByTagName("item")[address]
		globalNode = doc.getElementsByTagName("global_parameters")[0]
		downscalNode = globalNode.getElementsByTagName("downScal_NIM_mask")[0]
		downscalList = downscalNode.getElementsByTagName("item")[address]
		row = []
		row.append(self.getValue(itemNodes.getElementsByTagName("lut_detAmask")[0].childNodes))
		row.append(self.getValue(itemNodes.getElementsByTagName("lut_detBmask")[0].childNodes))
		row.append(self.getValue(itemNodes.getElementsByTagName("lut_detCmask")[0].childNodes))
		row.append(self.getValue(itemNodes.getElementsByTagName("lut_detDmask")[0].childNodes))
		row.append(self.getValue(itemNodes.getElementsByTagName("lut_detEmask")[0].childNodes))
		return ''.join(row) + ":" + str(self.getValue(downscalList.childNodes))
	
	def findPrimMask(self, address):
		try:
			doc = self.importFile()
		except:
			raise BadConfigException("Unable to parse for Prim " + str(address)) 
		rootNode = doc.getElementsByTagName("LUT_parameters")[0]
		itemNodes = rootNode.getElementsByTagName("item")[address]
		row = []
		row.append(self.getValue(itemNodes.getElementsByTagName("lut_detAmask")[0].childNodes).zfill(2))
		row.append(self.getValue(itemNodes.getElementsByTagName("lut_detBmask")[0].childNodes).zfill(2))
		row.append(self.getValue(itemNodes.getElementsByTagName("lut_detCmask")[0].childNodes).zfill(2))
		return ''.join(row)
		

	def getRefDetNim(self):
		try:
			doc = self.importFile()
			referenceDet = self.getValue(doc.getElementsByTagName("referenceDet_NIM")[0].childNodes)
		except:
			try:
				referenceDet = self.getPropertie("referenceDet_NIM")
			except:
				raise BadConfigException("Unable to parse for referenceDet_NIM")
		return int(referenceDet)
	
	def getRefDetPrim(self):
		try:
			doc = self.importFile()
			referenceDet = self.getValue(doc.getElementsByTagName("referenceDet")[0].childNodes)
		except:
			try:
				referenceDet = self.getPropertie("referenceDet")
			except:
				raise BadConfigException("Unable to parse for referenceDet")
		return int(referenceDet)