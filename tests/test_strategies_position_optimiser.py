# -*- coding: utf-8 -*-

import os

import numpy as np
import pytest
from shapely.geometry import Polygon

from yaml import dump
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


from dtocean_core.core import Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import Strata
from dtocean_core.strategies.position_optimiser.positioner import (
                                                        ParaPositioner)
from dtocean_core.strategies.position_optimiser import (PositionParams,
                                                        PositionCounter,
                                                        PositionEvaluator,
                                                        _get_range_fixed,
                                                        _get_range_multiplier,
                                                        _get_param_control)


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


def test_PositionCounter_set_params():
    
    counter = PositionCounter()
    evaluation = counter.next_evaluation()
    mock = ["mock"] * 12
    counter.set_params(evaluation, *mock)
    
    search_dict = counter.search_dict
    params = search_dict[evaluation]
    
    assert isinstance(params, PositionParams)
    assert params.grid_orientation == "mock"


def test_PositionCounter_get_cost():
    
    counter = PositionCounter()
    evaluation = counter.next_evaluation()
    mock = ["mock"] * 12
    counter.set_params(evaluation, *mock)
    
    assert not counter.get_cost(mock)


def test_PositionEvaluator_init_bad_objective(mocker,
                                              lease_polygon,
                                              layer_depths):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir",
                 autospec=True)
    
    positioner = ParaPositioner(lease_polygon,
                                layer_depths)
    
    mocker.patch("dtocean_core.strategies.position_optimiser.get_positioner",
                 return_value=positioner,
                 autospec=True)

    mock_core = mocker.MagicMock()
    
    mock_simulation = mocker.MagicMock()
    mock_simulation.get_output_ids.return_value = ["mock"]
    
    mock_project = mocker.MagicMock()
    mock_project.get_simulation.return_value = mock_simulation
    
    with pytest.raises(RuntimeError) as excinfo:
        PositionEvaluator(mock_core,
                          mock_project,
                          "mock",
                          "mock",
                          "not_mock")
    
    assert "is not an output of the base" in str(excinfo)


@pytest.fixture
def evaluator(mocker, lease_polygon, layer_depths):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir",
                 autospec=True)
    
    positioner = ParaPositioner(lease_polygon,
                                layer_depths)
    
    mocker.patch("dtocean_core.strategies.position_optimiser.get_positioner",
                 return_value=positioner,
                 autospec=True)
    
    mock_core = mocker.MagicMock()
    
    mock_simulation = mocker.MagicMock()
    mock_simulation.get_output_ids.return_value = ["mock"]
    
    mock_project = mocker.MagicMock()
    mock_project.get_simulation.return_value = mock_simulation
    
    test = PositionEvaluator(mock_core,
                             mock_project,
                             "mock",
                             "mock",
                             "mock")
    
    return test


def test_PositionEvaluator_init(evaluator):
    assert evaluator._objective_var == "mock"
    assert evaluator._violation_log_path == os.path.join("mock",
                                                         "violations.txt")


def test_PositionEvaluator_init_counter(evaluator):
    counter = evaluator._init_counter()
    assert isinstance(counter, PositionCounter)


def test_PositionEvaluator_get_popen_args(evaluator):
    
    worker_project_path = "mock"
    n_evals = 1.0
    args = ["mock"] * 6 + [1.0]
    
    popen_args = evaluator._get_popen_args(worker_project_path, n_evals, *args)
    
    assert popen_args == ['_dtocean-optim-pos'] + \
                         ['mock'] * 7 + \
                         ['--dev_per_string', '1', '--n_evals', '1']


def test_PositionEvaluator_get_worker_results_success(mocker, evaluator):
    
    mock_stg_dict = {"status": "Success",
                     "results": {"mock": 1}}
    
    mocker.patch('dtocean_core.strategies.position_optimiser.open',
                 mocker.mock_open(read_data=dump(mock_stg_dict,
                                                 Dumper=Dumper)))
    
    results = evaluator._get_worker_results(1)
    
    assert results == {'status': 'Success',
                       'worker_results_path': os.path.join('mock',
                                                           'mock_1.yaml'),
                       'cost': 1,
                       'results': {'mock': 1}}


def test_PositionEvaluator_get_worker_results_exception(mocker, evaluator):
    
    mock_stg_dict = {"status": "Exception",
                     "error": "mock"}
    
    mocker.patch('dtocean_core.strategies.position_optimiser.open',
                 mocker.mock_open(read_data=dump(mock_stg_dict,
                                                 Dumper=Dumper)))
    
    results = evaluator._get_worker_results(1)
    
    assert results == {'status': 'Exception',
                       'worker_results_path': os.path.join('mock',
                                                           'mock_1.yaml'),
                       'cost': np.nan,
                       'error': 'mock'}


def test_PositionEvaluator_get_worker_results_bad_flag(mocker, evaluator):
    
    mock_stg_dict = {"status": "mock"}
    
    mocker.patch('dtocean_core.strategies.position_optimiser.open',
                 mocker.mock_open(read_data=dump(mock_stg_dict,
                                                 Dumper=Dumper)))
    
    with pytest.raises(RuntimeError) as excinfo:
        evaluator._get_worker_results(1)
    
    assert 'Unrecognised flag' in str(excinfo)


def test_PositionEvaluator_set_counter_params_no_results(evaluator):
    
    evaluation = 1
    worker_project_path = "mock"
    results = None
    flag = "mock"
    n_evals = 1
    args = ["mock"] * 7
    
    evaluator._set_counter_params(evaluation,
                                  worker_project_path,
                                  results,
                                  flag,
                                  n_evals,
                                  *args)
    
    search_dict = evaluator._counter.search_dict
    params = search_dict[evaluation]
    
    assert params.n_evals == n_evals
    assert params.yaml_file_path is None
    assert np.isnan(params.cost)


def test_PositionEvaluator_set_counter_params_results(evaluator):
    
    evaluation = 1
    worker_project_path = "mock"
    cost = 1
    results = {"worker_results_path": "mock",
               "cost": cost}
    flag = "mock"
    n_evals = 1
    args = ["mock"] * 7
    
    evaluator._set_counter_params(evaluation,
                                  worker_project_path,
                                  results,
                                  flag,
                                  n_evals,
                                  *args)
    
    search_dict = evaluator._counter.search_dict
    params = search_dict[evaluation]
    
    assert params.n_evals == n_evals
    assert params.yaml_file_path == "mock"
    assert params.cost == cost


def test_PositionEvaluator_pre_constraints_hook(mocker, tmpdir, evaluator):
    
    evaluator._violation_log_path = os.path.join(str(tmpdir),
                                                 "violations.txt")
    
    mocker.patch.object(evaluator._tool_man,
                        'execute_tool',
                        autospec=True)
    
    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = 0.5
    t2 = 0.5
    dev_per_string = 5
    
    args = (grid_orientation,
            delta_row,
            delta_col,
            n_nodes,
            t1,
            t2,
            dev_per_string)
    
    assert not evaluator.pre_constraints_hook(*args)
    assert len(tmpdir.listdir()) == 0


@pytest.mark.parametrize("n_nodes, t1,  expected", [
                         (2000,    0.5, "number of nodes not found"),
                         (5,       1.5, "lies outside of valid domain")])
def test_PositionEvaluator_pre_constraints_hook_position_true(mocker,
                                                              tmpdir,
                                                              evaluator,
                                                              n_nodes,
                                                              t1,
                                                              expected):
    
    evaluator._violation_log_path = os.path.join(str(tmpdir),
                                                 "violations.txt")
    
    mocker.patch.object(evaluator._tool_man,
                        'execute_tool',
                        autospec=True)
    
    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    t2 = 0.5
    dev_per_string = 5
    
    args = (grid_orientation,
            delta_row,
            delta_col,
            n_nodes,
            t1,
            t2,
            dev_per_string)
    
    assert evaluator.pre_constraints_hook(*args)
    assert len(tmpdir.listdir()) == 1
    
    with open(evaluator._violation_log_path, 'r') as f:
        line = f.readline()
    
    assert expected in line


def test_PositionEvaluator_pre_constraints_hook_position_error(mocker,
                                                               tmpdir,
                                                               evaluator):
    
    evaluator._violation_log_path = os.path.join(str(tmpdir),
                                                 "violations.txt")
    
    expected = "mock_positioner"
    mocker.patch.object(evaluator,
                        '_positioner',
                        side_effect=RuntimeError(expected),
                        autospec=True)
    
    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = 0.5
    t2 = 0.5
    dev_per_string = 5
    
    args = (grid_orientation,
            delta_row,
            delta_col,
            n_nodes,
            t1,
            t2,
            dev_per_string)
    
    with pytest.raises(RuntimeError) as excinfo:
        evaluator.pre_constraints_hook(*args)
    
    assert len(tmpdir.listdir()) == 0
    assert expected in str(excinfo)


def test_PositionEvaluator_pre_constraints_hook_spacing_true(mocker,
                                                             tmpdir,
                                                             evaluator):
    
    evaluator._violation_log_path = os.path.join(str(tmpdir),
                                                 "violations.txt")
    
    expected = "Violation of the minimum distance constraint"
    mocker.patch.object(evaluator._tool_man,
                        'execute_tool',
                        side_effect=RuntimeError(expected),
                        autospec=True)
    
    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = 0.5
    t2 = 0.5
    dev_per_string = 5
    
    args = (grid_orientation,
            delta_row,
            delta_col,
            n_nodes,
            t1,
            t2,
            dev_per_string)
    
    assert evaluator.pre_constraints_hook(*args)
    assert len(tmpdir.listdir()) == 1
    
    with open(evaluator._violation_log_path, 'r') as f:
        line = f.readline()
    
    assert expected in line


def test_PositionEvaluator_pre_constraints_hook_spacing_error(mocker,
                                                              tmpdir,
                                                              evaluator):
    
    evaluator._violation_log_path = os.path.join(str(tmpdir),
                                                 "violations.txt")
    
    expected = "mock_spacing"
    mocker.patch.object(evaluator._tool_man,
                        'execute_tool',
                        side_effect=RuntimeError(expected),
                        autospec=True)
    
    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = 0.5
    t2 = 0.5
    dev_per_string = 5
    
    args = (grid_orientation,
            delta_row,
            delta_col,
            n_nodes,
            t1,
            t2,
            dev_per_string)
    
    with pytest.raises(RuntimeError) as excinfo:
        evaluator.pre_constraints_hook(*args)
    
    assert len(tmpdir.listdir()) == 0
    assert expected in str(excinfo)


def test_PositionEvaluator_cleanup_hook(tmpdir, evaluator):
    
    p = tmpdir.join("mock.txt")
    p.write("content")
    
    assert len(tmpdir.listdir()) == 1
    
    evaluator._cleanup_hook(str(p), None, None)
    
    assert len(tmpdir.listdir()) == 0


def test_get_range_fixed():
    a = 1
    b = 2
    assert _get_range_fixed(a, b) == (a, b)


@pytest.fixture
def mock_core_get_data_value(mocker):
    
    mock_core = Core()
    
    mocker.patch.object(mock_core,
                        'get_data_value',
                        return_value=2,
                        autospec=True)
    
    return mock_core


def test_get_range_multiplier(mock_core_get_data_value):
    
    (a, b) = _get_range_multiplier(mock_core_get_data_value, None, None, 1, 2)
    
    assert a == 2
    assert b == 4


def test_get_param_control(mock_core_get_data_value):
    
    param_fixed = {"fixed": 0}
    param_range_fixed = {"range": {"type": "fixed",
                                   "min": 1,
                                   "max": 2}}
    param_range_fixed_x0 = {"range": {"type": "fixed",
                                       "min": 1,
                                       "max": 2},
                             "x0": 1.5}
    param_range_fixed_int = {"range": {"type": "fixed",
                                       "min": 1,
                                       "max": 2},
                             "integer": True}
    param_range_multiplier = {"range": {"type": "multiplier",
                                        "variable": "mock",
                                        "min_multiplier": 1,
                                        "max_multiplier": 2}}
    parameters = {"grid_orientation": param_fixed,
                  "delta_row": param_range_fixed,
                  "delta_col": param_range_fixed_x0,
                  "n_nodes": param_range_fixed_int,
                  "t1": param_range_multiplier,
                  "t2": param_range_multiplier}
    
    config = {"parameters": parameters}
    
    result = _get_param_control(mock_core_get_data_value, None, config)
    
    assert result == {'ranges': [(1, 2), (1, 2), (1, 2), (2, 4), (2, 4)],
                      'x0s': [None, 1.5, None, None, None],
                      'fixed_params': {0: np.pi / 2, 6: None},
                      'x_ops': [None, None, np.floor, None, None],
                      'integer_variables': [2]}


def test_get_param_control_more():
    
    param_range_fixed = {"range": {"type": "fixed",
                                   "min": 1,
                                   "max": 2}}
    param_range_fixed_x0 = {"range": {"type": "fixed",
                                       "min": -90,
                                       "max": 90},
                             "x0": 0}
    param_range_fixed_int = {"range": {"type": "fixed",
                                       "min": 1,
                                       "max": 2},
                             "integer": True}
    parameters = {"grid_orientation": param_range_fixed_x0,
                  "delta_row": param_range_fixed,
                  "delta_col": param_range_fixed,
                  "n_nodes": param_range_fixed_int,
                  "t1": param_range_fixed,
                  "t2": param_range_fixed,
                  "dev_per_string": param_range_fixed_int}
    
    config = {"parameters": parameters}
    
    result = _get_param_control(None, None, config)
    
    assert result == {'ranges': [[0, np.pi]] + [(1, 2)] * 6,
                      'x0s': [np.pi / 2, None, None, None, None, None, None],
                      'fixed_params': None,
                      'x_ops': [None, None, None, np.floor, None, None, np.floor],
                      'integer_variables': [3, 6]}
