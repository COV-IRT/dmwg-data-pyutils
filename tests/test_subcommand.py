"""Tests the `dmwg_data_pyutils.subcommands.base.Subcommand` class"""
import unittest

from dmwg_data_pyutils.subcommands import Subcommand
from dmwg_data_pyutils.__main__ import main

from utils import captured_output


class TestSubcommand(unittest.TestCase):
    class Example(Subcommand):
        @classmethod
        def __add_arguments__(cls, subparser):
            pass

        @classmethod
        def __main__(cls, options):
            pass

        @classmethod
        def __get_description__(cls):
            return "Example description"

    def test_get_name(self):
        self.assertEqual(TestSubcommand.Example.__tool_name__(), "Example")
        self.assertEqual(Subcommand.__tool_name__(), "Subcommand")

    def test_get_description(self):
        self.assertEqual(
            TestSubcommand.Example.__get_description__(), "Example description"
        )
        self.assertIsNone(Subcommand.__get_description__())

    def test_no_inputs(self):
        with captured_output() as (_, stderr):
            with self.assertRaises(SystemExit) as context:
                main(args=["Example"])
        self.assertTrue("invalid choice: 'Example'" in stderr.getvalue())

    def test_extra_subparser(self):
        with captured_output() as (_, stderr):
            with self.assertRaises(SystemExit) as context:
                main(args=["Example", "--fake"], extra_subparser=TestSubcommand.Example)
        self.assertTrue("unrecognized arguments: --fake" in stderr.getvalue())
