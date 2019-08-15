#!/usr/bin/env python
# -*- coding: utf-8 -*-

"Python DSL to leverage translation of dictionaries and SQLAlchemy into Protobuf objects"


import ast
import os
from setuptools import setup, find_packages


local_file = lambda *f: open(os.path.join(os.path.dirname(__file__), *f)).read()


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = 'version'

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except:
            pass


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file('mercator', 'version.py')))
    return finder.version


def read_requirements():
    return local_file('requirements.txt').splitlines()


def read_test_requirements():
    return local_file('test_requirements.txt').splitlines()


def read_readme():
    """Read README content.
    If the README.rst file does not exist yet
    (this is the case when not releasing)
    only the short description is returned.
    """
    try:
        return local_file('README.rst')
    except IOError:
        return __doc__


setup(
    author='NewStore Inc.',
    author_email='engineering@newstore.com',
    description=read_version(),
    include_package_data=True,
    install_requires=read_requirements(),
    long_description=read_readme(),
    long_description_content_type='text/x-rst',
    name='mercator',
    url='https://mercator.readthedocs.io/en/latest/',
    download_url='https://github.com/NewStore/mercator/releases',
    packages=find_packages(exclude=['*tests*']),
    test_require=read_test_requirements(),
    test_suite='nose.collector',
    version=read_version(),
    package_data={
        'mercator': [
            '*.cfg',
            '*.py',
            '*.rst',
            '*.txt',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    zip_safe=False,
)
