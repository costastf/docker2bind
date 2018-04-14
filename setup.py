#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
version = open('.VERSION').read()

# get the requirements from the requirements.txt
requirements_file =  [line.strip() for line in open('requirements.txt').readlines()
                     if line.strip() and not line.startswith('#')]
requirements = requirements_file

# get the test requirements from the test_requirements.txt
test_requirements = [line.strip() for line in open('requirements/testing.txt').readlines()
                     if line.strip() and not line.startswith('#')]

setup(
    name='''docker2bind''',
    version=version,
    description='''"A tool to dynamically update a bind9 server with records based on docker events"''',
    long_description=readme + '\n\n' + history,
    author='''Costas Tyfoxylos''',
    author_email='''costas.tyf@gmail.com''',
    url='''//docker2bind''',
    packages=find_packages(where='.', exclude=('tests', 'hooks')),
    package_dir={'''docker2bind''':
                 '''docker2bind'''},
    include_package_data=True,
    install_requires=requirements,
    license="LGPL 3",
    zip_safe=False,
    keywords='''docker2bind''',
    entry_points={
        'console_scripts': [
            # enable this to automatically generate a script in /usr/local/bin called myscript that points to your
            #  docker2bind.docker2bind:main method
            'docker2bind = docker2bind.docker2bind:main'
        ]
    },
    classifiers=[
        'Development Status :: Perpetual Beta',
        'Intended Audience :: Everyone',
        'License :: In-house development',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5.1',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    data_files=[
        ('', [
            '.VERSION',
            'LICENCE',
            'AUTHORS.rst',
            'CONTRIBUTING.rst',
            'HISTORY.rst',
            'README.rst',
            'USAGE.rst',
        ]),
    ]
)
