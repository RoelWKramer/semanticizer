#!/usr/bin/env python

from distutils.core import setup

pkgs = (["semanticizer"] +
        ["semanticizer." + sub for sub in ("processors", "dbinsert",
                                           "server", "util", "wpm")])
#package_dir = {'': 'src'},
#packages = find_packages('src'),

setup(
    name="semanticizer",
    description="Entity Linking for the masses",
    packages=pkgs,
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing",
    ],
    install_requires=[
        "flask",
        "leven",
        "lxml",
        "mock",
        "networkx",
        "nltk",
        "numpy",
        "pyyaml",
        "redis>=2.8.0",
        "scikit-learn",
        "simplejson",
    ],
)
