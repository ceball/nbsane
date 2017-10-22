#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-nbsane',
    version='0.0.1',
    author='IOAM',
    author_email='developers@topographica.org',
    maintainer='IOAM',
    maintainer_email='developers@topographica.org',
    license='BSD-3',
    url='https://github.com/ioam/pytest-nbsane',
    description='Run and lint notebooks',
    long_description=read('README.rst'),
    py_modules=['pytest_nbsane'],
    install_requires=['pytest>=3.1.1',
                      'jupyter_client',
                      'nbformat',
                      'nbconvert',
                      'pyflakes'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
    ],
    entry_points={
        'pytest11': [
            'nbsane = pytest_nbsane',
        ],
    },
)
