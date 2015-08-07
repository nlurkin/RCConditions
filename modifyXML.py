#!/bin/env python
# encoding: utf-8
'''
modifyXML -- shortdesc

modifyXML is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2015 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import os
import sys

from lxml import etree

from XMLExtract.TEL62Decoder import TEL62Decoder
import shutil
from XMLExtract.XMLDoc import xmlDocument


__all__ = []
__version__ = 0.1
__date__ = '2015-08-07'
__updated__ = '2015-08-07'

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2015 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    # Setup argument parser
    parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
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
    
    if args.mode == "replace":
        replace = True
    else:
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
            
        shutil.copyfile(xmlFile, "%s.bckp" % xmlFile)
        with open(xmlFile, "w") as fd:
            fd.write(etree.tostring(xmldoc._xml, pretty_print=True))
    return 0

if __name__ == "__main__":

    sys.exit(main())
