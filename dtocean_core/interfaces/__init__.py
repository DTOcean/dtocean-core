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
Created on Sat Apr 11 21:38:18 2015

@author: Winston
"""

from aneris.boundary.interface import (FileInterface,
                                       MapInterface,
                                       MetaInterface,
                                       WeightedInterface)

class ProjectInterface(MapInterface):

    '''QueryInterface subclass for database queries'''


class ModuleInterface(WeightedInterface, MapInterface):

    '''MapInterface subclass for the computational modules'''


class ThemeInterface(WeightedInterface, MapInterface):

    '''MapInterface subclass for the thematic assessement modules'''

    
class FileInputInterface(FileInterface):
    
    '''FileInterface subclass for inputting data through files'''
    
    @classmethod
    def declare_inputs(cls):

        return None
        
    @classmethod
    def declare_optional(cls):

        return None
    

class FileOutputInterface(FileInterface):
    
    '''FileInterface subclass for outputting data through files'''
    
    @classmethod
    def declare_optional(cls):

        return None
    
    @classmethod
    def declare_outputs(cls):

        return None


class PlotInterface(MetaInterface):

    '''MapInterface subclass for the thematic assessement modules'''
    
    def __init__(self):
        
        super(PlotInterface, self).__init__()
        self.fig_handle = None
        
        return

    @classmethod
    def declare_optional(cls):

        return None
    
    @classmethod
    def declare_outputs(cls):

        return None



