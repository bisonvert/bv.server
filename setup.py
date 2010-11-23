#!/usr/bin/env python
# -*- coding: utf-8 -
#

import os
import sys

if not hasattr(sys, 'version_info') or sys.version_info < (2, 5, 0, 'final'):
    raise SystemExit("Bisonvert lib client requires Python 2.5 or later.")

from setuptools import setup, find_packages


name = 'bv.server'
setup(
    name = name,
    namespace_packages = ['bv', name],
    version = '0.1',
    description = 'A client for bison vert',
    long_description = file(
        os.path.join(
            os.path.dirname(__file__),
            'README.rst'
        )
    ).read(),
    author = 'Makina Corpus',
    author_email = 'python@makina-corpus.com',
    license = 'BSD',
    url = 'http://bitbucket.org/bisonvert/bv.server',
    install_requires = [
            'GDAL',
            'simplejson',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages = find_packages('src'),
    package_dir = {'': 'src'},

    # Make setuptools include all data files under version control,
    # svn and CVS by default
    include_package_data=True,
    zip_safe=False,
    # Tells setuptools to download setuptools_git before running setup.py so
    # it can find the data files under Hg version control.
    setup_requires=['setuptools_hg'],
    extras_require={'test': ['IPython', 'zope.testing', 'mocker']},
    entry_points = {
        'console_scripts': [
            'bv-server.manage = bv.server.manage:main' ,
        ],
    }
)


