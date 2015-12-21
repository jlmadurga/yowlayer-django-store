#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import yowlayer_store

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = yowlayer_store.__version__

if sys.argv[-1] == 'publish':
    try:
        import wheel
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='yowlayer-django-store',
    version=version,
    description="""Storage layer for yowsup in django""",
    long_description=readme + '\n\n' + history,
    author='Juan Madurga',
    author_email='jlmadurga@gmail.com',
    url='https://github.com/jlmadurga/yowlayer-django-store',
    packages=[
        'yowlayer_store',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="GPL-3+",
    zip_safe=False,
    keywords='yowlayer-django-store',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',        
    ],
)
