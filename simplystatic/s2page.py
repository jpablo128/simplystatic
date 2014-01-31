# -*- coding: utf-8 -*-

"""This module provides functionality to manage a Page entity.

Classes included:

    - Page: Manages creation, loading, rendering, writing, etc. of
            a "page" in a site. This structure refers to the "source"
            page.

"""

import os
import datetime
import glob
import shutil
import codecs

from mako.template import Template
from mako.runtime import Context
from StringIO import StringIO

import markdown
import mdx_mathjax

import util



class Page(object):
    """Represent a Page and provide tools for creation, management, etc.

    When an object of this class is created, it's necessary to pass a
    reference to a site, since a Page is created/managed/rendered in the
    context of a site.

    If a page name is passed on creation, the program will check whether
    it exists in the site. If it does, it loads the page source and
    parses it (setting the instance variables accordingly.) If it does
    not exist, it only creates the instance variables that it can.

    """

    def __init__(self, site, ptitle, isslug=False):
        """Initialize the page object created.

        Arguments:

            - ptitle: A string with the page title.

            - isslug: Boolean that indicates whether the title is a
                         "real" title (with spaces, etc.) or if it is
                         the "sanitized" version (lower case, no spaces,
                         underscores, no punctuation)

        This way of encoding the initialization parameters makes it
        easy to automatically initialize the object whether it is for
        creation of a new page, or it is to load an existing page.

        If "isslug" is omitted or false, the program assumes that we
        want to create a new page with that title (although it will
        check). It "sanitized" is true, it's supposed to be the
        reference to an existing page, and the program will try to load
        the pertinent information.

        """
        self.site = site
        self._config = None

        self._exists_on_disk = None

        self._slug = None
        self._title = None
        self._content = None

        self._dirs = {'www_dir': None,
                      'www_filename': None,
                      'source_dir': None,
                      'source_filename': None
        }
        #self._dir = None
        #self._file_name = None
        #self._mathjax = mdx_mathjax.MathJaxExtension()

        if not isslug:  #it's a title, we'll create a page
            self._create(ptitle)
        else:
            if self.site.page_exists_on_disk(ptitle):
                self._exists_on_disk = True
                self._load(ptitle)
            else:
                raise ValueError
                #print "Specified slug does not exist."

    def __repr__(self): # pragma: no cover
        return '\n'.join([str(self._slug), str(self._title),
                          str(self._content)])

    def _create(self, rawtitle):
        """Create a page with this title, if it doesn't exist.

        This method first checks whether a page with the same slug
        (sanitized name) exists_on_disk. If it does, it doesn't do anthing.
        Otherwise, the relevant attributes are created.
        Nothing is written to disc (to the source file). You must call
        the write_page method to do that. Doing it this way, after
        creation you can call a method to add random text, for example,
        before committing the page to disk.

        """
        slug = util.make_slug(rawtitle)
        if self.site.page_exists_on_disk(slug):
            raise ValueError
            #print "Attempted to create a page which already exists."
            #return False

        self._title = rawtitle
        self._slug = slug

        self._dirs['source_dir'] = os.path.join(self.site.dirs['source'], slug)
        self._dirs['source_filename'] = os.path.join(self._dirs['source_dir'],
                                                     slug + '.md')

        self._dirs['www_dir'] = os.path.join(self.site.dirs['www'], slug)
        self._dirs['www_filename'] = os.path.join(self._dirs['www_dir'], \
                                                  'index.html')
        self._config = self._create_config()
        return True

    def write(self):
        """Write the s2 page to the corresponding source file.

        It always writes the (serialized) config first, and then the
        content (normally markdown). The destination file is in the
        source_dir of the site.

        """
        if not os.path.isdir(self._dirs['source_dir']):
            os.mkdir(self._dirs['source_dir'])
        fout = open(self._dirs['source_filename'], 'w')
        fout.write(self._config_to_text())
        if self._content:
            fout.write('\n')
            fout.write(self._content)
            fout.write('\n')
        fout.close()

    def rename(self, new_title):
        """Rename an existing s2 page.

        For an existing s2 page, updates the directory and file name,
        as well as the internal configuration information (since it
        contains the title and the slug)

        """
        if not isinstance(new_title, str) and \
                not isinstance(new_title, unicode):
            raise TypeError
            # print "Cannot rename page. New title must be string or unicode."

        new_slug = util.make_slug(new_title)
        if self.site.page_exists_on_disk(new_slug):
            raise ValueError
            # print "Cannot rename page. A page with the same \
            # title/slug already exists."

        #wipe the source directory for this page
        shutil.rmtree(self._dirs['source_dir'])

        #just change dirinfo, config, and write
        self._title = new_title
        self._slug = new_slug
        self._config['title'] = [self._title]
        self._config['slug'] = [self._slug]

        self._dirs['source_dir'] = os.path.join(self.site.dirs['source'],
                                                new_slug)
        self._dirs['source_filename'] = os.path.join(self._dirs['source_dir'],
                                                     new_slug + '.md')

        self._dirs['www_dir'] = os.path.join(self.site.dirs['www'], new_slug)
        #self._dirs['www_filename'] = os.path.join(self._dirs['www_dir'], \
        #                                       new_slug + '.html')
        self.write()


    def render(self):
        """Render this page and return the rendition.

        Converts the markdown content to html, and then renders the
        (mako) template specified in the config, using that html.

        The task of writing of the rendition to a real file is
        responsibility of the generate method.

        """
        (pthemedir, ptemplatefname) = self._theme_and_template_fp()
        makotemplate = Template(filename=ptemplatefname,
                                module_directory=self.site._makodir)

        # I don't really need to use the meta extension here, because I render self._content (has no metadata)
        #page_html = markdown.markdown(self._content)

        md = markdown.Markdown(extensions=['meta','fenced_code', 'codehilite'],output_format="html5")
        page_html = md.convert(self._content)   # need to trigger the conversion to obtain md.Meta

        # We assume that the page is always in a dir one level below www
        themepath = "../themes/" + os.path.split(pthemedir)[1] + '/'
        commonpath = "../common/"

        # HERE I'll pass the config variable to the mako template, so I can use the title etc.
        #buf = StringIO()
        #ctx = Context(buf, dict(pageContent=page_html, isFrontPage=False, themePath=themepath, pageTitle='pedo',
        #                        commonPath=commonpath))
        #makotemplate.render_context(ctx)
        #rendition = buf.getvalue()
        rendition = makotemplate.render(pageContent=page_html,isFrontPage=False,
                                         themePath=themepath,
                                         commonPath=commonpath,
                                         pageTitle=self.title)
        return rendition

    # test generate should copy all other pages and dirs in the page
    # directory, except those in a especially named folder!
    def generate(self):
        """Generate the page html file.

        Just open the destination file for writing and write the result
        of rendering this page.

        """
        generated_content = ''
        if (self._config['status'][0]).lower() == 'published':
            if os.path.isdir(self.dirs['www_dir']):
                shutil.rmtree(self.dirs['www_dir'])
            os.mkdir(self.dirs['www_dir'])
            # copy the whole source directory of the page,
            # excluding 'nowww' and *s2md
            sfl = glob.glob(os.path.join(self.dirs['source_dir'], "*"))
            dirlist = [f for f in sfl if os.path.isdir(f)]
            filelist = [f for f in sfl if os.path.isfile(f)]
            for f in filelist:
                if not '.md' in os.path.split(f)[1]:
                    shutil.copy(f, self.dirs['www_dir'])
            for d in dirlist:
                rfn = os.path.split(d)[1]
                if rfn != 'nowww':
                    shutil.copytree(d, os.path.join(self.dirs['www_dir'], rfn))
                #write the rendered "page" to file

            #fout = open(self.dirs['www_filename'], 'w')
            #fout.write(self.render())
            #fout.close()

            generated_content = self.render()
            fout = codecs.open(self.dirs['www_filename'], "w", encoding="utf-8", errors="xmlcharrefreplace")
            fout.write(generated_content)
            fout.close()

        return generated_content

    def set_published(self):
        """Change the page configuration to make the page 'published' """
        self._config['status'][0] = 'published'

    def _create_config(self):
        """Create the default configuration dictionary for this page."""
        configinfo = {'creation_date': [ datetime.datetime.now().date().isoformat()],
                      'author': [self.site.site_config['default_author']],
                      'status': [u'draft'],
                      'lang': [u''],
                      'tags': [u''],
                      'title': [self._title],
                      'slug': [self._slug],
                      'theme': [u''],
                      'template': [u'']}  # when theme and template are empty, the generator uses the defaults. Thus, initially
                                          # they should be empty, to allow for global changes just by changing the site config files.
        return configinfo

    def _load(self, slug):
        """Load the page. The _file_name param is known, because this
        method is only called after having checked that the page exists.

        """
        #here we know that the slug exists
        self._slug = slug
        page_dir = os.path.join(self.site.dirs['source'], self._slug)
        page_file_name = os.path.join(page_dir, self._slug + '.md')
        self._dirs['source_dir'] = page_dir
        self._dirs['source_filename'] = page_file_name
        self._dirs['www_dir'] = os.path.join(self.site.dirs['www'], slug)
        self._dirs['www_filename'] = os.path.join(self._dirs['www_dir'],  'index.html')

        #pf = open(self._dirs['source_filename'], 'r')
        #page_text = pf.read()
        #pf.close()
        # need to decode!
        pf = codecs.open(self._dirs['source_filename'], mode="r", encoding="utf-8")
        page_text = pf.read()
        pf.close()

        self._parse_text(page_text)
        if not self._check_config():
            raise ValueError
            #sys.exit()
        self._title = self._config['title'][0]

    def _check_config(self):
        """Verify that the configuration is correct."""
        required_data = ['creation_date',
                         'author',
                         'status',
                         'lang',
                         'tags',
                         'title',
                         'slug',
                         'theme',
                         'template']
        isok = True
        # exclude some statements from coverage analysis. I would need to
        # refactor how the config is loaded/handled etc. It's not worth
        # to do that now. Maybe when I change yaml for the markdwn extension.
        for e in self._config.keys():
            if not e in required_data: # pragma: no cover
                print "The configuration in page '" + \
                      self._slug + "' is corrupt."
                isok = False
            # check that the theme and template exist, even if they're default.
        (pthemedir, ptemplatefname) = self._theme_and_template_fp()
        if not os.path.isdir(pthemedir): # pragma: no cover
            print "Theme " + self._config['theme'][0] + \
                  " specified in page '" + \
                  self._slug + "' does not exist."
            isok = False
        if not os.path.isfile(ptemplatefname): # pragma: no cover
            print "Template " + self._config['template'][0] + \
                  " specified in page '" + self._slug + \
                  "' does not exist."
            isok = False
        return isok

    def _theme_and_template_fp(self):
        """Return the full paths for theme and template in this page"""
        ptheme = self._config['theme'][0]
        if ptheme == "":
            ptheme = self.site.site_config['default_theme']
        pthemedir = os.path.join(self.site.dirs['themes'], ptheme)
        ptemplate = self._config['template'][0]
        if ptemplate == "":
            ptemplate = self.site.site_config['default_template']
        ptemplatefname = os.path.join(pthemedir, ptemplate)
        return (pthemedir, ptemplatefname)

    def _parse_text(self, page_text):
        """Extract the s2config and the content from the raw page text."""

        # 1 sanitize: remove leading blank lines
        # 2 separate "config text" from content, store content
        # 3 convert config text + \n to obtain Meta, this is the config.

        lines = page_text.split('\n')
        i = 0
        while lines[i].strip() == '':
            i += 1
        if i > 0: # i points to the first non-blank line.  Else, i is 0, there are no leading blank lines
            lines = lines[i:]  #remove leading blank lines

        i = 0
        while lines[i].strip() != '':
            i += 1
            # i points to the first blank line
        cfg_lines = '\n'.join(lines[0:i + 1])  #config lines, plus the empty line

        md = markdown.Markdown(extensions=['meta','fenced_code', 'codehilite'],output_format="html5")
        md.convert(cfg_lines)   # need to trigger the conversion to obtain md.Meta

        self._config = md.Meta
        self._content =  '\n'.join(lines[i+1:])


    def _config_to_text(self):
        """Render the configuration as text."""
        r = ''
        for k in self._config:
            # if k == 'creation_date':
            #     r +=  k + ": " + self._config[k][0] + '\n'
            # else:
            r +=  k + ": " + '\n        '.join(self._config[k]) + '\n'
        r += '\n'
        return r

    @property
    def content(self):
        """Return the content for the page (getter)"""
        return self._content

    @content.setter     # pylint: disable-msg=E1101
    def content(self, value): # pylint: disable-msg=E0102
        """Set the content of the page (setter)"""
        self._content = value

    @property
    def dirs(self):
        """Return the directory information for the page (getter)"""
        return self._dirs

    @property
    def slug(self):
        """Return the slug for the page (getter)"""
        return self._slug

    @property
    def title(self):
        """Return the title for the page (getter)"""
        return self._title

    @property
    def published(self):
        """Return if the page is published or not"""
        return (self._config['status'][0]).lower() == 'published'

    @property
    def creation_date(self):
        """Return the date from the configuration (getter)"""
        return self._config['creation_date'][0]

    @creation_date.setter     # pylint: disable-msg=E1101
    def creation_date(self, value): # pylint: disable-msg=E0102
        """Set the date in the configuraton (setter)"""
        if not isinstance(value, datetime.date):
            raise TypeError
        self._config['creation_date'][0] = value.isoformat()

    @property
    def tags(self):
        """Return the tags from the configuration (getter)"""
        return self._config['tags']

    @tags.setter     # pylint: disable-msg=E1101
    def tags(self, value): # pylint: disable-msg=E0102
        """Set the tags in the configuraton (setter)"""
        if not isinstance(value, list):
            raise TypeError
        self._config['tags'] = value

    @property
    def theme_path(self):
        """Return the full path of the theme used by this page."""
        return self._theme_and_template_fp()[0]
    
    @property
    def author(self):
        """Return the full path of the theme used by this page."""
        r = self.site.site_config['default_author']
        if 'author' in self._config:
            r = self._config['author']
        return r
