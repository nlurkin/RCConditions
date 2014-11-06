'''
Created on Nov 5, 2014

@author: ncl
'''

import datetime
import textwrap

import MySQLdb


class DBConnector(object):
    '''
    DBConnector
    '''
    wrapper = textwrap.TextWrapper(initial_indent=" --->", width=150, subsequent_indent='     ')
    
    def __init__(self):
        self.db = None
        self.cursor = None
    
    def indent(self, txt, stops=1):
        return self.wrapper.fill(txt)
    ##---------------------------------------
    #    Utility functions for DB actions
    ##---------------------------------------
    def connectDB(self):
        '''Create Database connection and cursor for SQL requests'''
        
        self.db = MySQLdb.connect(host="127.0.0.1", # your host, usually localhost
                             user="root", # your username
                             passwd="xxx", # your password
                             db="testRC") # name of the data base
        self.cursor = self.db.cursor()
    
    def executeInsert(self, sqlCommand, params=[]):
        print self.indent(sqlCommand % tuple(params))
        try:
            self.cursor.execute(sqlCommand, params)
            self.db.commit()
            return self.cursor.lastrowid
        except MySQLdb.Error, e:
            print sqlCommand % tuple(params)
            print ""
            print e
            self.db.rollback()
            raise e
    
    def executeGet(self, sqlCommand, params=[]):
        res = ()
        try:
            self.cursor.execute(sqlCommand, params)
            res = self.cursor.fetchall()
        except MySQLdb.Error, e:
            print sqlCommand % tuple(params)
            print ""
            raise e
        return res
    
    def getResultSingle(self, sqlCommand, params=[]):
        res = self.executeGet(sqlCommand, params)
        
        if len(res)==0:
            return False
        
        return res[0][0]

    def getResultMultiple(self, sqlCommand, params=[]):
        res = self.executeGet(sqlCommand, params)
        
        if len(res)==0:
            return False
        
        return [int(x[0]) for x in res]
    
    def toSQLTime(self, timestamp):
        if timestamp==None:
            return ''
        else:
            return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    ##---------------------------------------
    #    Get INDEX ID from database table
    ##---------------------------------------
    def _getRunID(self,runNumber):
        return self.getResultSingle("SELECT id FROM run WHERE number=%s", [runNumber])
    
    def _getRunTypeID(self, runType):
        return self.getResultSingle("SELECT id FROM runtype WHERE runtypename=%s", [runType])
    
    def _getPeriodicTriggerTypeID(self, period):
        return self.getResultSingle("SELECT id FROM triggerperiodictype WHERE period=%s", [period])
    
    def _getPeriodicTriggerID(self, triggerID, typeID=None):
        if triggerID==None:
            return self.getResultMultiple("SELECT id FROM triggerperiodic WHERE runtrigger_id=%s",[triggerID])
        else:
            return self.getResultSingle("SELECT id FROM triggerperiodic WHERE runtrigger_id=%s AND triggerperiodictype_id=%s", [triggerID, typeID])

    def _getNIMTriggerTypeID(self, mask):
        return self.getResultSingle("SELECT id FROM triggernimtype WHERE mask=%s",[mask])
    
    def _getNIMTriggerID(self, triggerID, typeID):
        return self.getResultSingle("SELECT id FROM triggernim WHERE runtrigger_id=%s AND triggernimtype_id=%s", [triggerID, typeID])

    def _getPrimitiveTriggerTypeID(self, mask):
        return self.getResultSingle("SELECT id FROM triggerprimitivetype WHERE mask=%s", [mask])
    
    def _getPrimitiveTriggerID(self, triggerID, typeID):
        return self.getResultSingle("SELECT id FROM triggerprimitive WHERE runtrigger_id=%s AND triggerprimitivetype_id=%s", [triggerID, typeID])

    def _getSyncTriggerID(self, triggerID):
        return self.getResultSingle("SELECT id FROM triggersync WHERE runtrigger_id=%s", [triggerID])

    def _getCalibTriggerID(self, triggerID):
        return self.getResultSingle("SELECT id FROM triggercalib WHERE runtrigger_id=%s", [triggerID])
    
    def _getTriggerID(self, runID, startTS, endTS):
        startT = self.toSQLTime(startTS)
        endT = self.toSQLTime(endTS)
        
        if endTS==None:
            return self.getResultSingle("SELECT id FROM runtrigger WHERE run_id=%s AND validitystart=%s AND validityend IS NULL", [runID, startT])
        else:
            return self.getResultSingle("SELECT id FROM runtrigger WHERE run_id=%s AND validitystart=%s AND validityend=%s", [runID, startT, endT])
    
    def _getEnabledDetectorID(self, runID, detectorName, startTS, endTS):
        startT = self.toSQLTime(startTS)
        endT = self.toSQLTime(endTS)
        
        if endTS==None:
            return self.getResultSingle("SELECT id FROM enableddetectors WHERE run_id=%s AND detectorName=%s AND validitystart=%s AND validityend IS NULL", [runID, detectorName, startT])
        else:
            return self.getResultSingle("SELECT id FROM enableddetectors WHERE run_id=%s AND detectorName=%s AND validitystart=%s AND validityend=%s", [runID, detectorName, startT, endT])
        
    
    def _getNIMDetNameID(self, startTS, endTS, detNumber):
        startT = self.toSQLTime(startTS)
        endT = self.toSQLTime(endTS)
        
        if endTS==None:
            return self.getResultSingle("SELECT id FROM nimdetname WHERE detnumber=%s AND validitystart=%s AND validityend IS NULL", [detNumber, startT])
        else:
            return self.getResultSingle("SELECT id FROM nimdetname WHERE detnumber=%s AND validitystart=%s AND validityend=%s", [detNumber, startT, endT])
        
    ##---------------------------------------
    #    Get INDEX ID from database table, create the entry if does not exist
    ##---------------------------------------
    def _setRunType(self, runType):
        typeID = self._getRunTypeID(runType)
        
        if typeID==False:
            return self.executeInsert("INSERT INTO runtype (runtypename, runtypedesc) VALUES (%s, '')", [runType])
        return typeID 

    def _setPeriodicTriggerType(self, period):
        typeID = self._getPeriodicTriggerTypeID(period)
        
        if typeID==False:
            return self.executeInsert("INSERT INTO triggerperiodictype (period) VALUES (%s)", [period])
        return typeID 

    def _setPeriodicTrigger(self, triggerID, periodTypeID):
        periodicID = self._getPeriodicTriggerID(triggerID, periodTypeID)
        
        if periodicID==False:
            return self.executeInsert("INSERT INTO triggerperiodic (runtrigger_id, triggerperiodictype_id) VALUES (%s, %s)", [triggerID, periodTypeID])
        return periodicID 

    def _setNIMTriggerType(self, mask):
        typeID = self._getNIMTriggerTypeID(mask)
        
        if typeID==False:
            return self.executeInsert("INSERT INTO triggernimtype (mask) VALUES (%s)", [mask])
        return typeID 

    def _setNIMTrigger(self, triggerID, nimTypeID):
        nimID = self._getNIMTriggerID(triggerID, nimTypeID)
        
        if nimID==False:
            return self.executeInsert("INSERT INTO triggernim (runtrigger_id, triggernimtype_id) VALUES (%s, %s)", [triggerID, nimTypeID])
        return nimID 

    def _setPrimitiveTriggerType(self, mask):
        typeID = self._getPrimitiveTriggerTypeID(mask)
        
        if typeID==False:
            return self.executeInsert("INSERT INTO triggerprimitivetype (mask) VALUES (%s)", [mask])
        return typeID 
    
    def _setPrimitiveTrigger(self, triggerID, primitiveTypeID):
        primitiveID = self._getPrimitiveTriggerID(triggerID, primitiveTypeID)
        
        if primitiveID==False:
            return self.executeInsert("INSERT INTO triggerprimitive (runtrigger_id, triggerprimitivetype_id) VALUES (%s, %s)", [triggerID, primitiveTypeID])
        return primitiveID 

    def _setSyncTrigger(self, triggerID):
        syncID = self._getSyncTriggerID(triggerID)
        
        if syncID==False:
            return self.executeInsert("INSERT INTO triggersync (runtrigger_id) VALUES (%s)", [triggerID])
        return syncID 

    def _setCalibTrigger(self, triggerID):
        calibID = self._getCalibTriggerID(triggerID)
        
        if calibID==False:
            return self.executeInsert("INSERT INTO triggercalib (runtrigger_id) VALUES (%s)", [triggerID])
        return calibID 

    def _setTrigger(self, runID, startTS, endTS, trigger):
        triggerID = self._getTriggerID(runID, startTS, endTS)
        
        if triggerID==False:
            if endTS==None:
                triggerID = self.executeInsert("INSERT INTO runtrigger (run_id, validitystart) VALUES (%s, %s)", [runID, self.toSQLTime(startTS)])
            else:
                triggerID = self.executeInsert("INSERT INTO runtrigger (run_id, validitystart, validityend) VALUES (%s, %s, %s)", [runID, self.toSQLTime(startTS), self.toSQLTime(endTS)])

        if trigger[0]=='Periodic':
            periodicType = self._setPeriodicTriggerType(trigger[1])
            self._setPeriodicTrigger(triggerID, periodicType)
        if trigger[0]=='NIM':
            nimType = self._setNIMTriggerType(trigger[1])
            self._setNIMTrigger(triggerID, nimType)
        if trigger[0]=='Primitive':
            primitiveType = self._setPrimitiveTriggerType(trigger[1])
            self._setPrimitiveTrigger(triggerID, primitiveType)
        if trigger[0]=='Sync':
            self._setSyncTrigger(triggerID)
        if trigger[0]=='Calib':
            self._setCalibTrigger(triggerID)

        return triggerID
                        
    def _setEnabledDetector(self, runID, startTS, endTS, detectorName, detectorValues):
        enabledID = self._getEnabledDetectorID(runID, detectorName, startTS, endTS)
        
        if enabledID==False:
            if endTS==None:
                return self.executeInsert("INSERT INTO enableddetectors (run_id, detectorid, detectorname, validitystart) VALUES (%s, %s, %s, %s)", 
                                          [runID, detectorValues[1], detectorName, self.toSQLTime(startTS)])                
            else:
                return self.executeInsert("INSERT INTO enableddetectors (run_id, detectorid, detectorname, validitystart, validityend) VALUES (%s, %s, %s, %s, %s)", 
                                          [runID, detectorValues[1], detectorName, self.toSQLTime(startTS), self.toSQLTime(endTS)])
        return enabledID
    
    def _setNIMDetName(self, startTS, endTS, detector):
        detID = self._getNIMDetNameID(startTS, endTS, detector[0])
        if detID==False:
            if endTS==None:
                return self.executeInsert("INSERT INTO nimdetname (detnumber, detname, validitystart) VALUES (%s, %s, %s)", 
                                          [detector[0], detector[1], self.toSQLTime(startTS)])                
            else:
                return self.executeInsert("INSERT INTO nimdetname (detnumber, detname, validitystart, validityend) VALUES (%s, %s, %s, %s)",
                                          [detector[0], detector[1], self.toSQLTime(startTS), self.toSQLTime(endTS)])
        return detID
    
    ##---------------------------------------
    #    Create new run entries in database
    ##---------------------------------------
    def setRunInfo(self, runInfo):
        runID = self._getRunID(runInfo["RunNumber"])
        
        runTypeID = self._setRunType(runInfo["RunType"])
        if runID==False:
            self.executeInsert("INSERT INTO run (number, timestart, timestop, startcomment, endcomment, runtype_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                            [int(runInfo["RunNumber"]), runInfo["RunStartTime"], runInfo["RunStopTime"], 
                            runInfo["StartRunComment"], runInfo["EndRunComment"], runTypeID])
        #else:
        #    self.executeInsert("UPDATE run SET timestart=%s, timestop=%s, startcomment=%s, endcomment=%s, runtype_id=%s WHERE id=%s", [runInfo["RunStartTime"], runInfo["RunStopTime"], 
        #                    runInfo["StartRunComment"], runInfo["EndRunComment"], runTypeID, runID])
            
        
    def setPeriodicTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = sorted(trigger.keys())
        for index, trigg in enumerate(triggList, 1):
            if trigger[trigg][0]==True:
                startTS = trigg
                if index<len(triggList):
                    endTS = triggList[index]
                else:
                    endTS = None
                self._setTrigger(runID, startTS, endTS, ['Periodic', trigger[trigg][1]])

    def setNIMTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = sorted(trigger.keys())
        for index, trigg in enumerate(triggList, 1):
            if trigger[trigg][0]==True:
                startTS = trigg
                if index<len(triggList):
                    endTS = triggList[index]
                else:
                    endTS = None
                for mask in trigger[trigg][1]:
                    self._setTrigger(runID, startTS, endTS, ['NIM', mask])
                    
    def setPrimitiveTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = sorted(trigger.keys())
        for index, trigg in enumerate(triggList, 1):
            if trigger[trigg][0]==True:
                startTS = trigg
                if index<len(triggList):
                    endTS = triggList[index]
                else:
                    endTS = None
                for mask in trigger[trigg][1]:
                    self._setTrigger(runID, startTS, endTS, ['Primitive', mask])
    
    def setSyncTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = sorted(trigger.keys())
        for index, trigg in enumerate(triggList, 1):
            if trigger[trigg][0]==True:
                startTS = trigg
                if index<len(triggList):
                    endTS = triggList[index]
                else:
                    endTS = None
                self._setTrigger(runID, startTS, endTS, ['Sync'])
    
    def setCalibTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = sorted(trigger.keys())
        for index, trigg in enumerate(triggList, 1):
            if trigger[trigg][0]==True:
                startTS = trigg
                if index<len(triggList):
                    endTS = triggList[index]
                else:
                    endTS = None
                self._setTrigger(runID, startTS, endTS, ['Calib'])
    
    def setEnabledDetectorList(self, enabled, runNumber):
        runID = self._getRunID(runNumber)
        
        for det in enabled:
            tsList = sorted(enabled[det].keys())
            for index, tsVal in enumerate(tsList, 1):
                if enabled[det][tsVal][0]==True:
                    startTS = tsVal
                    if index<len(tsList):
                        endTS = tsList[index]
                    else:
                        endTS = None
                    self._setEnabledDetector(runID, startTS, endTS, det, enabled[det][tsVal])
     
    def setNIMNames(self, startTS, endTS, detNames):
        for det in detNames:
            self._setNIMDetName(startTS, endTS, det)
            
    def close(self):
        if self.db.open:
            self.db.close()
        
    def __del__(self):
        self.close()