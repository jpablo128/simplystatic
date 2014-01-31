# -*- coding: utf-8 -*-

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

from simplystatic import s2site
from simplystatic import s2page
from simplystatic import util


class TestInstantiationWriteExistsLoad(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.site = s2site.Site(self.temp_dir)
        self.site.init_structure()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # __init__(self, site, ptitle, isslug=False):
    # inst stands for instantiation
    def test_inst_withSlug_nonExitentPage_should_raise_valueError(self):
        self.assertRaises(ValueError,s2page.Page,self.site,"this_is_my_title",isslug=True)

    def test_inst_noSlug_should_create_page(self):
        p = s2page.Page(self.site,"This is a new page")
        self.assertIsInstance(p,s2page.Page,"Page instantiation did not create a page object.")

    def test_write_should_create_file(self):
        p1 = s2page.Page(self.site,"This is a new page")
        p1.write()
        self.assertTrue( os.path.isdir(p1.dirs['source_dir']) and \
                         os.path.isfile(p1.dirs['source_filename']),
                         "No directory and/or file created after page write.")

    def test_inst_noSlug_pageExists_should_raise_valueError(self):
        p1 = s2page.Page(self.site,"This is a new page")
        p1.write()
        self.assertRaises(ValueError,s2page.Page,self.site,"This is a new page")

# I use a new class because I'm going to use the same setUp for several tests.
class TestInstRenderAndGenerate(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.site = s2site.Site(self.temp_dir)
        self.site.init_structure()
        #first create a page
        self.p1title = "This is a new page" 
        self.p1slug = util.make_slug(self.p1title)
        self.p1 = s2page.Page(self.site,self.p1title)
        content = util.random_text()
        self.p1.content = content

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_inst_slug_pageExists_should_load_page(self):
        self.p1.write()
        p2 = s2page.Page(self.site,self.p1slug,isslug=True)
        self.assertEqual(p2.content,'\n'+self.p1.content+'\n',"Page content is not correct after loading page.")

    def test_render_should_return_string_or_unicode(self):
        r = self.p1.render()
        self.assertTrue(isinstance(r,unicode) or isinstance(r,str),
                          "render did no return a unicode string.")

    def test_render_should_return_same_rendition_after_write(self):
        r1 = self.p1.render()
        self.p1.write()
        p2 = s2page.Page(self.site,self.p1slug,isslug=True)
        r2 = p2.render()
        self.assertEqual(r1,r2,"render gave different rendition after reading from file.")

    def test_generate_should_create_directory_in_www(self):
        self.p1.set_published()
        #self.p1.write()  #not necessary here to write the source...
        os.mkdir(self.p1.dirs['www_dir']) #just to force coverage of line 211 in s2page.py
        self.p1.generate()
        flist = glob.glob(os.path.join(self.site.dirs['www'],"*"))
        self.assertTrue(self.p1.dirs['www_dir'] in flist,'wpage directory not created after generate')

    
    # test generate should copy all other pages and dirs in the page directory, except those in a 
    # especially named folder!
    def test_generate_should_copy_files_to_target_wdir(self):
        '''Verify that all files and directories (except the directory
        called 'nowww' and the page .md file ) are copied from the
        page source to the corresponding page www directory. 
        This test is more complex because it generates random files and then 
        verifies that the structure in the generated directory is the same
        as in the source, except for those 2 things. 

        '''
        self.p1.set_published()
        self.p1.write()
        # add a random number of random files and dirs in the page source directory
        for i in range(0,random.randrange(5,21)):
            fname = uuid.uuid1().hex[0:9]
            if random.random() > 0.2:
                fname = os.path.join(self.p1.dirs['source_dir'],'staticfile_' + fname)
                open(fname,'w').close()
            else:
                fname = os.path.join(self.p1.dirs['source_dir'],'staticdir_' + fname)
                os.mkdir(fname)
        # make a nowww dir
        os.mkdir(os.path.join(self.p1.dirs['source_dir'],'nowww'))
        # aux function to walk dirs
        def vis(cflist,dirname,names):
            for n in names:
                if n != 'nowww' and not '.md' in n:
                    fcp = os.path.join(dirname,n)
                    cflist.append( fcp )
        self.p1.generate()
        csourcelist = []
        cwwwlist = []
        os.path.walk(self.p1.dirs['source_dir'],vis,csourcelist)  
        os.path.walk(self.p1.dirs['www_dir'],vis,cwwwlist)  
        # remove basedir + source from csourcelist, and basedir+source from cwwwlist
        startchar = len(self.site.dirs['source']) + 1
        csourcelist = [ fn[startchar:] for fn in csourcelist]
        startchar = len(self.site.dirs['www']) + 1
        cwwwlist = [ fn[startchar:] for fn in cwwwlist]
        # remove the <page_name>/<generated_html_file> element from cwwwlist
        ghtmlfile = os.path.join(os.path.split(self.p1.dirs['source_dir'])[1] , os.path.split(self.p1.dirs['www_filename'])[1] )
        cwwwlist.remove(ghtmlfile)
        csourceset = set(csourcelist)
        cwwwset = set(cwwwlist)
        #print str(cwwwset) + '\n'
        #print csourceset
        self.assertEqual(cwwwset.difference(csourceset),set([]),"after generate, not all the files are in the page www directory.")


    def test_rename_with_existing_title_should_raise_ValueError(self):
        self.p1.write()
        newpagetitle = "Some new page here"
        #newpageslug = util.make_slug(newpagetitle)
        p2 = s2page.Page(self.site,newpagetitle,isslug=False)
        p2.write()
        #try to rename p1 and give it the same title as p2
        self.assertRaises(ValueError,self.p1.rename,newpagetitle)

    def test_rename_nonstring_newtitle_should_raise_TypeError(self):
        self.p1.write()
        self.assertRaises(TypeError,self.p1.rename,3)
        self.assertRaises(TypeError,self.p1.rename,4.2)
        self.assertRaises(TypeError,self.p1.rename,[1,'a',5.2])
        self.assertRaises(TypeError,self.p1.rename,{})
        self.assertRaises(TypeError,self.p1.rename,{'1':'a','2':'b'})

    def test_rename_new_sourcedir_shoud_exist_in_source(self):
        self.p1.write()
        newpagetitle = "Some new page here"
        newpageslug = util.make_slug(newpagetitle)
        self.p1.rename(newpagetitle)
        self.assertTrue(self.site.page_exists_on_disk(newpageslug),"The new page slug does not exist in source after rename.")
        #if the dir exists, the file exists. exists_on_disk checks both

    def test_rename_old_sourcedir_shoud_not_exist_in_source(self):
        self.p1.write()
        oldpageslug = self.p1slug
        newpagetitle = "Some new page here"
        newpageslug = util.make_slug(newpagetitle)
        self.p1.rename(newpagetitle)
        self.assertFalse(self.site.page_exists_on_disk(oldpageslug),"The old page slug still exists in source after rename.")

    def test_rename_content_should_be_the_same(self):
        self.p1.write()
        oldcontent = self.p1.content
        oldpageslug = self.p1slug
        newpagetitle = "Some new page here"
        newpageslug = util.make_slug(newpagetitle)
        self.p1.rename(newpagetitle)
        newcontent = self.p1.content
        self.assertEqual(newcontent,oldcontent,"The content of the page has changed after rename.")


class TestVariousGetAndSet(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.site = s2site.Site(self.temp_dir)
        self.site.init_structure()
        #first create a page
        self.p1title = "This is a new page" 
        self.p1slug = util.make_slug(self.p1title)
        self.p1 = s2page.Page(self.site,self.p1title)
        content = util.random_text()
        self.p1.content = content

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_set_published_and_write_read_again_should_read_correct_status(self):
        self.p1.set_published()
        self.p1.write()
        p2 = s2page.Page(self.site,self.p1slug,isslug=True)
        self.assertTrue(p2.published,"after setting status to published, write, and then read, status was not published.")

    def test_set_date_with_no_datetime_pamar_should_raise_error(self):
        #need auxiliary callable to test setter
        def run_test():
            self.p1.creation_date="3/3/70"
        self.assertRaises(TypeError, run_test)

    def test_set_date_read_date_should_be_same_as_written_date(self):
        #need auxiliary callable to test setter
        d = util.random_date()
        self.p1.creation_date = d
        self.p1.write()
        p2 = s2page.Page(self.site,self.p1slug,isslug=True)
        self.assertEqual(p2.creation_date,d.isoformat(),"read date was not the same as written date.")

    def test_set_tags_with_non_array_argument_should_raise_typeError(self):
        #need auxiliary callable to test setter
        def run_test():
            self.p1.tags = "hello"
        self.assertRaises(TypeError, run_test)

    def test_set_tags_read_tags_should_be_same_as_written_tags(self):
        #need auxiliary callable to test setter
        t = [u'elearning',u'arduino',u'tincan']
        self.p1.tags = t
        self.p1.write()
        p2 = s2page.Page(self.site,self.p1slug,isslug=True)
        self.assertEqual(p2.tags,t,"read tags were not the same as written tags")



if __name__ == "__main__":
     unittest.main()
