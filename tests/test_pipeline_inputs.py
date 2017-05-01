
import pytest

from copy import deepcopy

from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu, ThemeMenu 
from dtocean_core.pipeline import Tree, InputVariable

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
    '''Share a ModuleMenu object'''  
    
    return ThemeMenu()
    
def test_tree(project):
    
    var_tree = Tree()
        
    assert isinstance(var_tree, Tree)

def test_get_branch_input_status(core, project, module_menu, tree):

    mod_name = "Hydrodynamics"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)
    
    hydro_branch = tree.get_branch(core, project, mod_name)
    inputs = hydro_branch.get_input_status(core, project)
    
    assert "bathymetry.layers" in inputs.keys()
    assert inputs["bathymetry.layers"] == 'required'
    
def test_get_input_variable(core, project, module_menu, tree):

    mod_name = "Hydrodynamics"
    var_id = "device.cut_in_velocity"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)
    
    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)
    
    assert isinstance(new_var, InputVariable)
    
#def test_get_raw_interfaces(core, project, module_menu, tree):
#    
#    mod_name = "Hydrodynamics"
#    var_id = "device.cut_in_velocity"
#    
#    module_menu.activate(core, project, mod_name)
#    
#    hydro_branch = tree.get_branch(project, mod_name)
#    new_var = hydro_branch.get_input_variable(core, project, var_id)
#    
#    list_raw = new_var.get_raw_interfaces(core)
#    
#    assert 'Hydrodynamics Raw Inputs' in list_raw
#
#def test_set_raw_interface(core, project, module_menu, tree):
#    
#    var_id = "corridor.max_water_depth"
#    var_id = "device.system_type"
#    
#    module_menu.activate(core, project, mod_name)
#    
#    hydro_branch = tree.get_branch(project, mod_name)
#    new_var = hydro_branch.get_input_variable(core, project, var_id)
#    
#    new_var.set_raw_interface(core, "Tidal Fixed")
#        
#    assert new_var._interface.data[var_id] == 'Tidal Fixed'
        
def test_connect(core, project, module_menu, tree):
    
    mod_name = "Hydrodynamics"
    var_id = "device.system_type"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)
    
    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)
    
    new_var.set_raw_interface(core, 'Tidal Fixed')
    
    new_var.read(core, project)
    
    inputs = hydro_branch.get_input_status(core, project)
    
    assert inputs["device.system_type"] == 'satisfied'
    
def test_module_unavailable_inputs(core, project, module_menu, tree):

    project = deepcopy(project) 

    module_menu.activate(core, project, "Hydrodynamics")
    module_menu.activate(core, project, "Electrical Sub-Systems")
    module_menu.activate(core, project, "Mooring and Foundations")
    
    electric_branch = tree.get_branch(core, project, "Electrical Sub-Systems") 
    moorings_branch = tree.get_branch(core, project, "Mooring and Foundations") 
    
    inputs = electric_branch.get_input_status(core, 
                                              project)
        
    assert inputs['device.power_rating'] == 'unavailable'
    assert inputs['project.layout'] == 'unavailable'
    
#    inputs = moorings_branch.get_input_status(core, 
#                                              project)
#    
#    assert inputs['project.layout'] == 'unavailable'

def test_get_theme_inputs(core, project, theme_menu, tree):

    mod_name = "Economics"

    project = deepcopy(project) 
    theme_menu.activate(core, project, mod_name)
    
    eco_branch = tree.get_branch(core, project, mod_name)
    inputs = eco_branch.get_input_status(core, project)
        
    assert "project.discount_rate" in inputs.keys()
    assert inputs["project.discount_rate"] == 'optional'
    
def test_get_metadata(core, project, module_menu, tree):
    
    mod_name = "Hydrodynamics"
    var_id = "device.system_type"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)
    metadata = new_var.get_metadata(core)
        
    assert metadata.title == "Device Technology Type"
    
def test_get_value(core, project, module_menu, tree):
    
    mod_name = "Hydrodynamics"
    var_id = "device.system_type"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)
    new_var.set_raw_interface(core, 'Tidal Fixed')
    new_var.read(core, project)
    
    value = new_var.get_value(core, project)
        
    assert value == "Tidal Fixed"
    
    