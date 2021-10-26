# -*- coding: utf-8 -*-

import pytest
import numpy as np
from shapely.geometry import Polygon

from dtocean_core.core import OrderedSim, Project, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import Strata
from dtocean_core.menu import ModuleMenu
from dtocean_core.pipeline import Branch
from dtocean_core.strategies.basic import BasicStrategy
from dtocean_core.strategies.position_optimiser.positioner import (
                                                ParaPositioner)
from dtocean_core.strategies.position_optimiser.iterator import (
                                                _get_branch,
                                                prepare,
                                                _get_basic_strategy, 
                                                iterate,
                                                get_positioner)

# Check for module
pytest.importorskip("dtocean_hydro")


@pytest.fixture
def lease_polygon():
    return Polygon([(100, 50), (900, 50), (900, 250), (100, 250)])


@pytest.fixture
def layer_depths():

    x = np.linspace(0.,1000.,101)
    y = np.linspace(0.,300.,31) 
    nx = len(x)
    ny = len(y)
    
    X, Y = np.meshgrid(x,y)
    Z = -X * 0.1 - 1
    depths = Z.T[:, :, np.newaxis]
    
    sediments = np.chararray((nx,ny,1), itemsize=20)
    sediments[:] = "rock"
       
    raw = {"values": {'depth': depths,
                      'sediment': sediments},
           "coords": [x, y, ["layer 1"]]}
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x",
                                    "y",
                                    "layer",
                                    "depth",
                                    "sediment"]})
    
    test = Strata()
    a = test.get_data(raw, meta)
    
    return test.get_value(a)


def test_get_branch():
    
    core = Core()
    project = Project("mock")
    new_sim = OrderedSim("Default")
    new_sim.set_inspection_level(core._markers["initial"])
    project.add_simulation(new_sim)
    core.register_level(project,
                        core._markers["initial"],
                        None)
    
    core.new_hub(project) # project hub
    core.new_hub(project) # modules hub
    
    branch_name = "Hydrodynamics"
    
    menu = ModuleMenu()
    menu.activate(core, project, branch_name)
    
    test = _get_branch(core, project, branch_name)
    
    assert isinstance(test, Branch)


def test_prepare(mocker, lease_polygon, layer_depths):
    
    modules = ['Hydrodynamics',
               'Electrical Sub-Systems',
               'Mooring and Foundations',
               'Installation',
               'Operations and Maintenance']
    
    module_menu = mocker.MagicMock()
    module_menu.get_active.return_value = modules
    
    mocker.patch('dtocean_core.strategies.position_optimiser.iterator.'
                 'ModuleMenu',
                  return_value=module_menu)
    
    mock_var = mocker.MagicMock()
    mock_branch = mocker.MagicMock()
    mock_branch.get_input_variable.return_value = mock_var
    
    _get_branch = mocker.patch('dtocean_core.strategies.position_optimiser.'
                               'iterator._get_branch',
                               return_value=mock_branch)
    
    core = mocker.MagicMock()
    core.get_data_value.return_value = 1
    
    project = Project("mock")
    
    positioner = ParaPositioner(lease_polygon,
                                layer_depths)
    
    grid_orientation = np.pi / 2
    delta_row = 20
    delta_col = 10
    t1 = 0.5
    t2 = 0.5
    n_nodes = 9
    dev_per_string = 5
    n_evals = 2
    
    prepare(core,
            project,
            positioner,
            grid_orientation,
            delta_row,
            delta_col,
            n_nodes,
            t1,
            t2,
            dev_per_string,
            n_evals)
    
    expecteds = ['Hydrodynamics',
                 'Electrical Sub-Systems',
                 'Operations and Maintenance']
    
    for call, expected in zip(_get_branch.call_args_list, expecteds):
        assert call.args[2] == expected


def test_get_basic_strategy():
    basic_strategy = _get_basic_strategy()
    assert isinstance(basic_strategy, BasicStrategy)


def test_iterate(mocker):
    
    mocker.patch('dtocean_core.strategies.position_optimiser.iterator.'
                 'prepare')
    
    basic_strategy = mocker.MagicMock()
    
    mocker.patch('dtocean_core.strategies.position_optimiser.iterator.'
                 '_get_basic_strategy',
                 return_value=basic_strategy)
    
    iterate(None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None)
    
    assert basic_strategy.execute.called


def test_get_positioner(mocker,
                        lease_polygon,
                        layer_depths):
    
    def give_data(dummy, var):
        
        if var == "site.lease_boundary":
            return lease_polygon
        
        if var == "bathymetry.layers":
            return layer_depths
        
        if var == 'device.installation_depth_max':
            return None
        
        if var == 'device.installation_depth_min':
            return None
        
        if var == 'farm.nogo_areas':
            return (Polygon([(800, 0),
                             (1000, 0),
                             (1000, 150),
                             (800, 150)]),
                    Polygon([(800, 150),
                             (1000, 150),
                             (1000, 300),
                             (800, 300)]))
        
        if var == 'options.boundary_padding':
            return 10
        
        if var == 'device.turbine_interdistance':
            return 20
    
    core = mocker.MagicMock()
    core.has_data.return_value = True
    core.get_data_value = give_data
    
    positioner = get_positioner(core, None)
    
    assert isinstance(positioner, ParaPositioner)
