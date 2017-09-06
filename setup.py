#!/usr/bin/env python

import os
from glob import glob
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    LONG_DESCRIPTION = readme.read()
    
CLASSIFIERS = [
    "License :: OSI Approved :: MIT License",
    "Intended Audience :: Healthcare Industry",
    "Development Status :: ",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Operating System :: OS Independent",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
    "Topic :: Scientific/Engineering :: Physics",
]

KEYWORDS = "medical physics python radiation oncology django"
NAME = "django-rt-pdb"
URL = "https://github.com/scaramallion/django-rt-pdb.git"
DOWNLOAD_URL = "https://github.com/scaramallion/django-rt-pdb/archive/master.zip"
LICENSE = "MIT"
VERSION = '1.0.0'
REQUIRES = ['numpy',
            'scipy',
            'django']


def sample_files():
    sample_files = []
    sample_roots = ['samples']
    for sample_root in sample_roots:
        for root, subfolder, files in os.walk(sample_root):
            files = [x for x in glob(root + '/*')]
            sample_files = sample_files + files

    return sample_files

PACKAGE_DATA = {'django-rt-pdb' : sample_files()}

opts = dict(name=NAME,
            version=VERSION,
            long_description=LONG_DESCRIPTION,
            url=URL,
            download_url=DOWNLOAD_URL,
            license=LICENSE,
            keywords=KEYWORDS,
            classifiers=CLASSIFIERS,
            packages=find_packages(),
            package_data=PACKAGE_DATA,
            include_package_data=True,
            install_requires=REQUIRES,
            zip_safe=False)            


if __name__ == '__main__':
    setup(**opts)
