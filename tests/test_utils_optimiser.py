# -*- coding: utf-8 -*-

import queue
from collections import namedtuple

import pytest
import numpy as np

from dtocean_core.utils.optimiser import NormScaler, Counter, Iterator


@pytest.fixture
def norm_scaler():
    return NormScaler(0, 12, 9)


def test_NormScaler_bad_x0():
    
    with pytest.raises(ValueError) as excinfo:
        NormScaler(0, 1, -1)
    
    assert "x0 must lie between" in str(excinfo)


def test_NormScaler_x0(norm_scaler):
    assert np.isclose(norm_scaler.x0, 3)


@pytest.mark.parametrize("value", range(13))
def test_NormScaler_scaling(norm_scaler, value):
    scaled = norm_scaler.scaled(value)
    assert np.isclose(norm_scaler.inverse(scaled), value)

MockParams = namedtuple('MockParams', ['cost', 'x'])

class MockCounter(Counter):
    
    def _set_params(self, *args):
        """Build a params (probably namedtuple) object to record iteration."""
        return MockParams(args[0], args[1:])
    
    def _get_cost(self, params, *args):
        
        print params.x
        print args
        
        if np.isclose(params.x, args).all():
            return params.cost
        
        return None


def test_Counter_set_params():
    
    counter = MockCounter()
    iteration = counter.get_iteration()
    counter.set_params(iteration, 11, 1)
    iteration = counter.get_iteration()
    counter.set_params(iteration, 12, 2)
    
    search_dict = counter.copy_search_dict()
    
    assert len(search_dict) == 2
    assert search_dict[1] == MockParams(12, (2,))


def test_Counter_set_params_bad_iter():
    
    counter = MockCounter()
    iteration = counter.get_iteration()
    counter.set_params(iteration, 1, 11)
    
    with pytest.raises(ValueError) as excinfo:
        counter.set_params(iteration, 2, 12)
    
    assert "has already been recorded" in str(excinfo)


@pytest.mark.parametrize("value, expected",
                         [(1, 11),
                          (2, 12),
                          (3, False)])
def test_Counter_get_cost(value, expected):
    
    counter = MockCounter()
    iteration = counter.get_iteration()
    counter.set_params(iteration, 11, 1)
    iteration = counter.get_iteration()
    counter.set_params(iteration, 12, 2)
    
    assert counter.get_cost(value) == expected


class MockIterator(Iterator):
    
    def _init_counter(self):
        return MockCounter()
    
    def _get_popen_args(self, worker_project_path, *args):
        "Return the arguments to create a new process thread using Popen"
        self._args = args
        return ["python", "-V"]
    
    def _get_worker_results(self, iteration):
        """Return the results for the given iteration as a dictionary that
        must include the key "cost". For constraint violation the cost key
        should be set to np.nan"""
        
        # Sphere (squared norm) test objective function
        c = 0.0
        x = np.array(self._args)
        
        if x[0] < c:
            cost =  np.nan
            print cost
        else:
            cost = -c**2 + sum((x + 0)**2)
            print cost
        
        return {"cost": cost}
    
    def _set_counter_params(self, iteration,
                                  worker_project_path,
                                  results,
                                  flag,
                                  *args):
        """Update the counter object with new data."""
        self._counter.set_params(results["cost"], *args)
        return
    
    def _log_exception(self, e, flag):
        
        print flag
        print e
        
        raise e


def test_iterator(mocker):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir")
    mock_core = mocker.MagicMock()
    
    test = MockIterator(mock_core, None, "mock", "mock")
    
    thread_queue = queue.Queue()
    result_queue = queue.Queue()
    
    item = [result_queue]
    item.append([1])
    item.append(["mock1"])
    
    thread_queue.put(item)
    
    item = [result_queue]
    item.append([10])
    item.append(["mock2"])
    
    thread_queue.put(item)
    print thread_queue.empty()
    
    test(thread_queue, stop_empty=True)
    
    print result_queue.get()
    print result_queue.get()
    
    assert False



