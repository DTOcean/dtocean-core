
import pytest

import os
from copy import deepcopy

import matplotlib.pyplot as plt

from dtocean_core.core import Core
from dtocean_core.menu import ProjectMenu 
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
    
    project_menu.activate(core,
                          new_project,
                          "Site Boundary Selection")

    boundaries_branch = tree.get_branch(core,
                                        new_project,
                                        "Site Boundary Selection")
    boundaries_branch.read_test_data(core,
                                     new_project,
                                     os.path.join(dir_path,
                                                  "inputs_boundary.pkl"))
    project_menu._execute(core,
                          new_project,
                          "Site Boundary Selection",
                          set_output_level=False)
             
    return new_project


def test_SiteBoundaryPlot_available(core, project, tree):
    
    project = deepcopy(project) 
    
    boundaries_branch = tree.get_branch(core,
                                        project,
                                        "Site Boundary Selection")
                                                       
    site_boundary = boundaries_branch.get_input_variable(
                                                    core,
                                                    project,
                                                    "hidden.site_boundaries")
    result = site_boundary.get_available_plots(core, project)
    
    assert "Site Boundary" in result


def test_SiteBoundaryPlot(core, project, tree):
    
    project = deepcopy(project) 
    
    boundaries_branch = tree.get_branch(core,
                                        project,
                                        "Site Boundary Selection")
                                                       
    site_boundary = boundaries_branch.get_input_variable(
                                                    core,
                                                    project,
                                                    "hidden.site_boundaries")
    site_boundary.plot(core, project, "Site Boundary")
    
    assert len(plt.get_fignums()) == 1
    
    plt.close("all")


def test_AllBoundaryPlot_available(core, project, tree):
    
    project = deepcopy(project) 
    
    boundaries_branch = tree.get_branch(core,
                                        project,
                                        "Site Boundary Selection")
                                                       
    site_boundary = boundaries_branch.get_output_variable(
                                                    core,
                                                    project,
                                                    "hidden.site_boundary")
    result = site_boundary.get_available_plots(core, project)
    
    assert "All Boundaries" in result


def test_AllBoundaryPlot(core, project, tree):
    
    project = deepcopy(project) 
    
    boundaries_branch = tree.get_branch(core,
                                        project,
                                        "Site Boundary Selection")
                                                       
    site_boundary = boundaries_branch.get_output_variable(
                                                    core,
                                                    project,
                                                    "hidden.site_boundary")
    site_boundary.plot(core, project, "All Boundaries")
    
    assert len(plt.get_fignums()) == 1
    
    plt.close("all")
    
    
def test_DesignBoundaryPlot_available(core, project, tree):
    
    project = deepcopy(project) 
    
    boundaries_branch = tree.get_branch(core,
                                        project,
                                        "Site Boundary Selection")
                                                       
    lease_boundary = boundaries_branch.get_output_variable(
                                                    core,
                                                    project,
                                                    "site.lease_boundary")
    result = lease_boundary.get_available_plots(core, project)
    
    assert "Design Boundaries" in result


def test_DesignBoundaryPlot(core, project, tree):
    
    project = deepcopy(project) 
    
    boundaries_branch = tree.get_branch(core,
                                        project,
                                        "Site Boundary Selection")
                                                       
    lease_boundary = boundaries_branch.get_output_variable(
                                                    core,
                                                    project,
                                                    "site.lease_boundary")
    lease_boundary.plot(core, project, "Design Boundaries")
    
    assert len(plt.get_fignums()) == 1
    
    plt.close("all")
