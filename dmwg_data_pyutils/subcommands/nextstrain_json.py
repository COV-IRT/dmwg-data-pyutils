"""Extracts patient metadata, viral divergence, and
viral mutations from the nextstrain JSON file.

@author: Kyle Hernandez <kmhernan@uchicago.edu>
"""
import os
import gzip

from typing import Tuple, Optional, List

from dmwg_data_pyutils.logger import Logger 
from dmwg_data_pyutils.subcommands import Subcommand
from dmwg_data_pyutils.common.io import load_json_file 
from dmwg_data_pyutils.types import ArgParserT, NamespaceT, LoggerT 
from dmwg_data_pyutils.common.nextstrain import NextStrainParser, NODE_ATTRS, MUTATION_KEYS


class ParseNextstrain(Subcommand):
    @classmethod
    def __add_arguments__(cls, parser: ArgParserT):
        """Add the arguments to the parser"""
        parser.add_argument("--json-path", type=str, default=None,
                            help="Optional path to Nextstrain JSON. If it "
                                 "exists, then a new version will not be "
                                 "downloaded from Nextstrain. If it doesn't "
                                 "exist, the file will be downloaded to this "
                                 "location. If no path is given, the JSON file "
                                 "will not be saved locally.")
        parser.add_argument("output", type=str,
                            help="Path to output TSV file.")

    @classmethod
    def main(cls, options: NamespaceT) -> None:
        """
        Entrypoint for ParseNextstrain.
        """
        logger = Logger.get_logger(cls.__tool_name__())
        logger.info(cls.__get_description__())

        # Get json 
        run_download, dl_location = cls._setup_download(options.json_path, logger)

        nstree = cls._load_nextstrain_json(run_download, dl_location)

        logger.info("Parsed data will be written to {}".format(options.output))
        ofunc = gzip.open if options.output.endswith('.gz') else open
        total = 0
        with ofunc(options.output, 'wt') as o:
            o.write("\t".join(cls.colnames()) + "\n")
            for record in nstree.mutation_traversal_generator():
                if total > 0 and total % 1000 == 0:
                    self.logger.info("Parsed {} records.".format(total))
                cls._write_record(record, o)
                total += 1
        logger.info("Completed. Parsed {} records.".format(total))

    @classmethod
    def colnames(cls) -> List[str]:
        """Returns a list of the column names"""
        return ["parent", "name"] + NODE_ATTRS + MUTATION_KEYS
 
    @classmethod
    def _write_record(cls, record: Dict[str, Any], o: TextIO) -> None:
        """Formats and writes mutation traversal record to file."""
        row = []
        for key in cls.colnames():
            if record[key] is None:
                row.append("NA")
            elif isinstance(record[key], list):
                row.append(",".join([str(i) for i in record[key]]))
            else:
                row.append(str(record[key]))
        o.write("\t".join(row) + '\n')

    @classmethod
    def _setup_download(cls, json_path: Optional[str], logger: LoggerT) -> Tuple[bool, Optional[str]]: 
        """Determines if download needs to happen and where it should go.""" 
        run_download = True 
        dl_location = json_path
        if json_path and os.path.isfile(json_path):
            logger.info("Found pre-existing JSON, skipping download")
            run_download = False
        elif json_path is not None:
            logger.info("Downloading JSON to {}".format(json_path))
            dl_location = json_path

        return run_download, dl_location

    @classmethod
    def _load_nextstrain_json(cls, run_download: bool, dl_location: Optional[str]) -> NextStrainParser: 
        """
        Performs the actual loading of the JSON file into a `NextStrainParser`
        instance.
        """
        if run_download:
            ns_obj = NextStrainTree.from_url()
            if dl_location:
                with open(dl_location, 'wt') as o:
                    json.dump(ns_obj.obj, o, sort_keys=True, indent=2)
        else:
            ns_obj = NextStrainTree.from_file_path(dl_location)

        return ns_obj 

    @classmethod
    def __get_description__(cls):
        """
        Tool description.
        """ 
        return ("Extracts patient metadata, viral divergence, and "
                "viral mutations from the nextstrain JSON file.")
