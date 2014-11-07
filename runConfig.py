'''
Created on Nov 6, 2014

@author: ncl
'''

class runParam(object):
    configFileTagName = None
    
    def __init__(self, runNumber):
        if int(runNumber) > 953:
            self.configFileTagName = "SplitContent"
        else:
            self.configFileTagName = "FileContent"