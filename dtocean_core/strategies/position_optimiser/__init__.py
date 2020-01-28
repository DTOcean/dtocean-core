# -*- coding: utf-8 -*-

"""
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os
import logging
from bisect import bisect_left
from collections import namedtuple

from ruamel.yaml import YAML
import numpy as np

from .iterator import get_positioner
from ...core import Core
from ...extensions import ToolManager
from ...utils import cma_optimiser as cma
from ...utils.files import remove_retry


# Set up logging
module_logger = logging.getLogger(__name__)

# Get this directory
THIS_DIR = os.path.dirname(os.path.realpath(__file__))


PositionParams = namedtuple('PositionParams', ['array_orientation',
                                               'delta_row',
                                               'delta_col',
                                               'n_nodes',
                                               't1',
                                               't2',
                                               'lcoe',
                                               'flag',
                                               'prj_file_path',
                                               'dat_file_path'])


class PositionCounter(cma.Counter):
    
    def _set_params(self, worker_project_path,
                          worker_results_path,
                          lcoe,
                          flag,
                          array_orientation_deg,
                          delta_row,
                          delta_col,
                          n_nodes,
                          t1,
                          t2):
        """Build a params (probably namedtuple) object to search against."""
        
        params = PositionParams(array_orientation_deg,
                                delta_row,
                                delta_col,
                                n_nodes,
                                t1,
                                t2,
                                lcoe,
                                flag,
                                worker_project_path,
                                worker_results_path)
        
        return params
    
    def _get_cost(self, params,
                        array_orientation_deg,
                        delta_row,
                        delta_col,
                        n_nodes,
                        t1,
                        t2):
        """Return cost if parameters in params object match input args, else
        return None."""
        
        if (params.array_orientation == array_orientation_deg and
            params.delta_row == delta_row and
            params.delta_col == delta_col and
            params.n_nodes == n_nodes and
            params.t1 == t1 and
            params.t2 == t2): return params.lcoe
        
        return


class PositionIterator(cma.Iterator):
    
    def __init__(self, root_project_base_name,
                       worker_directory,
                       base_project,
                       counter,
                       base_penalty=1.,
                       logging="module",
                       clean_existing_dir=False):
        
        super(PositionIterator, self).__init__(root_project_base_name,
                                               worker_directory,
                                               base_project,
                                               counter,
                                               base_penalty,
                                               logging,
                                               clean_existing_dir)
        
        self._tool_man = ToolManager()
        self._positioner = get_positioner(self._core, self._base_project)
        
        return
    
    def get_popen_args(self, worker_project_path, *args):
        "Return the arguments to create a new process thread using Popen"
        
        popen_args = ["_dtocean-optim-pos",
                      worker_project_path]
        popen_args += [str(x) for x in args]
        popen_args += [str(self._base_penalty)]
        
        return popen_args
    
    def pre_constraints_hook(self, *args):
        
        (array_orientation_deg,
         delta_row,
         delta_col,
         n_nodes,
         t1,
         t2) = args
        
        array_orientation = float(array_orientation_deg) * np.pi / 180
        beta = 90 * np.pi / 180
        psi = 0 * np.pi / 180
        
        try:
            
            positions = self._positioner(array_orientation,
                                         delta_row,
                                         delta_col,
                                         beta,
                                         psi,
                                         int(n_nodes),
                                         t1,
                                         t2)
        
        except RuntimeError as e:
            
            details = str(e)
            
            if "Expected number of nodes not found" in details:
                
                words = details.split()
                multiplier = int(words[-4]) - int(words[-1])
                
                return self._base_penalty * multiplier
        
        spacing_tool = self._tool_man.get_tool("Device Minimum Spacing Check")
        spacing_tool.configure(positions)
        
        try:
            
            self._tool_man.execute_tool(self._core,
                                        self._base_project,
                                        spacing_tool)
        
        except RuntimeError as e:
            
            details = str(e)
            
            if "Violation of the minimum distance constraint" in details:
                
                words = details.split()
                multiplier = 1 + float(words[-1])
                
                return self._base_penalty * multiplier
        
        return
    
    def get_worker_cost(self, lines):
        """Return the function cost based on the lines read from the worker
        results file."""
        
        lcoe = float(lines[1])
        flag = lines[2]
        
        if flag == "Exception":
            
            details = lines[3]
            
            if self._logging == "print":
                print flag
                print details
            elif self._logging == "module":
                module_logger.debug(flag)
                module_logger.debug(details)
        
        return lcoe
    
    def set_counter_params(self, iteration,
                                 worker_project_path,
                                 worker_results_path,
                                 cost,
                                 flag,
                                 *args):
        """Update the counter object with new data."""
        
        self._counter.set_params(iteration,
                                 worker_project_path,
                                 worker_results_path,
                                 cost,
                                 flag,
                                 *args)
        
        return
    
    def cleanup(self, worker_project_path, flag, lines):
        """Hook to clean up simulation files as required"""
        
        if lines is None: return
        
        dat_flag = lines[2]
        
        if dat_flag == "Exception":
            remove_retry(worker_project_path)
        
        return


def main(config, core=None, project=None):
    
    module_logger.info("Beginning position optimisation")
    
    root_project_path = config['root_project_path']
    worker_directory = config["worker_dir"]
    base_penalty = config["base_penalty"]
    n_threads = config["n_threads"]
    
    # Defaults
    clean_existing_dir = False
    max_simulations = None
    logging="module"
    
    if "clean_existing_dir" in config:
        clean_existing_dir = config["clean_existing_dir"]
    
    if "max_simulations" in config:
        max_simulations = config["max_simulations"]
    
    if "logging" in config:
        logging = config["logging"]
    
    if core is None: core = Core()
    if project is None: project = core.load_project(root_project_path)
    
    _, root_project_name = os.path.split(root_project_path)
    root_project_base_name, _ = os.path.splitext(root_project_name)
    
    fixed_params, ranges, nearest_ops = get_param_control(config,
                                                          core,
                                                          project)
    
    scaled_vars = [cma.NormScaler(*x) for x in ranges]
    x0 = [scaled.x0 for scaled in scaled_vars]
    low_bound = [scaler.scaled(x[0]) for x, scaler in zip(ranges, scaled_vars)]
    high_bound = [scaler.scaled(x[1])
                                    for x, scaler in zip(ranges, scaled_vars)]
    
    counter = PositionCounter()
    iterator = PositionIterator(root_project_base_name,
                                worker_directory,
                                project,
                                counter,
                                base_penalty=base_penalty,
                                logging=logging,
                                clean_existing_dir=clean_existing_dir)
    
    es = cma.main(worker_directory,
                  iterator,
                  x0,
                  low_bound,
                  high_bound,
                  scaled_vars,
                  nearest_ops,
                  fixed_index_map=fixed_params,
                  num_threads=n_threads,
                  max_simulations=max_simulations,
                  logging=logging)
    
    module_logger.info("Position optimisation complete")
    
    return es


def get_param_control(config, core, project):
    
    ranges = []
    nearest_ops = []
    fixed_params = {}
    
    param_names = ["array_orientation",
                   "delta_row",
                   "delta_col",
                   "n_nodes",
                   "t1",
                   "t2"]
    
    for i, param_name in enumerate(param_names):
        
        parameter = config["parameters"][param_name]
        
        if "fixed" in parameter:
            fixed_params[i] = parameter["fixed"]
            continue
        
        crange = parameter["range"]
        
        if crange["type"] == "fixed":
            prange = get_range_fixed(crange["min"], crange["max"])
        elif crange["type"] == "multiplier":
            prange = get_range_multiplier(core,
                                          project,
                                          crange["variable"],
                                          crange["min_multiplier"],
                                          crange["max_multiplier"])
            
        cinterp = parameter["interp"]
        
        if cinterp["type"] == "fixed":
            nearest_op = get_interp_fixed(cinterp["values"])
        elif  cinterp["type"] == "range":
            nearest_op = get_interp_range(prange, cinterp["delta"])
        
        ranges.append(prange)
        nearest_ops.append(nearest_op)
    
    if not fixed_params: fixed_params = None
    
    return fixed_params, ranges, nearest_ops


def nearest(a, value):
    
    # Round half towards positive infinity
    
    i = bisect_left(a, value)
        
    if i == 0:
        return a[i]
    elif i == len(a):
        return a[i - 1]
    elif value - a[i - 1] < a[i] - value:
        return a[i - 1]
    else:
        return a[i]


def get_range_fixed(rmin, rmax):
    return (rmin, rmax)


def get_range_multiplier(core, project, variable, mmin, mmax):
    
    value = core.get_data_value(project, variable)
    
    return (mmin * value, mmax * value)


def get_interp_fixed(values):
    
    f = lambda x: nearest(values, x)
    
    return f


def get_interp_range(irange, delta):
    
    extend = 0.
    
    if np.isclose((irange[1] - irange[0]) % delta, 0., atol=0):
        extend += delta
    
    f = lambda x: nearest(np.arange(irange[0], irange[1] + extend, delta), x)
    
    return f


def load_config(config_path):
    
    yaml = YAML()
    
    with open(config_path, "r") as stream:
        config = yaml.load(stream)
    
    return config


def load_config_template(config_name="config.yaml"):
    
    config_path = os.path.join(THIS_DIR, config_name)
    config = load_config(config_path)
    
    return config


def dump_config(config, config_path):
    
    yaml = YAML()
    
    with open(config_path, 'w') as stream:
        yaml.dump(config, stream)
    
    return
