"""
Abstract base class for all subcommands in dmwg-data-pyutils 
based off of Nils Homer's work (https://github.com/nh13).

@author: Kyle Hernandez <kmhernan@uchicago.edu>
"""
from abc import ABCMeta, abstractmethod

from dmwg_data_pyutils.types import ArgParserT, NamespaceT


class Subcommand(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def __add_arguments__(cls, parser: ArgParserT):
        """Add the arguments to the parser"""

    @classmethod
    @abstractmethod
    def main(cls, options: NamespaceT) -> None:
        """
        The default function when the subcommand is selected.  Returns None if
        executed successfully.
        """

    @classmethod
    def __get_description__(cls):
        """
        Optionally returns description
        """
        return None

    @classmethod
    def __tool_name__(cls):
        """
        Tool name to use for the subparser
        """
        return cls.__name__

    @classmethod
    def add(cls, subparsers: ArgParserT) -> ArgParserT:
        """Adds the given subcommand to the subparsers."""
        subparser = subparsers.add_parser(
            name=cls.__tool_name__(), description=cls.__get_description__()
        )

        cls.__add_arguments__(subparser)
        subparser.set_defaults(func=cls.main)
        return subparser
