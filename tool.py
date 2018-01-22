#!/usr/bin/env python
import argparse

PARSER = argparse.ArgumentParser(prog='idiots', description='Process some integers.')
PARSER.add_argument('integers', metavar='N', type=int, nargs='+',
                    help='an integer for the accumulator')
PARSER.add_argument('--sum', dest='accumulate', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')

ARGS = PARSER.parse_args()
print ARGS.accumulate(ARGS.integers)
