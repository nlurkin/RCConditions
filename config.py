'''
Created on Nov 5, 2014

@author: ncl
'''

import re

class ConfigFile(object):
    '''
    ConfigFile
    '''
    
    def __init__(self, string):
        self.content = string
        
    def getPropertie(self, name):
        m = re.findall("<"+name+"\>(.*)</"+name+">", self.content)
        if m:
            return m[0]
        return None