# -*- coding: utf-8 -*-
'''This module provides funtionality for managing the site.

Classes included:

    - Site: Manages creation of the site structure, generation, etc.

'''

import os
import sys
import os.path
import shutil
import glob
import math
import tempfile
import codecs
from datetime import datetime

import yaml
from mako.template import Template
from pyatom import AtomFeed


#from .simplystatic import s2page
#from .simplystatic import util
import s2page
import util

PREDEFINED_DIR_NAMES = ['s2', 'www', 'source', 'common', 'themes']

def verify_dir_structure(full_path):
    '''Check if given directory to see if it is usable by s2.

    Checks that all required directories exist under the given 
    directory, and also checks that they are writable.

    '''
    if full_path == None:
        return False
    r = True
    for d2c in PREDEFINED_DIR_NAMES:
        #if d2c == "s2":
        #    d2c = ".s2"
        cp2c = os.path.join(full_path, d2c)  #complete path to check
        if not os.path.isdir(cp2c):
            r = False
            break
        else:  #exists, let's check it's writable
            if not os.access(cp2c, os.W_OK): 
                r = False
                break
    return r

def dir_param_valid(d):
    '''True if d is a string and it's an existing directory.'''
    r = True
    if not isinstance(d, str) :
        r = False
        raise TypeError
    if not os.path.isdir(d):
        r = False
        raise ValueError
    return r

def dir_empty(d):
    '''Return True if given directory is empty, false otherwise.'''
    flist = glob.glob(os.path.join(d,'*'))
    return (len(flist) == 0)

def is_base_dir(d):
    '''True if the dir is valid and it contains a dir called s2'''
    if not dir_param_valid(d): # pragma: no cover
        raise 
    else:
        mfn = os.path.join(d,'s2') #marker name. it must be a directory.
        return os.path.isdir(mfn)

def discover_base_dir(start_dir):
    '''Return start_dir or the parent dir that has the s2 marker.

    Starting from the specified directory, and going up the parent
    chain, check each directory to see if it's a base_dir (contains
    the "marker" directory *s2*) and return it. Otherwise, return
    the start_dir.

    '''
    if is_base_dir(start_dir):
        return start_dir
    pcl = start_dir.split('/')  #path component list
    found_base_dir = None
    for i in range(1, len(pcl)+1):
        d2c = '/'.join(pcl[:-i])
        if (d2c == ''):
            d2c = '/'
        if is_base_dir(d2c):
            found_base_dir = d2c
            break
    return found_base_dir

# def write_page(p):
#     '''Write the given page to disk.

#     Just a convenience method to allow the Site to write a page.'''
#     p.write()

def package_data_location():
    '''Get the locations of themes distributed with this package.

    Just finds if there are templates, and returns a dictionary with
    the corresponding values.

    '''
    pkg_dir = os.path.split(__file__)[0]
    pkg_data_dir = os.path.join(pkg_dir,'data')
    return pkg_data_dir

class Site(object):
    '''Represent the structure of the site and provide basic management.

    The structure of the site is pretty much fixed, being:
        <base site directory>
            source
            common
            themes
            www
            s2

    When an instance of this class is initialized the caller can 
    specify an initial directory, which is what we've called 
    <site directory>. If specified, the directory must exist. Under this
    directory there will eventually exist five other directories:

        - s2:    It is empty. This directory is just a "marker" that is
                  automatically created when the site structure is 
                  initialized.

        - source: Contains one directory for each "page" of the site.
                  Also, it may contain one or more Mako templates, that
                  specify the overall structure of the html page.
                  Each "page" of the site has its own directory because
                  -obviously- a "page" might need many different files.
                  The main source file for the page is a markdown file
                  whose name ends with "s2md" (simply common markdown).
                  Other files (such as images, javascript or CSS) that
                  are specific to this "page" must be placed in the
                  corresponding page directory. Files that will be used
                  by more than one page should be placed in the *common*
                  directory.
                  When the site is generated, the structure in *www*
                  will reflect the structure in *source*. The *s2md* 
                  file will be manipulated by the system to generate an
                  html page, but the rest of the files will be just 
                  copied over.

        - common: Contains files that must be copied directly to the 
                  generated site, such as images, javascript files and
                  libraries, CSS files, etc. that are common to the 
                  whole site.

        - themes: Contains directories with the themes available for the
                  site.

        - www:    Contains the generated static site. This directory is 
                  wiped off every time the site is generated. 

    It is recommended to put the whole site directory under version
    control.

    '''

    def __init__(self, initial_dir=None):  # I WOULD NEED default theme and default template here
        '''Initialize variables with path information.

        Keyword arguments:

        - initial_dir: Specify an initial dir. 
                       If it is not empty, it will be assigned to the
                       instance variable base_dir. If it is empty, the
                       program will try to find a "base_dir" (a 
                       directory that has the s2 directory marker)
                       starting from the current working directory
                       upwards.

        This method is called upon initialization, and it sets several
        variables with *absolute* paths that are used frequently. 

        The initialization will trigger a call to set_directories, which
        in turn might trigger the auto-discovery of the structure. 

        '''
        self._predefined_dir_names = PREDEFINED_DIR_NAMES
        self._dirs = {'initial': initial_dir,
                      'run': os.getcwd()
                     }
        for dn in self._predefined_dir_names:
            self._dirs[dn] = None

        self._tree_ready = None

        self._set_directories()
        if self._tree_ready:
            self.site_config = self._read_site_config()
        #makodir is the directory where mako will cache the rendered templates
        self._makodir = tempfile.mkdtemp()

    def _set_directories(self):
        '''Initialize variables based on evidence about the directories.'''
        if self._dirs['initial'] == None:
            self._dirs['base'] = discover_base_dir(self._dirs['run'])  
        else:
            self._dirs['base'] = discover_base_dir(self._dirs['initial'])  
        # now, if 'base' is None (no base directory was found) then the only
        # allowed operation is init 
        self._update_dirs_on_base()
        # we might have set the directory variables fine, but the tree
        # might not exist yet. _tree_ready is a flag for that.
        self._tree_ready = verify_dir_structure(self._dirs['base'])
        if self._tree_ready:
            self._read_site_config()

    def _update_dirs_on_base(self):
        '''Fill up the names of dirs based on the contents of 'base'.'''
        if self._dirs['base'] != None:
            for d in self._predefined_dir_names:
                dstr = d
                #if d == "s2":
                #    dstr = '.'+d
                self._dirs[d] = os.path.join(self._dirs['base'], dstr) 
            # self._dirs['s2'] = os.path.join(self._dirs['base'],'s2')
            # self._dirs['www'] = os.path.join(self._dirs['base'],'www')
            # self._dirs['source'] = os.path.join(self._dirs['base'],'source')
            # self._dirs['common'] = os.path.join(self._dirs['base'],'common')
            # self._dirs['themes'] = os.path.join(self._dirs['base'],'themes')

    def init_structure(self):
        '''Initialize a directory to serve as a Simply Static site.

        Initialization is done on the base_dir (base_dir is set upon
        __init__, so it has a value when this method is called), and it
        is only performed if base_dir is empty and it is writeable.

        This operation creates the directories, copies any existing 
        templates to the source_dir and common_dir, and creates the 
        default configuration file within the directory s2

        '''
        if self._dirs['base'] != None:  # pragma: no cover 
            #there's a base here or up the chain
            raise ValueError   #cannot initialize
        else:
            if self._dirs['initial'] != None: # pragma: no cover
                self._dirs['base'] = self._dirs['initial']
            else:  # pragma: no cover
                self._dirs['base'] = self._dirs['run']
            #now proceed
            self._update_dirs_on_base()
            if (not dir_empty(self._dirs['base']) ) or  \
               (not os.access(self._dirs['base'], os.W_OK)):
                raise ValueError
            
            # copy the dirs from package data to the base dir (common,themes)
            pdl = package_data_location()
            datadirs = glob.glob(os.path.join(pdl,"*"))
            for dd in datadirs:
                if os.path.isdir(dd):
                    shutil.copytree(dd, os.path.join(self._dirs['base'],
                                    os.path.split(dd)[1]))
            # create all predefined dirs that don't exist yet in base
            for d in self._dirs:
                if not d in ['initial', 'run', 'base']:
                    if not os.path.isdir(self._dirs[d]):
                        os.mkdir(self._dirs[d])
            self._tree_ready = verify_dir_structure(self._dirs['base']) 
            self.site_config = self._create_default_config()

    def get_page_names(self):
        '''Return a list of page names (directories) under source_dir.'''
        fis = [p  for p in glob.glob(os.path.join(self._dirs['source'], \
                                     "*")) if os.path.isdir(p)]
        fis = [os.path.split(p)[1] for p in fis ]
        return fis
    #  generate should copy the common dir to www

    def _wipe_www_dir(self):
        wlist = glob.glob(os.path.join(self.dirs['www'], "*"))
        for fo in wlist:
            if os.path.isdir(fo):
                shutil.rmtree(fo)
            else:
                os.remove(fo)

    def generate(self):
        '''Generate the whole static site.

        Iterates through all existing s2 pages, rendering and writing
        them (and copying all common files along). 
        It also generates the toc, a sitemap, and the atom feed
        etc. (in the future it should handle tags and categories)

        '''
        if self._dirs['base'] == None or not self._tree_ready:
            #there's NO base here or up the chain
            raise ValueError   #cannot generate!

        # wipe www dir & recreate
        self._wipe_www_dir()#copy common files
        #shutil.copytree(self.dirs['common'],
        #                os.path.join(self.dirs['www'],"common"))
        slist = glob.glob(os.path.join(self.dirs['common'],"*"))
        for fo in slist:
            rfn = os.path.split(fo)[1]
            if os.path.isdir(fo):
                shutil.copytree(fo, os.path.join(self.dirs['www'], rfn))
            else:
                shutil.copy(fo, self.dirs['www'])

        # init atom file
        title = self.site_config['site_title']
        if title == '':
            title = "<No title>"
        feed = AtomFeed(title=title,
                subtitle=self.site_config['site_subtitle'],
                feed_url= os.path.join( self.site_config['site_url'],"atom.xml"),
                url=self.site_config['site_url'],
                author=self.site_config['default_author'])


        themes_to_copy = []  # full paths!
        generated_page_info = []
        for slug in self._pages_to_generate():  #this list of pages is in reverse chrono order
            p = s2page.Page(self, slug, isslug=True)
            generated_page_info.append( {'slug': p.slug,
                                         'title':p.title,
                                         'date': p.creation_date,
                                         'in_toc': p.in_toc })
            t = p.theme_path
            if not t in themes_to_copy:
                themes_to_copy.append(t)
            # wipe destination.
            self._wipe_www_page(slug)
            pg_content = p.generate() #generate page
            # add atom entry
            try:
                cdd = datetime.strptime(p.creation_date, '%Y-%m-%d') # feed.add needs the dat in datetime format
            except:
                print "Wrong date format in page '%s'. It should be YYYY-MM-DD."%p.slug
                print "Site Generation stopped!!  correct the date and generate again."
                self._wipe_www_dir()
                sys.exit()
            feed.add(title= p.title,
                     content=pg_content,
                     content_type="html",
                     author=p.author,
                     url=os.path.join( self.site_config['site_url'],"atom.xml") ,
                     updated=cdd)

        # copy themes
        wthemesdir = os.path.join(self.dirs['www'],"themes")
        os.mkdir(wthemesdir)
        for d in themes_to_copy:
            dname = os.path.split(d)[1]
            destpath = os.path.join(wthemesdir, dname)
            shutil.copytree(d, destpath)
            # delete tpl files
            ttr = glob.glob(os.path.join(destpath,"*tpl"))
            for f in ttr:
                os.remove(f)

        # write atom file
        atomfile= codecs.open(os.path.join(self.dirs['www'],"atom.xml"), "w", encoding="utf-8", errors="xmlcharrefreplace")
        atomfile.write(feed.to_string())
        atomfile.close()

        # create front page/s
        #print "generated_page_info for gf ",generated_page_info
        ff = self.site_config['fixed_frontpage']
        if ff != None and ff != '':
            self._set_fixed_frontpage(ff)
        else:
            self.generate_front(generated_page_info)
        self._generate_site_map(generated_page_info)


    def generate_front(self,generated_page_info, epp=10):
        themepath = "../themes/" + self.site_config['default_theme'] +'/'

        commonpath = self._dirs['common']
        template_path = os.path.join(self._dirs['themes'],
                                     self.site_config['default_theme'],
                                     self.site_config['default_template'])
        makotemplate = Template(filename=template_path,
                                module_directory=self._makodir)

        # remove pages which should not be in TOC
        generated_page_info = [gpi for gpi in generated_page_info if gpi['in_toc']]
        generated_page_info = sorted(generated_page_info, key=lambda x : x['date'],reverse=True)
        frontpage_iterator = self.renderfront_chronological_plain(generated_page_info,epp)
        i = 0
        for fpo in frontpage_iterator:
            i += 1
            rendition = makotemplate.render(pageContent=fpo['content'],isFrontPage=True,
                                            themePath=themepath,
                                            commonPath=commonpath,
                                            pageTitle="TOC - " + str(i))
            if i == 1:
                fname = "index.html"
            else:
                fname = str(i) + '.html'
            fullpath = os.path.join(self._dirs['www'],fname)

            fout = codecs.open(fullpath, "w", encoding="utf-8", errors="xmlcharrefreplace")
            fout.write(rendition)
            fout.close()

    def renderfront_chronological_plain(self,generated_page_info, epp=10):
        # renderfront methods should return an iterator
        # gpi is [{'slug': p.slug, 'title': p.title, 'date': p.creation_date },...]
        innertemplate_path = os.path.join(self._dirs['themes'],
                                     self.site_config['default_theme'],
                                     "chronological_plain_front.tpl")
        innertemplate = Template(filename=innertemplate_path,
                                module_directory=self._makodir)

        # divide the generated page info in slices of size epp
        numpages = math.ceil(float(len(generated_page_info))/epp)
        i = -epp
        c = 1
        # then loop and yield what the template renders.
        while c <= numpages:
            i = i + epp
            chunk = generated_page_info[i: i+epp]
            frontpage_obj = { 'content' : None,
                              'next_page_url': None,
                              'back_page_url': None }
            if c < numpages:
                frontpage_obj['next_page_url'] = str(c+1)+'.html'
            if c == 2 :
                frontpage_obj['back_page_url'] = "index.html"
            else:
                if c > 2:
                    frontpage_obj['back_page_url'] = str(c-1)+'.html'

            frontpage_obj['content'] = innertemplate.render(generatedPageInfo=chunk,
                backPageUrl = frontpage_obj['back_page_url'],
                nextPageUrl = frontpage_obj['next_page_url'])
            c += 1
            yield frontpage_obj


    def _set_fixed_frontpage(self,ff):
        target = os.path.join(self._dirs['www'],ff, "index.html")
        if not os.path.isfile(target):
            print "Value for fixed_frontpage in site configuration (s2/config.yml) is not a valid page."
            raise ValueError
        link_name = os.path.join(self._dirs['www'],"index.html")
        os.symlink(target, link_name)

    def _generate_site_map(self,generated_page_info):
        fon = os.path.join(self._dirs['www'] ,"sitemap.txt")
        pfix = self.site_config['site_url']
        if not pfix.endswith('/'):
            pfix = pfix + '/'
        fout = open(fon,"w")
        for p in generated_page_info:
            fout.write( pfix + p['slug'] + "/\n") 
        fout.close()

    def add_page(self, page_title):
        '''Add a page to the site.'''
        p = s2page.Page(self, page_title)
        return p

    def random_page(self, title=None, content=None, 
                    creation_date=None, tags=None):
        '''Generate random page, write it and return the corresponding \
object.'''
        if title == None:
            title = util.random_title()
        if content == None:
            content = util.random_md_page()
        if creation_date == None:
            creation_date = util.random_date()
        if tags == None:
            tags = []
        # yes, we pass self as a param. It's a ref to this site, that
        # is needed by the page
        p = s2page.Page(self, title)
        #here, set date and tags??
        # date = util.random_date()
        p.content = content
        p.creation_date = creation_date
        p.tags = tags
        p.write()
        return p

    def page_exists_on_disk(self, slug):
        '''Return true if post directory and post file both exist.'''

        r = False
        page_dir = os.path.join(self.dirs['source'], slug)
        page_file_name = os.path.join(page_dir, slug + '.md')
        if os.path.isdir(page_dir):
            if os.path.isfile(page_file_name):
                r = True
        return r

    def rename_page(self, old_slug, new_title):
        '''Load the page corresponding to the slug, and rename it.'''
        #load page
        p = s2page.Page(self, old_slug, isslug=True)
        p.rename(new_title)

    @property
    def dirs(self):
        '''Return the information about site directories.'''
        return self._dirs

    @property 
    def tree_ready(self):
        '''Return whether the tree is ready.'''
        return self._tree_ready

    def _wipe_www_page(self, slug):
        '''Remove all data in www about the page identified by slug.'''
        wd = os.path.join(self._dirs['www'], slug)
        if os.path.isdir(wd): # pragma: no cover
            shutil.rmtree(wd)

    def _pages_to_generate(self):
        '''Return list of slugs that correspond to pages to generate.'''
        # right now it gets all the files. In theory, It should only
        # get what's changed... but the program is not doing that yet.

        all_pages = self.get_page_names()
        # keep only those whose status is published
        ptg = []
        for slug in all_pages:
            p = s2page.Page(self, slug, isslug=True)
            if p.published:
                ptg.append({'slug': p.slug, 'title':p.title, 'date': p.creation_date })

        # sort the ptg array in reverse chronological order of its entries.
        sptg = sorted(ptg, key=lambda x : x['date'],reverse=True)
        res = [ pinfo['slug'] for pinfo in sptg]
        return res

    def _create_default_config(self):
        '''Create and write to disk a default site config file.'''
        # maybe I should read the default config from somewhere in the package?
        cfg = { 'site_title': '',
                'site_subtitle': '',
                'default_author': '',
                'site_url': '',
                'default_theme': 'blog1',
                'default_template': 'main.html.tpl',
                'fixed_frontpage': ''
              }


        file_name = os.path.join(self._dirs['s2'],'config.yml')
        f = open(file_name,'w')
        f.write(yaml.dump(cfg,default_flow_style=False))
        f.close()
        return cfg

    def _read_site_config(self):
        '''Read and return the site config, as a dictionary.'''
        file_name = os.path.join(self._dirs['s2'],'config.yml')
        if os.path.isfile(file_name):
            f = open(file_name,'r')
            cfg = yaml.load(f.read())
            f.close()
        else:
            cfg = self._create_default_config()
        return cfg
