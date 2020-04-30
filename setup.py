from setuptools import setup, find_packages

setup(
    name = "dmwg-data-pyutils",
    author = "Kyle Hernandez",
    author_email = "kmhernan@uchicago.edu",
    version = 0.1, 
    description = "Utility tools for data munging",
    license = "Apache 2.0",
    packages = find_packages(),
    python_requires='>=3.5',
    entry_points= ''' 
        [console_scripts]
        dmwg-data-pyutils=dmwg_data_pyutils.__main__:main
    ''', 
)
