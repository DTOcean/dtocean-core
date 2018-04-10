
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

# Set up logging
import logging

module_logger = logging.getLogger(__name__)

from . import Strategy

class BasicStrategy(Strategy):
    
    """A basic strategy which will run all selected modules and themes in
    sequence."""
        
    @classmethod         
    def get_name(cls):

        return "Basic"
        
    def configure(self, kwargs=None):
        
        """Does nothing in this case"""

        return
        
    def get_variables(self):
        
        return None
        
    def execute(self, core, project):
        
        # Check the project is active and record the simulation number
        sim_index = project.get_active_index()
        
        if sim_index is None:
            
            errStr = "Project has not been activated."
            raise RuntimeError(errStr)
            
        self.add_simulation_index(sim_index)
        
        current_mod = self._module_menu.get_current(core, project)
        
        while current_mod:
            
            self._module_menu.execute_current(core,
                                              project,
                                              allow_unavailable=True,
                                              force_themes_completed=True)
            current_mod = self._module_menu.get_current(core, project)
            
        return
        
