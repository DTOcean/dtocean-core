
import os
import pkg_resources

import pytest

from dtocean_core.core import Core
from dtocean_core.extensions import ToolManager
from dtocean_core.menu import ModuleMenu, ProjectMenu
from dtocean_core.pipeline import Tree
from dtocean_core.utils.version import Version

# Check for module and version
pkg_title = "dtocean-hydrodynamics"
pkg_import = "dtocean_hydro"
major_version = 3

pytest.importorskip(pkg_import)
version = pkg_resources.get_distribution(pkg_title).version
pytestmark = pytest.mark.skipif(Version(version).major != major_version,
                                reason="module has incorrect major version")

dir_path = os.path.dirname(__file__)


@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    return Core()


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture()
def project(core):
    '''Share a Project object'''
    
    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    var_tree = Tree()
    mod_name = "Hydrodynamics"
    
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
    
    module_menu.activate(core, new_project, mod_name)
    project_menu.initiate_dataflow(core, new_project)
    
    hydro_branch = var_tree.get_branch(core, new_project, mod_name)
    hydro_branch.read_test_data(core,
                                new_project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
    
    return new_project


@pytest.fixture()
def wave_project(core):
    '''Share a Project object'''
    
    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    var_tree = Tree()
    mod_name = "Hydrodynamics"
    
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
    
    module_menu.activate(core, new_project, mod_name)
    project_menu.initiate_dataflow(core, new_project)
    
    hydro_branch = var_tree.get_branch(core, new_project, mod_name)
    hydro_branch.read_test_data(core,
                                new_project,
                                os.path.join(dir_path,
                                             "inputs_wp2_wave.pkl"))
    
    return new_project


def test_available():
    tool_man = ToolManager()
    assert "Device Minimum Spacing Check" in tool_man.get_available()


def test_can_execute_tool(core, project):
    
    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")
    
    assert tool_man.can_execute_tool(core, project, tool)


def test_execute_tool_no_config(core, project):
    
    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")
    
    with pytest.raises(RuntimeError) as excinfo:
        tool_man.execute_tool(core, project, tool)
    
    assert "Was configure called?" in str(excinfo)


def test_execute_tool(core, project):
    
    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")
    
    layout = [(450., 100.),
              (550., 100.),
              (450., 150.),
              (550., 150.)]
    tool.configure(layout)
    
    tool_man.execute_tool(core, project, tool)


def test_execute_tool_wave(core, wave_project):
    
    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")
    
    layout = [(450., 100.),
              (550., 100.),
              (450., 150.),
              (550., 150.)]
    tool.configure(layout)
    
    tool_man.execute_tool(core, wave_project, tool)


def test_execute_tool_fail_minimum_distance(core, project):
    
    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")
    
    layout = [(450., 100.),
              (455., 100.),
              (450., 105.),
              (455., 105.)]
    tool.configure(layout)
    
    with pytest.raises(RuntimeError) as excinfo:
        tool_man.execute_tool(core, project, tool)
    
    assert "Violation of the minimum distance constraint" in str(excinfo)
