# -*- coding: utf-8 -*-

import numpy as np
import pytest
from shapely.geometry import Polygon

from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import Strata
from dtocean_core.strategies.position_optimiser.positioner import (
                                                    _buffer_lease_polygon,
                                                    _get_depth_exclusion_poly,
                                                    DevicePositioner)

# Check for module
pytest.importorskip("dtocean_hydro")


@pytest.fixture
def lease_polygon():
    return Polygon([(100, 50), (900, 50), (900, 250), (100, 250)])


@pytest.fixture
def layer_depths():

    x = np.linspace(0.,1000.,101)
    y = np.linspace(0.,300.,31) 
    nx = len(x)
    ny = len(y)
    
    X, Y = np.meshgrid(x,y)
    Z = -X * 0.1 - 1
    depths = Z.T[:, :, np.newaxis]
    
    sediments = np.chararray((nx,ny,1), itemsize=20)
    sediments[:] = "rock"
       
    raw = {"values": {'depth': depths,
                      'sediment': sediments},
           "coords": [x, y, ["layer 1"]]}
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x",
                                    "y",
                                    "layer",
                                    "depth",
                                    "sediment"]})
    
    test = Strata()
    a = test.get_data(raw, meta)
    
    return test.get_value(a)


@pytest.fixture
def nogo_polygons():
    return (Polygon([(800, 0), (1000, 0), (1000, 150), (800, 150)]),
            Polygon([(800, 150), (1000, 150), (1000, 300), (800, 300)]))


def test_buffer_lease_polygon(lease_polygon):
    test = _buffer_lease_polygon(lease_polygon)
    assert test == lease_polygon


def test_buffer_lease_polygon_lease_padding(lease_polygon):
    test = _buffer_lease_polygon(lease_polygon, 10)
    assert test.area == 780 * 180


def test_buffer_lease_polygon_turbine_interdistance(lease_polygon):
    test = _buffer_lease_polygon(lease_polygon, 10, 20)
    assert test.area == 760 * 160


def test_get_depth_exclusion_poly(layer_depths):
    
    test = _get_depth_exclusion_poly(layer_depths,
                                     max_depth=-21)
    
    assert test.bounds == (0.0, 0.0, 200.0, 300.0)


def test_DevicePositioner_valid_poly(lease_polygon,
                                     layer_depths):
    
    test = DevicePositioner(lease_polygon,
                            layer_depths,
                            max_depth=-21)
    
    assert test._valid_poly.bounds == (200.0, 50.0, 900.0, 250.0)


def test_DevicePositioner_valid_poly_nogo(lease_polygon,
                                          layer_depths,
                                          nogo_polygons):
    
    test = DevicePositioner(lease_polygon,
                            layer_depths,
                            max_depth=-21,
                            nogo_polygons=nogo_polygons)
    
    assert test._valid_poly.bounds == (200.0, 50.0, 800.0, 250.0)
