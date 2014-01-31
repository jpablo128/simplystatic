#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import simplystatic

setup (
    name ='simplystatic',
    description = 'A static website generator written in Python.',
    author= 'jPablo Caballero (jpablo128)',
    url = 's2.jpablo128.com',
    download_url= 's2.jpablo128.com/download',
    author_email= 'jpablo@jpablo128.com',
    version= simplystatic.__version__,
    install_requires= ['PyYAML','Markdown','Mako','Markdown','MarkupSafe','PyYAML',
                       'Pygments','argparse','coverage','mock','nose','pyatom','wsgiref'],
    packages= ['simplystatic'],
    scripts= ['bin/s2.py','bin/s2'],
    include_package_data=True
)
