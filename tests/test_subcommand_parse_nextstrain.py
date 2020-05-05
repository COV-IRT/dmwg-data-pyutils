"""Tests the `dmwg_data_pyutils.subcommands.ParseNextStrain` class"""
import unittest
import tempfile
import attr
import json

from dmwg_data_pyutils.subcommands import ParseNextStrain
from dmwg_data_pyutils.__main__ import main

from utils import captured_output, cleanup_files
from test_common_nextstrain import build_test_tree


@attr.s
class MockArgs:
    json_path = attr.ib()
    output = attr.ib()

class TestParseNextStrain(unittest.TestCase):
    to_remove = []

    def test_main(self):
        dat = build_test_tree()
        (in_fd, in_fn) = tempfile.mkstemp()
        self.to_remove.append(in_fn)

        with open(in_fn, "wt") as o:
            json.dump(dat, o)

        (out_fd, out_fn) = tempfile.mkstemp()
        self.to_remove.append(out_fn)

        args = MockArgs(in_fn, out_fn)
        ParseNextStrain.main(args)
        hdr = []
        with open(out_fn, 'rt') as fh:
            hdr = fh.readline().rstrip('\r\n').split('\t')
            self.assertEqual(hdr, ParseNextStrain.colnames())
            rec = dict(zip(hdr, fh.readline().rstrip('\r\n').split('\t')))
            self.assertEqual(rec['parent'], rec['name'])
            self.assertEqual(rec['sex'], 'NA')
            rec = dict(zip(hdr, fh.readline().rstrip('\r\n').split('\t')))
            self.assertEqual(rec['parent'], 'root')
            self.assertEqual(rec['name'], 'left0')
            self.assertEqual(rec['age'], '10')
            rec = dict(zip(hdr, fh.readline().rstrip('\r\n').split('\t')))
            self.assertEqual(rec['parent'], 'left0')
            self.assertEqual(rec['name'], 'left2')
            self.assertEqual(rec['age'], 'NA')
            self.assertEqual(rec['S'], 'A')
            self.assertEqual(rec['nuc'], 'B')
            rec = dict(zip(hdr, fh.readline().rstrip('\r\n').split('\t')))
            self.assertEqual(rec['parent'], 'left2')
            self.assertEqual(rec['name'], 'left3')
            rec = dict(zip(hdr, fh.readline().rstrip('\r\n').split('\t')))
            self.assertEqual(rec['parent'], 'left0')
            self.assertEqual(rec['name'], 'left1')
            rec = dict(zip(hdr, fh.readline().rstrip('\r\n').split('\t')))
            self.assertEqual(rec, {'parent': ''}) 

    def test_cli(self):
        dat = build_test_tree()
        (in_fd, in_fn) = tempfile.mkstemp()
        self.to_remove.append(in_fn)

        with open(in_fn, "wt") as o:
            json.dump(dat, o)

        (out_fd, out_fn) = tempfile.mkstemp()
        self.to_remove.append(out_fn)

        with captured_output() as (_, stderr):
            main(args=["ParseNextStrain", "--json-path", in_fn, out_fn])
        serr = stderr.getvalue()
        self.assertTrue('dmwg_data_pyutils.ParseNextStrain' in serr)
        self.assertTrue('Found pre-existing JSON, skipping download' in serr)
        self.assertTrue('Completed. Parsed 5 records.' in serr)
        self.assertTrue('[dmwg_data_pyutils.main] - Finished!' in serr)

    def tearDown(self):
        cleanup_files(TestParseNextStrain.to_remove)
