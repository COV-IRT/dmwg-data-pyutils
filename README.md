# dmwg-data-pyutils

Data modeling WG Python CLI for data utils.

# Install

It is always preferred to install within a virtual environment.

*Requirements*

* `python >= 3.5`

```
git clone git@github.com:COV-IRT/dmwg-data-pyutils.git
cd dmwg-data-pyutils
python3 -m virtualenv venv
source venv/bin/activate

pip install .
```

# Usage

This tool has one entrypoint `dmwg-data-pyutils` with several
subcommands.

## `ParseNextStrain`

This subcommands parses the NextStrain JSON file into flat TSV collecting patient metadata and
cummulative mutations.

```
dmwg-data-pyutils ParseNextStrain -h
usage: DMWG Data Utils ParseNextStrain [-h] [--json-path JSON_PATH] output

Extracts patient metadata, viral divergence, and viral mutations from the
nextstrain JSON file.

positional arguments:
  output                Path to output TSV file.

optional arguments:
  -h, --help            show this help message and exit
  --json-path JSON_PATH
                        Optional path to Nextstrain JSON. If it exists, then a
                        new version will not be downloaded from Nextstrain. If
                        it doesn't exist, the file will be downloaded to this
                        location. If no path is given, the JSON file will not
                        be saved locally.
```

# How to add a new tool

* All new subcommands should be placed within `dmwg_data_pyutils/subcommands`
* Inherit from the abstract base class `dmwg_data_pyutils.subcommands.Subcommand`
* Add argument parser elements to classmethod `__add_arguments__(cls, parser: ArgParserT)`
* Add string description of tool functionality to classmethod `__get_description__(cls)`
* Define main tool logic in classmethod `main(cls, options: NamespaceT)`
* Add class import to `dmwg_data_pyutils.subcommands.__init__`
* Import class in `dmwg_data_pyutils.__main__` (e.g., `from dmwg_data_pyutils.subcommands import MyClass`)
* Add subparsers in `dmwg_data_pyutils.__main__.main(args=None, extra_subparser=None)` (e.g., `MyClass.add(subparsers=subparsers)`) 
* Write tests please :-)

*Note: The subcommand's class name will be used as the subcommand name*
