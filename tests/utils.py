"""Utilities for testing."""
import sys
import os

from io import StringIO
from contextlib import contextmanager

from dmwg_data_pyutils.logger import Logger


@contextmanager
def captured_output():
    """Captures stderr and stdout and returns them"""
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        Logger.setup_root_logger()
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def cleanup_files(files):
    """
    Takes a file or a list of files and removes them.
    """

    def _do_remove(fil):
        if os.path.exists(fil):
            os.remove(fil)

    flist = []
    if isinstance(files, list):
        flist = files[:]
    else:
        flist = [files]

    for fil in flist:
        _do_remove(fil)
