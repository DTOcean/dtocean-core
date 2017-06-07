import pytest

import matplotlib.pyplot as plt

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import (AutoPlot,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import PointList


def test_PointList_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PointList" in all_objs.keys()


def test_PointList():

    raw = [(0., 0.),
           (1., 1.),
           (2., 2.)
           ]

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = PointList()
    
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b[0].x == 0
    assert b[1].y == 1
            
    raw = [(0., 0., 0.),
           (1., 1., 1.),
           (2., 2., 2.)
           ]
    
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b[0].x == 0
    assert b[1].y == 1 
    assert b[2].z == 2
            
    raw = [(0., 0., 0., 0.),
           (1., 1., 1., 1.),
           (2., 2., 2., 2.)
           ]
    
    with pytest.raises(ValueError):
        test.get_data(raw, meta)
        

def test_PointList_auto_plot(tmpdir):
        
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    raw = [(0., 0.),
           (1., 1.),
           (2., 2.)
           ]
    
    test = PointList()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")
