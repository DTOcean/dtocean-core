# -*- coding: utf-8 -*-

from collections import namedtuple

import pytest
import numpy as np

from dtocean_core.utils.optimiser import NormScaler, Counter


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

MockParams = namedtuple('MockParams', ['mock', 'cost'])

class MockCounter(Counter):
    
    def _set_params(self, mock, cost):
        """Build a params (probably namedtuple) object to record iteration."""
        return MockParams(mock, cost)
    
    def _get_cost(self, params, *args):
        
        if params.mock == args[0]:
            return params.cost
        
        return None


def test_Counter_set_params():
    
    counter = MockCounter()
    iteration = counter.get_iteration()
    counter.set_params(iteration, 1, 11)
    iteration = counter.get_iteration()
    counter.set_params(iteration, 2, 12)
    
    search_dict = counter.copy_search_dict()
    
    assert len(search_dict) == 2
    assert search_dict[1] == MockParams(2, 12)


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
    counter.set_params(iteration, 1, 11)
    iteration = counter.get_iteration()
    counter.set_params(iteration, 2, 12)
    
    assert counter.get_cost(value) == expected
