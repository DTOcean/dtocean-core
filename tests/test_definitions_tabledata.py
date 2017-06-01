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
from dtocean_core.data.definitions import TableData, TableDataColumn


def test_TableData_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "TableData" in all_objs.keys()


def test_TableData():
    
    idx = range(1000)
        
    values = np.random.rand(len(idx))
    raw = {"index": idx,
           "a": values,
           "b": values}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["index", "a", "b"],
                         "units": [None, "kg", None]})
    
    test = TableData()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert "a" in b
    assert len(b) == len(idx)

@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_TableData_auto_file(tmpdir, fext):
    
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
        
    idx = range(1000)
        
    values = np.random.rand(len(idx))
    raw = {"index": idx,
           "a": values,
           "b": values}
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["index", "a", "b"],
                         "units": [None, "kg", None]})
    
    test = TableData()
    
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
    
    assert "a" in result
    assert len(result) == len(idx)


def test_TableDataColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "TableDataColumn" in all_objs.keys()
    

def test_TableDataColumn_auto_db(mocker):
    
    idx = range(1000)
    values = np.random.rand(len(idx))
    
    mock_dict = {"index": idx,
                 "a": values,
                 "b": values}
    mock_df = pd.DataFrame(mock_dict)
    
    mocker.patch('dtocean_core.data.definitions.get_table_df',
                 return_value=mock_df)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["index", "a", "b"],
                         "tables": ["mock.mock", "index", "a", "b"]})
    
    test = TableDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
    result = test.get_data(query.data.result, meta)
        
    assert "a" in result
    assert len(result) == len(idx)


def test_TableDataColumn_auto_db_empty(mocker):
    
    mock_dict = {"index": [],
                 "a": [],
                 "b": []}
    mock_df = pd.DataFrame(mock_dict)
    
    mocker.patch('dtocean_core.data.definitions.get_table_df',
                 return_value=mock_df)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["index", "a", "b"],
                         "tables": ["mock.mock", "index", "a", "b"]})
    
    test = TableDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_TableDataColumn_auto_db_none(mocker):
    
    mock_dict = {"index": [None, None],
                 "a": [None, None],
                 "b": [None, None]}
    mock_df = pd.DataFrame(mock_dict)
    
    mocker.patch('dtocean_core.data.definitions.get_table_df',
                 return_value=mock_df)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["index", "a", "b"],
                         "tables": ["mock.mock", "index", "a", "b"]})
    
    test = TableDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None
