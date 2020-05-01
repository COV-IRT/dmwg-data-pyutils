"""Tests the `dmwg_data_pyutils.common.nextstrain` module"""
import unittest
import tempfile
import json

from dmwg_data_pyutils.common.nextstrain import NextStrainParser

from utils import captured_output, cleanup_files


class TestNextStrainParser(unittest.TestCase):
    to_remove = []

    def test_from_file_path_assert(self):
        tobj = {"_tree": 1}
        (fd, fn) = tempfile.mkstemp()
        self.to_remove.append(fn)
        with open(fn, "wt") as o:
            json.dump(tobj, o)

        with self.assertRaises(AssertionError):
            res = NextStrainParser.from_file_path(fn)

    def test_from_file_path(self):
        tobj = {"tree": 1}
        (fd, fn) = tempfile.mkstemp()
        self.to_remove.append(fn)
        with open(fn, "wt") as o:
            json.dump(tobj, o)

        res = NextStrainParser.from_file_path(fn)
        self.assertTrue(isinstance(res, NextStrainParser))
        self.assertEqual(res.obj, tobj)

    def test_get_value(self):
        dat = {'tree': {'value': 0}}
        obj = NextStrainParser(dat)
        res = obj.get_value(dat['tree'])
        self.assertEqual(res, 0)

        dat = {'tree': 0}
        res = obj.get_value(dat['tree'])
        self.assertEqual(res, 0)

    def test_parse_attrs(self):
        dat = {'tree': {'A': {'value': 0}, 'B': 0}}
        obj = NextStrainParser(dat)
        res = obj.parse_attrs(dat['tree'], ['A'])
        self.assertEqual(res, {'A': 0}) 

        res = obj.parse_attrs(dat['tree'], ['A', 'B'])
        self.assertEqual(res, {'A': 0, 'B': 0}) 

        res = obj.parse_attrs(dat['tree'], ['A', 'B', 'C'])
        self.assertEqual(res, {'A': 0, 'B': 0, 'C': None}) 

    def test_append_parents(self):
        dat = {'tree': {'name': "node0", "children": [{"name": "node1"}]}}
        obj = NextStrainParser(dat)
        obj._append_parents()
        self.assertEqual(obj.root["parent"]['name'], obj.root["name"])
        self.assertEqual(obj.root['name'], obj.root["children"][0]['parent']['name'])

    def test__flatten_nodes(self):
        dat = {'tree': {'name': "node0", "children": [{"name": "node1"}]}}
        obj = NextStrainParser(dat)
        obj._append_parents()
        res = obj._flatten_nodes()
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['name'], 'node0')
        self.assertEqual(res[1]['name'], 'node1')

    def test__mut_reduc(self):
        obj = NextStrainParser({'tree': None})
        dat = [
            {'A': [1, 2]},
            {'A': [1, 2, 3], 'B': [1]}
        ]
        res = obj._mut_reduce(dat)
        self.assertEqual(res, {'A': [1, 2, 3], 'B': [1]}) 

    def tearDown(self):
        cleanup_files(TestNextStrainParser.to_remove)
