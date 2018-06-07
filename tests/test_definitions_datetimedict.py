import pytest
import datetime

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import DateTimeDict


def test_DateTimeDict_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "DateTimeDict" in all_objs.keys()


def test_DateTimeDict():

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = DateTimeDict()
    
    raw = {"a": datetime.datetime.now(),
           "b": datetime.datetime.utcnow()}
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b["a"] == raw["a"]
    assert b["b"] == raw["b"]
    
    
def test_get_None():
    
    test = DateTimeDict()
    result = test.get_value(None)
    
    assert result is None
    

@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_SimpleDict_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
           
    raw = {"a": datetime.datetime.now(),
           "b": datetime.datetime.utcnow()}
        
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})

    test = DateTimeDict()
    
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
    
    # Microseconds are lost in xls case
    assert result["a"].replace(microsecond=0) == \
                                            raw["a"].replace(microsecond=0)
    assert result["b"].replace(microsecond=0) == \
                                            raw["b"].replace(microsecond=0)
