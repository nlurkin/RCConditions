'''
Created on Nov 5, 2014

@author: ncl
'''

import datetime
import sys
import textwrap

import MySQLdb
from dateutil import tz 


class DBConnector(object):
    '''
    DBConnector
    '''
    wrapper = textwrap.TextWrapper(initial_indent=" --->", width=150, subsequent_indent='     ')
    
    def __init__(self, dry_run=True, exitOnFailure=True):
        self.db = None
        self.cursor = None
        self.dryRun = dry_run
        
        self.host = ""
        self.user = ""
        self.passwd = ""
        self.dbName = ""
        self.port = -1
        
        self.exitOnFailure = exitOnFailure
        self.lastError = ""
        self.silent = False
    
    def initConnection(self, host="nlurkinsql.cern.ch", user="nlurkin", passwd="", db="testRC", port=3307):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbName = db
        self.port = port
        
    def close(self):
        if self.db and self.db.open:
            self.db.close()
        
    def __del__(self):
        self.close()
        
    def indent(self, txt, stops=1):
        return self.wrapper.fill(txt)
    
    def getLastError(self):
        return self.lastError
    
    def setSilent(self, flag):
        self.silent = flag
    ##---------------------------------------
    #    Utility functions for DB actions
    ##---------------------------------------
    def openConnection(self):
        '''Create Database connection and cursor for SQL requests'''
        
        try:
            self.db = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.dbName, port=self.port)
            self.cursor = self.db.cursor()
        except MySQLdb.Error, e:
            self.lastError =  "Unable to initiate connection with database " + self.dbName + " at " + self.user + "@" + self.host + "\n" + str(e)
            print self.lastError
            if self.exitOnFailure:
                sys.exit()
    
    def executeInsert(self, sqlCommand, params=[]):
        print self.indent(sqlCommand % tuple(params))
        if self.dryRun:
            return -1
        try:
            self.cursor.execute(sqlCommand, params)
            self.db.commit()
            return self.cursor.lastrowid
        except MySQLdb.Error, e:
            self.lastError =  "Unable to execute insert statement: " + (sqlCommand % tuple(params)) + "\n" + str(e)
            print self.lastError
            self.db.rollback()
            if self.exitOnFailure:
                sys.exit()
        
        return -1
    
    def executeGet(self, sqlCommand, params=[]):
        if not self.silent:
            print self.indent(sqlCommand % tuple(params))
        if self.db==None:
            return ()
        res = -1
        try:
            self.cursor.execute(sqlCommand, params)
            fields = map(lambda x:x[0], self.cursor.description)
            res = [dict(zip(fields,row)) for row in self.cursor.fetchall()]
        except MySQLdb.Error, e:
            self.lastError =  "Unable to execute select statement: " + (sqlCommand % tuple(params)) + "\n" + str(e)
            print self.lastError
            if self.exitOnFailure:
                sys.exit()
        return res
    
    def getResultSingle(self, sqlCommand, params=[]):
        res = self.executeGet(sqlCommand, params)
        
        if len(res)==0:
            return False
        
        return res[0].itervalues().next()

    def getResultMultiple(self, sqlCommand, params=[]):
        res = self.executeGet(sqlCommand, params)
        
        if len(res)==0:
            return False
        
        return [int(x.itervalues().next()) for x in res]
    
    def toSQLTime(self, timestamp):
        if timestamp==None:
            return ''
        else:
            tzHere = tz.tzlocal()
            tzGeneva = tz.gettz('Europe/Brussels')
            localTime = datetime.datetime.fromtimestamp(timestamp)
            localTime = localTime.replace(tzinfo=tzHere)
            genevaTime = localTime.astimezone(tzGeneva) 
            return genevaTime.strftime('%Y-%m-%d %H:%M:%S')
    
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
    
    def _getNIMTriggerID(self, triggerID, typeID, downscaling, reference):
        rid = self.getResultSingle("SELECT id FROM triggernim WHERE runtrigger_id=%s AND triggernimtype_id=%s AND triggernimdownscaling=%s AND triggernimreference=%s", [triggerID, typeID, downscaling, reference])
        if rid==False:
            rid = self.getResultSingle("SELECT id FROM triggernim WHERE runtrigger_id=%s AND triggernimtype_id=%s AND triggernimdownscaling=%s AND triggernimreference is NULL", [triggerID, typeID, downscaling])
            return True,rid
        return False, rid

    def _getPrimitiveTriggerTypeID(self, masks):
        return self.getResultSingle("SELECT id FROM triggerprimitivetype WHERE maskA=%s AND maskB=%s AND maskC=%s AND maskD=%s AND maskE=%s AND maskF=%s AND maskG=%s", 
                                    [masks.detA, masks.detB, masks.detC, masks.detD, masks.detE, masks.detF, masks.detG])
    
    def _getPrimitiveTriggerID(self, triggerID, typeID, downscaling, reference):
        rid = self.getResultSingle("SELECT id FROM triggerprimitive WHERE runtrigger_id=%s AND triggerprimitivetype_id=%s AND triggerprimitivedownscaling=%s AND triggerprimitivereference=%s", [triggerID, typeID, downscaling,reference])
        if rid==False:
            rid = self.getResultSingle("SELECT id FROM triggerprimitive WHERE runtrigger_id=%s AND triggerprimitivetype_id=%s AND triggerprimitivedownscaling=%s AND triggerprimitivereference is NULL", [triggerID, typeID, downscaling])
            return True, rid
        return False, rid

    def _getControlTriggerID(self, triggerID, downscaling, mask, detector):
        params = [triggerID, detector, downscaling]
        mask2 = mask[:]
        mask2.extend([None]*(7-len(mask2)))
        params.extend(mask2)
        return self.getResultSingle("SELECT id FROM triggercontrol WHERE runtrigger_id=%s AND det_id=%s AND downscaling=%s AND mask=%s AND maskB=%s AND maskC=%s AND maskD=%s AND maskE=%s AND maskF=%s and MASKG=%s", params)

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
            return self.getResultSingle("SELECT id FROM runtrigger WHERE run_id=%s AND validitystart=%s AND (validityend=%s OR validityend IS NULL) ORDER BY validityend DESC", [runID, startT, endT])
    
    def _getEnabledDetectorID(self, runID, detectorName, startTS, endTS):
        startT = self.toSQLTime(startTS)
        endT = self.toSQLTime(endTS)
        
        if endTS==None:
            return self.getResultSingle("SELECT id FROM enableddetectors WHERE run_id=%s AND detectorName=%s AND validitystart=%s AND validityend IS NULL", [runID, detectorName, startT])
        else:
            return self.getResultSingle("SELECT id FROM enableddetectors WHERE run_id=%s AND detectorName=%s AND validitystart=%s AND (validityend=%s OR validityend IS NULL)", [runID, detectorName, startT, endT])
        
    
    def _getNIMDetNameID(self, startTS, endTS, detNumber):
        startT = self.toSQLTime(startTS)
        endT = self.toSQLTime(endTS)
        
        if endTS==None:
            return self.getResultSingle("SELECT id FROM nimdetname WHERE detnumber=%s AND validitystart=%s AND validityend IS NULL", [detNumber, startT])
        else:
            return self.getResultSingle("SELECT id FROM nimdetname WHERE detnumber=%s AND validitystart=%s AND validityend=%s", [detNumber, startT, endT])
    
    def _getPrimitiveDetNameID(self, startTS, endTS, detector, mask):
        startT = self.toSQLTime(startTS)
        endT = self.toSQLTime(endTS)
        
        #if endTS==None:
        return self.getResultSingle("SELECT id FROM primitivedetname WHERE detnumber=%s AND detmask=%s AND validitystart<%s AND (validityend>%s OR validityend IS NULL)", [detector, mask, startT, startT])
        #else:
        #    return self.getResultSingle("SELECT id FROM primitivedetname WHERE detnumber=%s AND detmask=%s AND validitystart=%s AND validityend=%s", [detector, mask, startT, endT])
    
    def _getIntensityID(self, startTS):
        startT = self.toSQLTime(startTS)
        
        return self.getResultSingle("SELECT id FROM T10_intensity WHERE time=%s", [startT])
          
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

    def _setNIMTrigger(self, triggerID, nimTypeID, downscaling, reference):
        exist, nimID = self._getNIMTriggerID(triggerID, nimTypeID, downscaling, reference)
        
        if nimID==False:
            return self.executeInsert("INSERT INTO triggernim (runtrigger_id, triggernimtype_id, triggernimdownscaling, triggernimreference) VALUES (%s, %s, %s, %s)", [triggerID, nimTypeID, downscaling, reference])
        elif exist==True:
            return self.executeInsert("UPDATE triggernim SET triggernimreference=%s WHERE id=%s", [reference, nimID])
        return nimID 

    def _setPrimitiveTriggerType(self, masks):
        typeID = self._getPrimitiveTriggerTypeID(masks)
        
        if typeID==False:
            return self.executeInsert("INSERT INTO triggerprimitivetype (maskA,maskB,maskC,maskD,maskE,maskF,maskG) VALUES (%s,%s,%s,%s,%s,%s,%s)", 
                                      [masks.detA,masks.detB,masks.detC,masks.detD,masks.detE,masks.detF,masks.detG])
        return typeID 
    
    def _setPrimitiveTrigger(self, triggerID, primitiveTypeID, downscaling, maskNumber, reference):
        exist, primitiveID = self._getPrimitiveTriggerID(triggerID, primitiveTypeID, downscaling, reference)
        
        if primitiveID==False:
            return self.executeInsert("INSERT INTO triggerprimitive (runtrigger_id, triggerprimitivetype_id, triggerprimitivedownscaling, triggerprimitivereference, maskNumber) VALUES (%s, %s, %s, %s, %s)", [triggerID, primitiveTypeID, downscaling, reference, maskNumber])
        elif exist==True:
            return self.executeInsert("UPDATE triggerprimitive SET triggerprimitivereference=%s, maskNumber=%s WHERE id=%s", [reference, maskNumber, primitiveID])
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

    def _setControlTrigger(self, triggerID, downscaling, mask, detector):
        controlID = self._getControlTriggerID(triggerID, downscaling, mask, detector)
        
        if controlID==False:
            params = [triggerID, detector, downscaling]
            mask2 = mask[:]
            mask2.extend([None]*(7-len(mask2)))
            params.extend(mask2)
            return self.executeInsert("INSERT INTO triggercontrol (runtrigger_id, det_id, downscaling, mask, maskB, maskC, maskD, maskE, maskF, maskG) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", params)
        return controlID 

    def _setTrigger(self, runID, startTS, endTS, triggerList):
        triggerID = self._getTriggerID(runID, startTS, endTS)
        
        Down = "NULL"
        if len(triggerList)>=2 and hasattr(triggerList[1], "Downscaling"):
            Down = triggerList[1].Downscaling
        
        if triggerID==False:
            if endTS==None:
                triggerID = self.executeInsert("INSERT INTO runtrigger (run_id, validitystart) VALUES (%s, %s)", [runID, self.toSQLTime(startTS)])
            else:
                triggerID = self.executeInsert("INSERT INTO runtrigger (run_id, validitystart, validityend) VALUES (%s, %s, %s)", [runID, self.toSQLTime(startTS), self.toSQLTime(endTS)])
        elif not endTS is None:
            self.executeInsert("UPDATE runtrigger SET validityend=%s WHERE id=%s", [self.toSQLTime(endTS), triggerID])
            
        if triggerList[0]=='Periodic':
            periodicType = self._setPeriodicTriggerType(triggerList[1])
            self._setPeriodicTrigger(triggerID, periodicType)
        if triggerList[0]=='NIM':
            nimType = self._setNIMTriggerType(triggerList[1].Mask)
            self._setNIMTrigger(triggerID, nimType, Down, triggerList[2])
        if triggerList[0]=='Primitive':
            primitiveType = self._setPrimitiveTriggerType(triggerList[1])
            self._setPrimitiveTrigger(triggerID, primitiveType, Down, triggerList[1].MaskNumber , triggerList[2])
            pass
        if triggerList[0]=='Sync':
            self._setSyncTrigger(triggerID)
        if triggerList[0]=='Calib':
            self._setCalibTrigger(triggerID)
        if triggerList[0]=='Control':
            self._setControlTrigger(triggerID, Down, triggerList[1].Mask, triggerList[1].Detector)

        return triggerID
                        
    def _setEnabledDetector(self, runID, startTS, endTS, detectorName, detectorValues):
        enabledID = self._getEnabledDetectorID(runID, detectorName, startTS, endTS)
        
        if enabledID==False:
            if endTS==None:
                return self.executeInsert("INSERT INTO enableddetectors (run_id, detectorid, detectorname, validitystart) VALUES (%s, %s, %s, %s)", 
                                          [runID, detectorValues.Name, detectorName, self.toSQLTime(startTS)])                
            else:
                return self.executeInsert("INSERT INTO enableddetectors (run_id, detectorid, detectorname, validitystart, validityend) VALUES (%s, %s, %s, %s, %s)", 
                                          [runID, detectorValues.Name, detectorName, self.toSQLTime(startTS), self.toSQLTime(endTS)])
        elif not endTS is None:
            return self.executeInsert("UPDATE enableddetectors SET validityend=%s WHERE id=%s", 
                                      [self.toSQLTime(endTS), enabledID])
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
    
    def _setPrimitiveDetName(self, startTS, endTS, detector, mask, meaning):
        if detector=="A":
            detector = 0
        if detector=="B":
            detector = 1
        if detector=="C":
            detector = 2
        if detector=="D":
            detector = 3
        if detector=="E":
            detector = 4
        if detector=="F":
            detector = 5
        if detector=="G":
            detector = 6
            
        detID = self._getPrimitiveDetNameID(startTS, endTS, detector, mask)
        if detID==False:
            if endTS==None:
                return self.executeInsert("INSERT INTO primitivedetname (detnumber, detmask, detname, validitystart) VALUES (%s, %s, %s, %s)", 
                                          [detector, mask, meaning, self.toSQLTime(startTS)])                
            else:
                return self.executeInsert("INSERT INTO primitivedetname (detnumber, detmask, detname, validitystart, validityend) VALUES (%s, %s, %s, %s, %s)",
                                          [detector, mask, meaning, self.toSQLTime(startTS), self.toSQLTime(endTS)])
        return detID
    
    def _setT10Intensity(self, startTS, value):
        intensityID = self._getIntensityID(startTS)
        if intensityID==False:
                return self.executeInsert("INSERT INTO T10_intensity (time, value) VALUES (%s, %s)", [self.toSQLTime(startTS), value])
        
        return intensityID
    ##---------------------------------------
    #    Create new run entries in database
    ##---------------------------------------
    def setRunInfo(self, runInfo):
        runID = self._getRunID(runInfo["RunNumber"])
        
        runTypeID = self._setRunType(runInfo["RunType"])
        if runID==False:
            self.executeInsert("INSERT INTO run (number, timestart, timestop, startcomment, endcomment, runtype_id, totalburst, totalL0, totalL1, totalL2, totalMerger) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                            [int(runInfo["RunNumber"]), runInfo["RunStartTime"], runInfo["RunStopTime"], 
                            runInfo["StartRunComment"], runInfo["EndRunComment"], runTypeID, runInfo["TotalBurst"], runInfo["TotalL0"], runInfo["TotalL1"], runInfo["TotalL2"], runInfo["TotalMerger"]])
        else:
            self.executeInsert("UPDATE run SET timestart=%s, timestop=%s, startcomment=%s, endcomment=%s, runtype_id=%s, totalburst=%s, totalL0=%s, totalL1=%s, totalL2=%s, totalMerger=%s WHERE id=%s", 
                            [runInfo["RunStartTime"], runInfo["RunStopTime"], runInfo["StartRunComment"], runInfo["EndRunComment"], runTypeID, runInfo["TotalBurst"], 
                            runInfo["TotalL0"], runInfo["TotalL1"], runInfo["TotalL2"], runInfo["TotalMerger"], runID])
            
        
    def setPeriodicTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = trigger.getList()
        for index, (startTS, trigg) in enumerate(triggList, 1):
            if trigg.Enabled==True and not trigg.Propertie is None:
                if index<len(triggList):
                    endTS = triggList[index][0]
                else:
                    endTS = None
                self._setTrigger(runID, startTS, endTS, ['Periodic', trigg.Propertie])

    def setNIMTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = trigger.getList()
        for index, (startTS, trigg) in enumerate(triggList, 1):
            if trigg.Enabled==True and not trigg.Propertie is None:
                if index<len(triggList):
                    endTS = triggList[index][0]
                else:
                    endTS = None
                for info in trigg.Propertie:
                    self._setTrigger(runID, startTS, endTS, ['NIM', info, trigg.RefDetector])
                    
    def setPrimitiveTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = trigger.getList()
        for index, (startTS, trigg) in enumerate(triggList, 1):
            if trigg.Enabled==True and not trigg.Propertie is None:
                if index<len(triggList):
                    endTS = triggList[index][0]
                else:
                    endTS = None
                for info in trigg.Propertie:
                    self._setTrigger(runID, startTS, endTS, ['Primitive', info, trigg.RefDetector])
    
    def setSyncTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = trigger.getList()
        for index, (startTS, trigg) in enumerate(triggList, 1):
            if trigg.Enabled==True:
                if index<len(triggList):
                    endTS = triggList[index][0]
                else:
                    endTS = None
                self._setTrigger(runID, startTS, endTS, ['Sync'])
    
    def setCalibTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = trigger.getList()
        for index, (startTS, trigg) in enumerate(triggList, 1):
            if trigg.Enabled==True:
                if index<len(triggList):
                    endTS = triggList[index][0]
                else:
                    endTS = None
                self._setTrigger(runID, startTS, endTS, ['Calib'])

    def setControlTriggerList(self, trigger, runNumber):
        runID = self._getRunID(runNumber)
        
        triggList = trigger.getList()
        for index, (startTS, trigg) in enumerate(triggList, 1):
            if trigg.Enabled==True and not trigg.Propertie is None:
                if index<len(triggList):
                    endTS = triggList[index][0]
                else:
                    endTS = None
                self._setTrigger(runID, startTS, endTS, ['Control', trigg.Propertie])
    
    def setEnabledDetectorList(self, enabled, runNumber):
        runID = self._getRunID(runNumber)
        
        for det in enabled:
            tsList = enabled[det].getList()
            for index, (startTS, detector) in enumerate(tsList, 1):
                if detector.Enabled==True:
                    if index<len(tsList):
                        endTS = tsList[index][0]
                    else:
                        endTS = None
                    self._setEnabledDetector(runID, startTS, endTS, det, detector)
     
    def setNIMNames(self, startTS, endTS, detNames):
        for det in detNames:
            self._setNIMDetName(startTS, endTS, det)
            
    def setPrimitivesNames(self, startTS, endTS, detNames, mask):
        self._setPrimitiveDetName(startTS, endTS, "A", mask.detA, detNames.detA)
        self._setPrimitiveDetName(startTS, endTS, "B", mask.detB, detNames.detB)
        self._setPrimitiveDetName(startTS, endTS, "C", mask.detC, detNames.detC)
        self._setPrimitiveDetName(startTS, endTS, "D", mask.detD, detNames.detD)
        self._setPrimitiveDetName(startTS, endTS, "E", mask.detE, detNames.detE)
        self._setPrimitiveDetName(startTS, endTS, "F", mask.detF, detNames.detF)
        self._setPrimitiveDetName(startTS, endTS, "G", mask.detG, detNames.detG)
    
    def setT10IntensityList(self, intensity):
        for startTS, value in intensity:
            self._setT10Intensity(startTS, value)
            
