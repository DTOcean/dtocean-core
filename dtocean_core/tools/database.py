# -*- coding: utf-8 -*-

#    Copyright (C) 2016 'Mathew Topper, Vincenzo Nava, David Bould, Rui Duarte,
#                       'Francesco Ferri, Adam Collin'
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

# Set up logging
import logging
import warnings

module_logger = logging.getLogger(__name__)

import time
import datetime as dt

import numpy as np
import pandas as pd
from shapely import wkb


def bathy_records_to_strata_old(bathy_records, time_loop_iterations=1000):
    
    """Convert the bathymetry layers table returned by the database into 
    Strata structure raw input"""
    
    msg = "Building DataFrame from {} records".format(len(bathy_records))
    module_logger.debug(msg)
    
    bathy_table = pd.DataFrame.from_records(bathy_records, columns=[
                                                            "utm_point",
                                                            "depth",
                                                            "mannings_no",
                                                            "layer_order",
                                                            "sediment_type",
                                                            "initial_depth",
                                                            "total_depth",
                                                            "terminal_depth"])
    
    if bathy_table.empty:
        
        errStr = "No bathymetry records were retrieved"
        raise ValueError(errStr)
        
    msg = "Converting PostGIS Point types to coordinates..."
    module_logger.debug(msg)

    bathy_table = point_to_xy(bathy_table)
    
    msg = "Getting grid extents..."
    module_logger.debug(msg)
    
    xi, yj = get_grid_coords(bathy_table)
        
    layers = list(set(bathy_table["layer_order"]))
    layers.sort()
    
    nx = len(xi)
    ny = len(yj)
    nlayers = len(layers)
    
    msg = ("Creating grids for {} x coordinates, {} y coordinates and "
           "{} layers").format(nx, ny, nlayers)
    module_logger.debug(msg)
    
    depth_layers = []
    sediment_layers = []

    i_record = 0
    loop_start_time = time.clock()

    for z in layers:
        
        depths = []
        sediments = []
        
        for y in yj:
            
            d = []
            s = []
            
            for x in xi:
                
                point_df = bathy_table.loc[(bathy_table['x'] == x) &
                                           (bathy_table['y'] == y) &
                                           (bathy_table['layer_order'] == z)]
                
                if point_df.empty:
                    
                    d.append(None)
                    s.append(None)
                    
                else:
                
                    i_record += 1
                    
                    if i_record % time_loop_iterations == 0:
                        
                        loop_end_time = time.clock()
                        loop_time = loop_end_time - loop_start_time
                        loop_start_time = loop_end_time
                    
                        msg = ("Time elapsed setting {} records is "
                               "{}").format(time_loop_iterations, loop_time)
                        module_logger.debug(msg)
                    
                    d.append((point_df["depth"] -
                                        point_df["initial_depth"]).values[0])
                    s.append(point_df["sediment_type"].values[0])
                    
            depths.append(d)
            sediments.append(s)
            
        depth_layers.append(depths)
        sediment_layers.append(sediments)
        
    depth_array = np.swapaxes(np.array(depth_layers, dtype=float), 0, 2)
    sediment_array = np.swapaxes(np.array(sediment_layers), 0, 2)
    
    layer_names = ["layer {}".format(x) for x in layers]
    
    raw_strata = {"values": {"depth": depth_array,
                             "sediment": sediment_array},
                  "coords": [xi, yj, layer_names]}
    
    return raw_strata

def bathy_records_to_strata(bathy_records=None, pre_bathy=None):
    
    """Convert the bathymetry layers table returned by the database into 
    Strata structure raw input"""
    
    loop_start_time = time.clock()
    
    # Allow a predefined bathymetry table and grid dimensions to be passed
    # instead of the DB records.
    if bathy_records is None and pre_bathy is None:
        
        errStr = "One of arguments bathy_records or pre_bathy must be given"
        raise ValueError(errStr)
        
    elif bathy_records is not None:
    
        bathy_table, xi, yj = init_bathy_records(bathy_records)
        
    else:
        
        bathy_table, xi, yj = pre_bathy
        
    msg = "Building layers..."
    module_logger.debug(msg)
            
    layers = list(set(bathy_table["layer_order"]))
    layers.sort()
    
    bathy_layer_groups = bathy_table.groupby("layer_order")
    
    layer_depths = []
    layer_sediments = []
    
    for layer in layers:
        
        layer_table = bathy_layer_groups.get_group(layer)
        layer_depth, layer_sediment = build_bathy_layer(layer_table, xi, yj)
        
        layer_depths.append(layer_depth)
        layer_sediments.append(layer_sediment)

        
    depth_array = np.dstack(layer_depths)
    sediment_array = np.dstack(layer_sediments)
    
    layer_names = ["layer {}".format(x) for x in layers]
    
    raw_strata = {"values": {"depth": depth_array,
                             "sediment": sediment_array},
                  "coords": [xi, yj, layer_names]}

    loop_end_time = time.clock()
    loop_time = loop_end_time - loop_start_time

    msg = ("Time elapsed building {} layer(s) was "
           "{} seconds").format(len(layers), loop_time)
    module_logger.debug(msg)
    
    return raw_strata
    
def bathy_records_to_mannings_old(bathy_records):
    
    """Convert the bathymetry layers table returned by the database into 
    Strata structure raw input"""
    
    bathy_table = pd.DataFrame.from_records(bathy_records, columns=[
                                                            "utm_point",
                                                            "depth",
                                                            "mannings_no",
                                                            "layer_order",
                                                            "sediment_type",
                                                            "initial_depth",
                                                            "total_depth",
                                                            "terminal_depth"])
                                                            
    if bathy_table.empty:
        
        errStr = "No mannings number records were retrieved"
        raise ValueError(errStr)
    
    bathy_table = point_to_xy(bathy_table)
    xi, yj = get_grid_coords(bathy_table)
    
    mannings_grid = []
        
    for y in yj:
        
        mannings_row = []
        
        for x in xi:
            
            point_df = bathy_table.loc[(bathy_table['x'] == x) &
                                       (bathy_table['y'] == y) &
                                       (bathy_table['layer_order'] == 1)]
            
            if point_df.empty:
                
                mannings_row.append(None)
                
            else:
                
                mannings_row.append(point_df["mannings_no"].values[0])
                
        mannings_grid.append(mannings_row)
        
    mannings_array = np.swapaxes(np.array(mannings_grid, dtype=float), 0, 1)
    
    mannings_raw = {"values": mannings_array,
                    "coords": [xi, yj]}
    
    return mannings_raw
    
def bathy_records_to_mannings(bathy_records=None, pre_bathy=None):
    
    """Convert the bathymetry layers table returned by the database into 
    mannings layer structure raw input"""
    
    loop_start_time = time.clock()
    
    # Allow a predefined bathymetry table and grid dimensions to be passed
    # instead of the DB records.
    if bathy_records is None and pre_bathy is None:
        
        errStr = "One of arguments bathy_records or pre_bathy must be given"
        raise ValueError(errStr)
        
    elif bathy_records is not None:
    
        bathy_table, xi, yj = init_bathy_records(bathy_records)

    else:
        
        bathy_table, xi, yj = pre_bathy
        
    msg = "Building mannings..."
    module_logger.debug(msg)
    
    bathy_layer_groups = bathy_table.groupby("layer_order")
    layer_one_table = bathy_layer_groups.get_group(1)
    
    mannings_array = build_mannings_layer(layer_one_table, xi, yj)
    
    mannings_raw = {"values": mannings_array,
                    "coords": [xi, yj]}

    loop_end_time = time.clock()
    loop_time = loop_end_time - loop_start_time

    msg = ("Time elapsed building mannings number array was "
           "{} seconds").format(loop_time)
    module_logger.debug(msg)
    
    return mannings_raw
    
def tidal_series_records_to_xset_old(tidal_records):
    
    """Convert the bathymetry layers table returned by the database into 
    Strata structure raw input"""
    
    tidal_table = pd.DataFrame.from_records(tidal_records, columns=[
                                                    'fk_farm_array',
                                                    'project_bathymetry_id',
                                                    'fk_farm_id',
                                                    'local_index',
                                                    'fk_site_id',
                                                    'utm_point',
                                                    'measure_date',
                                                    'measure_time',
                                                    'u',
                                                    'v',
                                                    'id',
                                                    'turbulence_intensity',
                                                    'ssh',
                                                    'fk_point_id'])
                                                    
    if tidal_table.empty:
        
        errStr = "No tidal time series records were retrieved"
        raise ValueError(errStr)
    
    tidal_table = point_to_xy(tidal_table)
    xi, yj = get_grid_coords(tidal_table)

    tidal_table["datetime"] = [dt.datetime.combine(date, time) for
                                date, time in zip(tidal_table["measure_date"],
                                                  tidal_table["measure_time"])]
                                              
    tidal_table = tidal_table.drop("measure_date", 1)
    tidal_table = tidal_table.drop("measure_time", 1)
    
    steps = list(set(tidal_table["datetime"]))
    steps.sort()

    u_steps = []
    v_steps = []
    ssh_steps = []
    ti_steps = []
    
    for t in steps:
        
        us = []
        vs = []
        sshs = []
        tis = []
        
        for y in yj:
            
            u = []
            v = []
            ssh = []
            ti = []
            
            for x in xi:
                
                point_df = tidal_table.loc[(tidal_table['x'] == x) &
                                           (tidal_table['y'] == y) &
                                           (tidal_table['datetime'] == t)]
                
                if point_df.empty:
                    u.append(None)
                    v.append(None)
                    ssh.append(None)
                    ti.append(None)
                else:
                    u.append(point_df["u"].values[0])
                    v.append(point_df["v"].values[0])
                    ssh.append(point_df["ssh"].values[0])
                    ti.append(point_df["turbulence_intensity"].values[0])
                    
            us.append(u)
            vs.append(v)
            sshs.append(ssh)
            tis.append(ti)
            
        u_steps.append(us)
        v_steps.append(vs)
        ssh_steps.append(sshs)
        ti_steps.append(tis)
            
    u_array = np.swapaxes(np.array(u_steps, dtype=float), 0, 2)
    v_array = np.swapaxes(np.array(v_steps, dtype=float), 0, 2)
    ssh_array = np.swapaxes(np.array(ssh_steps, dtype=float), 0, 2)
    ti_array = np.swapaxes(np.array(ti_steps, dtype=float), 0, 2)
        
    raw = {"values": {"U": u_array,
                      'V': v_array,
                      "SSH": ssh_array,
                      "TI": ti_array},
           "coords": [xi, yj, steps]}
    
    return raw
    
def tidal_series_records_to_xset(tidal_records):
    
    """Convert the bathymetry layers table returned by the database into 
    tidal time series structure raw input"""
    
    loop_start_time = time.clock()
    
    msg = "Building DataFrame from {} records".format(len(tidal_records))
    module_logger.debug(msg)
    
    tidal_table = pd.DataFrame.from_records(tidal_records, columns=[
                                                    'fk_farm_array',
                                                    'project_bathymetry_id',
                                                    'fk_farm_id',
                                                    'local_index',
                                                    'fk_site_id',
                                                    'utm_point',
                                                    'measure_date',
                                                    'measure_time',
                                                    'u',
                                                    'v',
                                                    'id',
                                                    'turbulence_intensity',
                                                    'ssh',
                                                    'fk_point_id'])
                                                    
    if tidal_table.empty:
        
        errStr = "No tidal time series records were retrieved"
        raise ValueError(errStr)
    
    msg = "Converting PostGIS Point types to coordinates..."
    module_logger.debug(msg)

    tidal_table = point_to_xy(tidal_table)
    
    msg = "Getting grid extents..."
    module_logger.debug(msg)
    
    xi, yj = get_grid_coords(tidal_table)
    
    msg = "Joining dates and times..."
    module_logger.debug(msg)

    tidal_table["datetime"] = [dt.datetime.combine(d, t) for
                                      d, t in zip(tidal_table["measure_date"],
                                                  tidal_table["measure_time"])]
                                              
    tidal_table = tidal_table.drop("measure_date", 1)
    tidal_table = tidal_table.drop("measure_time", 1)
    
    msg = "Building time steps..."
    module_logger.debug(msg)
    
    steps = list(set(tidal_table["datetime"]))
    steps.sort()
    
    tidal_table_groups = tidal_table.groupby("datetime")

    u_steps = []
    v_steps = []
    ssh_steps = []
    ti_steps = []

    for step in steps:
        
        step_table = tidal_table_groups.get_group(step)
        (u_step,
         v_step,
         ssh_step,
         ti_step) = build_tidal_series_step(step_table, xi, yj)
        
        u_steps.append(u_step)
        v_steps.append(v_step)
        ssh_steps.append(ssh_step)
        ti_steps.append(ti_step)
            
    u_array = np.dstack(u_steps)
    v_array = np.dstack(v_steps)
    ssh_array = np.dstack(ssh_steps)
    ti_array = np.dstack(ti_steps)
        
    raw = {"values": {"U": u_array,
                      'V': v_array,
                      "SSH": ssh_array,
                      "TI": ti_array},
           "coords": [xi, yj, steps]}

    loop_end_time = time.clock()
    loop_time = loop_end_time - loop_start_time

    msg = ("Time elapsed building {} step(s) was "
           "{} seconds").format(len(steps), loop_time)
    module_logger.debug(msg)
    
    return raw
    
def init_bathy_records(bathy_records):
    
    msg = "Building DataFrame from {} records".format(len(bathy_records))
    module_logger.debug(msg)
    
    bathy_table = pd.DataFrame.from_records(bathy_records, columns=[
                                                            "utm_point",
                                                            "depth",
                                                            "mannings_no",
                                                            "layer_order",
                                                            "sediment_type",
                                                            "initial_depth",
                                                            "total_depth",
                                                            "terminal_depth"])
    
    if bathy_table.empty:
        
        errStr = "No bathymetry records were retrieved"
        raise ValueError(errStr)
        
    msg = "Converting PostGIS Point types to coordinates..."
    module_logger.debug(msg)

    bathy_table = point_to_xy(bathy_table)
    
    msg = "Getting grid extents..."
    module_logger.debug(msg)
    
    xi, yj = get_grid_coords(bathy_table)
    
    return bathy_table, xi, yj

def point_to_xy(df,
                point_column="utm_point",
                decimals=2,
                drop_point_column=True):
    
    x = []
    y = []
    
    for point_hex in df[point_column]:
        point = wkb.loads(point_hex, hex=True)
        coords = list(point.coords)[0]
        x.append(coords[0])
        y.append(coords[1])
        
    x = np.array(x)
    x = x.round(decimals)
    
    y = np.array(y)
    y = y.round(decimals)

    df["x"] = x
    df["y"] = y

    if drop_point_column: df = df.drop(point_column, 1)
    
    return df
    
def get_grid_coords(df, xlabel="x", ylabel="y"):

    xi = np.unique(df[xlabel])
    xdist = xi[1:] - xi[:-1]
        
    if len(np.unique(xdist)) != 1:
        
        safe_dist = [str(x) for x in np.unique(xdist)]
        dist_str = ", ".join(safe_dist)
        errStr = ("Distances in x-direction are not equal. Unique lengths "
                  "are: {}").format(dist_str)
        raise ValueError(errStr)
        
    yj = np.unique(df[ylabel])
    ydist = yj[1:] - yj[:-1]

    if len(np.unique(ydist)) != 1:
        
        safe_dist = [str(y) for y in np.unique(ydist)]
        dist_str = ", ".join(safe_dist)
        errStr = ("Distances in y-direction are not equal. Unique lengths "
                  "are: {}").format(dist_str)
        raise ValueError(errStr)
        
    return xi, yj
    
def build_bathy_layer(layer_table, xi, yj):
    
    depth_array = np.zeros([len(xi), len(yj)]) * np.nan
    sediment_array = np.full([len(xi), len(yj)], None, dtype="object")
    
    for record in layer_table.itertuples():
        
        xidxs = np.where(xi == record.x)[0]
        assert len(xidxs) == 1
        xidx = xidxs[0]

        yidxs = np.where(yj == record.y)[0]
        assert len(yidxs) == 1
        yidx = yidxs[0]
        
        depth = record.depth - record.initial_depth
        sediment = record.sediment_type
        
        depth_array[xidx, yidx] = depth
        sediment_array[xidx, yidx] = sediment

    return depth_array, sediment_array
    
def build_mannings_layer(layer_table, xi, yj):
    
    mannings_array = np.zeros([len(xi), len(yj)]) * np.nan
    
    for record in layer_table.itertuples():
        
        xidxs = np.where(xi == record.x)[0]
        assert len(xidxs) == 1
        xidx = xidxs[0]

        yidxs = np.where(yj == record.y)[0]
        assert len(yidxs) == 1
        yidx = yidxs[0]

        mannings_array[xidx, yidx] = record.mannings_no

    return mannings_array
    
def build_tidal_series_step(step_table, xi, yj):
    
    u_array = np.zeros([len(xi), len(yj)]) * np.nan
    v_array = np.zeros([len(xi), len(yj)]) * np.nan
    ssh_array = np.zeros([len(xi), len(yj)]) * np.nan
    ti_array = np.zeros([len(xi), len(yj)]) * np.nan
    
    for record in step_table.itertuples():
        
        xidxs = np.where(xi == record.x)[0]
        assert len(xidxs) == 1
        xidx = xidxs[0]

        yidxs = np.where(yj == record.y)[0]
        assert len(yidxs) == 1
        yidx = yidxs[0]

        u_array[xidx, yidx] = record.u
        v_array[xidx, yidx] = record.v
        ssh_array[xidx, yidx] = record.ssh
        ti_array[xidx, yidx] = record.turbulence_intensity

    return u_array, v_array, ssh_array, ti_array

