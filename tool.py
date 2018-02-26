#!/usr/bin/env python
from argparse import ArgumentParser
from glob import glob
from os import path
from os import walk

parser = ArgumentParser(description='Export/Import NTI/QTI packages.')
parser.add_argument('file', type=file, help='This is the file to be parsed.')
parser.add_argument('parse', choices=['NTI', 'QTI'], help='Select NTI to convert file(s) to NTI'
                                                          'and likewise for QTI.')
args = parser.parse_args()
print args.file
print args.parse
'''if args.parse.lower() == 'nti':
    
else:
    result = [y for x in walk(args.file) for y in glob(path.join(x[0], '*.txt'))]'''
