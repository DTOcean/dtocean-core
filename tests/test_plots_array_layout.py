
import pytest

import os
from copy import deepcopy

import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

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


def test_ArrayLeasePlot_available(core, project, tree):

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Electrical Sub-Systems"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path, "inputs_wp3.pkl"))

    # Force addition of lease area
    lease_area = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    core.add_datastate(project,
                       identifiers=["site.lease_boundary"],
                       values=[lease_area])


    layout = mod_branch.get_input_variable(core, project, "project.layout")
    result = layout.get_available_plots(core, project)

    assert "Lease Area Array Layout" in result


def test_ArrayLeasePlot(core, project, tree):

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Electrical Sub-Systems"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path, "inputs_wp3.pkl"))

    # Force addition of lease area
    lease_area = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    core.add_datastate(project,
                       identifiers=["site.lease_boundary"],
                       values=[lease_area])

    layout = mod_branch.get_input_variable(core, project, "project.layout")
    layout.plot(core, project, "Lease Area Array Layout")

    assert len(plt.get_fignums()) == 1

    plt.close("all")
    
    
def test_ArrayCablesPlot_available(core, project, tree):
    
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Electrical Sub-Systems"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    # Need to provide these inputs:
    #   "site.lease_boundary",
    #   "corridor.landing_point",
    #   "project.layout",
    #   "project.cable_routes",
    #   "project.substation_layout"
    
    lease_area = Polygon([(0, 0), (20, 0), (20, 50), (0, 50)])
    landing_point = [10, 0]
    layout = {"device001": (10, 40)}
    substation = {"array": [10, 20]}
    
    cable_dict = {"Marker": [0, 0, 0, 1, 1, 1],#
                  "UTM X": [10, 10, 10, 10, 10, 10],
                  "UTM Y": [40, 30, 20, 20, 10, 0],
                  "Key Identifier": [None, None, None, None, None, None],
                  "Depth": [None, None, None, None, None, None],
                  "Burial Depth": [None, None, None, None, None, None],
                  "Sediment": [None, None, None, None, None, None],
                  "Split Pipe": [None, None, None, None, None, None]}
    cable_df = pd.DataFrame(cable_dict)
    
    core.add_datastate(project,
                       identifiers=["site.lease_boundary",
                                    "corridor.landing_point",
                                    "project.layout",
                                    "project.substation_layout",
                                    "project.cable_routes"],
                       values=[lease_area,
                               landing_point,
                               layout,
                               substation,
                               cable_df])

    mod_branch = tree.get_branch(core, project, mod_name)
    cables = mod_branch.get_output_variable(core,
                                            project,
                                            "project.cable_routes")
    result = cables.get_available_plots(core, project)

    assert "Array Cable Layout" in result


def test_ArrayCablesPlot(core, project, tree):
    
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Electrical Sub-Systems"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    # Need to provide these inputs:
    #   "site.lease_boundary",
    #   "corridor.landing_point",
    #   "project.layout",
    #   "project.cable_routes",
    #   "project.substation_layout"
    
    lease_area = Polygon([(0, 0), (20, 0), (20, 50), (0, 50)])
    landing_point = [10, 0]
    layout = {"device001": (10, 40)}
    substation = {"array": [10, 20]}
    
    cable_dict = {"Marker": [0, 0, 0, 1, 1, 1],
                  "UTM X": [10, 10, 10, 10, 10, 10],
                  "UTM Y": [40, 30, 20, 20, 10, 0],
                  "Key Identifier": [None, None, None, None, None, None],
                  "Depth": [None, None, None, None, None, None],
                  "Burial Depth": [None, None, None, None, None, None],
                  "Sediment": [None, None, None, None, None, None],
                  "Split Pipe": [None, None, None, None, None, None]}
    cable_df = pd.DataFrame(cable_dict)
    
    core.add_datastate(project,
                       identifiers=["site.lease_boundary",
                                    "corridor.landing_point",
                                    "project.layout",
                                    "project.substation_layout",
                                    "project.cable_routes"],
                       values=[lease_area,
                               landing_point,
                               layout,
                               substation,
                               cable_df])

    mod_branch = tree.get_branch(core, project, mod_name)
    cables = mod_branch.get_output_variable(core,
                                            project,
                                            "project.cable_routes")
    cables.plot(core, project, "Array Cable Layout")

    assert len(plt.get_fignums()) == 1

    plt.close("all")
