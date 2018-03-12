#!/usr/bin/env python
from argparse import ArgumentParser

from glob import glob

from os import walk

from os.path import join

PARSER = ArgumentParser(description='Export/Import NTI/QTI packages.')
PARSER.add_argument('file', type=file, help='This is the file to be parsed.')
PARSER.add_argument('parse', choices=['NTI', 'QTI'], help='Select NTI to convert file(s) to NTI'
                                                          'and likewise for QTI.')
ARGS = PARSER.parse_args()
print ARGS.file
print ARGS.parse
if ARGS.parse.lower() == 'nti':
    pass
else:
    RESULT = [y for x in walk(ARGS.file) for y in glob(join(x[0], '*.txt'))]
