from os import path
from setuptools import setup, find_packages, Extension
import sys
import versioneer


min_pybind11_version = (2, 3)
# NOTE: This file must remain Python 2 compatible for the foreseeable future,
# to ensure that we error out properly for people with outdated setuptools
# and/or pip.
min_version = (3, 6)
if sys.version_info < min_version:
    error = """
autocorr does not support Python {0}.{1}.
Python {2}.{3} and above is required. Check your Python version like so:

python3 --version

This may be due to an out-of-date pip. Make sure you have pip >= 9.0.1.
Upgrade pip like so:

pip install --upgrade pip
""".format(*(sys.version_info[:2] + min_version))
    sys.exit(error)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(path.join(here, 'requirements.txt')) as requirements_file:
    # Parse requirements.txt, ignoring any commented-out lines.
    requirements = [line for line in requirements_file.read().splitlines()
                    if not line.startswith('#')]

extensions = []

def get_pybind11_headers():
    import pybind11
    major, minor, _ = pybind11.version_info
    if major < 2 or minor < 3:
        raise Exception(
            "autocorr requires pybind11 "
            "{0}.{1} or higher".format(*min_pybind11_version))
    return pybind11.get_include()

c_mulittau = Extension(
    'autocorr.cAutocorr',
    sources=['src/pyMultiTau.cpp', 'src/cpu_multitau.cpp' ], #  'src/fftautocorr.cpp'],
    include_dirs=[get_pybind11_headers()],
    extra_compile_args=['-std=c++11', '-fopenmp'],
    #libraries=['fftw3_omp', 'm', 'gomp']
    libraries=['gomp']
)
extensions.append(c_mulittau)

setup(
    name='autocorr',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Library for XPCS and image autocorrelation in general",
    long_description=readme,
    author="BES Data Solutions Pilot",
    author_email='dallan@bnl.gov',
    url='https://github.com/scikit-beam/autocorr',
    python_requires='>={}'.format('.'.join(str(n) for n in min_version)),
    packages=find_packages(exclude=['docs', 'tests']),
    entry_points={
        'console_scripts': [
            # 'command = some.module:some_function',
        ],
    },
    include_package_data=True,
    package_data={
        'autocorr': [
            # When adding files here, remember to update MANIFEST.in as well,
            # or else they will not be included in the distribution on PyPI!
            # 'path/to/data_file',
        ]
    },
    install_requires=requirements,
    license="BSD (3-clause)",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    ext_modules=extensions
)
