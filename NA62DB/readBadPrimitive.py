#!/usr/bin/env python

'''
Created on Jul 27, 2016

@author: ncl
'''
import sys

from database import DBConnector
from DBConfig import DBConfig as DB
import math 
from argparse import ArgumentParser, RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2016-05-27'
__updated__ = '2016-05-28'

myconn = None

def printActiveBits(mask):
    mask = int(mask, 0)
    dc = mask >> 16
    prim = mask & 0xffff

    inv_dc = ~dc & 0xffff
    inv_prim = ~prim & 0xffff
    pos_bits = prim & inv_dc
    neg_bits = inv_prim & inv_dc

    nbitList = []
    while neg_bits!=0:
        bitval = int(math.log(neg_bits, 2))
        if bitval!=15:
            nbitList.append(str(bitval)) 
        neg_bits = neg_bits - (1<<bitval)

    pbitList = []
    while pos_bits!=0:
        bitval = int(math.log(pos_bits, 2))
        if bitval!=14 or len(nbitList)==0:
            pbitList.append(str(bitval)) 
        pos_bits = pos_bits - (1<<bitval)
            
    return "+:{0} -:{1}".format(",".join(pbitList), ",".join(nbitList))

def processMask(primType, trig, d, maskID, printAll):
    if maskID==0:
        maskName = "maskA"
    elif maskID==1:
        maskName = "maskB"
    elif maskID==2:
        maskName = "maskC"
    elif maskID==3:
        maskName = "maskD"
    elif maskID==4:
        maskName = "maskE"
    elif maskID==5:
        maskName = "maskF"
    elif maskID==6:
        maskName = "maskG"

    if primType[maskName]!="0x7fff7fff":
        d["maskID"] = maskID
        d["mask"] = primType[maskName]
        maskDetails = myconn.executeGet("SELECT detname,id FROM primitivedetname WHERE detnumber=%s AND detmask=%s AND validitystart<%s AND (validityend>%s OR validityend IS NULL)", [maskID, primType[maskName], trig["validitystart"], trig["validityend"]])
        if len(maskDetails)==0:
            print "Run {run_id} | trigger {runtrigg_id} | prim {triggerprimitivetype_id} {masknumber}/{triggerprimitivedownscaling} | {maskName}({maskID}): {mask} Not found: {0}".format(printActiveBits(primType[maskName]), **d)
        for name in [x for x in maskDetails if (x["detname"]=="" or printAll)]:
            d.update(name)
            d["maskName"] = maskName
            print "Run {run_id} | trigger {runtrigg_id} | prim {triggerprimitivetype_id} {masknumber}/{triggerprimitivedownscaling} | {maskName}({maskID}): {detname:>10}   {id:>3}: {0}".format(printActiveBits(primType[maskName]), **d)

def processRequest(runNumber, triggerIndex, printAll, verbose):
    global myconn
    myconn = DBConnector()
    myconn.initConnection(passwd=DB.passwd, host=DB.host, db=DB.dbName, user=DB.userName, port=DB.port)
    myconn.openConnection()
    myconn.setSilent(verbose)
    
    run = myconn.executeGet("SELECT id, timestart,timestop FROM run WHERE number=%s", [runNumber])[0]
    run_id = run["id"]
    trig = myconn.executeGet("SELECT id as runtrigg_id,validitystart, validityend FROM runtrigger WHERE run_id=%s AND validitystart<%s AND (validityend>ADDDATE(%s, INTERVAL 5 SECOND) OR validityend IS NULL)", [run_id, run["timestop"], run["timestart"]])[triggerIndex]
    primList = myconn.executeGet("SELECT triggerprimitivetype_id,triggerprimitivedownscaling, masknumber FROM triggerprimitive WHERE runtrigger_id=%s", [trig["runtrigg_id"]])
    
    d = {"run_id":run_id}
    d.update(trig)
    for prim in primList:
        d.update(prim)
        primType = myconn.executeGet("SELECT * FROM triggerprimitivetype WHERE id=%s", [prim["triggerprimitivetype_id"]])[0]
        processMask(primType, trig, d, 0, printAll)
        processMask(primType, trig, d, 1, printAll)
        processMask(primType, trig, d, 2, printAll)
        processMask(primType, trig, d, 3, printAll)
        processMask(primType, trig, d, 4, printAll)
        processMask(primType, trig, d, 5, printAll)
        processMask(primType, trig, d, 6, printAll)
        print "------------------------------"
    
    
    
def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    
    # Setup argument parser
    parser = ArgumentParser(description=program_shortdesc, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-r", "--run", action="store", help="Run number", type=int, required=True)
    parser.add_argument("-a", "--all", action="store_true", help="Print all primitives", default=False)
    parser.add_argument("-t", "--trigger", action="store", help="Trigger index", default=0, type=int)
    parser.add_argument("-v", "--verbose", action="store_false", help="Silent db queries", default=True)
    parser.add_argument('-V', '--version', action='version', version=program_version_message)

    # Process arguments
    args = parser.parse_args()

    processRequest(runNumber=args.run, triggerIndex=args.trigger, printAll=args.all, verbose=args.verbose)

    return 0

if __name__ == '__main__':
    main()
