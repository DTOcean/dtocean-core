
import os
from copy import deepcopy
from pprint import pprint

import pytest

from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ModuleMenu, ProjectMenu, ThemeMenu 
from dtocean_core.pipeline import Tree, _get_connector

dir_path = os.path.dirname(__file__)

@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()
    
    return new_core

@pytest.fixture(scope="module")
def var_tree():

    return Tree()

@pytest.fixture(scope="module")
def module_menu(core):
    '''Share a ModuleMenu object'''  
       
    return ModuleMenu()

@pytest.fixture(scope="module")
def theme_menu(core):
    '''Share a ModuleMenu object'''  
    
    return ThemeMenu()

# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def tidal_project(core, var_tree):
    '''Share a Project object'''

    project_menu = ProjectMenu()
    
    new_project = project_menu.new_project(core, "test tidal")
    
    options_branch = var_tree.get_branch(core,
                                         new_project,
                                         "System Type Selection")
    device_type = options_branch.get_input_variable(core,
                                                    new_project,
                                                    "device.system_type")
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)
        
    project_menu.initiate_pipeline(core, new_project)
        
    if False: #new_project.get_database_credentials() is not None:
        
        project_branch = var_tree.get_branch(core,
                                             new_project,
                                             "Site and System Options")
                                             
        new_var = project_branch.get_input_variable(core,
                                                    new_project,
                                                    "site.names")
        new_var.read_auto(core, new_project)
        available_sites = new_var.get_value(core, new_project)
        
        filter_branch = var_tree.get_branch(core,
                                            new_project,
                                            "Database Filtering Interface")
        new_var = filter_branch.get_input_variable(core,
                                                   new_project,
                                                   "site.selected_site")
        new_var.set_raw_interface(core, available_sites[1])
        new_var.read(core, new_project)

    return new_project

@pytest.fixture(scope="module") 
def wave_project(core, var_tree):
    '''Share a Project object'''

    project_menu = ProjectMenu()

    new_project = project_menu.new_project(core, "test wave")
        
    options_branch = var_tree.get_branch(core,
                                         new_project,
                                         "System Type Selection")
    device_type = options_branch.get_input_variable(core,
                                                    new_project,
                                                    "device.system_type")
    device_type.set_raw_interface(core, "Wave Floating")
    device_type.read(core, new_project)
    
    project_menu.initiate_pipeline(core, new_project)
        
    if False: #new_project.get_database_credentials() is not None:
        
        project_branch = var_tree.get_branch(core,
                                             new_project,
                                             "System Type Selection")
                                             
        new_var = project_branch.get_input_variable(core,
                                                    new_project,
                                                    "site.names")
        new_var.read_auto(core, new_project)
        available_sites = new_var.get_value(core, new_project)
        
        filter_branch = var_tree.get_branch(core,
                                            new_project,
                                            "Database Filtering Interface")
        new_var = filter_branch.get_input_variable(core,
                                                   new_project,
                                                   "site.selected_site")
        new_var.set_raw_interface(core, available_sites[1])
        new_var.read(core, new_project)
        
    project_menu.initiate_options(core, new_project)

    return new_project
    
def test_wave_not_inputs(module_menu, core, wave_project, var_tree):
        
    mod_name = "Hydrodynamics"
#    project_menu = ProjectMenu()
    
    project = deepcopy(wave_project)
    module_menu.activate(core, project, mod_name)
#    project = project_menu.initiate_filter(core, project)
    
    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_input_status = hydro_branch.get_input_status(core, 
                                                       project)
                                                       
    assert "device.cut_in_velocity" not in hydro_input_status
    
def test_get_wave_interface(module_menu, core, wave_project, var_tree):

    mod_name = "Hydrodynamics"
#    project_menu = ProjectMenu()

    project = deepcopy(wave_project)     
    module_menu.activate(core, project, mod_name)
#    project = project_menu.initiate_filter(core, project)
    
    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_wave.pkl"))
    
    can_execute = module_menu.is_executable(core, project, mod_name)
    
    if not can_execute:
        
        inputs = hydro_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
    
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
    
    assert interface.data.wave_data_directory is not None
    
def test_wave_interface_entry(module_menu, core, wave_project, var_tree):
        
    mod_name = "Hydrodynamics"
    
    project = deepcopy(wave_project) 
    module_menu.activate(core, project, mod_name)
#    project_menu.initiate_filter(core, project)
    
    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_wave.pkl"))
                                                       
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = hydro_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    interface.connect(debug_entry=True)
                                        
    assert True
    
def test_tidal_inputs(module_menu, core, tidal_project, var_tree):
        
    mod_name = "Hydrodynamics"
#    project_menu = ProjectMenu()
    
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
#    project_menu.initiate_filter(core, project)
    
    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_input_status = hydro_branch.get_input_status(core, 
                                                       project)
                                                    
    assert "device.cut_in_velocity" in hydro_input_status

def test_get_tidal_interface(module_menu, core, tidal_project, var_tree):
        
    mod_name = "Hydrodynamics"
#    project_menu = ProjectMenu()
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                                       
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = hydro_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    assert interface.data.perf_curves is not None
    
def test_tidal_interface_entry(module_menu, core, tidal_project, var_tree):
        
    mod_name = "Hydrodynamics"
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                                       
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = hydro_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    interface.connect(debug_entry=True)
                                        
    assert True
    
def test_electrical_inputs(module_menu, core, tidal_project, var_tree):
        
    mod_name = "Electrical Sub-Systems"
#    project_menu = ProjectMenu()
    data_menu = DataMenu()
    project_menu = ProjectMenu()
    
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    data_menu.load_data(core, project)
    
    electrical_branch = var_tree.get_branch(core, project, mod_name)
   
    
    electrical_input_status = electrical_branch.get_input_status(core, 
                                                                 project)
                                                    
    assert "component.transformers" in electrical_input_status
    
def test_get_electrical_interface(module_menu, core, tidal_project, var_tree):
    
    mod_name = "Electrical Sub-Systems"
#    project_menu = ProjectMenu()
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    electrical_branch = var_tree.get_branch(core, project, mod_name)
    electrical_branch.read_test_data(core,
                                     project,
                                     os.path.join(dir_path,
                                                  "inputs_wp3.pkl"))
    electrical_branch.read_auto(core, project)
    
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = electrical_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    assert interface.data.voltage is not None
    
def test_electrical_interface_entry(module_menu, core, tidal_project, var_tree):
    
    mod_name = "Electrical Sub-Systems"
    #    project_menu = ProjectMenu()

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    electrical_branch = var_tree.get_branch(core, project, mod_name)
    electrical_branch.read_test_data(core,
                                     project,
                                     os.path.join(dir_path,
                                                  "inputs_wp3.pkl"))
    electrical_branch.read_auto(core, project)
    
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = electrical_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    interface.connect(debug_entry=True)
                                        
    assert True
    
def test_moorings_inputs(module_menu, core, tidal_project, var_tree):
        
    mod_name = "Mooring and Foundations"
    data_menu = DataMenu()
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    data_menu.load_data(core, project)
    
    moorings_branch = var_tree.get_branch(core, project, mod_name)
   
    
    moorings_input_status = moorings_branch.get_input_status(core,
                                                               project)
                                                    
    assert "device.dry_beam_area" in moorings_input_status
    
def test_get_moorings_interface(module_menu, core, tidal_project, var_tree):
    
    mod_name = "Mooring and Foundations"
#    project_menu = ProjectMenu()
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    moorings_branch = var_tree.get_branch(core, project, mod_name)
    moorings_branch.read_test_data(core,
                                   project,
                                   os.path.join(dir_path,
                                                "inputs_wp4.pkl"))
    moorings_branch.read_auto(core, project)
    
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = moorings_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    assert interface.data.winddir is not None

def test_moorings_interface_entry(module_menu, core, tidal_project, var_tree):
    
    mod_name = "Mooring and Foundations"
#    project_menu = ProjectMenu()
 
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    moorings_branch = var_tree.get_branch(core, project, mod_name)
    moorings_branch.read_test_data(core,
                                   project,
                                   os.path.join(dir_path,
                                                "inputs_wp4.pkl"))
    moorings_branch.read_auto(core, project)
    
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = moorings_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    interface.connect(debug_entry=True)
                                        
    assert True

def test_installation_inputs(module_menu, core, tidal_project, var_tree):
        
    mod_name = "Installation"
    data_menu = DataMenu()
    project_menu = ProjectMenu()
    
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    data_menu.load_data(core, project)
    
    installation_branch = var_tree.get_branch(core, project, mod_name)
   
    
    installation_input_status = installation_branch.get_input_status(core,
                                                                   project)
                                                    
    assert "component.ports" in installation_input_status

def test_get_installation_interface(module_menu, core, tidal_project,
                                    var_tree):
    
    mod_name = "Installation"
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    installation_branch = var_tree.get_branch(core, project, mod_name)
    installation_branch.read_test_data(core,
                                     project,
                                     os.path.join(dir_path,
                                                  "inputs_wp5.pkl"))
    installation_branch.read_auto(core, project)
    
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = installation_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    assert interface.data.site is not None
    
def test_installation_interface_entry(module_menu,
                                      core,
                                      tidal_project,
                                      var_tree):
    
    mod_name = "Installation"
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    installation_branch = var_tree.get_branch(core, project, mod_name)
    installation_branch.read_test_data(core,
                                     project,
                                     os.path.join(dir_path,
                                                  "inputs_wp5.pkl"))
    installation_branch.read_auto(core, project)
    
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = installation_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    interface.connect(debug_entry=True)
                                        
    assert True
    
def test_operations_inputs(module_menu, core, tidal_project, var_tree):
        
    mod_name = 'Operations and Maintenance'
    data_menu = DataMenu()
    project_menu = ProjectMenu()
    
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    data_menu.load_data(core, project)
    
    operations_branch = var_tree.get_branch(core, project, mod_name)
   
    
    operations_input_status = operations_branch.get_input_status(core,
                                                                   project)
                                                    
    assert "options.operations_inspections" in operations_input_status

def test_get_operations_interface(module_menu, core, tidal_project, var_tree):
    
    mod_name = 'Operations and Maintenance'
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    operations_branch = var_tree.get_branch(core, project, mod_name)
    operations_branch.read_test_data(core,
                                     project,
                                     os.path.join(dir_path,
                                                  "inputs_wp6.pkl"))
    operations_branch.read_auto(core, project)
    
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = operations_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    assert interface.data.system_type is not None
    
def test_operations_interface_entry(module_menu,
                                    core,
                                    tidal_project,
                                    var_tree):
    
    mod_name = 'Operations and Maintenance'
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    operations_branch = var_tree.get_branch(core, project, mod_name)
    operations_branch.read_test_data(core,
                                     project,
                                     os.path.join(dir_path,
                                                  "inputs_wp6.pkl"))
    operations_branch.read_auto(core, project)
    
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = operations_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    interface.connect(debug_entry=True)
                                        
    assert True


def test_environmental_inputs(theme_menu, core, tidal_project, var_tree):
        
    theme_name = "Environmental Impact Assessment"
    data_menu = DataMenu()
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)
    data_menu.load_data(core, project)
    
    environmental_branch = var_tree.get_branch(core, project, theme_name)
   
    environmental_input_status = environmental_branch.get_input_status(core,
                                                                       project)
                                                    
    assert "project.hydro_collision_risk_weight" in environmental_input_status


def test_get_environmental_interface(theme_menu,
                                     core,
                                     tidal_project,
                                     var_tree):
    
    theme_name = "Environmental Impact Assessment"

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)
    
    environmental_branch = var_tree.get_branch(core, project, theme_name)
    environmental_branch.read_test_data(core,
                                   project,
                                   os.path.join(dir_path,
                                                "inputs_environmental.pkl"))
    environmental_branch.read_auto(core, project)
    
    can_execute = theme_menu.is_executable(core, project,  theme_name)
    
    if not can_execute:
        
        inputs = environmental_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "themes")
    interface = connector.get_interface(core,
                                        project,
                                        theme_name)
                                        
#    
    assert interface.data.layout is not None


def test_environmental_interface_entry(theme_menu,
                                       core,
                                       tidal_project,
                                       var_tree):
                                       
    
    theme_name = "Environmental Impact Assessment"
#    project_menu = ProjectMenu()
 
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)
    
    environmental_branch = var_tree.get_branch(core, project, theme_name)
    environmental_branch.read_test_data(core,
                                   project,
                                   os.path.join(dir_path,
                                                "inputs_environmental.pkl"))
    environmental_branch.read_auto(core, project)
    
    can_execute = theme_menu.is_executable(core, project,  theme_name)
    
    if not can_execute:
        
        inputs = environmental_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "themes")
    interface = connector.get_interface(core,
                                        project,
                                        theme_name)
                                        
    interface.connect(debug_entry=True)
                                        
    assert True


def test_reliability_inputs(theme_menu, core, tidal_project, var_tree):
        
    theme_name = "Reliability"
    data_menu = DataMenu()
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)
    data_menu.load_data(core, project)
    
    reliability_branch = var_tree.get_branch(core, project, theme_name)
   
    
    reliability_input_status = reliability_branch.get_input_status(core,
                                                               project)
                                                    
#    assert "device.dry_beam_area" in moorings_input_status
    
def test_get_reliability_interface(theme_menu, core, tidal_project, var_tree):
    
    theme_name = "Reliability"
#    project_menu = ProjectMenu()
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)
    
    reliability_branch = var_tree.get_branch(core, project, theme_name)
    reliability_branch.read_test_data(core,
                                   project,
                                   os.path.join(dir_path,
                                                "inputs_reliability.pkl"))
    reliability_branch.read_auto(core, project)
    
    can_execute = theme_menu.is_executable(core, project,  theme_name)
    
    if not can_execute:
        
        inputs = reliability_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "themes")
    interface = connector.get_interface(core,
                                        project,
                                        theme_name)
                                        
    assert interface.data.mission_time is not None
    
def test_reliability_interface_entry(theme_menu, core, tidal_project, var_tree):
    
    theme_name = "Reliability"
#    project_menu = ProjectMenu()
 
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)
    
    reliability_branch = var_tree.get_branch(core, project, theme_name)
    reliability_branch.read_test_data(core,
                                   project,
                                   os.path.join(dir_path,
                                                "inputs_reliability.pkl"))
    reliability_branch.read_auto(core, project)
    
    can_execute = theme_menu.is_executable(core, project,  theme_name)
    
    if not can_execute:
        
        inputs = reliability_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "themes")
    interface = connector.get_interface(core,
                                        project,
                                        theme_name)
                                        
    interface.connect(debug_entry=True)
                                        
    assert True    


if __name__ == "__main__":
    
    from dtocean_core import start_logging
    start_logging()
    
    my_core = core()
    my_var_tree = var_tree()
    
    my_tidal_project = tidal_project(my_core, my_var_tree)
    

