
import pytest

from copy import deepcopy

from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu, ThemeMenu 
from dtocean_core.pipeline import Tree, OutputVariable

# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()
    
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

    mod_name = "Hydrodynamics"

    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)
    
    hydro_branch = tree.get_branch(core, project, "Hydrodynamics")
    outputs = hydro_branch.get_output_status(core, project)
    
    assert 'project.annual_energy' in outputs.keys()
    assert outputs['project.annual_energy'] == 'unavailable'
    
def test_get_output_variable(core, project, module_menu, tree):

    mod_name = "Hydrodynamics"
    var_id = "project.annual_energy"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)
    
    hydro_branch = tree.get_branch(core, project, "Hydrodynamics")
    new_var = hydro_branch.get_output_variable(core, project, var_id)
    
    assert isinstance(new_var, OutputVariable)
  
def test_module_overwritten_outputs(core, project, module_menu, tree):

    project = deepcopy(project) 

    module_menu.activate(core, project, "Hydrodynamics")
    module_menu.activate(core, project, "Electrical Sub Systems")
    
    hydro_branch = tree.get_branch(core, project, "Hydrodynamics")
    outputs = hydro_branch.get_output_status(core, project)
    
    assert outputs["project.number_of_devices"] == 'unavailable'
    
def test_get_theme_outputs(core, project, theme_menu, tree):

    mod_name = "Economics"

    project = deepcopy(project) 
    theme_menu.activate(core, project, mod_name)
    
    eco_branch = tree.get_branch(core, project, mod_name)
    outputs = eco_branch.get_output_status(core, project)
    
    assert "project.capex_total" in outputs.keys()
    assert outputs["project.capex_total"] == 'unavailable'
    
def test_get_metadata(core, project, module_menu, tree):
    
    mod_name = "Hydrodynamics"
    var_id = "project.number_of_devices"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_output_variable(core, project, var_id)
    metadata = new_var.get_metadata(core)
        
    assert metadata.title == "Number of Devices"
    
    