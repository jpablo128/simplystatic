
# s2 - SimplyStatic

SimplyStatic is a command-line static website generator written in Python. It is **simple** to use, and it is meant to be used for **simple** websites: blogs, small company websites, product pages, or landing pages in which the most important *feature* is the content itself. 

s2 uses very simple [Mako](http://www.makotemplates.org/ "Mako home page") templates to define the main areas of the page (content, header, footer, sidebars...) and CSS to style those elements. The content is written in Markdown.

s2 has been developed and tested in Ubuntu 12.04, with Python 2.7.


# Installation

If you have `pip` installed:

    ~$ sudo pip install simplystatic

Or you can use `easy_install` instead:

    ~$ sudo easy_install simplystatic


You can also clone the github repo and install from it:

    ~$ git clone git://github.com/jpablo128/SimplyStatic.git
    ~$ cd simplystatic
    ~$ sudo python setup.py install

**Note**: If you are using virtual environments, get into the virtual environment where you want to install and don't use `sudo`!

# Basics

Once it is installed, you can type s2 at the command line to see the usage:

    ~$ s2
    usage: s2 [-h] {init,add,gen,rename,serve,ls} ...
    s2: error: too few arguments
    ~$ 

With -h or --help you can get more information:

    ~$ s2 -h
    usage: s2 [-h] {init,add,gen,rename,serve,ls} ...

    Create and manage a SimplyStatic site.

    positional arguments:
      {init,add,gen,rename,serve,ls}
                            commands
        init                Initialize a SimplyStatic directory structure
        add                 Add a page to the site.
        gen                 Generates the site.
        rename              Renames a page in the site.
        serve               Serves the site on localhost.
        ls                  List pages, drafts, or most recently edited page.

    optional arguments:
      -h, --help            show this help message and exit
    ~$ 

So everything is done with `s2 \<command\> [options]`.

You can use -h or --help with a specific command to get help about that command:

    ~$ s2 init -h
    usage: s2 init [-h] [-d DIRNAME] [-r] [-n NUMPAGES]

    optional arguments:
      -h, --help            show this help message and exit
      -d DIRNAME, --dirname DIRNAME
                            Directory to initialize
      -r, --randomsite      Add random pages to the site (useful for testing)
      -n NUMPAGES, --numpages NUMPAGES
                            Number of random pages to add to the site.
    ~$ 

s2 commands always operate on a specific directory, which is called an *s2 tree* or *s2 structure*. Most commands can take an argument to specify this directory, but the easiest thing to do is to cd into the directory you want to manipulate, and then call s2.

The only command that can be (and has to be) used in an empty directory is <code>init</code>. As its name implies, it initializes an s2 tree. All the other commands must refer to an existing s2 tree (that is, a directory that has been initialized with <code>s2 init</code>)

Other generators make a distinction between posts, pages, resources, etc. **s2 does not**. In s2, everything is a generic *page*.

# Creating a site

To create an empty site, just `s2 init` in the directory:

    ~$ mkdir myblog
    ~$ cd myblog
    ~/myblog$ s2 init
    Initialized directory.
    ~/myblog$ tree -L 2
    .
    |-- .s2
    |   `-- config.yml
    |-- common
    |   |-- favicon.ico
    |   |-- font-awesome
    |   |-- s2.ico
    |   `-- s2.png
    |-- source
    |-- themes
    |   |-- blog1
    |   |-- blog2
    |   `-- company1
    `-- www

    8 directories, 3 files
    ~/myblog$ 

The `init` command can create a set of random pages with random text. Both the name of the pages and their contents are total gibberish, but sometimes it is useful to start with a non-empty site to try things out (adjusting templates, configuration, generating the site, etc.)

Calling `s2 init -r` will generate 20 random pages by default. If you want to generate a specific number of pages, use `-n`:

    ~/myblog$ s2 init -r -n 5
    Initialized directory.
    added page  methodological_it_rather_in_26e4040a8
    added page  functional_with_lexicon_exclusive_26e53a468
    added page  on_of_semigrammaticalness_considered_26e7967e8
    added page  considered_the_base_be_26e9e2808
    added page  to_to_the_is_26eaa6168
    ~/myblog$ tree -L 2 -a
    .
    |-- .s2
    |   `-- config.yml
    |-- common
    |   |-- favicon.ico
    |   |-- font-awesome
    |   |-- s2.ico
    |   `-- s2.png
    |-- source
    |   |-- considered_the_base_be_26e9e2808
    |   |-- functional_with_lexicon_exclusive_26e53a468
    |   |-- methodological_it_rather_in_26e4040a8
    |   |-- on_of_semigrammaticalness_considered_26e7967e8
    |   `-- to_to_the_is_26eaa6168
    |-- themes
    |   |-- blog1
    |   |-- blog2
    |   `-- company1
    `-- www

    14 directories, 4 files
    ~/myblog$ 


### Configuration

In the .s2 directory there is a YAML file with configuration parameters for the site:

    ~/myblog$ cat .s2/config.yml 
    default_author: ''
    default_template: main.html.tpl
    default_theme: blog1
    fixed_frontpage: ''
    site_subtitle: ''
    site_title: ''
    site_url: ''
    ~/myblog$ 

* **default\_author**, **site\_title**, **site\_subtitle**, and **site\_url** are used mainly to generate the Atom feed.
* **default\_theme** and **default\_template** are the theme and template that will be applied to any page that doesn't specify any other default and template in its own configuration section. This way, it's easy to change the look of all (or most) of the pages, but also you can make any page in the site look different (or use different css files, js scripts, etc.)
* **fixed\_frontpage** allows you to specify the *slug* of the main page of the site. If you leave this blank, when you generate the site s2 will generate a list of pages in reverse chronological order of creation, and it will paginate this list including 10 items per page. Obviously, this is meant for blogs. 

### Structure

An s2 tree has the following subdirectories:

    ~/myblog$ tree -L 1 -a
    .
    |-- .s2
    |-- common
    |-- source
    |-- themes
    `-- www

    5 directories, 0 files
    ~/myblog$ 


* **`.s2`** serves as a mark to identify a tree as an s2 tree (although the program also checks the existence of the other directories.) It also contains the YAML file `config.yml`
* **`source`** contains the source files to generate the content of the site. There is a directory per page (its name is the *slug* for the page, which is just the title without spaces, all lower case, etc.). You might want to include custom css or javascript files for individual pages, so having a directory for each page helps to keep things tidy, not only in the source directory, but also in the generated site.
* **`themes`** contains the themes that will be used in the site. Normally it would only be one, but you can have more. A theme is just a directory that contains different Mako templates, css files, image files, and any other assets that you want to use. There are three very simple themes included in s2 (blog1, blog2, and company1). Whenever you create an s2 site, those three themes will be included in the `themes` directory. They are not elaborate at all, but it's easy to copy/rename one and use it as a starting point.
* **`common`** serves as a catch-all directory where you can put anything that you want to share between all the pages. Upon site generation everything in the common directory will be copied to the root of the site (to www/). This is a good place to put things like favicon files, or fonts, or javascript libraries that you want to use in more than one page and across themes. You can always put js libraries or css or anything inside a specific page directory. But as soon as you want to use those same assets in two or more pages, it makes sense to move them to `common` to avoid duplication and to take advantage of caching in the browser.
* **`www`** contains the generated site. This is the directory you will have to set up as the documentroot (in Apache2 terms) of your site. This directory gets wiped every time the site is generated... so **never edit anything under `www`**, because you will lose the changes. 

# Adding content

The easiest way to add a page is to use the `s2 add` command:

    ~$ cd myblog/
    ~/myblog$ ls
    common  source  themes  www
    ~/myblog$ s2 add "My first s2 page"
    Added page 'My first s2 page'
    ~/myblog$ ls source/
    my_first_s2_page
    ~/myblog$ ls source/my_first_s2_page/
    my_first_s2_page.md
    ~/myblog$ 

The `add` command takes the title of the page as an argument. Notice that you have to put the title in quotes (in the unlikely case that the title only has one word, you can skip the quotes).

Notice that the directory and markdown file for the newly added page are named with a modified version of the title (lower case, underscores instead of spaces...) we will refer to this as the **slug** of the page.

### Renaming a page 

To rename a page you must provide the slug of the page you want to rename, and the new **title** that you want to give to your page:

    ~/myblog$ s2 rename my_first_s2_page "Brand new s2 page"
    Renamed page.
    ~/myblog$ ls source/
    brand_new_s2_page
    ~/myblog$ ls source/brand_new_s2_page/
    brand_new_s2_page.md
    ~/myblog$ 

There is no command to delete a page, since it's just a matter of deleting the corresponding directory under `source`:

    ~/myblog$ s2 add "An ephemeral page"
    Added page 'An ephemeral page'
    ~/myblog$ ls source/
    an_ephemeral_page  brand_new_s2_page
    ~/myblog$ rm -rf source/an_ephemeral_page/
    ~/myblog$ 


### Page contents

When a page is created, the corresponding markdown file is filled with the default configuration for the page:

    ~/myblog$ cat source/brand_new_s2_page/brand_new_s2_page.md 
    status: draft
    lang: 
    title: Brand new s2 page
    author: 
    creation_date: 2014-01-31
    theme: 
    template: 
    slug: brand_new_s2_page
    tags: 

    ~/myblog$ 

s2 uses the [Meta-data extension](http://pythonhosted.org/Markdown/extensions/meta_data.html "Python Markdon Meta-data extension") of Markdown, so the first few lines of the page source contain some metadata that s2 uses (or might use in the future).
It is **very** important to leave a blank line between the last metadata item and the rest of the file.

So, you would edit the file, and add your content:

    ~/myblog$ cat source/brand_new_s2_page/brand_new_s2_page.md 
    status: draft
    lang: 
    title: Brand new s2 page
    author: 
    creation_date: 2014-01-31
    theme: 
    template: 
    slug: brand_new_s2_page
    tags: 

    # My first heading

    This is a dull paragraph.

    ## This is a level 2 heading

    Some more text here. Enough.

    ~/myblog$ 

The configuration items that you are more likely to use are *status*, *theme*, and *template*:

* *status*: can be either "draft" or "published". Notice that by default it is "draft", and when s2 generates the site it will **ignore** draft pages. This way, you can be working on one or more pages, leave them unfinished, and if you generate the site and publish it, you won't have to worry about them.
* *theme* and *template*: if these are left blank, the page will be formatted and styled according to the default theme and template defined in the site configuration file (in `.s2/config.yml`). However, if you enter the name of a theme and/or a template in these variables, they will be used in this particular page. 

## Including html

s2 uses [Markdown](http://daringfireball.net/projects/markdown/syntax "Markdown") because it's very simple and allows one to concentrate on writing content. However, it is perfectly ok to include html content if you need to. This is particularly useful if you want to use any custom css and/or javascript in the page:


    <link rel="stylesheet" href="test.css" type="text/css" />
    <style>
        /* here go my inline styles */
    </style>

    <!-- link to an external library -->
    <script src="http://d3js.org/d3.v3.min.js"></script>
    <!-- custom script -->
    <script>
        //here goes my javascript
    </script>


* To link to files that you put in the `common` directory, the link should be relative to the root of the site, e.g.: `href="/mycustom.css"`
* To link to files that you put in the page directory (where your Markdown file is), the link should not include any path component, e.g.: `href="mycustom.css"`
* If you want to create subdirectories in your page directory, you can do so, and the links must take your paths into account, e.g.: `href="somedir/mycustom.css"`


# Listing pages

Even though it's straightforward to list the contents of the `source` directory, there's a convenience `s2 ls` command that also allows you to list the pages whose status is *draft*, and the last page that was modified.

    ~/myblog$ s2 ls -h
    usage: s2 ls [-h] [-d DIRNAME] [-f] [-r]

    optional arguments:
      -h, --help            show this help message and exit
      -d DIRNAME, --dirname DIRNAME
                            Directory of site root, or any place under site root.
      -f, --drafts          List pages whose status is draft.
      -r, --recent          List the most recently edited page.
    ~/myblog$ 


# Themes and templates

A theme is just a directory that contains a set of related Mako templates, css files, graphics, fonts, etc.

    ~/myblog$ ls themes/  
    blog1  blog2  company1
    ~/myblog$ ls themes/blog2
    chronological_plain_front.tpl  fonts  header1.jpg  main.html.tpl  style.css
    ~/myblog$ 

The default blog1 theme contains a few more files.

Templates are fairly simple. The main template for a site is intended to provide pretty much all of the structure around the page content.

There are only five variables that are passed to the Mako templates when they're being rendered: 

* `pageContent`
* `isFrontPage`
* `themePath`
* `commonPath`
* `pageTitle`

You can use these variables in your templates. 
When the site is being generated, the markdown file for each page is converted to html and the result of that conversion is passed to the Mako template in the variable `pageContent`.

At some point in your template you can have something like this:

    <article class="page-content">
        ${pageContent}
    </article>

At the beginning when creating a site, there's more effort involved to create the templates, the styles, etc.

# Generating the site

To generate the site, just use the `gen` command:

    ~/myblog$ s2 gen
    Generated Site in 0.070719 seconds.
    ~/myblog$ tree -L 2    
    .
    |-- common
    |   |-- favicon.ico
    |   |-- font-awesome
    |   |-- s2.ico
    |   `-- s2.png
    |-- source
    |   `-- brand_new_s2_page
    |-- themes
    |   |-- blog1
    |   |-- blog2
    |   `-- company1
    `-- www
        |-- atom.xml
        |-- brand_new_s2_page
        |-- favicon.ico
        |-- font-awesome
        |-- index.html
        |-- s2.ico
        |-- s2.png
        |-- sitemap.txt
        `-- themes
    ~/myblog$ ls www/brand_new_s2_page/
    index.html
    ~/myblog$

Here is what happens when the site is generated:

* The directory `www` gets wiped clean.
* Everything under `common` gets copied to `www/`
* All themes that are used by the pages are copied to `www/themes/` 
* For each page that has a status of *published*:
    * a directory with the same slug is created under `www/`
    * all files **except those that end in .md** in the source page directory are copied to the corresponding directory under `www/`
    * the source page file (markdown file) is converted to html, then the templates are applied to create the final html file. The resulting file is in `www/<page_slug>/index.html'
* The `sitemap.txt` file is created and placed in `www/`
* The `atom.xml` file is generated and placed in `www/`
* If the `fixed_frontpage` configuration variable (in `.s2/config.yml`) is empty, the TOC pages are created and placed in the site's root `www/`. Each TOC page contains links to 10 "pages". The files are index.html, 2.html, 3.html etc. 
* If the `fixed_frontpage` configuration variable (in `.s2/config.yml`) contains a slug, then no TOC pages will be generated. Instead, a symbolic link called `index.html` will be placed in `www/`, pointing to `www/<page_slug>/`

Remember that draft pages are **not** generated. If you expect to see a page in the generated site and it's not there, check the *status* property of the page.

The site is always generated in full, there is no way to do *incremental* generations. This might seem inefficient, and -in a way- it is. However, the time it takes to generate a site even with several dozen (or a few hundred) pages is just a few seconds. Most of the time is spent just editing the markdown file for a page, and that is very easy to preview (e.g., if you use  Sublime Text 2, there's a plugin that will render the markdown and show it in the browser). The normal/expected workflow is to edit many times, and to generate/deploy far fewer times, so the inefficiency in generation time is negligible. At this point there's no need to do any premature optimizations in this regard.

### Viewing the site

If you want to take a look at your site without having to deploy and/or set up a production-grade server (apache2, nginx, etc.), the easiest way to do it is using the `s2 serve` command:

    ~/myblog$ s2 serve --help
    usage: s2 serve [-h] [-p PORT] [-i IP]

    optional arguments:
      -h, --help            show this help message and exit
      -p PORT, --port PORT  Port for the server.
      -i IP, --ip IP        IP address for the server.
    ~/myblog$

This command will run a basic python web server, so you can see the site. It's convenient to open up a different terminal window to do this.

You can specify the port and the IP. If you don't, the server will listen on 127.0.0.1:8000. When the server is running, open up your browser and go to the corresponding ip/port. You should see the site, and the terminal window where the server is running will log the requests:

    ~/myblog$ s2 serve
    Serving HTTP on 127.0.0.1 port 8000 ...
    localhost - - [31/Jan/2014 18:26:17] "GET / HTTP/1.1" 200 -
    localhost - - [31/Jan/2014 18:26:17] "GET /themes/blog1/pygments_default.css HTTP/1.1" 200 -
    localhost - - [31/Jan/2014 18:26:17] "GET /font-awesome/css/font-awesome.css HTTP/1.1" 200 -
    localhost - - [31/Jan/2014 18:26:17] "GET /themes/blog1/style.css HTTP/1.1" 200 -
    localhost - - [31/Jan/2014 18:26:17] "GET /themes/blog1/header1.jpg HTTP/1.1" 200 -
    localhost - - [31/Jan/2014 18:26:17] "GET /themes/blog1/fonts/Cicle_Fina.ttf HTTP/1.1" 200 -
    localhost - - [31/Jan/2014 18:26:17] "GET /font-awesome/font/fontawesome-webfont.woff?v=3.2.1 HTTP/1.1" 200 -
    localhost - - [31/Jan/2014 18:26:17] "GET /themes/blog1/fonts/Cicle_Gordita.ttf HTTP/1.1" 200 -
    localhost - - [31/Jan/2014 18:26:22] "GET /the_this_that_complex_c6413c6a8/ HTTP/1.1" 200 -
    localhost - - [31/Jan/2014 18:26:25] "GET /subsume_accuracy_pronouns_determines_c64336288/ HTTP/1.1" 200 -


# Deployment

One of the advantages of static sites is that they are very easy to deploy. They are also very efficient when served by production-grade servers (apache2, nginx, etc.). 
With s2, it would be very easy to write a script to ftp or rsync the contents of the `www` directory to the server.

However, it's also a good idea to use a version control system (*git*, for example) on the whole s2 directory. This way it's easy to keep track of changes and it's safe to try new things. Combining s2 with a deployment scheme like the one that Joe Maller proposes in
[A web-focused Git workflow](http://joemaller.com/990/a-web-focused-git-workflow/), provides a very easy and efficient way to manage and deploy your static site.





