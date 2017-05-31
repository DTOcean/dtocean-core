
import pytest

from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import AutoFileInput, AutoFileOutput, AutoPlot, Core
from dtocean_core.menu import ProjectMenu
from dtocean_core.pipeline import Tree
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import (SeriesData,
                                           IndexTable,
                                           Histogram,
                                           HistogramDict,
                                           LineTable,
                                           NumpyLineDict,
                                           PointData,
                                           PointDict,
                                           PointList,
                                           PolygonData,
                                           PolygonList,
                                           TimeSeries,
                                           TimeTable,
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
                                                    tree, 
                                                    "device.system_type")
    device_type.set_raw_interface(core, "Wave Floating")
    new_project = device_type.connect(core, new_project, tree)
             
    return new_project

def test_SeriesData():
    
    raw = np.random.rand(100)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['mass'],
                         "units": ["kg"]})
    
    test = SeriesData()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert len(b) == len(raw)


def test_SeriesData_auto_file(tmpdir):
        
    raw = np.random.rand(100)
    test_path = tmpdir.mkdir("sub").join("test.csv")
    test_path_str = str(test_path)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['mass'],
                         "units": ["kg"]})
    
    test = SeriesData()
    
    fout_factory = InterfaceFactory(AutoFileOutput)
    FOutCls = fout_factory(meta, test)
    
    fout = FOutCls()
    fout._path = test_path_str
    fout.data.result = test.get_data(raw, meta)

    fout.connect()
    
    assert len(tmpdir.listdir()) == 1
              
    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)
              
    fin = FInCls()
    fin._path = test_path_str
    
    fin.connect()
    
    assert len(fin.data.result) == len(raw)


def test_TimeSeries(core):
    
    dates = []
    dt = datetime(2010, 12, 01)
    end = datetime(2010, 12, 02, 23, 59, 59)
    step = timedelta(seconds=3600)
    
    while dt < end:
        dates.append(dt)
        dt += step
        
    values = np.random.rand(len(dates))
    raw = [(d, v) for d, v in zip(dates, values)]

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['mass'],
                         "units": ["kg"]})
    
    test = TimeSeries()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert len(b) == len(dates)
    assert len(b.resample('D').mean()) == 2


def test_TimeSeries_auto_file(tmpdir):
        
    dates = []
    dt = datetime(2010, 12, 01)
    end = datetime(2010, 12, 02, 23, 59, 59)
    step = timedelta(seconds=3600)
    
    while dt < end:
        dates.append(dt)
        dt += step
        
    values = np.random.rand(len(dates))
    raw = [(d, v) for d, v in zip(dates, values)]

    test_path = tmpdir.mkdir("sub").join("test.csv")
    test_path_str = str(test_path)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['mass'],
                         "units": ["kg"]})
    
    test = TimeSeries()
    
    fout_factory = InterfaceFactory(AutoFileOutput)
    FOutCls = fout_factory(meta, test)
    
    fout = FOutCls()
    fout._path = test_path_str
    fout.data.result = test.get_data(raw, meta)

    fout.connect()
    
    assert len(tmpdir.listdir()) == 1
              
    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)
              
    fin = FInCls()
    fin._path = test_path_str
    
    fin.connect()
    result = fin.data.result
    
    assert len(result) == len(dates)
    assert len(result.resample('D').mean()) == 2


def test_TimeSeries_auto_plot(tmpdir):
        
    dates = []
    dt = datetime(2010, 12, 01)
    end = datetime(2010, 12, 02, 23, 59, 59)
    step = timedelta(seconds=3600)
    
    while dt < end:
        dates.append(dt)
        dt += step
        
    values = np.random.rand(len(dates))
    raw = [(d, v) for d, v in zip(dates, values)]
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['mass'],
                         "units": ["kg"]})
    
    test = TimeSeries()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")
    
    
def test_TimeTable(core):
    
    dates = []
    dt = datetime(2010, 12, 01)
    end = datetime(2010, 12, 02, 23, 59, 59)
    step = timedelta(seconds=3600)
    
    while dt < end:
        dates.append(dt)
        dt += step
        
    values = np.random.rand(len(dates))
    raw = {"DateTime": dates,
           "a": values,
           "b": values}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["a", "b"],
                         "units": ["kg", None]})
    
    test = TimeTable()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert "a" in b
    assert len(b) == len(dates)
    assert len(b.resample('D').mean()) == 2
    
def test_IndexTable(core):
    
    labels = list(map(chr, range(10)))
    data = [2 * float(x) for x in range(10)]
    
    raw = {"Label"   : labels,
           "Data"     : data}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Label",
                                    "Data"]})
    
    test = IndexTable()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert "Data" in b
    assert len(b) == len(data)
    assert b.index.name == "Label"
    
def test_LineTable(core):
    
    velocity = [float(x) for x in range(10)]
    thrust = [2 * float(x) for x in range(10)]
    power = [3 * float(x) for x in range(10)]
    
    raw = {"Velocity"   : velocity,
           "Thrust"     : thrust,
           "Power"      : power}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Velocity",
                                    "Thrust",
                                    "Power"]})
    
    test = LineTable()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert "Thrust" in b
    assert len(b) == len(velocity)
    assert b.index.name == "Velocity"
    
def test_NumpyLineDict(core):
    
    coarse_sample = np.linspace(0., 2*np.pi, num=5)
    fine_sample = np.linspace(0., 2*np.pi, num=9)
    
    coarse_sin = zip(coarse_sample, np.sin(coarse_sample))
    fine_cos = zip(fine_sample, np.cos(fine_sample))
    
    raw = {"Sin(x)" : coarse_sin,
           "Cos(x)" : fine_cos}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x", "f(x)"]})
    
    test = NumpyLineDict()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert "Sin(x)" in b
    assert max(b["Sin(x)"][:,1]) == 1
    assert b["Cos(x)"][0,1] == b["Cos(x)"][-1,1]
    
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
    

