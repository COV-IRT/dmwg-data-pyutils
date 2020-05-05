"""Tests the `dmwg_data_pyutils.common.nextstrain` module"""
import unittest
import tempfile
import json

from dmwg_data_pyutils.common.nextstrain import NextStrainParser

from utils import captured_output, cleanup_files


def get_basic_node(name):
    """Utility function to generate basic node template"""
    curr = {"name": name, "node_attrs": {}, "branch_attrs": {}, "children": []}
    return curr


def build_test_tree():
    """Utility to get small test tree"""
    root = get_basic_node("root")

    left = get_basic_node("left0")
    left["branch_attrs"]["mutations"] = {"S": ["A"]}
    left["node_attrs"]["age"] = {"value": "10"}

    left_1 = get_basic_node("left1")
    del left_1["children"]
    left["children"].append(left_1)

    left_2 = get_basic_node("left2")
    left_2["branch_attrs"]["mutations"] = {"nuc": ["B"]}
    left_3 = get_basic_node("left3")
    del left_3["children"]
    left_2["children"].append(left_3)
    left["children"].append(left_2)
    root["children"].append(left)

    tree = {"tree": root}
    return tree


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
        dat = {"tree": {"value": 0}}
        obj = NextStrainParser(dat)
        res = obj.get_value(dat["tree"])
        self.assertEqual(res, 0)

        dat = {"tree": 0}
        res = obj.get_value(dat["tree"])
        self.assertEqual(res, 0)

    def test_parse_attrs(self):
        dat = {"tree": {"A": {"value": 0}, "B": 0}}
        obj = NextStrainParser(dat)
        res = obj.parse_attrs(dat["tree"], ["A"])
        self.assertEqual(res, {"A": 0})

        res = obj.parse_attrs(dat["tree"], ["A", "B"])
        self.assertEqual(res, {"A": 0, "B": 0})

        res = obj.parse_attrs(dat["tree"], ["A", "B", "C"])
        self.assertEqual(res, {"A": 0, "B": 0, "C": None})

    def test_append_parents(self):
        dat = {"tree": {"name": "node0", "children": [{"name": "node1"}]}}
        obj = NextStrainParser(dat)
        obj._append_parents()
        self.assertEqual(obj.root["parent"]["name"], obj.root["name"])
        self.assertEqual(obj.root["name"], obj.root["children"][0]["parent"]["name"])

    def test__flatten_nodes(self):
        dat = {"tree": {"name": "node0", "children": [{"name": "node1"}]}}
        obj = NextStrainParser(dat)
        obj._append_parents()
        res = obj._flatten_nodes()
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]["name"], "node0")
        self.assertEqual(res[1]["name"], "node1")

    def test__mut_reduce(self):
        obj = NextStrainParser({"tree": None})
        dat = [{"A": [1, 2]}, {"A": [1, 2, 3], "B": [1]}]
        res = obj._mut_reduce(dat)
        self.assertEqual(res, {"A": [1, 2, 3], "B": [1]})

    def test__collect_mutations(self):
        dat = build_test_tree()
        exp = {
            "root": {},
            "left0": {"S": ["A"]},
            "left2": {"nuc": ["B"], "S": ["A"]},
            "left3": {"nuc": ["B"], "S": ["A"]},
            "left1": {"S": ["A"]},
        }
        obj = NextStrainParser(dat)
        obj._append_parents()
        mdict = {}
        for node in obj._flatten_nodes():
            key = node["name"]
            self.assertTrue(key not in mdict)
            mdict[key] = obj._collect_mutations(node)

        self.assertEqual(mdict, exp)

    def test_mutation_traversal_generator(self):
        dat = build_test_tree()
        obj = NextStrainParser(dat)
        gen = obj.mutation_traversal_generator()
        curr = next(gen)
        self.assertEqual(curr["name"], curr["parent"])
        self.assertIsNone(curr["age"])
        self.assertIsNone(curr["S"])
        curr = next(gen)
        self.assertEqual(curr["name"], "left0")
        self.assertEqual(curr["parent"], "root")
        self.assertEqual(curr["age"], "10")
        self.assertEqual(curr["S"], ["A"])
        curr = next(gen)
        self.assertEqual(curr["name"], "left2")
        self.assertEqual(curr["parent"], "left0")
        self.assertIsNone(curr["age"])
        self.assertEqual(curr["S"], ["A"])
        self.assertEqual(curr["nuc"], ["B"])
        curr = next(gen)
        self.assertEqual(curr["name"], "left3")
        self.assertEqual(curr["parent"], "left2")
        self.assertIsNone(curr["age"])
        self.assertEqual(curr["S"], ["A"])
        self.assertEqual(curr["nuc"], ["B"])
        curr = next(gen)
        self.assertEqual(curr["name"], "left1")
        self.assertEqual(curr["parent"], "left0")
        self.assertIsNone(curr["age"])
        self.assertEqual(curr["S"], ["A"])
        self.assertIsNone(curr["nuc"])
        with self.assertRaises(StopIteration):
            curr = next(gen)

    def tearDown(self):
        cleanup_files(TestNextStrainParser.to_remove)
