"""
Main entrypoint for all dmwg-data-pyutils. 
"""
import argparse
import datetime
import sys

from dmwg_data_pyutils.logger import Logger


def main(args=None, extra_subparser=None):
    """
    The main method for dmwg-data-pyutils.
    """
    # Setup logger
    Logger.setup_root_logger()

    logger = Logger.get_logger("main")

    # Get args
    p = argparse.ArgumentParser("DMWG Data Utils")
    subparsers = p.add_subparsers(dest="subcommand")
    subparsers.required = True

    if extra_subparser:
        extra_subparser.add(subparsers=subparsers)

    options = p.parse_args(args)

    # Run
    options.func(options)

    # Finish
    logger.info("Finished!")

if __name__ == '__main__':
    main()
