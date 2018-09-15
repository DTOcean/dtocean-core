
import pytest

import os
from copy import deepcopy

from aneris.entity import Pipeline
from dtocean_core.core import Core
from dtocean_core.interfaces import ModuleInterface, ThemeInterface
from dtocean_core.menu import DataMenu, ModuleMenu, ProjectMenu, ThemeMenu
from dtocean_core.pipeline import Tree
from polite.paths import Directory

dir_path = os.path.dirname(__file__)


class MockModule(ModuleInterface):
    
    @classmethod
    def get_name(cls):
        
        return "Mock Module"
        
    @classmethod         
    def declare_weight(cls):
        
        return 998

    @classmethod
    def declare_inputs(cls):
        
        input_list = ["device.turbine_performance",
                      "device.cut_in_velocity",
                      "device.system_type"]
        
        return input_list

    @classmethod
    def declare_outputs(cls):
        
        output_list = None
        
        return output_list
        
    @classmethod
    def declare_optional(cls):
        
        return None
        
    @classmethod
    def declare_id_map(self):
        
        id_map = {"dummy1": "device.turbine_performance",
                  "dummy2": "device.cut_in_velocity",
                  "dummy3": "device.system_type"}
                  
        return id_map
                 
    def connect(self, debug_entry=False,
                      export_data=True):
        
        return


class MockTheme(ThemeInterface):
    
    @classmethod
    def get_name(cls):
        
        return "Mock Theme"
        
    @classmethod         
    def declare_weight(cls):
        
        return 999

    @classmethod
    def declare_inputs(cls):
        
        input_list = ["project.discount_rate"]
        
        return input_list

    @classmethod
    def declare_outputs(cls):
        
        output_list = ['project.capex_total']
                
        return output_list
        
    @classmethod
    def declare_optional(cls):
        
        option_list = ["project.discount_rate"]
        
        return option_list
        
    @classmethod
    def declare_id_map(self):
        
        id_map = {"dummy1": "project.discount_rate",
                  "dummy2": "project.capex_total"}
                  
        return id_map
                 
    def connect(self, debug_entry=False,
                      export_data=True):
        
        return


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()
    
    socket = new_core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)
    
    socket = new_core.control._sequencer.get_socket("ThemeInterface")
    socket.add_interface(MockTheme)
    
    return new_core
    
@pytest.fixture(scope="module")
def project(core):
    '''Share a Project object'''

    project_title = "Test"  
    
    project_menu = ProjectMenu()
    var_tree = Tree()
    
    new_project = project_menu.new_project(core, project_title)
    
    options_branch = var_tree.get_branch(core,
                                         new_project,
                                         "System Type Selection")
    device_type = options_branch.get_input_variable(core,
                                                    new_project,
                                                    "device.system_type")
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)
    
    project_menu.initiate_pipeline(core, new_project)
    
    return new_project
    
@pytest.fixture(scope="module")
def module_menu(core):
    '''Share a ModuleMenu object'''  
    
    return ModuleMenu()
    
@pytest.fixture(scope="module")
def theme_menu(core):
    '''Share a ThemeMenu object'''  
    
    return ThemeMenu()

def test_new_project():
    
    project_title = "Test"    
    
    new_core = Core()
    new_project = new_core.new_project(project_title)
    
    assert new_project.title == project_title
  
def test_initiate_pipeline(core, project):
    
    project = deepcopy(project) 
    simulation = project.get_simulation()
    assert isinstance(simulation._hubs["modules"], Pipeline)

def test_get_available_modules(core, project, module_menu):
    
    project = deepcopy(project) 
    names = module_menu.get_available(core, project)
    
    assert "Mock Module" in names
    
def test_activate_module(core, project, module_menu):

    mod_name = "Mock Module"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)
    simulation = project.get_simulation()
    pipeline = simulation.get_hub("modules")
    module = pipeline._scheduled_interface_map.popitem(last=False)[1]
    
    assert isinstance(module, MockModule)
    
def test_get_available_themes(core, project, theme_menu):
    
    project = deepcopy(project) 
    names = theme_menu.get_available(core, project)
    
    assert "Mock Theme" in names
    
def test_activate_theme(core, project, theme_menu):

    mod_name = "Mock Theme"
    
    project = deepcopy(project) 
    theme_menu.activate(core, project, mod_name)
    simulation = project.get_simulation()
    hub = simulation.get_hub("themes")
    module = hub._scheduled_interface_map["MockTheme"]
    
    assert isinstance(module, MockTheme)
    
def test_DataMenu_get_available_databases(mocker, tmpdir):

    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.menu.UserDataDirectory',
                 return_value=mock_dir)
                 
    datamenu = DataMenu()
    dbs = datamenu.get_available_databases()
    
    assert len(dbs) > 0
              
              
def test_DataMenu_get_database_dict(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.menu.UserDataDirectory',
                 return_value=mock_dir)
                 
    datamenu = DataMenu()
    dbs = datamenu.get_available_databases()
    db_id = dbs[0]
    
    db_dict = datamenu.get_database_dict(db_id)
    
    assert "host" in db_dict.keys()
    
    
def test_DataMenu_update_database(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.menu.UserDataDirectory',
                 return_value=mock_dir)
                 
    datamenu = DataMenu()
    dbs = datamenu.get_available_databases()
    db_id = dbs[0]
    
    db_dict = datamenu.get_database_dict(db_id)
    datamenu.update_database(db_id, db_dict)
    
    assert len(config_tmpdir.listdir()) == 1
              
              
def test_ModuleMenu_execute_current_nothemes(core,
                                             project,
                                             module_menu):
    
    var_tree = Tree()
    project = deepcopy(project)
    mod_name = "Mock Module"
    
    module_menu.activate(core, project, mod_name)
    mod_branch = var_tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path, "inputs_wp2_tidal.pkl"))
                 
    module_menu.execute_current(core, project, execute_themes=False)
    
    assert True
