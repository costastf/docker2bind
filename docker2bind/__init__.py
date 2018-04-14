# -*- coding: utf-8 -*-
"""
docker2bind package

Imports all parts from docker2bind here
"""
from ._version import __version__
from modules import BindServer, Container

__author__ = '''Costas Tyfoxylos'''
__email__ = '''costas.tyf@gmail.com'''

# This is to 'use' the module(s), so lint doesn't complain
assert __version__

# assert objects
assert BindServer
assert Container