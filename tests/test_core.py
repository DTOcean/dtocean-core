
import pytest

import os
import shutil
from copy import deepcopy

from dtocean_core.core import Core, Project
from dtocean_core.menu import ModuleMenu, ProjectMenu, ThemeMenu
from dtocean_core.pipeline import Tree


dir_path = os.path.dirname(__file__)


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()
    
    return new_core
    

@pytest.fixture(scope="module")
def var_tree():

    return Tree()


@pytest.fixture(scope="module")
def project(core, var_tree):
    '''Share a Project object'''

    project_title = "Test"  
    
    project_menu = ProjectMenu()
    
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


def test_init_core():
    
    new_core = Core()
    
    assert isinstance(new_core, Core)


def test_init_project():
    
    new_project = Project("Test")
    
    assert isinstance(new_project, Project)


def test_is_valid_variable():
    
    core = Core()
    test_var = "device.selected_name"
    
    result = core.is_valid_variable(test_var)
    
    assert result


def test_execute_output_level(core, var_tree):
    
    project_title = "Test"  
    
    project_menu = ProjectMenu()
    
    new_project = project_menu.new_project(core, project_title)
    
    options_branch = var_tree.get_branch(core,
                                         new_project,
                                         "System Type Selection")
    device_type = options_branch.get_input_variable(core,
                                                    new_project,
                                                    "device.system_type")
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)
    
    project_menu._execute(core,
                          new_project,
                          "System Type Selection")
    
    current_sim = new_project.get_simulation()
    output_level = "System Type Selection {}".format(core._markers["output"])
    
    assert current_sim._execution_level == output_level.lower()


def test_dump_project(core, project, var_tree, tmpdir):
    
    project = deepcopy(project) 

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Hydrodynamics")
    theme_menu.activate(core, project,  "Economics")
    
    project_menu.initiate_dataflow(core, project)
                                   
    hydro_branch = var_tree.get_branch(core, project, "Hydrodynamics")
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                             
    eco_branch = var_tree.get_branch(core, project, "Economics")
    eco_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path,
                                           "inputs_economics.pkl"))
    core.dump_project(project, str(tmpdir))
    project_file_path = os.path.join(str(tmpdir), "project.pkl")
    
    assert os.path.isfile(project_file_path)

    
def test_dump_project_archive(core, project, var_tree, tmpdir):
    
    project = deepcopy(project) 

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Hydrodynamics")
    theme_menu.activate(core, project,  "Economics")
    
    project_menu.initiate_dataflow(core, project)
                                   
    hydro_branch = var_tree.get_branch(core, project, "Hydrodynamics")
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                             
    eco_branch = var_tree.get_branch(core, project, "Economics")
    eco_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path,
                                           "inputs_economics.pkl"))

    project_file_name = "my_project.prj"
    project_file_path = os.path.join(str(tmpdir), project_file_name)
    
    core.dump_project(project, project_file_path)
    
    assert os.path.isfile(project_file_path)
    
    
def test_dump_project_nodir(core, project, var_tree):
    
    project = deepcopy(project) 

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Hydrodynamics")
    theme_menu.activate(core, project,  "Economics")
    
    project_menu.initiate_dataflow(core, project)

    with pytest.raises(ValueError):
        core.dump_project(project, "some_path")

    
def test_load_project_archive(core, project, var_tree, tmpdir):
    
    project = deepcopy(project) 

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Hydrodynamics")
    theme_menu.activate(core, project,  "Economics")
    
    project_menu.initiate_dataflow(core, project)
                                   
    hydro_branch = var_tree.get_branch(core, project, "Hydrodynamics")
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                             
    eco_branch = var_tree.get_branch(core, project, "Economics")
    eco_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path,
                                           "inputs_economics.pkl"))

    project_file_name = "my_project.prj"
    project_file_path = os.path.join(str(tmpdir), project_file_name)
    
    core.dump_project(project, project_file_path)

    del(project)
    
    assert os.path.isfile(project_file_path)
    
    new_root = os.path.join(str(tmpdir), "test")
    os.makedirs(new_root)
    
    move_file_path = os.path.join(str(tmpdir), "test", project_file_name)
    
    shutil.copy2(project_file_path, move_file_path)
    
    loaded_project = core.load_project(move_file_path)
    active_sim = loaded_project.get_simulation()

    assert loaded_project.check_integrity()
    assert active_sim.get_title() == "Default"
    assert "Hydrodynamics" in module_menu.get_scheduled(core, loaded_project)


def test_dump_datastate(core, project, var_tree, tmpdir):
    
    project = deepcopy(project) 

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Hydrodynamics")
    theme_menu.activate(core, project,  "Economics")
    
    project_menu.initiate_dataflow(core, project)
                                   
    hydro_branch = var_tree.get_branch(core, project, "Hydrodynamics")
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                             
    eco_branch = var_tree.get_branch(core, project, "Economics")
    eco_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path,
                                           "inputs_economics.pkl"))
    core.dump_datastate(project, dump_path=str(tmpdir))
    
    datastate_file_path = os.path.join(str(tmpdir), "datastate_dump.json")
    pool_file_path = os.path.join(str(tmpdir), "pool.pkl")
    
    assert os.path.isfile(datastate_file_path)
    assert os.path.isfile(pool_file_path)

    
def test_dump_datastate_archive(core, project, var_tree, tmpdir):
    
    project = deepcopy(project) 

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Hydrodynamics")
    theme_menu.activate(core, project,  "Economics")
    
    project_menu.initiate_dataflow(core, project)
                                   
    hydro_branch = var_tree.get_branch(core, project, "Hydrodynamics")
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                             
    eco_branch = var_tree.get_branch(core, project, "Economics")
    eco_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path,
                                           "inputs_economics.pkl"))

    datastate_file_name = "my_datastate.dts"
    datastate_file_path = os.path.join(str(tmpdir), datastate_file_name)
    
    core.dump_datastate(project, dump_path=datastate_file_path)
    
    assert os.path.isfile(datastate_file_path)
    
    
def test_dump_datastate_nodir(core, project, var_tree):
    
    project = deepcopy(project) 

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Hydrodynamics")
    theme_menu.activate(core, project,  "Economics")
    
    project_menu.initiate_dataflow(core, project)

    with pytest.raises(ValueError):
        core.dump_datastate(project, dump_path="some_path")
        

def test_dump_datastate_nonepath(core, project, var_tree):
    
    project = deepcopy(project) 

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Hydrodynamics")
    theme_menu.activate(core, project,  "Economics")
    
    project_menu.initiate_dataflow(core, project)

    with pytest.raises(ValueError):
        core.dump_datastate(project)


def test_load_datastate_archive(core, project, var_tree, tmpdir):
    
    temp_project = deepcopy(project) 

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, temp_project, "Hydrodynamics")
    theme_menu.activate(core, temp_project,  "Economics")
    
    project_menu.initiate_dataflow(core, temp_project)
                                   
    hydro_branch = var_tree.get_branch(core, temp_project, "Hydrodynamics")
    hydro_branch.read_test_data(core,
                                temp_project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                             
    eco_branch = var_tree.get_branch(core, temp_project, "Economics")
    eco_branch.read_test_data(core,
                              temp_project,
                              os.path.join(dir_path,
                                           "inputs_economics.pkl"))


    datastate_file_name = "my_datastate.dts"
    datastate_file_path = os.path.join(str(tmpdir), datastate_file_name)
    
    core.dump_datastate(temp_project, dump_path=datastate_file_path)
    
    del(temp_project)
    
    assert os.path.isfile(datastate_file_path)
    
    new_root = os.path.join(str(tmpdir), "test")
    os.makedirs(new_root)
    
    move_file_path = os.path.join(str(tmpdir), "test", datastate_file_name)
    shutil.copy2(datastate_file_path, move_file_path)
    
    temp_project = deepcopy(project) 

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, temp_project, "Hydrodynamics")
    
    project_menu.initiate_dataflow(core, temp_project)
    
    assert not core.has_data(temp_project, "device.turbine_interdistance")
    
    core.load_datastate(temp_project, move_file_path)

    assert temp_project.check_integrity()
    assert core.has_data(temp_project, "device.turbine_interdistance")
