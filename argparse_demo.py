#!/usr/bin/env python
# encoding: utf-8


import argparse

parser = argparse.ArgumentParser()
help(parser.add_argument) 
parser.add_argument("echo")
parser.add_argument('-p', '--port', type=int, default=8005)
args = parser.parse_args()
print args.echo
print args.port
