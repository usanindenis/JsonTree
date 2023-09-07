#!/usr/bin/env python

import setuptools
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="JsonTree",
    version="0.0.1",
    description="Build package for JsonTree",
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=("Programming Language :: Python :: 3.11",),
    install_requires=[],
    include_package_data=True,
    license='MIT',
    author='Usanin Denis',
)
