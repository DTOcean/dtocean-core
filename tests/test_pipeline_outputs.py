
from copy import deepcopy

import pytest

from dtocean_core.core import Core
from dtocean_core.interfaces import ModuleInterface, ThemeInterface
from dtocean_core.menu import ModuleMenu, ProjectMenu, ThemeMenu 
from dtocean_core.pipeline import Tree, OutputVariable


class MockModule(ModuleInterface):
    
    @classmethod
    def get_name(cls):
        
        return "Mock Module"
        
    @classmethod         
    def declare_weight(cls):
        
        return 998

    @classmethod
    def declare_inputs(cls):
        
        input_list = ["bathymetry.layers",
                      "device.cut_in_velocity",
                      "device.system_type"]
        
        return input_list

    @classmethod
    def declare_outputs(cls):
        
        output_list = ['device.power_rating',
                       'project.layout',
                       'project.annual_energy',
                       'project.number_of_devices']
        
        return output_list
        
    @classmethod
    def declare_optional(cls):
        
        return None
        
    @classmethod
    def declare_id_map(self):
        
        id_map = {"dummy1": "bathymetry.layers",
                  "dummy2": "device.cut_in_velocity",
                  "dummy3": "device.system_type",
                  "dummy4": "device.power_rating",
                  "dummy5": "project.layout",
                  "dummy6": "project.annual_energy",
                  "dummy7": "project.number_of_devices"}
                  
        return id_map
                 
    def connect(self, debug_entry=False,
                      export_data=True):
        
        return


class AnotherMockModule(ModuleInterface):
    
    @classmethod
    def get_name(cls):
        
        return "Mock Module 2"
        
    @classmethod         
    def declare_weight(cls):
        
        return 999

    @classmethod
    def declare_inputs(cls):
        
        input_list = ['device.power_rating',
                      'project.layout',
                      'project.number_of_devices']
        
        return input_list

    @classmethod
    def declare_outputs(cls):
        
        return None
        
    @classmethod
    def declare_optional(cls):
        
        return None
        
    @classmethod
    def declare_id_map(self):
        
        id_map = {"dummy1": "device.power_rating",
                  "dummy2": "project.layout",
                  "dummy3": "project.number_of_devices"}
                  
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
    socket.add_interface(AnotherMockModule)
    
    socket = new_core.control._sequencer.get_socket("ThemeInterface")
    socket.add_interface(MockTheme)
    
    return new_core
    
@pytest.fixture(scope="module")
def tree():
    '''Share a Tree object'''
    
    new_tree = Tree()
        
    return new_tree
    
@pytest.fixture(scope="module")
def project(core, tree):
    '''Share a Project object'''

    project_title = "Test"  
    
    project_menu = ProjectMenu()
    
    new_project = project_menu.new_project(core, project_title)
    
    options_branch = tree.get_branch(core, 
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

def test_get_branch_output_status(core, project, module_menu, tree):

    mod_name = "Mock Module"

    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)
    
    hydro_branch = tree.get_branch(core, project, mod_name)
    outputs = hydro_branch.get_output_status(core, project)
    
    assert 'project.annual_energy' in outputs.keys()
    assert outputs['project.annual_energy'] == 'unavailable'
    
def test_get_output_variable(core, project, module_menu, tree):

    mod_name = "Mock Module"
    var_id = "project.annual_energy"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)
    
    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_output_variable(core, project, var_id)
    
    assert isinstance(new_var, OutputVariable)
  
def test_module_overwritten_outputs(core, project, module_menu, tree):

    project = deepcopy(project) 

    module_menu.activate(core, project, "Mock Module")
    module_menu.activate(core, project, "Mock Module 2")
    
    hydro_branch = tree.get_branch(core, project, "Mock Module")
    outputs = hydro_branch.get_output_status(core, project)
    
    assert outputs["project.number_of_devices"] == 'unavailable'
    
def test_get_theme_outputs(core, project, theme_menu, tree):

    mod_name = "Mock Theme"

    project = deepcopy(project) 
    theme_menu.activate(core, project, mod_name)
    
    eco_branch = tree.get_branch(core, project, mod_name)
    outputs = eco_branch.get_output_status(core, project)
    
    assert "project.capex_total" in outputs.keys()
    assert outputs["project.capex_total"] == 'unavailable'
    
def test_get_metadata(core, project, module_menu, tree):
    
    mod_name = "Mock Module"
    var_id = "project.number_of_devices"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_output_variable(core, project, var_id)
    metadata = new_var.get_metadata(core)
        
    assert metadata.title == "Number of Devices"
    
    