#!/usr/bin/env python
import argparse


parser = argparse.ArgumentParser(description='Crossly export and import QTI and NTI packages.')
parser.add_argument('echo', nargs='+')

args = parser.parse_args()
print ' '.join(args.echo)
