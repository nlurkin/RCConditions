'''
Created on Jul 16, 2015

@author: nlurkin
'''
import operator
import copy

def combine_dict(d1, d2, op=operator.add):
    return dict(d1.items() + d2.items() + [(k, op(d1[k], d2[k])) for k in set(d1) & set(d2)])
    
class ConflictException(Exception):
    def __init__(self, field, lvalue, rvalue):
        self.value = "Conflict: (" + repr(field) + ") " + repr(lvalue) + "<->" + repr(rvalue)
    
    def __str__(self):
        return repr(self.value)

class tlObject(object):
    def __init__(self):
        pass
    def merge(self, other):
        pass
    def __str__(self):
        return ""
    def _equal(self, other):
        pass
    def _similar(self, other):
        pass
    
    def __repr__(self):
        return self.__str__()
    def __eq__(self, other):
        if other==None:
            return False
        return self._equal(other)
    def __add__(self, other):
        return self.merge(other)
    def like(self, other):
        if other is None:
            return False
        return self._similar(other)
    
class TriggerObject(tlObject):
    
    def __init__(self):
        self.Enabled = None
        self.Propertie = None
        self.RefDetector = None
    
    def merge(self, other):
        if self.Enabled is None:
            self.Enabled = other.Enabled
        elif not other.Enabled is None:
            raise ConflictException("Enabled", self.Enabled, other.Enabled)
        if self.Propertie is None:
            self.Propertie = other.Propertie
        elif not other.Propertie is None:
            raise ConflictException("Propertie", self.Propertie, other.Propertie)
        if self.RefDetector is None:
            self.RefDetector = other.RefDetector
        elif not other.RefDetector is None:
            raise ConflictException("RefDetector", self.RefDetector, other.RefDetector)
    
    def __str__(self):
        return "[Enabled:" + repr(self.Enabled) + ",Propertie:" + repr(self.Propertie) + ",RefDetector:"+repr(self.RefDetector) + "]"
    
    def _equal(self, other):
        if self.Enabled == other.Enabled and \
            self.Propertie == other.Propertie and \
            self.RefDetector == other.RefDetector:
            return True
        return False
        
    def _similar(self, other):
        if not other.Enabled is None:
            if self.Enabled != other.Enabled:
                return False
        if not other.Propertie is None:
            if self.Propertie != other.Propertie:
                return False
        if not other.RefDetector is None:
            if self.RefDetector != other.RefDetector:
                return False
        return True
             
class DetectorObject(tlObject):
    
    def __init__(self):
        self.Enabled = None
        self.Name = None

    def merge(self, other):
        if self.Enabled is None:
            self.Enabled = other.Enabled
        else:
            raise ConflictException("Enabled", self.Enabled, other.Enabled)
        if self.Name is None:
            self.Name = other.Name
        else:
            raise ConflictException("Name", self.Name, other.Name)

    def __str__(self):
        return "[Enabled:" + repr(self.Enabled) + ",Name:" + repr(self.Name) + "]"
    
    def _equal(self, other):
        if self.Enabled == other.Enabled and \
            self.Name == other.Name:
            return True
        return False
    
    def _similar(self, other):
        if not other.Enabled is None:
            if self.Enabled != other.Enabled:
                return False
        if not other.Name is None:
            if self.Name != other.Name:
                return False
    
class Timeline(object):
    '''
    classdocs
    '''


    def __init__(self, refObject):
        '''
        Constructor
        '''
        self._tl = {}
        self._refObject = refObject
        
    def addTS(self, timeStamp):
        self._tl[timeStamp] = self._refObject()
        return self._tl[timeStamp]
    
    def _getTS(self):
        return sorted(self._tl.keys())
    
    def merge(self, right, spread=False):
        keys_left = self._getTS()
        self._tl = combine_dict(self._tl, right._tl)
        
        
        if spread:
            previousTS_left = None
            previousVal_left = None
            previousTS_right = None
            previousVal_right = None
            for k in self._getTS():
                if k in keys_left:
                    previousTS_left = k
                    previousVal_left = copy.copy(self._tl[k])
                    if not previousTS_right is None:
                        self._tl[k].merge(previousVal_right)
                else:
                    previousTS_right = k
                    previousVal_right = copy.copy(self._tl[k])
                    if not previousTS_left is None:
                        self._tl[k].merge(previousVal_left)
    
    def simplify(self, removeSimilar=None):
        prev = None
        for t in self._getTS():
            if self._tl[t]==prev:  ## if current entry is the same as the previous, delete the current
                del self._tl[t]
            elif self._tl[t].like(removeSimilar):  ## if the current entry is one that should be rejected, delete it
                del self._tl[t]    
            else:
                prev = self._tl[t]
    
    def cutAfter(self, ts):
        listDel = [x for x in self._tl.keys() if x>ts]
        for t in listDel:
            del self._tl[t]

    def cutBefore(self, ts, nKeep=0):
        listDel = sorted([x for x in self._tl.keys() if x<ts])

        if len(listDel)>=nKeep:
            if nKeep>0:
                listDel = listDel[:-nKeep]
        else:
            return
        for t in listDel:
            del self._tl[t]
    
    def getList(self):
        return sorted(self._tl.items())
    
    