import os
import re
import sys
import subprocess
from setuptools import setup, Extension

def find_version():
        with open('multitau/__init__.py', 'r') as version_file:
            buf = version_file.read()
            version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", buf, re.M)
            if version_match:
                return version_match.group(1)
            raise RuntimeError("Unable to find version string.")

def get_headers():
    try: 
        import pybind11
    except ImportError as e:
        print('pybind11 is requred to build multi-threaded extension. Try installing it ..')
        print('pip install pybind11')
        raise e

    major, minor, _ = pybind11.version_info
    if major < 2 or minor < 3:
        print('pybind11 version needs to be at least 2.3')
        raise Exception('pybind11 upgrade needed')
    return pybind11.get_include()

ext = Extension('multitau.cMultitau',
                sources = [
                    'src/pyMultiTau.cpp',
                    'src/cpu_multitau.cpp'
                ],
                include_dirs = [ get_headers() ],
                extra_compile_args = [ '-std=c++11', '-fopenmp' ],
                libraries = [ 'gomp' ]
                )
setup(
    name = 'multitau',
    version = find_version(),
    description = 'Multi-tau autocorrelation for Synchroton data',
    author = 'Dinesh Kumar',
    author_email = 'dkumar@lbl.gov',
    license = 'BSD',
    keywords = 'synchrotron xpcs',
    install_requires = [ 'pybind11' ],
    ext_modules = [ ext ],
    packages = [ 'multitau' ]
)
