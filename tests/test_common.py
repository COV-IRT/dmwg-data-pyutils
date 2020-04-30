"""Tests the `dmwg_data_pyutils.common` module"""
import unittest
import tempfile
import json

from dmwg_data_pyutils.common.io import load_json_file
from dmwg_data_pyutils.common.nextstrain import NextStrainParser

from utils import captured_output, cleanup_files


class TestCommonIO(unittest.TestCase):
    def test_load_json_file(self):
        tobj = {"tree": 1}
        (fd, fn) = tempfile.mkstemp()
        try:
            with open(fn, "wt") as o:
                json.dump(tobj, o)

            res = load_json_file(fn)
            self.assertEqual(res, tobj)
        finally:
            cleanup_files(fn)


class TestNextStrainParser(unittest.TestCase):
    def test_from_file_path(self):
        tobj = {"tree": 1}
        (fd, fn) = tempfile.mkstemp()
        try:
            with open(fn, "wt") as o:
                json.dump(tobj, o)

            res = NextStrainParser.from_file_path(fn)
            self.assertTrue(isinstance(res, NextStrainParser))
            self.assertEqual(res.obj, tobj)
        finally:
            cleanup_files(fn)
