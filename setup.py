# -*- coding: utf-8 -*-

import os
import sys
import glob
import shutil

from distutils.cmd import Command
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
    
        #import here, cause outside the eggs aren't loaded
        import pytest
        import shlex
        
        # Pickle data files and move to test directory
        data_dir = "test_data"
        test_dir = "tests"
        search_path = os.path.join(data_dir, "*.py")
        test_data_files = glob.glob(search_path)
                
        for test_data_path in test_data_files:
        
            src_path_root = os.path.splitext(test_data_path)[0]
            src_path = "{}.pkl".format(src_path_root)
            src_file = os.path.split(src_path)[1]
            dst_path = os.path.join(test_dir, src_file)
            dst_path = os.path.abspath(dst_path)

            sys_command = "python {}".format(test_data_path)
            os.system(sys_command)
            
            print "copy test data: {}".format(dst_path)
            shutil.copyfile(src_path, dst_path)
            
        # Move yaml definitions to test directory
        search_path = os.path.join(data_dir, "*.yaml")
        test_def_files = glob.glob(search_path)
        
        for test_def_path in test_def_files:
        
            src_file = os.path.split(test_def_path)[1]
            dst_path = os.path.join(test_dir, src_file)
            dst_path = os.path.abspath(dst_path)

            print "copy data definitions: {}".format(dst_path)
            shutil.copyfile(test_def_path, dst_path)
        
        # Run the tests
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


class CleanTest(Command):

    description = 'clean test files'
    clean_list = ['.pyc', '.pkl']
    user_options = []
    exclude_list = ['.eggs', '.git', '.idea', '.hg', '__pycache__', 'test_data']
     
    def initialize_options(self):
        pass
     
    def finalize_options(self):
        pass
     
    def run(self):
        print "start cleanup test files"
        for clean_path in self.pickup_clean():
            print "remove {}: {}".format(os.path.splitext(clean_path)[1],
                                         clean_path)
            os.remove(clean_path)
        print "end cleanup"
     
    def is_exclude(self, path):
        for item in CleanTest.exclude_list:
            if path.find(item) != -1:
                return True
        return False
     
    def is_clean(self, path):
        return path.endswith(tuple(CleanTest.clean_list))
     
    def pickup_clean(self):
        for root, dirs, files in os.walk(os.getcwd()):
            if self.is_exclude(root):
                continue
            for fname in files:
                if not self.is_clean(fname):
                    continue
                yield os.path.join(root, fname)

            
class Bootstrap(Command):
    
    user_options = []

    def initialize_options(self):
        """Abstract method that is required to be overwritten"""

    def finalize_options(self):
        """Abstract method that is required to be overwritten"""

    def run(self):
        
        # Setup paths
        xl_dir = "dds"
        yaml_dir = "dtocean_core\data\yaml"
        ignore_column = "Comments"
        sys_command = "bootstrap-dds -v -i {} -o {} {} ".format(ignore_column,
                                                                yaml_dir,
                                                                xl_dir)
        # Convert the files
        errno = os.system(sys_command)
        sys.exit(errno)


setup(name='dtocean-core',
      version='1.1.dev0',
      description='dtocean-core: The core component of the DTOcean tools',
      author=('Mathew Topper, '
              'Vincenzo Nava, '
              'David Bould, '
              'Rui Duarte, '
              'Francesco Ferri, '
              'Adam Collin'),
      author_email=('damm_horse@yahoo.co.uk, '
                    'vincenzo.nava@tecnalia.com, '
                    'david.bould@ed.ac.uk, '
                    'Rui.Duarte@france-energies-marines.org, '
                    'ff@civil.aau.dk, '
                    'acollin@staffmail.ed.ac.uk'),
      license="GPLv3",
      packages=find_packages(),
      install_requires=[
        'aneris>=0.9',
        'basemap',
        'dtocean-hydrodynamics>=1.0',
        'dtocean-electrical>=1.0',
        'dtocean-moorings>=1.0',
        'dtocean-installation>=1.0',
        'dtocean-maintenance>=1.0',
        'dtocean-economics>=1.0',
        'dtocean-reliability>=1.0',
        'dtocean-environment>=1.0',
        'geoalchemy2',
        'matplotlib',
        'netcdf4',
        'numpy',
        'openpyxl',
        'pandas>=0.18',
        'pil',
        'polite>=0.9,<0.10',
        'psycopg2',
        'pyproj',
        'python-dateutil',
        'pyyaml',
        'setuptools',
        'shapely',
        'xarray',
        'xlrd',
        'xlwt'
      ],
      entry_points={
          'console_scripts':
              [
               'add-Te = dtocean_core.utils.hydrodynamics:add_Te_interface',
               ]},
      package_data={'dtocean_core': ['data/yaml/*.yaml',
                                     'interfaces/reliability_data/*.yaml',
                                     'config/*.ini',
                                     'config/*.yaml']
                    },
      zip_safe=False, # Important for reading config files
      # scripts=['post-install.py'],
      tests_require=['pytest'],
      cmdclass = {'test': PyTest,
                  'cleantest': CleanTest,
                  'bootstrap': Bootstrap,
                  },
      )
      