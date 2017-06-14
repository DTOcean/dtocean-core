
import pytest

from copy import deepcopy

from aneris.entity import Pipeline
from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ModuleMenu, ProjectMenu, ThemeMenu 
from dtocean_core.pipeline import Tree
from dtocean_core.interfaces.hydrodynamics import HydroInterface
from dtocean_core.interfaces.economics import EconomicInterface
from dtocean_core.interfaces.environmental import EnvironmentalInterface
from dtocean_core.interfaces.reliability import ReliabilityInterface
from polite.paths import Directory


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()    
    
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
    
    assert "Hydrodynamics" in names
    
def test_activate_module(core, project, module_menu):

    mod_name = "Hydrodynamics"
    
    project = deepcopy(project) 
    module_menu.activate(core, project, mod_name)
    simulation = project.get_simulation()
    pipeline = simulation.get_hub("modules")
    module = pipeline._scheduled_interface_map.popitem(last=False)[1]
    
    assert isinstance(module, HydroInterface)
    
def test_get_available_themes(core, project, theme_menu):
    
    project = deepcopy(project) 
    names = theme_menu.get_available(core, project)
    
    assert "Economics" in names
    assert "Environmental Impact Assessment" in names
    assert "Reliability" in names
    
def test_activate_theme(core, project, theme_menu):

    mod_name = "Environmental Impact Assessment"
    
    project = deepcopy(project) 
    theme_menu.activate(core, project, mod_name)
    simulation = project.get_simulation()
    hub = simulation.get_hub("themes")
    module = hub._scheduled_interface_map["EnvironmentalInterface"]
    
    assert isinstance(module, EnvironmentalInterface)
    
    
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
