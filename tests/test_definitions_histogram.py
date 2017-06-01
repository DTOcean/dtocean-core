import pytest

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import Histogram, HistogramColumn


def test_Histogram_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "Histogram" in all_objs.keys()


def test_Histogram():
    
    bin_values = [1, 2, 3, 4, 5]
    bin_separators = [0, 2, 4, 6, 8, 10]
    
    raw = (bin_values, bin_separators)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x", "f(x)"]})
    
    test = Histogram()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert max(b["values"]) == 5
    assert max(b["bins"]) == 10
    

@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_Histogram_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
        
    bin_values = [1, 2, 3, 4, 5]
    bin_separators = [0, 2, 4, 6, 8, 10]
    
    raw = (bin_values, bin_separators)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x", "f(x)"]})
    
    test = Histogram()
    
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
    
    assert max(result["values"]) == 5
    assert max(result["bins"]) == 10


def test_Histogram_auto_plot(tmpdir):
        
    bin_values = [1, 2, 3, 4, 5]
    bin_separators = [0, 2, 4, 6, 8, 10]
    
    raw = (bin_values, bin_separators)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x", "f(x)"],
                         "units": [None, "m^{2}"]})
    
    test = Histogram()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")
    

def test_HistogramColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "HistogramColumn" in all_objs.keys()
    

def test_HistogramColumn_auto_db(mocker):
    
    bin_values = [1, 2, 3, 4, 5]
    bin_lowers = [0, 2, 4, 6, 8]
    bin_uppers = [2, 4, 6, 8, 10]

    mock_lists = [bin_values, bin_lowers, bin_uppers]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x", "f(x)"],
                         "units": [None, "m^{2}"],
                         "tables": ["mock.mock",
                                    "values",
                                    "lower_bounds",
                                    "upper_bounds"]})
    
    test = HistogramColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
    result = test.get_data(query.data.result, meta)
        
    assert max(result["values"]) == 5
    assert max(result["bins"]) == 10


def test_HistogramColumn_auto_db_empty(mocker):
    
    mock_lists = [[], [], []]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x", "f(x)"],
                         "units": [None, "m^{2}"],
                         "tables": ["mock.mock",
                                    "values",
                                    "lower_bounds",
                                    "upper_bounds"]})
    
    test = HistogramColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_HistogramColumn_auto_db_none(mocker):
    
    mock_lists = [[None, None], [None, None], [None, None]]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x", "f(x)"],
                         "units": [None, "m^{2}"],
                         "tables": ["mock.mock",
                                    "values",
                                    "lower_bounds",
                                    "upper_bounds"]})
    
    test = HistogramColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None

