import pytest

import matplotlib.pyplot as plt

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
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
        
        
def test_get_None():
    
    test = PointList()
    result = test.get_value(None)
    
    assert result is None
        
        
@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_PointList_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
           
    raws = [[(0., 0.),
             (1., 1.),
             (2., 2.)],
            [(0., 0., 0.),
             (1., 1., 1.),
             (2., 2., 2.)]]
    
    ztests = [False, True]
    
    for raw, ztest in zip(raws, ztests):
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test"})
    
        test = PointList()
        
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
        result = test.get_data(fin.data.result, meta)
        
        assert result[0].x == 0
        assert result[1].y == 1
        assert result[0].has_z == ztest
        

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
