#!/bin/env python

'''
Created on Aug 6, 2015

@author: nlurkin
'''

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import bz2
import urllib2
import sys
from XMLExtract import Extractor

__all__ = []
__version__ = 0.1
__date__ = '2015-08-05'
__updated__ = '2015-08-05'

def main(argv=None):
    '''Command line options.'''

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
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", dest="file", help="File to process")
    group.add_argument("-r", "--run", dest="run", help="Run number to extract", type=int)
    parser.add_argument("-g", "--get", action="store_true", dest="get", help="Get the file locally")
    parser.add_argument('-V', '--version', action='version', version=program_version_message)
    parser.add_argument("-d", "--dumpinit", action="store_true", dest="dumpinit", help="Dump all INIT files for TEL62")

    # Process arguments
    args = parser.parse_args()

    if not args.file is None:
        Extractor.startReading(args.file)
    elif not args.run is None:
        try:    
            response = urllib2.urlopen('https://na62runconditions.web.cern.ch/na62runconditions/XMLProcessed/{0}.xml.bz2'.format(args.run))
            html = response.read()
        except urllib2.HTTPError as e:
            print e
            return -1
        data = bz2.decompress(html)
        if args.get == True:
            with open("run_%i.xml" % args.run, "w") as fd:
                fd.write(data)
        elif args.dumpinit == True:
            Extractor.dumpAllInit(data, args.run)
        else:
            Extractor.startReading(data)
    return 0

if __name__ == "__main__":
    sys.exit(main())
    