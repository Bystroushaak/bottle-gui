#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from setuptools import setup, find_packages

from docs import getVersion


# Variables ===================================================================
changelog = open('CHANGES.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


# Functions & classes =========================================================
setup(
    name='bottle-gui',
    version=getVersion(changelog),
    description="Package used to vizualize services in Bottle web framework.",
    long_description=long_description,
    url='https://github.com/Bystroushaak/bottle-gui',

    author='Bystroushaak',
    author_email='bystrousak@kitakitsune.org',

    classifiers=[
        "Framework :: Bottle",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
    ],
    license='MIT',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "bottle",
        "napoleon2html"
    ],
    extras_require={
        "test": [
            "pytest",
            "requests"
        ],
        "docs": [
            "sphinx",
            "sphinxcontrib-napoleon",
        ]
    },
)
