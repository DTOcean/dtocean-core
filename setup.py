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
        if self.pytest_args:
			opts = shlex.split(self.pytest_args)
        else:
		    opts = []
		
        errno = pytest.main(opts)
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
      version='2.0.1',
      description='dtocean-core: The core component of the DTOcean tools',
      maintainer='Mathew Topper',
      maintainer_email='mathew.topper@dataonlygreater.com',
      license="GPLv3",
      packages=find_packages(),
      install_requires=[
        'aneris>=0.10',
        'basemap',
        'cmocean',
        'contours',
        'cycler',
        'descartes',
        'geoalchemy2',
        'matplotlib<2',
        'monotonic',
        'natsort',
        'netcdf4',
        'numpy',
        'openpyxl<3',
        'packaging',
        'pandas>=0.18',
        'pil',
        'polite>=0.10.0',
        'psycopg2',
        'pyproj',
        'pyshp',
        # 'PyQt4',
        'python-dateutil',
        'pyyaml',
        'ruamel.yaml',
        'scipy',
        'setuptools',
        'shapely',
        'utm',
        'xarray',
        'xlrd<2',
        'xlsxwriter<3',
        'xlwt'
      ],
      entry_points={
          'console_scripts':
              [
               'add-Te = dtocean_core.utils.hydrodynamics:add_Te_interface',
               'dtocean-core = dtocean_core.utils.execute:main_interface',
               'dtocean-core-config = '
                    'dtocean_core.utils.config:init_config_interface',
               'dtocean-database = '
                    'dtocean_core.utils.database:database_convert_interface',
               '_dtocean-optim-pos = dtocean_core.strategies.'
                                       'position_optimiser.iterator:interface'
               ]},
      package_data={'dtocean_core': ['data/yaml/*.yaml',
                                     'config/*.ini',
                                     'config/*.yaml',
                                     'strategies/position_optimiser/*.yaml']
                    },
      zip_safe=False, # Important for reading config files
      # scripts=['post-install.py'],
      tests_require=['pytest',
                     'pytest-mock'],
      cmdclass={'test': PyTest,
                'cleantest': CleanTest,
                'bootstrap': Bootstrap,
                },
      )
      