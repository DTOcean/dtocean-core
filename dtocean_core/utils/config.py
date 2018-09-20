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

"""
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import sys
import logging
import argparse

from polite.paths import (ObjDirectory,
                          UserDataDirectory,
                          DirectoryMap)

from .. import start_logging

# Set up logging
module_logger = logging.getLogger(__name__)


def init_config(logging=False, database=False, files=False, overwrite=False):
    
    """Copy config files to user data directory"""
    
    if not any([logging, database, files]): return
    
    objdir = ObjDirectory(__name__, "..", "config")
    datadir = UserDataDirectory("dtocean_core", "DTOcean", "config")
    dirmap = DirectoryMap(datadir, objdir)
    
    if logging: dirmap.copy_file("logging.yaml", overwrite=overwrite)
    if database: dirmap.copy_file("database.yaml", overwrite=overwrite)
    if files: dirmap.copy_file("files.ini", overwrite=overwrite)
            
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
    
    parser.add_argument("--logging",
                        help=("copy logging configuration"),
                        action="store_true")
    
    parser.add_argument("--database",
                        help=("copy database configuration"),
                        action="store_true")
    
    parser.add_argument("--files",
                        help=("copy log and debug files location "
                              "configuration"),
                        action="store_true")
    
    parser.add_argument("--overwrite",
                        help=("overwrite any existing configuration files"),
                        action="store_true")
    
    args = parser.parse_args(args)
                        
    logging = args.logging
    database = args.database
    files = args.files
    overwrite = args.overwrite
    
    return logging, database, files, overwrite


def init_config_interface():
    
    '''Command line interface for init_config.'''
    
    start_logging()
    
    logging, database, files, overwrite = init_config_parser(sys.argv[1:])
    dir_path = init_config(logging=logging,
                           database=database,
                           files=files,
                           overwrite=overwrite)
    
    if dir_path is not None:
        log_msg =  "Copying configuration files to {}".format(dir_path)
        module_logger.info(log_msg)

    return
