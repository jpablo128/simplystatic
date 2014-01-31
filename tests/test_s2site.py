#!/usr/bin/python

import sys
import unittest
import os
import random
import tempfile
import shutil
import stat
import glob
import string
import yaml
import datetime
import uuid
import types
import math

from simplystatic import s2site
from simplystatic import s2page
from simplystatic import util

# GLOBAL AUXILIARY FUNCTIONS for the tests #
def set_directory_writability(dir_name,writable=False):
    fperms = stat.S_IMODE(os.lstat(dir_name)[stat.ST_MODE])
    if writable:
        fperms = fperms | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    else:
        fperms = fperms & ~stat.S_IWUSR & ~ stat.S_IWGRP & ~stat.S_IWOTH
    os.chmod(dir_name,fperms)

def random_path(depth=3):
    pcs = []
    for i in range(0,depth+1):
        pcs.append(util.make_slug(util.random_title()))
    rp = '/'.join(pcs)
    return rp

def create_random_folders(startdir,depth=4,randombase=True):
    '''Creates a random sequence of folders, and marks one of them as base.'''
    rp = random_path(depth)
    plst = rp.split('/')
    newpath = startdir
    for p in plst:
        ptc = os.path.join(newpath,p)
        os.mkdir(ptc)
        newpath = ptc
    fullpath = newpath
    plst = fullpath.split('/')
    plst = plst[3:-2]
    basepath = ''
    if randombase:
        rb = random.choice(plst)
        idx = plst.index(rb)
        plst = plst[0:idx+1]
        basepath = os.path.join(startdir,'/'.join(plst) ) 
        os.mkdir(os.path.join(basepath,'.s2'))
    return {'fullpath':fullpath,'basepath':basepath}


# END GLOBAL AUXILIARY FUNCTIONS #

class TestVerifyDirStructure(unittest.TestCase):
    def setUp(self):
        # create fake tempdir with the structure
        temp_dir = tempfile.mkdtemp()
        self.dirs = ['.s2', 'source', 'www', 'common','themes']
        self.base_dir = temp_dir
        self.s2_dir = os.path.join(temp_dir,'.s2')
        self.source_dir = os.path.join(temp_dir,'source')
        self.www_dir = os.path.join(temp_dir,'www')
        self.common_dir =  os.path.join(temp_dir,'common')
        self.themes_dir =  os.path.join(temp_dir,'themes')
        os.mkdir(self.s2_dir)
        os.mkdir(self.source_dir)
        os.mkdir(self.www_dir)
        os.mkdir(self.common_dir)
        os.mkdir(self.themes_dir)

    def tearDown(self):
        shutil.rmtree(self.base_dir)

    def test_verify_dir_structure_inexistent_dir_should_return_false(self):
        rp = random_path()
        self.assertFalse(s2site.verify_dir_structure(rp), 
                       'verify_tree_structure did not return False on an inexistent random directory')

    def test_verify_dir_structure_on_writable_complete_s2dir_should_return_true(self):
        self.assertTrue(s2site.verify_dir_structure(self.base_dir), 
                       'verify_tree_structure did not return true on a writable complete s2 dir.')

    def test_verify_dir_structure_on_writable_incomplete_s2dir_should_return_false(self):
        # rename each dir in turn, and assess the call
        for d in self.dirs:
            fp = os.path.join(self.base_dir,d)
            ffp = fp + 'x'
            shutil.move(fp,ffp)
            self.assertFalse(s2site.verify_dir_structure(self.base_dir), 
                             'verify_tree_structure did NOT return False on a writable incomplete s2 dir.')

    def test_verify_dir_structure_on_nonwritable_complete_s2dir_should_return_false(self):
        # rename each dir in turn,set non-writable and assess the call
        for d in self.dirs:
            fp = os.path.join(self.base_dir,d)
            set_directory_writability(fp,False)
            self.assertFalse(s2site.verify_dir_structure(self.base_dir), 
                             'verify_tree_structure did NOT return False on a non-writable complete s2 dir.')

    def test_verify_dir_structure_on_nonwritable_incomplete_s2dir_should_return_false(self):
        #just test one case, it's enough. Make one dir non writeable, and rename another one
        fp = os.path.join(self.base_dir,'www')
        set_directory_writability(fp,False)
        fp = os.path.join(self.base_dir,'common')
        ffp = fp + 'x'
        shutil.move(fp,ffp)
        self.assertFalse(s2site.verify_dir_structure(self.base_dir), 
                             'verify_tree_structure did NOT return False on a non-writable incomplete s2 dir.')

class TestVariousDirFunctions(unittest.TestCase):

    def test_dir_param_nostring_should_raise_typeerror(self):
        self.assertRaises(TypeError,s2site.dir_param_valid,3)
        self.assertRaises(TypeError,s2site.dir_param_valid,4.2)
        self.assertRaises(TypeError,s2site.dir_param_valid,[1,'a',5.2])
        self.assertRaises(TypeError,s2site.dir_param_valid,{})
        self.assertRaises(TypeError,s2site.dir_param_valid,{'1':'a','2':'b'})

    def test_dir_param_invalid_dir_should_raise_valueerror(self):
        rp = random_path()
        self.assertRaises(ValueError,s2site.dir_param_valid,rp)

    def test_dir_empty_with_empty_dir_should_return_true(self):
        temp = tempfile.mkdtemp()
        self.assertTrue(s2site.dir_empty(temp), 'dir_empty did not return True with empty dir.')
        shutil.rmtree(temp)

    def test_dir_empty_with_nonempty_dir_should_return_false(self):
        temp = tempfile.mkdtemp()
        f = open(os.path.join(temp,'afile.txt'),'w')
        f.write('some text')
        f.close()
        self.assertFalse(s2site.dir_empty(temp), 'dir_empty did not return False with non-empty dir.')
        shutil.rmtree(temp)

    def test_is_base_dir_with_s2marked_dir_should_return_true(self):
        temp = tempfile.mkdtemp()
        os.mkdir(os.path.join(temp,'.s2'))
        self.assertTrue(s2site.is_base_dir(temp), 'is_base_dir did not return True with s2-marked dir.')
        shutil.rmtree(temp)

    def test_is_base_dir_with_no_s2marked_dir_should_return_false(self):
        temp = tempfile.mkdtemp()
        self.assertFalse(s2site.is_base_dir(temp), 'is_base_dir did not return False on an empty dir.')
        shutil.rmtree(temp)

    # TEST discover_base_dir
class TestDiscoverBaseDir(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    #dbd is short for discover_base_dir
    def test_dbd_on_nonstring_dir_should_raise_typeError(self):
        self.assertRaises(TypeError,s2site.discover_base_dir,5)
        self.assertRaises(TypeError,s2site.discover_base_dir,{'a':3})
        self.assertRaises(TypeError,s2site.discover_base_dir,(3,2))
        self.assertRaises(TypeError,s2site.discover_base_dir,2.8)
        self.assertRaises(TypeError,s2site.discover_base_dir,[1, 2, 3])

    def test_dbd_on_nonexistent_dir_should_raise_valueError(self):
        self.assertRaises(ValueError,s2site.discover_base_dir,random_path())

    def test_dbd_initialdir_is_real_basedir_should_return_initialdir(self):
        temp_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(temp_dir,'.s2'))
        self.assertEqual(s2site.discover_base_dir(temp_dir),temp_dir,'discover_base_dir did not return the start dir when it was a true base dir.')
        shutil.rmtree(temp_dir)

    def test_dbd_initialdir_is_nonbase_and_no_base_upwards_should_return_Empty(self):
        temp_dir = tempfile.mkdtemp()
        #check id there's an .s2, remove it...
        if os.path.isdir(os.path.join(temp_dir,'.s2')):
            shutil.rmtree(os.path.join(temp_dir,'.s2'))
        dtd = s2site.discover_base_dir(temp_dir)
        self.assertEqual(dtd,None,'discover_base_dir not return empty string when initial_dir was NOT base, but had no base dir up the chain.')
        shutil.rmtree(temp_dir)

    def test_dbd_initialdir_is_nonbase_but_a_parent_is_base_should_return_thebase(self):
        temp_dir = tempfile.mkdtemp()
        rfr = create_random_folders(temp_dir,4,True)
        self.assertEqual(s2site.discover_base_dir(rfr['fullpath']),rfr['basepath'],'discover_base_dir not return the correct base_dir.')
        shutil.rmtree(temp_dir)


class TestInstantiation(unittest.TestCase):

    def setUp(self):
        # create fake tempdir with the structure
        temp_dir = tempfile.mkdtemp()
        self.dirs = ['.s2', 'source', 'www', 'common','themes']
        self.base_dir = temp_dir
        self.s2_dir = os.path.join(temp_dir,'.s2')
        self.source_dir = os.path.join(temp_dir,'source')
        self.www_dir = os.path.join(temp_dir,'www')
        self.common_dir =  os.path.join(temp_dir,'common')
        self.themes_dir =  os.path.join(temp_dir,'themes')
        
        pkg_dir, pkg_filename = os.path.split(s2site.__file__)
        self.themes_dirinfo  = os.path.join(pkg_dir,'themes')

        os.mkdir(self.s2_dir)
        os.mkdir(self.source_dir)
        os.mkdir(self.www_dir)
        os.mkdir(self.common_dir)
        os.mkdir(self.themes_dir)

    def tearDown(self):
        shutil.rmtree(self.base_dir)

    def test_init_site_without_params_should_set_tree_ready_to_false_when_called_from_non_s2dir(self):
        s = s2site.Site()
        self.assertFalse(s.tree_ready,"tree_ready is False after initialization with no dir in non-s2 dir.")

    def test_init_site_without_params_should_set_run_dir_to_CWD(self):
        s = s2site.Site()
        self.assertEqual(s.dirs['run'],os.getcwd(),"run dir is not set to CWD after initialization with no dir.")

    def test_init_site_with_initial_is_base_should_set_tree_ready_to_true(self):
        s = s2site.Site(self.base_dir)
        self.assertTrue(s.tree_ready,"tree_ready is NOT True after initialization with a real base dir.")

    def test_init_site_with_initial_is_under_real_base_should_set_tree_ready_to_true(self):
        s = s2site.Site(self.www_dir)
        self.assertTrue(s.tree_ready,"tree_ready is NOT True after initialization with a dir that is under a real base dir.")

    def test_init_site_with_nonexistent_initial_should_raise_valueError(self):
        self.assertRaises(ValueError,s2site.Site,random_path())

    def test_init_site_with_initial_is_under_real_base_should_set_correct_dirs(self):
        s = s2site.Site(self.www_dir)
        self.assertTrue(s.dirs['base'] == self.base_dir and \
                        s.dirs['source'] == self.source_dir and \
                        s.dirs['www'] == self.www_dir and \
                        s.dirs['common'] == self.common_dir and \
                        s.dirs['s2'] == self.s2_dir,
            "One or more of the dirs set up after creating site are not correct.")


class TestInitStructure(unittest.TestCase):

    def setUp(self):
        # create fake tempdir with the structure
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # _inst_ stands for init_structure
    def test_inst_on_nonempty_path_should_raise_valueError(self):
          #put something in the temp_dir
        fout = open(os.path.join(self.temp_dir,'afile'),'w')
        fout.close()
        s = s2site.Site(self.temp_dir)
        self.assertRaises(ValueError,s.init_structure)

    def test_inst_on_nonwritable_path_should_raise_valueError(self):
        # make temp_dir nonwritable
        set_directory_writability(self.temp_dir,writable=False)
        s = s2site.Site(self.temp_dir)
        self.assertRaises(ValueError,s.init_structure)

    def test_inst_on_ok_path_should_create_all_subdirs(self):
        s = s2site.Site(self.temp_dir)
        s.init_structure()
        allf = glob.glob(os.path.join(self.temp_dir,"*"))
        allf += glob.glob(os.path.join(self.temp_dir,".*"))
        dirlist = [f for f in allf if os.path.isdir(f)] #filter for dirs
        dirlist = [os.path.split(d)[1] for d in dirlist ] #remove leading path
        self.assertTrue( 'www' in dirlist and \
                         '.s2' in dirlist and \
                         'common' in dirlist and \
                         'source' in dirlist ,
                          "init_structure did not create all the necessary subdirectories.")

    def test_inst_on_ok_path_should_not_create_extraneous_subdirs(self):
        s = s2site.Site(self.temp_dir)
        s.init_structure()
        allf = glob.glob(os.path.join(self.temp_dir,"*"))
        allf += glob.glob(os.path.join(self.temp_dir,".*"))
        dirlist = [f for f in allf if os.path.isdir(f)] #filter for dirs
        dirset = set([os.path.split(d)[1] for d in dirlist ]) #remove leading path
        expectedset = set(['www','.s2', 'common', 'source','themes'])
        self.assertEqual(dirset.difference(expectedset),set([]),"init_structure created some extraneous subdirectories.")

    def test_inst_should_copy_data_dirs(self):
        pdl = s2site.package_data_location()
        pddirlist = glob.glob(os.path.join(pdl,"*"))
        pddirset = set([os.path.split(d)[1] for d in pddirlist])
        s = s2site.Site(self.temp_dir)
        s.init_structure()
        strucfilelist = glob.glob(os.path.join(s.dirs['base'],"*"))
        strucfileset = set( [os.path.split(d)[1] for d in strucfilelist] )
        self.assertTrue(pddirset.issubset(strucfileset),"init_structure did not copy the package data dirs.")

    def test_inst_should_add_default_config(self):
        s = s2site.Site(self.temp_dir)
        s.init_structure()
        sfs = glob.glob(os.path.join(s.dirs['s2'],"*"))
        sfs = [os.path.split(p)[1] for p in sfs]
        self.assertTrue('config.yml' in sfs,"init_structure did not create the config file.")

class TestGetPageNames(unittest.TestCase):
    def setUp(self):
        # create fake tempdir with the structure
        self.temp_dir = tempfile.mkdtemp()
        self.s2 = s2site.Site(self.temp_dir)
        self.s2.init_structure()
        # create a bunch of fake pages
        pgs = []
        for i in range(0,11):
            pg = util.make_slug(util.random_title())
            pgs.append(pg)
            pgfp = os.path.join(self.s2.dirs['source'],pg)
            os.mkdir(pgfp)
            fname = os.path.join(pgfp,pg) + '.s2md'
            fout = open(fname,'w')
            fout.close()
        self.pages = pgs

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_gpn_should_return_correct_names(self):
        realset = set(self.s2.get_page_names())
        expectedset = set(self.pages)
        self.assertEqual(realset.difference(expectedset),set([]),"get_page_name did not return the correct page list.")


class TestPages(unittest.TestCase):

    def setUp(self):
        # create fake tempdir with the structure
        self.temp_dir = tempfile.mkdtemp()
        self.s2 = s2site.Site(self.temp_dir)
        self.s2.init_structure()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # gpn stands for get page names
    # well, some of these tests depend on s2page functioning correctly...

    # peod stands for page_exists_on_disk
    def test_peod_on_existing_page_should_return_true(self):
        title = "This is a new page" 
        slug = util.make_slug(title)
        p1 = s2page.Page(self.s2,title)
        p1.write()
        self.assertTrue(self.s2.page_exists_on_disk(slug),"page_exists_on_disk returned False on existing page.")

    def test_peod_on_nonexisting_page_should_return_false(self):
        title = "This is a new page" 
        slug = util.make_slug(title)
        #p1 = s2page.Page(self.s2,title)
        # we DO NOT write it, so it doesn't exist!
        self.assertFalse(self.s2.page_exists_on_disk(slug),"page.exists returned True on a non-existing page.")


    def test_random_page_should_return_s2page(self):
        p = self.s2.random_page()
        self.assertIsInstance(p,s2page.Page,"random_page is not returning an s2page Page object.")

    def test_add_page_should_return_s2page(self):
        title = "This is a new page" 
        p1 = self.s2.add_page(title)
        self.assertIsInstance(p1,s2page.Page,"add_page is not returning an s2page Page object.")


class TestGenerateAndRename(unittest.TestCase):

    def setUp(self):
        # create fake tempdir with the structure
        self.temp_dir = tempfile.mkdtemp()
        self.s2 = s2site.Site(self.temp_dir)
        self.s2.init_structure()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_generate_should_wipe_www_and_create_pages_in_www(self):
        # create a bunch of random pages, make them published.
        for i in range(0,random.randint(21,51)):
            p = self.s2.random_page() 
            p.set_published()
            p.write()
        slist = glob.glob(os.path.join(self.s2.dirs['source'],'*'))
        slist = [f for f in slist if os.path.isdir(f) ] #keep only directories
        sset = set([os.path.split(f)[1] for f in slist])
        # generate, and see whether the dirs created in www are the same
        self.s2.generate()
        # let's call generate again... it should wipe the existing contents of wwwc
        self.s2.generate()
        wlist = glob.glob(os.path.join(self.s2.dirs['www'],'*'))
        wset = set([os.path.split(f)[1] for f in wlist])
        self.assertEqual(sset.difference(wset),set([]),"generate did not create the right files in www.")

    # TEST generate should copy the common dir 
    def test_generate_should_copy_common_dir_to_www(self):
        '''Verify that all files and directories in common are copied 
        to the root of www. 
        This test is more complex because it generates random files and then 
        verifies that the structure in the www directory (excluding all the 
        "page directories") is the same as the structure in "common"

        '''
        # add a random number of random files and directories in the common directory
        commonfileslist = [] #save list of generated files/dirs for later
        for i in range(0,random.randrange(15,41)):
            fname = uuid.uuid1().hex[0:9]
            if random.random() > 0.2:
                fname = os.path.join(self.s2.dirs['common'],'sfile_' + fname)
                open(fname,'w').close()
            else:
                fname = os.path.join(self.s2.dirs['common'],'sdir_' + fname)
                os.mkdir(fname)
            commonfileslist.append(os.path.split(fname)[1])
        # aux function to walk dirs
        def vis(cflist,dirname,names):
            for n in names:
                if n != 'nowww' and not '.s2md' in n:
                    fcp = os.path.join(dirname,n)
                    cflist.append( fcp )

        # create a bunch of random source pages
        for i in range(0,random.randint(21,51)):
            self.s2.random_page()  #generate, write, and forget
        self.s2.generate()
        wfileslist = glob.glob(os.path.join(self.s2.dirs['www'],'*'))
        wfilesset = set([os.path.split(f)[1] for f in wfileslist])
        commonfilesset = set(commonfileslist)
        self.assertTrue(commonfilesset.issubset(wfilesset),"after generate, common files are not correctly copied to www.")

    def test_rename_page_should_create_correct_data_in_sourcedir(self):
        title = "This is a new page" 
        slug = util.make_slug(title)
        p = s2page.Page(self.s2,title)
        p.write()
        new_title = "This HELLO dude will be the new name"
        self.s2.rename_page(slug,new_title)
        slist = self.s2.get_page_names()
        self.assertTrue(util.make_slug(new_title) in slist,"The new name does not exist in the source.")

class TestFrontMatter(unittest.TestCase):
    def setUp(self):
       # create fake tempdir with the structure
        self.temp_dir = tempfile.mkdtemp()
        self.site = s2site.Site(self.temp_dir)
        self.site.init_structure()
        self.ntg = random.randint(8,100)
        self.gpi= []
        for i in range(0,self.ntg):
            title = util.random_title()
            self.gpi.append( { 'slug': util.make_slug(title),
                          'title': title,
                          'date': util.random_date()}
                      )   
        self.epp = random.randint(5,self.ntg)
        self.correctnumpag = math.ceil(float(self.ntg)/self.epp)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # rfcp stands for renderfront_chronological_plain
    def test_rfp_should_return_iterator(self):
        gpi = [ { 'slug': "slug1", 'title': "title1", 'date': util.random_date()}, 
                { 'slug': "slug2", 'title': "title2", 'date': util.random_date()}, 
                { 'slug': "slug3", 'title': "title3", 'date': util.random_date()}, 
                { 'slug': "slug4", 'title': "title4", 'date': util.random_date()}, 
                { 'slug': "slug5", 'title': "title5", 'date': util.random_date()}
              ]
        r = self.site.renderfront_chronological_plain(gpi,2)
        self.assertIsInstance(r,types.GeneratorType,"renderfront_chronological_page did not return an iterator.")
        # for p in r:
        #    print p

    def test_rfp_should_return_correct_number_of_pages(self):
        r = self.site.renderfront_chronological_plain(self.gpi,self.epp)
        i = 0
        for p in r:
            i += 1
        self.assertEqual(i,self.correctnumpag,"renderfront_chronological_page did not return the correct number of pages.")

    def test_generate_front_should_create_correct_set_of_files(self):
        eflist = ['index.html'] # expected file list
        for i in range (2,int(self.correctnumpag)+1):
            eflist.append( str(i)+'.html')
        efset = set(eflist)

        self.site.generate_front(self.gpi,self.epp)
        rflist = glob.glob(os.path.join(self.site.dirs['www'],"*.html"))
        rflist = [os.path.split(f)[1] for f in rflist]
        rfset = set(rflist)
        self.assertEqual(rfset,efset,"generate_front did not create the right set of front-matter files.")

if __name__ == "__main__":
     unittest.main()
