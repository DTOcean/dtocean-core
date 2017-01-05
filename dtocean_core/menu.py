
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
import warnings

module_logger = logging.getLogger(__name__)

import os
import abc
import yaml

from aneris.utilities.database import check_host_port
from polite.paths import ObjDirectory, UserDataDirectory, DirectoryMap
from polite.configuration import ReadYAML

from .core import Connector
from .pipeline import Tree, set_output_scope

class ConnectorMenu(object):
    
    """Hub agnostic superclass for menu functions"""

    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def _hub_name(self):

        return 'Should never get here'

    def get_available(self, core, 
                            project):

        """Return all the available modules found as plugins"""
        
        connector = self._get_connector(project)

        names = connector.get_available_interfaces(core,
                                                   project)

        return names

    def activate(self, core,
                       project,
                       interface_name):

        """Move an interface into the pipelines list."""
        
        connector = self._get_connector(project)

        # Store an object of the interface
        connector.activate_interface(core,
                                     project,
                                     interface_name)

        return

    def get_active(self, core, project):
        
        connector = self._get_connector(project)

        active_interface_names = connector.get_active_interface_names(core,
                                                                      project)

        return active_interface_names
        
    def get_current(self, core, project):
        
        connector = self._get_connector(project)
        
        interface_name = connector.get_current_interface_name(core, project)

        return interface_name
        
    def get_scheduled(self, core, project):
        
        connector = self._get_connector(project)
        
        interface_names = connector.get_scheduled_interface_names(core,
                                                                  project)

        return interface_names
        
    def get_completed(self, core, project):
        
        connector = self._get_connector(project)
        
        interface_names = connector.get_completed_interface_names(core,
                                                                  project)

        return interface_names
        
    def is_executable(self, core,
                            project,
                            interface_name,
                            allow_unavailable=False):
        
        connector = self._get_connector(project)

        core.unmask_states(project)
        result = connector.is_interface_executable(core,
                                                   project,
                                                   interface_name,
                                                   allow_unavailable)

        return result
        
    def is_completed(self, core,
                           project,
                           interface_name):
        
        connector = self._get_connector(project)

        result = connector.is_interface_completed(core,
                                                  project,
                                                  interface_name)

        return result
        
    def _get_connector(self, project, hub_name=None):
                
        if hub_name is None: hub_name = self._hub_name
        
        simulation = project.get_simulation()
        hub_ids = simulation.get_hub_ids()
        
        if hub_ids is None or hub_name not in hub_ids:
            
            errStr = ('Hub name "{}" is not contained in the '
                      'project.').format(hub_name)
            raise ValueError(errStr)
            
        result = Connector(hub_name)
        
        return result

    def _execute(self, core,
                       project,
                       interface_name,
                       force_level=None,
                       allow_unavailable=False):

        '''Execute the given interface
        '''
        
        connector = self._get_connector(project)

        # Execute the interface
        connector.execute_interface(core,
                                    project,
                                    interface_name,
                                    level=force_level,
                                    allow_unavailable=allow_unavailable)

        return
        
    def _auto_execute(self, core,
                            project,
                            force_level=None):

        '''Auto execute all interfaces in the Hub.
        '''
        
        connector = self._get_connector(project)

        connector.auto_execute(core,
                               project,
                               force_level)

        return


class ProjectMenu(ConnectorMenu):
    
    @property
    def _hub_name(self):
        
        return 'project'
        
    def new_project(self, core, project_title):
        
        """Create a new project with a default simulation.
        
        Args:
          core (dtocean_core.core.Core): A Core object.
          project: (dtocean_core.core.Project): A Core object.
          project_title (str): The title of the project.
          
        Returns:
          dtocean_core.core.Project: A new Project object.
        
        """
        
        new_project = core.new_project(project_title)
        core.new_hub(new_project)
        
        self.activate(core,
                      new_project,
                      "System Type Selection")

        return new_project
        
    def initiate_pipeline(self, core, project):
                                    
        """Add the module and theme Hub objects to the core simulation.
        The input requirements of the "System Type Selection" interface
        must be met.
        
        Note:
          It is assumed that the core contains an active simulation at this
          stage.
        
        Args:
          core (dtocean_core.core.Core): A Core object.
          
        Returns:
          dtocean_core.core.Core: Updated copy of Core object.
           
        """
                
        self._execute(core, project, "System Type Selection")
        
        # Build the module and theme hubs
        core.new_hub(project)
        core.new_hub(project)

        # Load the top level data - check the status of the database.
        if project.get_database_credentials() is None: return
        
        self.activate(core,
                      project,
                      "Site and System Options")
        
        # Its necessary to load the site and system data from the database now
        # so a Tree is required.              
        tree = Tree()
                
        options_branch = tree.get_branch(core,
                                         project,
                                         "Site and System Options")
        options_branch.read_auto(core, project)

        return
        
    def initiate_options(self, core, project):
        
        # Load the top level data - check the status of the database.
        if project.get_database_credentials() is None: return
        
        if not "Site and System Options" in self.get_active(core, project):
                                      
            errStr = ("The pipeline must be initialised before "
                      "initalising the database options.")
            raise RuntimeError(errStr)
            
        self._execute(core,
                      project,
                      "Site and System Options")

        self.activate(core,
                      project,
                      "Site Boundary Selection")
                                              
        self.activate(core,
                      project,
                      "Database Filtering Interface")
                
        return
        
    def initiate_bathymetry(self, core, project):
        
        """Initiate selection of lease area for bathymetry filtering"""
        
        # Load the top level data - check the status of the database.
        if project.get_database_credentials() is None: return
            
        if not "Site Boundary Selection" in self.get_active(core, project):
                                      
            errStr = ("Database options must be initialised prior to "
                      "initalising the bathymetry.")
            raise RuntimeError(errStr)
                            
        self._execute(core,
                      project,
                      "Site Boundary Selection")
                      
        self.activate(core,
                      project,
                      "Project Boundaries Interface")
                      
        return

    def initiate_filter(self, core, project):

        """Filter the database based on user selections."
        
        Args:
          core (dtocean_core.core.Core): A Core object.
          
        Returns:
          dtocean_core.core.Core: Updated copy of Core object.
           
        """
        
        # Load the top level data - check the status of the database.
        if project.get_database_credentials() is None: return

        if not "Database Filtering Interface" in self.get_active(core,
                                                                 project):
                                      
            errStr = ("Database options must be initialised prior to "
                      "filtering the database.")
            raise RuntimeError(errStr)

        self._execute(core,
                      project,
                      "Database Filtering Interface")
        
        return
        
    def initiate_dataflow(self, core, project, _next_hub='modules'):
        
        """Add a marker level to indicate completion of the filtering steps and
        the beginning of preparing a simulation by collecting data. All modules
        and themes must be activated before calling this function"""
        
        if not core.has_data(project, "hidden.pipeline_active"):
            
            errStr = ("Dataflow can not be initiated before the pipeline")
            raise RuntimeError(errStr)
        
        # Add an indicator variable for this stage
        core.add_datastate(project,
                           identifiers=["hidden.dataflow_active"],
                           values=[True])
                           
        # Create a level for resetting to pre-data collection point                           
        init_level = "{} {}".format(_next_hub, core._markers["initial"])
        core.register_level(project,
                            init_level,
                            _next_hub)
        
        return


class ModuleMenu(ConnectorMenu):
    
    """A class for controlling actions related to the simulations such as
    choosing which modules and themes are to be run and executing modules and
    themes.
    
    """

    @property
    def _hub_name(self):
        
        return 'modules'
        
    def activate(self, core,
                       project,
                       module_name):

        """Move a module into the pipelines list."""
        
        if core.has_data(project, "hidden.dataflow_active"):
            
            errStr = ("Modules can not be added after the dataflow has been "
                      "initiated")
            raise RuntimeError(errStr)
            
        super(ModuleMenu, self).activate(core,
                                         project,
                                         module_name)

        return
        
    def is_executable(self, core,
                            project,
                            module_name,
                            check_themes=True,
                            allow_unavailable=False):

        result = super(ModuleMenu, self).is_executable(core,
                                                       project,
                                                       module_name,
                                                       allow_unavailable)
                                                   
        if not check_themes: return result
            
        theme_connector = self._get_connector(project, "themes")

        can_execute_themes = theme_connector.is_auto_executable(
                                                    core,
                                                    project,
                                                    allow_unavailable=True)
                                                           
        result = result & can_execute_themes
        
        return result

    def execute_current(self, core,
                              project,
                              execute_themes=True,
                              allow_unavailable=False):
        
        module_name = self.get_current(core, project)

        if module_name is None: 
            
            errStr = "No interface is scheduled for execution."
            raise RuntimeError(errStr)
            
        # Check if execution is OK
        if not self.is_executable(core,
                                  project,
                                  module_name,
                                  check_themes=execute_themes,
                                  allow_unavailable=allow_unavailable):
                                      
            errStr = "Not all inputs for module {}".format(module_name)
            
            if execute_themes:
                
                theme_connector = self._get_connector(project, "themes")
                theme_names = theme_connector.get_scheduled_interface_names(
                                                                    core,
                                                                    project)
                theme_str = ", ".join(theme_names)
               
                errStr = "{} or theme(s) {}".format(errStr, theme_str)
               
            errStr = "{} have been satisfied".format(errStr)
                                                   
            raise RuntimeError(errStr)
            
        # Unmask any states
        core.unmask_states(project)

        self._execute(core,
                      project,
                      module_name,
                      allow_unavailable=allow_unavailable)
                      
        if not execute_themes: return
                                      
        theme_connector = self._get_connector(project, "themes")
                
        if theme_connector.any_scheduled(core, project):
            
            # Run the themes just on local data. Mask all outputs then
            # unmask only those containing the module name.
            core.mask_states(project,
                             core._markers["output"],
                             no_merge=True,
                             update_status=False)
            core.unmask_states(project,
                               module_name,
                               update_status=False)
            
            local_level = "{} {}".format(module_name, core._markers["local"])
            theme_connector.auto_execute(core,
                                         project,
                                         local_level,
                                         register_level=False,
                                         allow_non_execution=True)
                                                        
            # Run the themes for global data. Unmask all the states and create
            # a modified level
            core.unmask_states(project)
            
            global_level = "{} {}".format(module_name, core._markers["global"])
            theme_connector.auto_execute(core,
                                         project,
                                         global_level,
                                         register_level=False,
                                         allow_non_execution=True)
            
            # Set global scope for theme outputs                             
            set_output_scope(core, project)
            
            # If the main hub has completed then force completed on the
            # themes            
            if not self.get_scheduled(core, project):
                theme_connector.force_completed(core, project)
                        
        return

        
class ThemeMenu(ConnectorMenu):
    
    """A class for controlling actions related to the simulations such as
    choosing which modules and themes are to be run and executing modules and
    themes.
    
    """

    @property
    def _hub_name(self):
        
        return 'themes'
        
    def activate(self, core,
                       project,
                       interface_name):

        """Move a theme into the pipelines list."""
        
        if core.has_data(project, "hidden.dataflow_active"):
            
            errStr = ("Themes can not be added after the dataflow has been "
                      "initiated")
            raise RuntimeError(errStr)
            
        super(ThemeMenu, self).activate(core,
                                        project,
                                        interface_name)

        return
        
        
        

    def execute_all(self, core, project):

        '''Execute a theme

        Process
        -------

        1. Test if data requirements are met
        2. Add the inputs into the interface and execute
        3. Add the results to the data state

        '''

        level = "themes"
        theme_connector = self._get_connector(project,"themes")
        
        # Unmask any states
        core.unmask_states(project)
        
        theme_connector.auto_execute(core,
                                     project,
                                     level)
                                     
        # If the main hub has completed then force completed on the
        # themes
        if self.get_scheduled(core, project) is None:
            theme_connector.force_completed(core, project)

        return

        
class DataMenu(object):
    
    """The DataMenu class is for actions relating to populating the core with
    data from various sources.
    """
    
    def __init__(self):

        self._tree = Tree()
        self._dbyaml = None
        self._dbconfig = None

        self._dbyaml, self._dbconfig = self._init_dbdefs()

        return

    def _init_dbdefs(self, db_config_name="database.yaml"):

        objdir = ObjDirectory(__name__, "config")
        datadir = UserDataDirectory("dtocean_core", "DTOcean", "config")
        dirmap = DirectoryMap(datadir, objdir)
        
        dbyaml = ReadYAML(dirmap, db_config_name)
        dbyaml.copy_config()
        
        config = dbyaml.read()
                
        return dbyaml, config
        
    def get_available_databases(self):
        
        return self._dbconfig.keys()
        
    def get_database_dict(self, identifier):
                               
        if identifier not in self._dbconfig:
            
            errStr = ("Identifier {} does not correspond to any found "
                      "database credentials.").format(identifier)
            raise ValueError(errStr)
            
        db_dict = self._dbconfig[identifier] 
        
        return db_dict
                
    def update_database(self, identifier,
                              db_dict,
                              allow_new=False):
                                  
        if not identifier:
            
            errStr = "Database identifier must be a valid string."
            raise ValueError(errStr)
                                  
        if not allow_new and identifier not in self._dbconfig:
            
            errStr = ("Identifier {} does not correspond to any found "
                      "database credentials.").format(identifier)
            raise ValueError(errStr)
                               
        safe_db_dict = {}
        
        for k, v in db_dict.iteritems():
            
            if not v: continue
            safe_db_dict[k] = v
            
        self._dbconfig[identifier] = safe_db_dict
        self._dbyaml.write(self._dbconfig)
        
        return
        
    def delete_database(self, identifier):
                               
        if identifier not in self._dbconfig:
            
            errStr = ("Identifier {} does not correspond to any found "
                      "database credentials.").format(identifier)
            raise ValueError(errStr)
            
        self._dbconfig.pop(identifier, None)
        self._dbyaml.write(self._dbconfig)
        
        return
        
    def check_database(self, identifier, pwd=None):
        
        if identifier not in self._dbconfig:
            
            errStr = ("Identifier {} does not correspond to any found "
                      "database credentials.").format(identifier)
            raise ValueError(errStr)
        
        credentials = self._dbconfig[identifier]
        
        if "pwd" not in credentials or pwd is not None:
            credentials["pwd"] = pwd
            
        if "port" in credentials:
            port = credentials["port"]
        else:
            port = 5432
            
        port_open, msg = check_host_port(credentials["host"], port)
        module_logger.debug(msg)

        return port_open
        
    def select_database(self, project, identifier, pwd=None):
        
        # Allow nullification of credentials
        if identifier is None:
            project.set_database_credentials(None)
            return
        
        if identifier not in self._dbconfig:
            
            errStr = ("Identifier {} does not correspond to any found "
                      "database credentials.").format(identifier)
            raise ValueError(errStr)
        
        if not self.check_database(identifier, pwd=None):
        
            errStr = ("Port could not be opened for database "
                      "{}.").format(identifier)
            raise RuntimeError(errStr)
            
        credentials = self._dbconfig[identifier]

        project.set_database_credentials(credentials)
        
        return
        
    def load_data(self, core, project):
        
        if not core.has_data(project, "hidden.dataflow_active"):
            
            errStr = ("Bulk data can not be loaded until the dataflow has "
                      "been initiated.")
            raise RuntimeError(errStr)
        
        # Load the main data - check the status of the database.
        if project.get_database_credentials() is None: return
        
        self._tree.read_auto(core,
                             project,
                             ("modules", "themes"))
        
        return

    # TODO: Remove in final version?
    def load_test_data(self, core,
                             project,
                             definitions_path,
                             load_only=None,
                             overwrite=False,
                             skip_missing=True):
                                 
        if not core.has_data(project, "hidden.dataflow_active"):
            
            errStr = ("Bulk data can not be loaded until the dataflow has "
                      "been initiated.")
            raise RuntimeError(errStr)
        
        with open(definitions_path, "r") as f:
            definitions = yaml.load(f)
            
        if load_only is not None:
            definitions = [x for x in definitions if x["branch"] in load_only]

        for definition in definitions:
            
            branch = self._tree.get_branch(core,
                                           project,
                                           definition["branch"])
            relative_path = definition["data_path"]
            dir_path = os.path.dirname(definitions_path)
            data_path = os.path.join(dir_path, relative_path)
            
            branch.read_test_data(core,
                                  project,
                                  data_path,
                                  overwrite=overwrite,
                                  skip_missing=skip_missing)
        
        return
        


