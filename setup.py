import os
import re
import sys
import subprocess
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from multitau.__init__ import __version__

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError('cmake is not installed. Install cmake and try again')

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]
        cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
        build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp) 
       

def find_version():
        with open('multitau/__init__.py', 'r') as version_file:
            buf = version_file.read()
            version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", buf, re.M)
            if version_match:
                return version_match.group(1)
            raise RuntimeError("Unable to find version string.")

setup(
    name = 'multitau',
    version = find_version(),
    description = 'Multi-tau autocorrelation for Synchroton data',
    author = 'Dinesh Kumar',
    author_email = 'dkumar@lbl.gov',
    license = 'BSD',
    keywords = 'synchrotron xpcs',
    install_requires = [ 'pybind11' ],
    ext_modules = [ CMakeExtension('multitau.cMultitau', 'src') ],
    cmdclass = dict(build_ext = CMakeBuild),
    packages = [ 'multitau' ]
)
