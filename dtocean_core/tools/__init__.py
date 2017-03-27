
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

import abc

from copy import deepcopy

from polite.abc import abstractclassmethod

from ..interfaces import MapInterface


class Tool(MapInterface):

    '''The base abstract class for all tool classes'''
        
    @abc.abstractmethod
    def configure(self):

        '''The configure method is collect information required for executing
        the tool.
        '''

        return
        
    def get_config(self):
        
        return deepcopy(self._config)
        
    def set_config(self, config_dict):
        
        self._config = config_dict
        
        return

