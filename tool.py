#!/usr/bin/env python
from argparse import ArgumentParser

from os.path import basename
from os.path import dirname
from os.path import realpath
from os.path import splitext

from nti_collector import NTICollector

from qti_collector import QTICollector

from extractor import Extractor

PARSER = ArgumentParser(description='Export/Import NTI/QTI packages.')
PARSER.add_argument('file', type=file, help='This is the file to be parsed.')
ARGS = PARSER.parse_args()

if ARGS.file.name.endswith('.json'):
    NTICollector(basename(ARGS.file.name), realpath(ARGS.file.name)[:-5] + '/')
elif ARGS.file.name.endswith('.zip'):
    Extractor(realpath(ARGS.file.name))
elif ARGS.file.name.endswith('.xml'):
    QTICollector(realpath(ARGS.file.name), dirname(realpath(ARGS.file.name)))
else:
    print 'file cannot end in ' + splitext(realpath(ARGS.file.name))[1]
    print 'file must end in either .json, .zip, or .xml'
