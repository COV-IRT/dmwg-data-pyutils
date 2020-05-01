"""Module for defining types for type annotations.

@author: Kyle Hernandez <kmhernan@uchicago.edu>
"""
from typing import NewType

from argparse import ArgumentParser, Namespace
from logging import Logger


# Argparser types
ArgParserT = NewType("ArgParserT", ArgumentParser)
NamespaceT = NewType("NamespaceT", Namespace)

# Logger types
LoggerT = NewType("LoggerT", Logger)
