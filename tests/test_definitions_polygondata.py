import pytest

import matplotlib.pyplot as plt
from geoalchemy2.elements import WKTElement

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import PolygonData, PolygonDataColumn


def test_PolygonData_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PolygonData" in all_objs.keys()


def test_PolygonData():

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})

    raw = [(0., 0.),
           (1., 1.),
           (2., 2.)
           ]
    
    test = PolygonData()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b.exterior.coords[0][0] == 0.
    assert b.exterior.coords[1][1] == 1.
            
    raw = [(0., 0., 0.),
           (1., 1., 1.),
           (2., 2., 2.)
           ]
    
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b.exterior.coords[0][0] == 0.
    assert b.exterior.coords[1][1] == 1.
    assert b.exterior.coords[2][2] == 2.
            
    raw = [(0., 0., 0., 0.),
           (1., 1., 1., 1.),
           (2., 2., 2., 2.)
           ]
    
    with pytest.raises(ValueError):
        test.get_data(raw, meta)


def test_get_None():
    
    test = PolygonData()
    result = test.get_value(None)
    
    assert result is None
    

@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_PolygonData_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
           
    raws = [[(0., 0.),
             (1., 1.),
             (2., 2.)],
            [(0., 0., 0.),
             (1., 1., 1.),
             (2., 2., 2.)]
            ]
    
    ztests = [False, True]
    
    for raw, ztest in zip(raws, ztests):
        
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test"})
    
        test = PolygonData()
        
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
        
        assert result.exterior.coords[0][0] == 0.
        assert result.exterior.coords[1][1] == 1.
        assert result.has_z == ztest


def test_PolygonData_auto_plot(tmpdir):
        
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    raw = [(0., 0., 0.),
           (1., 1., 1.),
           (2., 2., 2.)
           ]
    
    test = PolygonData()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_PolygonDataColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PolygonDataColumn" in all_objs.keys()
    

def test_PolygonDataColumn_auto_db(mocker):
    
    raws = [WKTElement("POLYGON ((0 0, 1 0, 1 1, 0 0))"),
            WKTElement("POLYGON ((0 0 0, 1 0 0, 1 1 0, 0 0 0))")]
    
    for raw in raws:

        mock_list = [raw]
        
        mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                     return_value=mock_list,
                     autospec=True)
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test",
                             "tables": ["mock.mock", "position"]})
        
        test = PolygonDataColumn()
        
        query_factory = InterfaceFactory(AutoQuery)
        QueryCls = query_factory(meta, test)
        
        query = QueryCls()
        query.meta.result = meta
        
        query.connect()
        result = test.get_data(query.data.result, meta)
            
        assert result.exterior.coords[0][0] == 0.
        assert result.exterior.coords[1][0] == 1.


def test_PolygonDataColumn_auto_db_empty(mocker):
    
    mock_list = None
        
    mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                 return_value=mock_list,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "position"]})

    test = PolygonDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_PolygonDataColumn_auto_db_none(mocker):
    
    mock_list = [None]
        
    mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                 return_value=mock_list,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "position"]})
    
    test = PolygonDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None

