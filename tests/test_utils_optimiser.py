# -*- coding: utf-8 -*-

import queue
import threading
from collections import namedtuple

import pytest
import numpy as np

from dtocean_core.utils.optimiser import (NormScaler,
                                          Counter,
                                          Iterator,
                                          Main,
                                          init_evolution_strategy)


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
        
        isclose = np.isclose(params.x, args)
        
        if isclose.size > 0 and isclose.all():
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


def sphere_cost(x, c=0.0):
    
    # Sphere (squared norm) test objective function
    
    if (x < c).any():
        cost =  np.nan
    else:
        cost = -c**2 + sum((x + 0)**2)
    
    return cost


class MockIterator(Iterator):
    
    def __init__(self, *args, **kwargs):
        super(MockIterator, self).__init__(*args, **kwargs)
        self.scaler = None
    
    def _init_counter(self):
        return MockCounter()
    
    def _get_popen_args(self, worker_project_path, n_evals, *args):
        "Return the arguments to create a new process thread using Popen"
        if self.scaler is not None:
            args = [self.scaler.inverse(x) for x in args]
        self._args = args
        return ["python", "-V"]
    
    def _get_worker_results(self, iteration):
        """Return the results for the given iteration as a dictionary that
        must include the key "cost". For constraint violation the cost key
        should be set to np.nan"""
        
        x = np.array(self._args)
        return {"cost": sphere_cost(x)}
    
    def _set_counter_params(self, iteration,
                                  worker_project_path,
                                  results,
                                  flag,
                                  n_evals,
                                  *args):
        """Update the counter object with new data."""
        
        cost = np.nan
        if results is not None: cost = results["cost"]
        
        self._counter.set_params(iteration, cost, *args)
        
        return
    
#    def _log_exception(self, e, flag):
#        
#        print flag
#        print e
#        
#        raise e


def test_iterator(mocker):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir")
    mock_core = mocker.MagicMock()
    
    test = MockIterator(mock_core, None, "mock", "mock")
    
    thread_queue = queue.Queue()
    result_queue = queue.Queue()
    
    item = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])
    
    thread_queue.put(item)
    
    item = [result_queue]
    item.append(None)
    item.append([10])
    item.append(["mock2"])
    
    thread_queue.put(item)
    
    test(thread_queue, stop_empty=True)
    
    assert result_queue.get() == (1.0, ['mock1'])
    assert result_queue.get() == (100.0, ['mock2'])


def test_iterator_threaded(mocker):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir")
    mock_core = mocker.MagicMock()
    
    test = MockIterator(mock_core, None, "mock", "mock")
    
    thread_queue = queue.Queue()
    result_queue = queue.Queue()
    
    worker = threading.Thread(target=test,
                              args=(thread_queue,))
    worker.setDaemon(True)
    worker.start()
    
    item = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])
    
    thread_queue.put(item)
    
    item = [result_queue]
    item.append(None)
    item.append([10])
    item.append(["mock2"])
    
    thread_queue.put(item)
    
    thread_queue.join()
    
    assert result_queue.get() == (1.0, ['mock1'])
    assert result_queue.get() == (100.0, ['mock2'])


def test_iterator_previous_cost(mocker):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir")
    mock_core = mocker.MagicMock()
    
    test = MockIterator(mock_core, None, "mock", "mock")
    
    mocker.patch.object(test._counter,
                        "get_cost",
                        side_effect = [False, "match"])
    
    thread_queue = queue.Queue()
    result_queue = queue.Queue()
    
    item = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])
    
    thread_queue.put(item)
    
    item = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock2"])
    
    thread_queue.put(item)
    
    test(thread_queue, stop_empty=True)
    
    assert result_queue.get() == (1.0, ['mock1'])
    assert result_queue.get() == ("match", ['mock2'])


def test_iterator_fail_send(caplog, mocker):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir")
    mock_core = mocker.MagicMock()
    
    exc_msg = 'Bang!'
    mock_core.dump_project.side_effect = KeyError(exc_msg)
    
    test = MockIterator(mock_core, None, "mock", "mock")
    
    thread_queue = queue.Queue()
    result_queue = queue.Queue()
    
    item = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])
    
    thread_queue.put(item)
    
    test(thread_queue, stop_empty=True)
    
    assert result_queue.get() == (np.nan, ['mock1'])
    assert "Fail Send" in caplog.text
    assert exc_msg in caplog.text


def test_iterator_fail_execute(caplog, mocker):
    
    mock_process = mocker.MagicMock()
    mock_process.wait.return_value = 1
    
    mocker.patch('dtocean_core.utils.optimiser.Popen',
                 return_value=mock_process)
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir")
    
    mock_core = mocker.MagicMock()
    test = MockIterator(mock_core, None, "mock", "mock")
    
    thread_queue = queue.Queue()
    result_queue = queue.Queue()
    
    item = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])
    
    thread_queue.put(item)
    
    test(thread_queue, stop_empty=True)
    
    assert result_queue.get() == (np.nan, ['mock1'])
    assert "Fail Execute" in caplog.text
    assert "External process failed to open" in caplog.text


def test_iterator_fail_receive(caplog, mocker):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir")
    mock_core = mocker.MagicMock()
    
    test = MockIterator(mock_core, None, "mock", "mock")
    
    exc_msg = 'Bang!'
    mocker.patch.object(test,
                        "_get_worker_results",
                        side_effect=KeyError(exc_msg))
    
    thread_queue = queue.Queue()
    result_queue = queue.Queue()
    
    item = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])
    
    thread_queue.put(item)
    
    test(thread_queue, stop_empty=True)
    
    assert result_queue.get() == (np.nan, ['mock1'])
    assert "Fail Receive" in caplog.text
    assert exc_msg in caplog.text


def test_main(mocker, tmpdir):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir")
    mock_core = mocker.MagicMock()
    
    mock_iter = MockIterator(mock_core, None, "mock", "mock")
    
    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_iter.scaler = scaler
    
    scaled_vars = [scaler] * 2
    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2
    x_ops = [None] * 2
    
    es = init_evolution_strategy(xhat0,
                                 xhat_low_bound,
                                 xhat_high_bound,
                                 tolfun=1e-1,
                                 logging_directory=str(tmpdir))
    
    test = Main(es, mock_iter, scaled_vars, x_ops, base_penalty=1e4)
    
    while not test.stop:
        test.next()
    
    sol = np.array([scaler.inverse(x) for x in es.result.xfavorite])
    
    assert (sol >= x_range[0]).all()
    assert (sol <= x_range[1]).all()
    assert (sol ** 2).sum() < 1e-1
