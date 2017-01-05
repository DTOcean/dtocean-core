

import pytest

import os
import pandas as pd
from shapely.geometry import Point

from dtocean_core.tools.database import bathy_records_to_strata

this_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(this_dir, "..", "test_data")
                                        
def test_bathy_records_to_strata():
    
    df = pd.read_csv(os.path.join(data_dir, "bathy_test_good.csv"))
    points = []
    for x, y in zip(df["x"], df["y"]):
        point = Point(x,y)
        points.append(point.wkb_hex)
        
    df["utm_point"] = points
    df = df.drop("x", 1)
    df = df.drop("y", 1)
    
    records = df.to_records()
    raw = bathy_records_to_strata(records)
    
    assert set(raw["values"].keys()) == set(['depth', 'sediment'])

def test_bathy_records_to_strata_fail():
    
    df = pd.read_csv(os.path.join(data_dir, "bathy_test_bad.csv"))
    points = []
    for x, y in zip(df["x"], df["y"]):
        point = Point(x,y)
        points.append(point.wkb_hex)
        
    df["utm_point"] = points
    df = df.drop("x", 1)
    df = df.drop("y", 1)
    
    records = df.to_records()
    
    with pytest.raises(ValueError):
        bathy_records_to_strata(records)
    
