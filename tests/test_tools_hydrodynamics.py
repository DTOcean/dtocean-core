
import pytest

from subprocess import call

import numpy as np
import pandas as pd

from dtocean_core.tools.hydrodynamics import (make_wave_statistics,
                                              make_tide_statistics)
                                        
def test_make_wave_statistics_propability():
    
    sample_size = 1000
        
    Hm0 = 9. * np.random.random_sample(sample_size)
    Te = 15. * np.random.random_sample(sample_size)    
    dir_rmean = 360. * np.random.random_sample(sample_size)
#    H_max = 16. * np.random.random_sample(sample_size)
#    Tp = 16. * np.random.random_sample(sample_size)
#    T02 = 12. * np.random.random_sample(sample_size)
#    dir_peak = 360. * np.random.random_sample(sample_size)
#    P = 600. * np.random.random_sample(sample_size)
#    Wind_speed = 30. * np.random.random_sample(sample_size)
#    Wind_dir = 360. * np.random.random_sample(sample_size)
    
    wave_dict = {"Hm0"          : Hm0,
                 "Te"           : Te,
                 "Dir"          : dir_rmean
#                 "H_max"        : H_max,
#                 "Tp"           : Tp,
#                 "T02"          : T02,
#                 "dir_peak"     : dir_peak,
#                 "P"            : P,
#                 "wind_speed"   : Wind_speed,
#                 "wind_dir"     : Wind_dir
                 }
                
    wave_df = pd.DataFrame(wave_dict)

    test = make_wave_statistics(wave_df)

    assert len(test["Tp"]) == test["p"].shape[0]    
    assert len(test["Hs"]) == test["p"].shape[1]    
    assert len(test["B"]) == test["p"].shape[2]
    assert np.allclose(np.sum(test["p"]), 1)

@pytest.mark.parametrize("nx, ny, nt, ns", 
                         [(50, 50, 24, 2),
#                          (20, 50, 48, 2)
                          ])
def test_make_tide_statistics_propability(nx, ny, nt, ns):
    
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    t = np.linspace(0, 1, nt)
                
    U = 2. * np.random.randn(nx, ny, nt)
    V = 2. * np.random.randn(nx, ny, nt)
    TI = 2. * np.random.randn(nx, ny, nt)
    SSH = 2. * np.random.randn(nx, ny, nt)

    xc = x[int(nx/2)]
    yc = y[int(ny/2)]
        
    dictinput = {'U'    : U,
                 'V'    : V,
                 'TI'   : TI,
                 'SSH'  : SSH,
                 't'    : t,
                 'xc'   : xc,
                 'yc'   : yc,
                 'x'    : x,
                 'y'    : y,
                 'ns'   : ns
                 }
                
    test = make_tide_statistics(dictinput)
    
    assert len(test["p"]) == ns
    assert test["U"].shape == (nx, ny, ns)
    assert np.allclose(np.sum(test["p"]), 1)

def test_make_tide_statistics_zero_V():
    
    nx = 50
    ny = 25
    nt = 24
    ns = 4
    
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    t = np.linspace(0, 1, nt)
                
    U = 2. * np.random.randn(nx, ny, nt)
    V = np.zeros((nx, ny, nt))
    TI = 2. * np.random.randn(nx, ny, nt)
    SSH = 2. * np.random.randn(nx, ny, nt)

    xc = x[int(nx/2)]
    yc = y[int(ny/2)]
        
    dictinput = {'U'    : U,
                 'V'    : V,
                 'TI'   : TI,
                 'SSH'  : SSH,
                 't'    : t,
                 'xc'   : xc,
                 'yc'   : yc,
                 'x'    : x,
                 'y'    : y,
                 'ns'   : ns
                 }
                
    test = make_tide_statistics(dictinput)
    
    assert len(test["p"]) == ns
    assert test["U"].shape == (nx, ny, ns)
    assert np.allclose(np.sum(test["p"]), 1)
    
#@pytest.mark.parametrize("ext, gamma", 
#                         [(".csv", 3.0),
#                          (".csv", 3.3),
#                          (".xlsx", 3.3),
#                          (".xlsx", 3.6)
#                          ])
#def test_add_Te_interface(tmpdir, ext, gamma):
#    
#    test_path_local = tmpdir.join("wave_data" + ext)
#    test_path = str(test_path_local)
#    
#    sample_size = 50
#        
#    Hm0 = 9. * np.random.random_sample(sample_size)
#    Tp = 16. * np.random.random_sample(sample_size)
#
#    wave_dict = {"Hm0"  : Hm0,
#                 "Tp"   : Tp
#                 }
#                
#    wave_df = pd.DataFrame(wave_dict)
#    
#    if ext == ".csv":
#        
#        wave_df.to_csv(test_path, index=False)
#        
#    elif ext == ".xlsx":
#        
#        wave_df.to_excel(test_path, index=False)
#        
#    else:
#        
#        raise ValueError("Someone call Superman")
#        
#    gamma_str = "-g {}".format(gamma)
#    
#    call(["add-Te", gamma_str, test_path])
#    
#    if ext == ".csv":
#        
#        wave_df = pd.read_csv(test_path)
#        
#    else:
#    
#        wave_df = pd.read_excel(test_path)
#    
#    assert "Te" in wave_df.columns
#    assert pd.notnull(wave_df["Te"]).all()
#    assert wave_df["Te"].min() >= 0.
#    assert wave_df["Te"].max() <= 16.

