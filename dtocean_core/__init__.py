# -*- coding: utf-8 -*-

#    Copyright (C) 2016 'Mathew Topper, Vincenzo Nava, David Bould, Rui Duarte,
#                       'Francesco Ferri, Adam Collin'
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The core component of the dtocean project.

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

import os
import sys
import argparse
import logging
from pkg_resources import get_distribution

from polite.configuration import ReadINI
from polite.paths import (Directory,
                          ObjDirectory,
                          UserDataDirectory,
                          DirectoryMap)
from polite.configuration import Logger

__version__ = get_distribution('dtocean-core').version


# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())


def start_logging():

    """Start python logger"""

    # Pick up the configuration from the user directory if it exists
    userdir = UserDataDirectory("dtocean_core", "DTOcean", "config")
            
    if userdir.isfile("files.ini") and userdir.isfile("logging.yaml"):
        configdir = userdir
    else:
        configdir = ObjDirectory("dtocean_core", "config")
    
    files_ini = ReadINI(configdir, "files.ini")
    files_config = files_ini.get_config()
    
    appdir_path = userdir.get_path("..")
    log_folder = files_config["logs"]["path"]
    log_path = os.path.join(appdir_path, log_folder)
    logdir = Directory(log_path)
    
    log = Logger(configdir)
    log_config_dict = log.read()
    
    # Update the file logger if present
    if "file" in log_config_dict["handlers"]:
        log_filename = log_config_dict["handlers"]["file"]["filename"]
        log_path = logdir.get_path(log_filename)
        log_config_dict["handlers"]["file"]["filename"] = log_path
        logdir.makedir()
    
    log.configure_logger(log_config_dict)
    log.add_named_logger("dtocean_core",
                         info_message="Begin logging for dtocean_core")
    
    return


def init_config(overwrite=False):
    
    """Copy config files to user data directory"""
    
    objdir = ObjDirectory(__name__, "config")
    datadir = UserDataDirectory("dtocean_core", "DTOcean", "config")
    dirmap = DirectoryMap(datadir, objdir)
    
    dirmap.copy_all(overwrite=overwrite)
    
    return datadir.get_path()


def init_config_parser(args):
    
    '''Command line parser for init_config.
    
    Example:
    
        To get help::
        
            $ dtocean-core-config -h
            
    '''
    
    epiStr = ('Mathew Topper (c) 2017.')
              
    desStr = ("Copy user modifiable configuration files to "
              "User\AppData\Roaming\DTOcean\dtocean-core\config")

    parser = argparse.ArgumentParser(description=desStr,
                                     epilog=epiStr)
    
    parser.add_argument("--overwrite",
                        help=("overwrite any existing configuration files"),
                        action="store_true")
                        
    args = parser.parse_args(args)
    overwrite = args.overwrite
    
    return overwrite


def init_config_interface():
    
    '''Command line interface for init_config.'''
    
    overwrite = init_config_parser(sys.argv[1:])
    dir_path = init_config(overwrite=overwrite)
    print "Copying configuration files to {}".format(dir_path)

    return
