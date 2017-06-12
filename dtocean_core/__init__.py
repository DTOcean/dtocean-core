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

import logging
from pkg_resources import get_distribution

from polite.paths import ObjDirectory, UserDataDirectory, DirectoryMap
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


def init_config():
    
    """Copy config files to user data directory"""
    
    objdir = ObjDirectory(__name__, "config")
    datadir = UserDataDirectory("dtocean_core", "DTOcean", "config")
    dirmap = DirectoryMap(datadir, objdir)
    
    dirmap.copy_all()
    
    return


def start_logging():

    """Start python logger"""

    datadir = UserDataDirectory("dtocean_core", "DTOcean", "config")

    log = Logger(datadir)
    log("dtocean_core", info_message="Begin logging for dtocean_core.")
    
    return

