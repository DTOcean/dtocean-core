
import os
import datetime

import pytest
import pandas as pd
from shapely.geometry import Point

from dtocean_core.utils.database import (bathy_records_to_strata,
                                         query_builder,
                                         convert_array,
                                         convert_bool,
                                         convert_geo,
                                         convert_time)

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


def test_query_builder():
    
    result = query_builder(['device', 'device_shared'],
                           ['id', None],
                           ['fk_device_id'],
                           [{'table#': 0, 'value': 1L}],
                             "project")
    
    results = result.split("\n")
    
    assert results[1] == "FROM project.device_shared t1"
    assert results[2] == "JOIN project.device t0 ON t0.id = t1.fk_device_id"
    assert results[3] == "WHERE t0.id = 1;"


def test_convert_array():
    
    df_dict = {"A": ["[test]", None],
               "B": [1, 2]}
    df = pd.DataFrame(df_dict)
    
    result = convert_array(df, ["A"])
    
    assert result["A"].iloc[0] == "{test}"
    assert result["A"].iloc[1] is None


def test_convert_bool():
    
    df_dict = {"A": [True, False, None],
               "B": [1, 2, 3]}
    df = pd.DataFrame(df_dict)
    
    result = convert_bool(df, ["A"])
    
    assert result["A"].iloc[0] == "yes"
    assert result["A"].iloc[1] == "no"
    assert result["A"].iloc[2] is None


def test_convert_geo():
    
    x = Point(0, 0).wkb.encode('hex')
    
    df_dict = {"A": [x, None],
               "B": [1, 2]}
    df = pd.DataFrame(df_dict)
    
    result = convert_geo(df, ["A"])

    assert result["A"].iloc[0] == "POINT (0 0)"
    assert result["A"].iloc[1] is None


def test_convert_geo_SRID(mocker):
    
    x = Point(0, 0).wkb.encode('hex')
    
    df_dict = {"A": [x, None],
               "B": [1, 2]}
    df = pd.DataFrame(df_dict)
    
    mocker.patch("dtocean_core.utils.database.geos.lgeos.GEOSGetSRID",
                 return_value=1,
                 autospec=True)
    
    result = convert_geo(df, ["A"])

    assert result["A"].iloc[0] == "SRID=1;POINT (0 0)"
    assert result["A"].iloc[1] is None


def test_convert_time():
    
    x = datetime.datetime(2018, 1, 1, 12, 31, 5)
    
    df_dict = {"A": [x, None],
               "B": [1, 2]}
    df = pd.DataFrame(df_dict)
    df2 = df.astype(object)
    df2 = df2.where(df2.notnull(), None)
    
    result = convert_time(df2, ["A"])

    assert result["A"].iloc[0] == "12:31:05"
    assert result["A"].iloc[1] is None
