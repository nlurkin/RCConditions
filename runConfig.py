'''
Created on Nov 6, 2014

@author: ncl
'''

class runParam(object):
    configFileTagName = None
    runNumber = None
    
    def __init__(self, runNumber):
        self.runNumber = runNumber
        if int(runNumber) > 953:
            self.configFileTagName = "SplitContent"
        else:
            self.configFileTagName = "FileContent"
        