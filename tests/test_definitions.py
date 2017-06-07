
import pytest

from datetime import datetime

import numpy as np

from dtocean_core.core import Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import (HistogramDict,
                                           XSet2D,
                                           XSet3D
                                           )

# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()
        
    return new_core
    

def test_XSet2D(core):
    
    raw = {"values": {"a": np.random.randn(2, 3),
                      "b": np.random.randn(2, 3)},
           "coords": [['a', 'b'], [-2, 0, 2]]}
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['x', 'y', 'a', 'b'],
                         "units": [None, 'm', 'POWER!', None]
                         })
    
    test = XSet2D()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b["a"].shape == (2,3)
    assert b["a"].units == 'POWER!'
    assert b.y.units == 'm'


def test_XSet3D(core):
    
    raw = {"values": {"a": np.random.randn(2, 3, 1),
                      "b": np.random.randn(2, 3, 1)},
           "coords": [['a', 'b'],
                      [-2, 0, 2],
                      [datetime(2010, 12, 01)]]}
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['x', 'y', 't', 'a', 'b'],
                         "units": [None, 'm', 's', 'POWER!', None]
                         })
    
    test = XSet3D()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b["a"].shape == (2,3,1)
    assert b["a"].units == 'POWER!'
    assert b.t.units == 's'

    
def test_HistogramDict(core):
    
    test_data_one = np.random.random(10)
    test_data_two = np.random.random(10)
    
    values_one, bins_one = np.histogram(test_data_one)
    values_two, bins_two = np.histogram(test_data_two)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
                         
    values_dict = {"test_one": (values_one, bins_one),
                   "test_two": (values_two, bins_two)}
    
    test = HistogramDict()
    a = test.get_data(values_dict, meta)
    b = test.get_value(a)

    assert len(b["test_one"]["values"]) == len(values_one)
    assert len(b["test_two"]["bins"]) == len(b["test_two"]["values"]) + 1
