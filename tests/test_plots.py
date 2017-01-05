
import pytest

import os
from copy import deepcopy

import matplotlib.pyplot as plt

from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu 
from dtocean_core.pipeline import Tree

dir_path = os.path.dirname(__file__)

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
    
def test_perf_plot_available(core, project, tree):
    
    project = deepcopy(project) 
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()
    
    mod_name = "Hydrodynamics"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                                       
    ct_curve = hydro_branch.get_input_variable(core,
                                               project,
                                               "device.turbine_performance")
    result = ct_curve.get_available_plots(core, project)
    
    assert 'Tidal Power Performance' in result
    
def test_thrust_plot(core, project, tree):
    
    project = deepcopy(project) 
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()
    
    mod_name = "Hydrodynamics"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    hydro_branch = tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                                       
    ct_curve = hydro_branch.get_input_variable(core,
                                               project,
                                               "device.turbine_performance")
    ct_curve.plot(core, project, 'Tidal Power Performance')
    
    assert len(plt.get_fignums()) == 1
    
    plt.close("all")

