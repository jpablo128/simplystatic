#!/usr/bin/env python

import argparse
import sys
import time
import os.path
import os
import random

# ONLY FOR DEVELOPMENT TESTING add one directory up to the sys.path
# so the imports work
#sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from simplystatic import s2site
from simplystatic import s2page

def setup_parser():
    '''Set up the command-line options.'''
    parser = argparse.ArgumentParser(description='Add random pages to existing site.')
    parser.add_argument('-d','--directory', action='store', default= os.getcwd(),
                                 help='Site directory (must be a valid s2 structure).')
    parser.add_argument('-n','--number', action='store', type=int, default = 20,
                                 help='Number of pages to generate.')

    return parser

def make_site_obj(argdict):
    '''Instantiate and return the site. This will be used for all commands'''
    d = os.getcwd() #'.'
    if 'directory' in argdict:
        d = argdict['directory']
    try:
        s = s2site.Site(d)
    except:
        print "Could not instantiate site object."
        sys.exit()
    return s


all_tags = ['tag1','tag2','tag3','tag4']

if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()
    argdict = vars(args)
    site = make_site_obj(argdict)
    if site.tree_ready:
        for i in range(1,argdict['number']+1):
            ptags = random.sample(all_tags,random.randint(1,len(all_tags)))
            p = site.random_page(tags=ptags) 
            p.set_published()
            p.write()
            print "added page ",p.slug