# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Mathew Topper
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

import logging

from . import Strategy
from .position_optimiser import main


# Set up logging
module_logger = logging.getLogger(__name__)


class AdvancedPosition(Strategy):
    
    """
    """
    
    @classmethod
    def get_name(cls):
        
        return "Advanced Positioning"
    
    def configure(self, config_path):
        
        config_dict = {"config_path": config_path}
        self.set_config(config_dict)
        
        return
    
    def get_variables(self):
        
        set_vars = ['options.user_array_layout',
                    'project.rated_power']
        
        return set_vars
    
    def execute(self, core, project):
        
        # Check the project is active and record the simulation number
        sim_index = project.get_active_index()
        
        if sim_index is None:
            
            errStr = "Project has not been activated"
            raise RuntimeError(errStr)
        
        if "Default" not in project.get_simulation_titles():
            
            err_msg = ('The posisiton optimiser requires a simulation with '
                       'title "Default"')
            raise RuntimeError(err_msg)
        
        if project.get_simulation_title() != "Default":
            
            log_str = 'Setting active simulation to "Default"'
            module_logger.info(log_str)
            
            project.set_active_index(title="Default")
        
        es = main(self._config["config_path"],
                  core=core,
                  project=project)
        
        return es

