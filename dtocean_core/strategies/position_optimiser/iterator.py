# -*- coding: utf-8 -*-

"""
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os
import sys

import numpy as np

from ...core import Core
from ...extensions import StrategyManager
from ...pipeline import Tree

from .positioner import ParaPositioner

try:
    import dtocean_hydro
    import dtocean_maintenance
except ImportError:
    err_msg = ("The DTOcean hydrodynamics and maintenance modules must be "
               "installed in order to use this module")
    raise ImportError(err_msg)


def main(core,
         prj_file_path,
         array_orientation_deg,
         delta_row,
         delta_col,
         n_nodes,
         t1,
         t2,
         penalty=1.):
    
    array_orientation = float(array_orientation_deg) * np.pi / 180
    delta_row = float(delta_row)
    delta_col = float(delta_col)
    n_nodes = int(float(n_nodes))
    t1 = float(t1)
    t2 = float(t2)
    penalty = float(penalty)
    
    params_template = "theta: {}; dr: {}; dc: {}; n_nodes: {}; t1: {}; t2: {}"
    params_str = params_template.format(array_orientation,
                                        delta_row,
                                        delta_col,
                                        n_nodes,
                                        t1,
                                        t2)
    
    e = None
    
    try:
        
        project = core.load_project(prj_file_path)
        
        positioner = get_positioner(core, project)
        
        lcoe = iterate(core,
                       project,
                       positioner,
                       array_orientation,
                       delta_row,
                       delta_col,
                       n_nodes,
                       t1,
                       t2)
        
        flag = "Success"
    
    except Exception as e:
        
        lcoe = penalty
        flag = "Exception"
    
    try:
        core.dump_project(project, prj_file_path)
    except:
        pass
    
    prj_base_path, _ = os.path.splitext(prj_file_path)
    dat_file_path = "{}.dat".format(prj_base_path)
    
    write_result_file(dat_file_path,
                      params_str,
                      lcoe,
                      flag,
                      str(e))
    
    return


def iterate(core,
            project,
            positioner,
            array_orientation,
            delta_row,
            delta_col,
            n_nodes,
            t1,
            t2):
    
    beta = 90 * np.pi / 180
    psi = 0 * np.pi / 180
    
    positions = positioner(array_orientation,
                           delta_row,
                           delta_col,
                           beta,
                           psi,
                           n_nodes,
                           t1,
                           t2)
    
    hydro_branch = _get_branch(core, project, "Hydrodynamics")
    
    user_array_layout = hydro_branch.get_input_variable(
                                        core,
                                        project,
                                        'options.user_array_layout')
    user_array_layout.set_raw_interface(core, positions)
    user_array_layout.read(core, project)
    
    power_rating = core.get_data_value(project, "device.power_rating")
    
    rated_power = hydro_branch.get_input_variable(core,
                                                  project,
                                                  'project.rated_power')
    rated_power.set_raw_interface(core, power_rating * n_nodes)
    rated_power.read(core, project)
    
    basic_strategy = _get_basic_strategy()
    basic_strategy.execute(core, project)
    
    lcoe = core.get_data_value(project, "project.lcoe_mode")

    return lcoe


def _get_branch(core, project, branch_name):
    
    tree = Tree()
    hydro_branch = tree.get_branch(core, project, branch_name)
    
    return hydro_branch


def _get_basic_strategy():
    
    strategy_manager = StrategyManager()
    basic_strategy = strategy_manager.get_strategy("Basic")
    
    return basic_strategy


def get_positioner(core, project):
    
    lease_boundary = core.get_data_value(project, "site.lease_boundary")
    bathymetry = core.get_data_value(project, "bathymetry.layers")
    installation_depth_max = core.get_data_value(project,
                                             'device.installation_depth_max')
    installation_depth_min = core.get_data_value(project,
                                             'device.installation_depth_min')
    minimum_distance_x = core.get_data_value(project,
                                             'device.minimum_distance_x')
    minimum_distance_y = core.get_data_value(project,
                                             'device.minimum_distance_y')
    
    nogo_areas = None
    boundary_padding = None
    turbine_interdistance = None
    
    if core.has_data(project,'farm.nogo_areas'):
        nogo_areas = core.get_data_value(project,'farm.nogo_areas')
    
    if core.has_data(project, 'options.boundary_padding'):
        boundary_padding = core.get_data_value(project,
                                               'options.boundary_padding')
    
    if core.has_data(project, 'device.turbine_interdistance'):
        turbine_interdistance = core.get_data_value(
                                                project,
                                                'device.turbine_interdistance')
    
    min_separation = [minimum_distance_x, minimum_distance_y]
    
    positioner = ParaPositioner(lease_boundary,
                                bathymetry,
                                min_depth=installation_depth_min,
                                max_depth=installation_depth_max,
                                min_separation=min_separation,
                                nogo_polygons=nogo_areas,
                                lease_padding=boundary_padding,
                                turbine_separation=turbine_interdistance)
    
    return positioner


def write_result_file(dat_file_path,
                      params_str,
                      lcoe,
                      flag,
                      e):
    
    data = [params_str, str(lcoe), flag]
    if e is not None: data.append(e)
    
    lines = "\n".join(data)
    
    with open(dat_file_path, "w") as f:
        f.write(lines)
    
    return


def interface():
    
    core = Core()
    
    (prj_file_path,
     array_orientation_deg,
     delta_row,
     delta_col,
     n_nodes,
     t1,
     t2,
     penalty) = sys.argv[1:]
    
    main(core,
         prj_file_path,
         array_orientation_deg,
         delta_row,
         delta_col,
         n_nodes,
         t1,
         t2,
         penalty)
