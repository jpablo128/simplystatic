#!/usr/bin/env python

'''Provide a command-line interface to the Simply Static system.

This module provides a very simple command-line interface to initialize,
manage, and generate a Simply Static site. It makes use of the s2site 
package.

'''
import argparse
import sys
import time
import os
import re
import random

import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

from simplystatic import s2site
from simplystatic import util

THIS_MODULE = sys.modules[__name__]

#site = None

def setup_parser():
    '''Set up the command-line options.'''
    p = argparse.ArgumentParser(description='Create and manage a \
SimplyStatic site.')
    subparsers = p.add_subparsers(help='commands', dest='command')

    # aliases are not supported in 2.7 for add_parser
    # init command
    init_cmd_parser = subparsers.add_parser('init',
                        help="Initialize a SimplyStatic directory structure")

    init_cmd_parser.add_argument('-d', '--dirname', action='store',
                                 help='Directory to initialize')

    init_cmd_parser.add_argument('-r', '--randomsite', action='store_true',
                                 help='Add random pages to the site (useful for testing)')

    init_cmd_parser.add_argument('-n', '--numpages', action='store',type=int, default = 20,
                                 help='Number of random pages to add to the site.')

    # add command
    add_cmd_parser = subparsers.add_parser('add',
                                           help='Add a page to the site.')
    add_cmd_parser.add_argument('title', help="Title for the page",
                                action='store')

    add_cmd_parser.add_argument('-d', '--dirname',
        help="Directory of site root, or any place under site root.",
        action='store')

    generate_cmd_parser = subparsers.add_parser('gen',
                                           help='Generates the site.')
    generate_cmd_parser.add_argument('-d', '--dirname',
        help="Directory of site root, or any place under site root.",
        action='store')

    # rename command
    rename_cmd_parser = subparsers.add_parser('rename',
                                    help='Renames a page in the site.')
    rename_cmd_parser.add_argument('slug', 
                            help="Slug of the page to be renamed",
                            action='store')
    rename_cmd_parser.add_argument('newtitle',
                help="New title in quotes (*NOT* a slug) for the page.",
                action='store')
    rename_cmd_parser.add_argument('-d', '--dirname', 
            help="Directory of site root, or any place under site root.",
            action='store')

    # servecommand

    serve_cmd_parser = subparsers.add_parser('serve',
                                    help='Serves the site on localhost.')
    serve_cmd_parser.add_argument('-p','--port', action='store', type=int, default = 8000,
                                 help='Port for the server.')

    serve_cmd_parser.add_argument('-i','--ip', action='store', default = '127.0.0.1',
                                 help='IP address for the server.')

    # ls command
    ls_cmd_parser = subparsers.add_parser('ls',
                        help="List pages, drafts, or most recently edited page.")

    ls_cmd_parser.add_argument('-d', '--dirname',
        help="Directory of site root, or any place under site root.",
        action='store')

    ls_cmd_parser.add_argument('-f', '--drafts', action='store_true',
                                   help='List pages whose status is draft.')

    ls_cmd_parser.add_argument('-r', '--recent', action='store_true',
                                 help='List the most recently edited page.')


    return p

def make_site_obj(argdict):
    '''Instantiate and return the site. This will be used for all commands'''
    #d = '.'
    d = None
    if 'dirname' in argdict:
        d = argdict['dirname']
    try:
        s = s2site.Site(d)
    except Exception : # pragma: no cover
        print "Could not instantiate site object."
        sys.exit()
    return s

def dispatch(argdict):
    '''Call the command-specific function, depending on the command.'''
    cmd = argdict['command']
    ftc = getattr(THIS_MODULE, 'do_'+cmd)
    ftc(argdict)

def do_init(argdict):
    '''Create the structure of a s2site.'''
    site = make_site_obj(argdict)
    try:
        site.init_structure()
        print "Initialized directory."
        if argdict['randomsite']:
            #all_tags = ['tag1','tag2','tag3','tag4']
            for i in range(1,argdict['numpages']+1):
                #ptags = random.sample(all_tags,random.randint(1,len(all_tags)))
                p = site.random_page()
                p.set_published()
                p.write()
                print "added page ",p.slug
    except ValueError: # pragma: no cover
        print "Cannot create structure. You're already within an s2 \
tree, or the directory is not empty or it is not writeable. "

def do_add(argdict):
    '''Add a new page to the site.'''
    site = make_site_obj(argdict)
    if not site.tree_ready:
        print "Cannot add page. You are not within a simplystatic \
tree and you didn't specify a directory."
        sys.exit()
    title = argdict['title']
    try: 
        new_page = site.add_page(title)
        new_page.write()
        print "Added page '"+ title + "'"
    except ValueError: # pragma: no cover
        print "Attempted to create a page which already exists."
        sys.exit()

def do_rename(argdict):
    '''Rename a page.'''
    site = make_site_obj(argdict)
    slug = argdict['slug']
    newtitle = argdict['newtitle']
    try:
        site.rename_page(slug, newtitle)
        print "Renamed page."
    except ValueError: # pragma: no cover
        print "Cannot rename. A page with the given slug does not exist."
        sys.exit()

def do_gen(argdict):
    '''Generate the whole site.'''
    site = make_site_obj(argdict)
    try:
        st = time.time()
        site.generate()
        et = time.time()
        print "Generated Site in %f seconds."% (et-st)
    except ValueError: # pragma: no cover
        print "Cannot generate. You are not within a simplystatic \
tree and you didn't specify a directory."

def do_ls(argdict):
    '''List pages.'''
    site = make_site_obj(argdict)
    if not site.tree_ready:
        print "Cannot list pages. You are not within a simplystatic \
tree and you didn't specify a directory."
        sys.exit()
    drafts = argdict['drafts']
    recent = argdict['recent']
    dir = site.dirs['source']

    r = site.get_page_names()
    if drafts:
        fr = [os.path.join(dir,pn , pn+".md") for pn in r]
        cpat = re.compile('status:\s+draft') #compiled pattern
        i=0
        print ''
        for f in fr:
            fcontent = open(f,'r').read().lower()
            res = cpat.search(fcontent)
            if res:
                print r[i]
            i += 1
        print ''
    else:
        if recent:
            fr = [os.path.join(dir,pn , pn+".md") for pn in r]
            bmt = 0
            i = 0
            for f in fr:
                mt = os.path.getmtime(f)
                if mt > bmt:
                    bmt = mt
                    fname = r[i]
                i += 1
            print '\n' + fname + '\n'
        else:
            print  '\n' + '\n'.join(r) + '\n'



def do_serve(argdict):
    '''Serve the site on localhost, for testing/development.'''
    site = make_site_obj(argdict)
    os.chdir(site.dirs['www'])

    HandlerClass = SimpleHTTPRequestHandler
    ServerClass  = BaseHTTPServer.HTTPServer
    Protocol     = "HTTP/1.0"
    server_address = (argdict['ip'], argdict['port'])
    HandlerClass.protocol_version = Protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()

if __name__ == "__main__": # pragma: no cover
    PARSER = setup_parser()
    ARGS = PARSER.parse_args()
    ARG_DICT = vars(ARGS)
    dispatch(ARG_DICT)

