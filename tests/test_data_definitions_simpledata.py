
import numpy as np

from dtocean_core.core import Core
from dtocean_core.data.definitions import SimpleData


def test_SimpleData_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures
    
    assert "SimpleData" in all_objs.keys()


def test_SimpleData_get_data():
    
    assert False


def test_SimpleData_equals():
    
    assert False


def test_SimpleData_not_equals():
    
    assert not True
