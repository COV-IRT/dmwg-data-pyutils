"""Module for traversing NextStrain JSON trees.

@author: Kyle Hernandez <kmhernan@uchicago.edu>
"""
import json
import gzip
import urllib.request
from typing import List, Dict, Any, Optional, Union, Callable

from dmwg_data_pyutils.common.logger import Logger
from dmwg_data_pyutils.common.io import load_json_file


NEXTSTRAIN_JSON_URL = "http://data.nextstrain.org/ncov_global.json"
# TODO - infer from json metadata?
NODE_ATTRS = [
    "country",
    "division",
    "location",
    "region",
    "clade_membership",
    "sex",
    "age",
    "div",
    "recency",
    "num_date",
]
MUTATION_KEYS = [
    "E",
    "M",
    "N",
    "ORF10",
    "ORF14",
    "ORF1a",
    "ORF1b",
    "ORF3a",
    "ORF6",
    "ORF7a",
    "ORF7b",
    "ORF8",
    "ORF9b",
    "S",
    "nuc",
]


class NextStrainParser:
    """
    Caution, this implementation will actually *mutate* the JSON object
    (`self.obj`). So my current usage in the subcommand.ParseNextStrain
    to write out the json object to a file is dangerous. Once I use the
    `mutation_traversal_generator` the object is modified.

    Things to potentially do differently in future:
    1. Make seprate class for loading the Nextstrain JSON.
    2. Separate "traversal" classes from this, and only pass *copy* of json object.
    """
    def __init__(self, obj: Dict[str, Any]):
        """Initialize the NextStrainTree by passing the deserialized
        JSON object.
        """
        self.logger = Logger.get_logger("NextStrainParser")
        self.obj = obj
        assert "tree" in self.obj

    @property
    def root(self) -> Dict[str, Any]:
        """Root of tree"""
        return self.obj["tree"]

    @classmethod
    def from_file_path(cls, file_path: str) -> object:
        """Initialize from file path"""
        dat = load_json_file(file_path)
        return cls(dat)

    @classmethod
    def from_url(cls, other_url: Optional[str] = None) -> object:
        """Initialize from URL. By default uses NEXTSTRAIN_JSON_URL."""
        _url = NEXTSTRAIN_JSON_URL if other_url is None else other_url
        dat = None
        with urllib.request.urlopen(_url) as f:
            # want to check if this is gzip, so check for magic.
            # right now it is gzipped.
            _obj = f.read()
            if _obj[:2] == b"\x1f\x8b":
                dat = json.loads(gzip.decompress(_obj))
            else:
                dat = json.loads(_obj)
        return cls(dat)

    def mutation_traversal_generator(self) -> Dict[str, Any]:
        """
        Public mutation traversal generator. Flattens into per-node
        records containing patient metadata and cumulative viral
        mutations.
        """
        self._append_parents()
        for node in self._flatten_nodes():
            dat = {"parent": node["parent"]["name"], "name": node["name"]}
            dat.update(self.parse_attrs(node["node_attrs"], NODE_ATTRS))
            mutations = self._collect_mutations(node)
            dat.update(self.parse_attrs(mutations, MUTATION_KEYS))
            yield dat

    def _append_parents(self) -> None:
        """
        Traverses the tree and adds in the parents. This *mutates*
        the object! This is adapted from Trevor Bradford and Richard Neher's
        javascript work in auspice (https://github.com/nextstrain/auspice).
        """
        self.root["parent"] = self.root
        stack = [self.root]
        while len(stack) != 0:
            node = stack.pop()
            if node.get("children"):
                for child in node["children"]:
                    child["parent"] = node
                    stack.append(child)

    def _flatten_nodes(self) -> List[Dict[str, Any]]:
        """
        Traverses the tree and returns a list of ordered nodes. 
        This is adapted from Trevor Bradford and Richard Neher's
        javascript work in auspice (https://github.com/nextstrain/auspice).
        """
        stack = [self.root]
        array = []
        dic = {}
        while len(stack) != 0:
            node = stack.pop()
            name = node["name"]
            if name not in dic:
                dic[name] = True
                array.append(node)

            if node.get("children"):
                for child in node["children"]:
                    child["parent"] = node
                    stack.append(child)
        return array

    def get_value(self, item: Any) -> Any:
        """
        Parse the value of an item in the node/branch attr
        """
        if isinstance(item, dict):
            return item["value"]
        else:
            return item

    def parse_attrs(self, attrs: Dict[str, Any], key_list: List[str]) -> Dict[str, Any]:
        """
        Parses the attr values into a dict determined by
        key_list. 
        """
        curr = {i: self.get_value(attrs.get(i)) for i in key_list}
        return curr

    def _collect_mutations(
        self,
        node: Dict[str, Any],
        muts: Optional[List[Dict[str, Union[str, List[str]]]]] = None,
    ) -> Dict[str, List[str]]:
        """
        Traverses all the way back to root from current node, collecting
        mutations.
        """
        if muts is None:
            muts = []
        parent = node["parent"]
        if node["name"] == parent["name"]:
            return self._mut_reduce(muts)
        muts.append(node.get("branch_attrs", {}).get("mutations", {}))
        return self._collect_mutations(parent, muts)

    def _mut_reduce(
        self, muts: List[Dict[str, Union[str, List[str]]]]
    ) -> Dict[str, List[str]]:
        """
        Gets the unique set of mutations after traversal.
        """
        dic = {}
        for d in muts:
            for k in d:
                if k not in dic:
                    dic[k] = []
                dic[k].extend(d[k])
        for k in dic:
            dic[k] = sorted(list(set(dic[k])))
        return dic
