# -*- coding: utf-8 -*-

import logging
import contextlib
from collections import namedtuple

import numpy as np

from dtocean_core.utils.optimiser import (NormScaler,
                                          Counter,
                                          Evaluator,
                                          Main,
                                          NoiseHandler,
                                          init_evolution_strategy,
                                          dump_outputs,
                                          load_outputs)


@contextlib.contextmanager
def caplog_for_logger(caplog, logger_name, level=logging.DEBUG):
    caplog.handler.records = []
    logger = logging.getLogger(logger_name)
    logger.addHandler(caplog.handler)
    logger.setLevel(level)
    yield
    logger.removeHandler(caplog.handler)


class MockParams(namedtuple('MockParams', ['cost', 'x'])):
    def __eq__(self, other):
        a = self.cost
        b = other.cost
        return ((a == b) | (np.isnan(a) & np.isnan(b)) and
                self.x == other.x)


class MockCounter(Counter):
    
    def _set_params(self, *args):
        """Build a params (probably namedtuple) object to record iteration."""
        return MockParams(args[0], args[1:])
    
    def _get_cost(self, params, *args):
        
        isclose = np.isclose(params.x, args)
        
        if isclose.size > 0 and isclose.all():
            return params.cost
        
        return None


def noisy_sphere_cost(x, noise=5, cond=1.0):
    
    #    The BSD 3-Clause License
    #    Copyright (c) 2014 Inria
    #    Author: Nikolaus Hansen, 2008-
    #    Author: Petr Baudis, 2014
    #    Author: Youhei Akimoto, 2016-
    #    
    #    Redistribution and use in source and binary forms, with or without
    #    modification, are permitted provided that the following conditions
    #    are met:
    #    
    #    1. Redistributions of source code must retain the above copyright and
    #       authors notice, this list of conditions and the following disclaimer.
    #    
    #    2. Redistributions in binary form must reproduce the above copyright
    #       and authors notice, this list of conditions and the following
    #       disclaimer in the documentation and/or other materials provided with
    #       the distribution.
    #    
    #    3. Neither the name of the copyright holder nor the names of its
    #       contributors nor the authors names may be used to endorse or promote
    #       products derived from this software without specific prior written
    #       permission.
    #    
    #    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    #    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    #    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    #    AUTHORS OR CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
    #    OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
    #    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    #    DEALINGS IN THE SOFTWARE.
    
    def elli(x, xoffset=0, cond=1e6):
        """Ellipsoid test objective function"""
        
        x = np.asarray(x)
        
        if not np.isscalar(x[0]):  # parallel evaluation
            return [elli(xi) for xi in x]  # could save 20% overall
        
        N = len(x)
        ftrue = sum(cond**(np.arange(N) / (N - 1.)) * (x + xoffset)**2) \
                                            if N > 1 else (x + xoffset)**2
        
        return ftrue
    
    # noise=10 does not work with default popsize,
    # ``cma.NoiseHandler(dimension, 1e7)`` helps"""
    
    test = np.random.rand()
    
    if test > 0.5:
        sign = 1
    else:
        sign = -1
    
    noise = sign * np.exp(noise * np.random.randn() / len(x))
    
    return elli(x, cond=cond) * noise


class MockEvaluator(Evaluator):
    
    def __init__(self, *args, **kwargs):
        super(MockEvaluator, self).__init__(*args, **kwargs)
        self.scaler = None
    
    def _init_counter(self):
        return MockCounter()
    
    def _get_popen_args(self, worker_project_path, n_evals, *args):
        "Return the arguments to create a new process thread using Popen"
        if self.scaler is not None:
            args = [self.scaler.inverse(x) for x in args]
        self._args = args
        self._n_evals = n_evals
        return ["python", "-V"]
    
    def _get_worker_results(self, iteration):
        """Return the results for the given iteration as a dictionary that
        must include the key "cost". For constraint violation the cost key
        should be set to np.nan"""
        
        x = np.array(self._args)
        all_costs = np.array([noisy_sphere_cost(x)
                                        for _ in xrange(self._n_evals)])
        cost = np.nanmean(all_costs)
        
        return {"cost": cost}
    
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


def test_main(mocker, tmpdir):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir")
    mock_core = mocker.MagicMock()
    
    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")
    
    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler
    
    scaled_vars = [scaler] * 3
    xhat0 = [scaler.x0] * 3
    xhat_low_bound = [scaler.scaled(x_range[0])] * 3
    xhat_high_bound = [scaler.scaled(x_range[1])] * 3
    x_ops = [None] * 3
    
    es = init_evolution_strategy(xhat0,
                                 xhat_low_bound,
                                 xhat_high_bound,
                                 tolfun=1e-2,
                                 logging_directory=str(tmpdir))
    
    nh = NoiseHandler(es.N, maxevals=[1, 1, 30])
    
    test = Main(es, mock_eval, scaled_vars, x_ops, nh=nh, base_penalty=1e9)
    
    max_noise = -np.inf
    costs = []
    
    while max_noise <= 0:
        max_noise = max(max_noise, nh._noise_predict())
        print  nh._noise_predict()
        cost = es.result.fbest
        costs.append(cost)
        test.next()
    
    assert max_noise > 0
    
    first_cost = costs[0]
    last_cost = costs[-1]
    
    assert first_cost > last_cost


def test_dump_load_outputs(mocker, tmpdir):
    
    mocker.patch("dtocean_core.utils.optimiser.init_dir")
    mock_core = mocker.MagicMock()
    
    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")
    
    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler
    
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
    
    nh = NoiseHandler(es.N, maxevals=[1, 1, 30])
    
    test = Main(es,
                mock_eval,
                scaled_vars,
                x_ops,
                nh=nh,
                base_penalty=1e4,
                auto_resample_iterations=2)
    
    i = 0
    
    while i < 4:
        test.next()
        i += 1
    
    counter_dict = mock_eval.get_counter_search_dict()
    pre_dump = len(tmpdir.listdir())
    
    dump_outputs(str(tmpdir), es, mock_eval, nh)
    
    assert len(tmpdir.listdir()) == pre_dump + 3
    
    new_es, new_counter_dict, new_nh = load_outputs(str(tmpdir))
    
    assert es.fit.hist == new_es.fit.hist
    assert new_counter_dict == counter_dict
    assert new_nh._noise_predict() == nh._noise_predict()
