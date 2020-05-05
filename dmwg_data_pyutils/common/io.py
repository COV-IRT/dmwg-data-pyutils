"""I/O common utilities.

@author: Kyle Hernandez <kmhernan@uchicago.edu>
"""
import json
from typing import Union, Dict, List, Any


def load_json_file(file_path: str) -> Union[Dict[str, Any], List[Any]]:
    """
    Helper function to open a JSON file and load.
    """
    dat = None
    with open(file_path, "rt") as fh:
        dat = json.load(fh)
    return dat
