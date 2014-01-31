#!/usr/bin/python
import unittest
import tempfile
import shutil
import os
import random
import glob
import sys
from argparse import ArgumentParser


from mock import MagicMock, patch

# s2 is in bin, because it's a command. I made it a package so I can
# import it, and nosetests can get it, but I still need this sys.path
# trickery
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from bin import s2
from simplystatic import s2site
from simplystatic import util

class TestCLIarguments(unittest.TestCase):
    def setUp(self):
        self.parser = s2.setup_parser()
    
    def test_setup_parser_should_return_ArgumentParser(self):
        self.assertIsInstance(self.parser,ArgumentParser,"setup_parser did not return a valid ArgumentParser.")

    #test dispatch
    def test_dispatch_should_call_init_if_command_is_init(self):
        args = self.parser.parse_args(['init'])
        argdict = vars(args)
        orig_do_init = s2.do_init
        s2.do_init = MagicMock(name='do_init') #we patch the original s2.do_init method
        s2.dispatch(argdict)
        s2.do_init.assert_called_once_with(argdict)
        # remove the patch!!
        s2.do_init = orig_do_init

    def test_dispatch_should_call_add_if_command_is_add(self):
        args = self.parser.parse_args(['add','This is the page title'])
        argdict = vars(args)
        orig_do_add = s2.do_add
        s2.do_add = MagicMock(name='do_add') #we patch the original s2.do_add method
        s2.dispatch(argdict)
        s2.do_add.assert_called_once_with(argdict)
        # remove the patch!!
        s2.do_add = orig_do_add

    def test_dispatch_should_call_rename_if_command_is_rename(self):
        args = self.parser.parse_args(['rename', 'a_slug', "a new title", '-d', 'some/dir'])
        argdict = vars(args)
        orig_do_rename = s2.do_rename
        s2.do_rename = MagicMock(name='do_rename') #we patch the original s2.do_rename method
        s2.dispatch(argdict)
        s2.do_rename.assert_called_once_with(argdict)
        # remove the patch!!
        s2.do_rename = orig_do_rename

    def test_dispatch_should_call_generate_if_command_is_generate(self):
        args = self.parser.parse_args(['gen'])
        argdict = vars(args)
        orig_do_gen = s2.do_gen
        s2.do_gen = MagicMock(name='do_gen') #we patch the original s2.do_rename method
        s2.dispatch(argdict)
        s2.do_gen.assert_called_once_with(argdict)
        # remove the patch!!
        s2.do_gen = orig_do_gen

class TestCLIcommands(unittest.TestCase):
    def setUp(self):
        self.parser = s2.setup_parser()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # now test that the do_* methods call the right things with the right args
    # This might have been tested just using mocks, and verifying that the right
    # methods are called. But it turns out that in most cases it's more complex
    # to set up the mocking infrastructure than to do the real calls and verify
    # the resuts... and doing the real calls gives us more robust tests... even
    # though it' a little overkill (because all of the other unit tests cover
    # the key operations) ...  so... no mocking here.
    def test_do_init_should_create_correct_structure(self):
        args = self.parser.parse_args(['init','-d',self.temp_dir])
        argdict = vars(args)
        s2.dispatch(argdict)  #this triggers call to do_init
        # now verify that the tree structure is correct.
        self.assertTrue(s2site.verify_dir_structure(self.temp_dir),"tree structure was incorrect after init command.")

    def test_do_add_should_create_page_in_source(self):
        # init site
        site = s2site.Site(self.temp_dir)
        site.init_structure()
        # add page
        title = 'This is the new page title'
        args = self.parser.parse_args(['add',title,'-d',self.temp_dir])
        argdict = vars(args)
        s2.dispatch(argdict)  #this triggers call to do_add
        # verify that the page is there
        self.assertTrue(site.page_exists_on_disk(util.make_slug(title)),"page does not exist after add_page.")

    def test_do_generate_should_create_directory_in_www(self):
        # init site
        site = s2site.Site(self.temp_dir)
        site.init_structure()
        # generate a random number of random pages
        slugs = []
        for i in range(0,random.randrange(11,31)):
            p = site.random_page()
            p.set_published()
            p.write()
            slugs.append(p.slug)
        args = self.parser.parse_args(['gen','-d',self.temp_dir])
        argdict = vars(args)
        s2.dispatch(argdict)  #this triggers call to generate
        # verify that the directories for the pages are there
        wlist = glob.glob(os.path.join(site.dirs['www'], "*"))
        wlist = [f for f in wlist if os.path.isdir(f)]
        wlist = [os.path.split(f)[1] for f in wlist]
        wset = set(wlist)
        slugset = set(slugs)
        self.assertTrue(slugset.issubset(wset),"after site generation, the addition of directories to www was not correct.")

    def test_do_rename_should_create_new_pagedir_in_source(self):
        # init site
        site = s2site.Site(self.temp_dir)
        site.init_structure()
        # add random page
        p = site.random_page()
        newtitle = "This will be the new title of the page."
        args = self.parser.parse_args(['rename', p.slug, newtitle, '-d', self.temp_dir])
        argdict = vars(args)
        s2.dispatch(argdict)  #this triggers call to do_rename
        # verify that the page is there
        self.assertTrue(site.page_exists_on_disk(util.make_slug(newtitle)),"new page directory does not exist after rename.")
        # and that the old page is not there.
        #Maybe it's a little unorthodox to do another assert in the same test... but it's for brevity
        self.assertFalse(site.page_exists_on_disk(p.slug),"old page still exists after rename.")

if __name__ == "__main__":
    unittest.main()