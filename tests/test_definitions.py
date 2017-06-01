
import pytest

from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import AutoFileInput, AutoFileOutput, AutoPlot, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import (Histogram,
                                           HistogramDict,
                                           PointData,
                                           PointDict,
                                           PointList,
                                           PolygonData,
                                           PolygonList,
                                           XGrid2D,
                                           XSet2D,
                                           XSet3D
                                           )

# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()
        
    return new_core
    
    
def test_XGrid2D_available(core):
    
    all_objs = core.control._store._structures

    assert "XGrid2D" in all_objs.keys()


def test_XGrid2D(core):
    
    raw = {"values": np.random.randn(2, 3),
           "coords": [['a', 'b'], [-2, 0, 2]]}
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['x', 'y'],
                         "units": [None, 'm', 'POWER!']})
    
    test = XGrid2D()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b.values.shape == (2,3)
    assert b.units == 'POWER!'
    assert b.y.units == 'm'
    
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
    
def test_PointData(core):
    
    coords = (0., 0.)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = PointData()
    a = test.get_data(coords, meta)
    b = test.get_value(a)

    assert b.x == 0.
    assert b.y == 0.
    
def test_PointDict(core):
    
    raw_dict = {"one"   : (0., 0.),
                "two"   : (1., 1.),
                "three" : (2., 2.)
                }

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = PointDict()
    a = test.get_data(raw_dict, meta)
    b = test.get_value(a)

    assert b["one"].x == 0.
    assert b["two"].y == 1.
    
def test_PointList(core):
    
    raw_list = [(0., 0.),
                (1., 1.),
                (2., 2.)
                ]

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = PointList()
    a = test.get_data(raw_list, meta)
    b = test.get_value(a)

    assert b[0].x == 0.
    assert b[1].y == 1.
    
def test_PolygonData(core):
    
    raw_list = [(0., 0.),
                (1., 0.),
                (1., 1.)
                ]

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = PolygonData()
    a = test.get_data(raw_list, meta)
    b = test.get_value(a)

    assert b.exterior.coords[0][0] == 0.
    assert b.exterior.coords[2][1] == 1.
    
def test_PolygonList(core):
    
    raw_list = [[(0., 0.),
                 (1., 0.),
                 (1., 1.)],
                [(10., 10.),
                 (11., 10.),
                 (11., 11.)]
                ]

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = PolygonList()
    a = test.get_data(raw_list, meta)
    b = test.get_value(a)

    assert b[0].exterior.coords[0][0] == 0.
    assert b[1].exterior.coords[2][1] == 11.

def test_Histogram(core):
    
    test_data = np.random.random(10)
    values, bins = np.histogram(test_data)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = Histogram()
    a = test.get_data((values, bins), meta)
    b = test.get_value(a)

    assert len(b["values"]) == len(values)
    assert len(b["bins"]) == len(values) + 1
    
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
    

