'''
Created on Nov 6, 2014

@author: ncl
'''

class runParam(object):
    configFileTagName = None
    
    l0tpFileNew = False
    
    def __init__(self, runNumber):
        if int(runNumber) > 953:
            self.configFileTagName = "SplitContent"
        else:
            self.configFileTagName = "FileContent"
        
        if int(runNumber) > 1307:
            self.l0tpFileNew = True
