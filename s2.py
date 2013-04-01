#!/usr/bin/python

import argparse
from s2_class import *
import sys
import os.path

#set up ref to global namespace
#gnamespace = __import__(__name__)


if __name__ == "__main__":
	#set up command-line argumnts
	#progname = sys.argv[0]
	#rundir = os.path.dirname(progname)
	parser = argparse.ArgumentParser(description='Create and manage S2 static site.')
	parser.add_argument('command', choices=['create', 'generate','addpost'],
						help='specify the command to execute.')

	parser.add_argument('-d','--dir',
						help='specify the directory. If omitted, use current directory.')

	parser.add_argument('-t','--title', 
						help='specify the post title.')

	args = parser.parse_args()

	#instantiate s2 interpreter
	s2 = S2(vars(args))
	#dispatch command
	ftc = getattr(s2,vars(args)['command'])
	ftc(vars(args))
