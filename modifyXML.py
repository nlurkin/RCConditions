#!/bin/env python
# encoding: utf-8
'''
modifyXML -- Simple command line script to modify TEL62 XML file content

Multiple files can be modified simultaneously. 
In the case of --tags, multiple values can be modified simultaneously.

Examples:
- Increment tdcOffset of tdc 2 of tdcb 1 of 25 for 2 files:
    ./modifyXML.py my_file1 my_file2 add --tdcb 1 --tdc 2 --tdcoff 25 --tdc 3 --tdcoff 25
  
- Replace channel offset of channel 13 of tdc 2 of tdcb 0 with 42 and 
number of slots with 6 for all pp for 1 file:
    ./modifyXML.py my_file1 replace --tdcb 0 ---tdc 2 --channel 13 --choff 42 
                 --tag pp[0].nslots=6 --tag pp[1].nslots=6 --tags pp[2].nslots=6 
                 --tags pp[3].nslots=6
'''

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import sys

from lxml import etree

from XMLExtract import TEL62Decoder
from XMLExtract.XMLDoc import xmlDocument
import XMLExtract

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_shortdesc = __import__('__main__').__doc__

    # Setup argument parser
    parser = ArgumentParser(description=program_shortdesc, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("file", action="append", nargs="+")
    parser.add_argument("mode", choices=["add", "replace"])
    parser.add_argument("--pp", type=int)
    parser.add_argument("--tdccphase", type=int)
    parser.add_argument("--trigrxphase", type=int)
    parser.add_argument("--tdcb", type=int)
    parser.add_argument("--tdc", type=int)
    parser.add_argument("--tdcoff", type=int)
    parser.add_argument("--channel", type=int)
    parser.add_argument("--choff", type=int)
    parser.add_argument("--tag", action="append")

    # Process arguments
    args = parser.parse_args()
    
    
    #Activate value history
    XMLExtract.setHistory(True)
    
    if args.mode == "replace":
        replace = True
    else:
        if not args.tag is None:
            print "Error: --tag is only valid with the replace command"
            sys.exit(-1)
        replace = False
    
    fileList = [item for sublist in args.file for item in sublist]
    for xmlFile in fileList:
        print "Processing file {0}".format(xmlFile)
        
        xmldoc = xmlDocument(xmlFile)
        xmldoc.identifyFileType()
        if xmldoc._type=="TEL":
            xmldoc = TEL62Decoder(xmldoc)
        else:
            print "Not a TEL62 configuration file... skipping"
            continue
        
        if not args.pp is None and not args.pp in xmldoc.pp:
            print "Specified PP does not exist in file. PP operations are ignored"
    
        if not args.tdcb is None and not args.tdcb in xmldoc.tdcb:
            print "Specified TDCB does not exist in file. TDCB operations are ignored"
        else:
            if not args.tdc is None and not args.tdcb is None and not args.tdc in xmldoc.tdcb[args.tdcb].tdc:            
                print "Specified TDC does not exist in file. TDC operations are ignored"
            else:
                if (not args.channel is None and not args.tdc is None and not args.tdcb is None and  
                    not args.channel in xmldoc.tdcb[args.tdcb].tdc[args.tdc].channelOffset):
                    print "Specified channel does not exist in file. Channel operations are ignored"
                    
        
        dotdccphase = False
        if not args.tdccphase is None:
            if args.pp is None:
                print "No PP specified. tdccphase is ignored."
            else:
                dotdccphase = True
        
        dotrigrxphase = False
        if not args.trigrxphase is None:
            if args.pp is None:
                print "No PP specified. trigrxphase is ignored."
            else:
                dotrigrxphase = True
        
        dotdcoff = False
        if not args.tdcoff is None:
            if args.tdcb is None or args.tdc is None:
                print "No TDCB specified. tdcoff is ignored"
            else:
                dotdcoff = True
        
        dochoff = False
        if not args.choff is None:
            if args.tdcb is None or args.tdc is None or args.channel is None:
                print "No TDCB specified. choff is ignored"
            else:
                dochoff = True
        
        if dotdccphase:
            if replace:
                xmldoc.pp[args.pp].replaceTDCCPhase(args.tdccphase)
            else:
                xmldoc.pp[args.pp].addToTDCCPhase(args.tdccphase)
        if dotrigrxphase:
            if replace:
                xmldoc.pp[args.pp].replaceTrigrXPhase(args.tdccphase)
            else:
                xmldoc.pp[args.pp].addToTrigrXPhase(args.tdccphase)
        if dotdcoff:
            if replace:
                xmldoc.tdcb[args.tdcb].tdc[args.tdc].replaceOffset(args.tdcoff)
            else:
                xmldoc.tdcb[args.tdcb].tdc[args.tdc].addToOffset(args.tdcoff)
        if dochoff:
            if replace:
                xmldoc.tdcb[args.tdcb].tdc[args.tdc].replaceChannelOffset(args.channel, args.choff)
            else:
                xmldoc.tdcb[args.tdcb].tdc[args.tdc].addToChannelOffset(args.channel, args.choff)
    
        if not args.tag is None:
            for pathEl in args.tag:
                [path, value] = pathEl.split("=")
                xmldoc.replacePath(path, value)
            
        with open(xmlFile, "w") as fd:
            fd.write(etree.tostring(xmldoc._xml, pretty_print=True))
    return 0

if __name__ == "__main__":

    sys.exit(main())
