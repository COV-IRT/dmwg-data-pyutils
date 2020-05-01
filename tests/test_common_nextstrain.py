"""Tests the `dmwg_data_pyutils.common.nextstrain` module"""
import unittest
import tempfile
import json

from dmwg_data_pyutils.common.nextstrain import NextStrainParser

from utils import captured_output, cleanup_files


class TestNextStrainParser(unittest.TestCase):
    to_remove = []

    def test_from_file_path(self):
        tobj = {"tree": 1}
        (fd, fn) = tempfile.mkstemp()
        self.to_remove.append(fn)
        with open(fn, "wt") as o:
            json.dump(tobj, o)

        res = NextStrainParser.from_file_path(fn)
        self.assertTrue(isinstance(res, NextStrainParser))
        self.assertEqual(res.obj, tobj)

    def tearDown(self):
        cleanup_files(TestNextStrainParser.to_remove)
