# -*- coding: utf-8 -*-

"""
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os
import re
import glob
import logging
from bisect import bisect_left
from collections import namedtuple

import numpy as np
from ruamel.yaml import YAML
from natsort import natsorted

from .iterator import get_positioner
from ...core import Core
from ...extensions import ToolManager
from ...utils import optimiser as opt
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
                                               'n_evals',
                                               'lcoe',
                                               'flag',
                                               'prj_file_path',
                                               'yaml_file_path'])


class PositionCounter(opt.Counter):
    
    def _set_params(self, worker_project_path,
                          worker_results_path,
                          lcoe,
                          flag,
                          array_orientation_deg,
                          delta_row,
                          delta_col,
                          n_nodes,
                          t1,
                          t2,
                          n_evals):
        """Build a params (probably namedtuple) object to search against."""
        
        params = PositionParams(array_orientation_deg,
                                delta_row,
                                delta_col,
                                n_nodes,
                                t1,
                                t2,
                                n_evals,
                                lcoe,
                                flag,
                                worker_project_path,
                                worker_results_path)
        
        return params
    
    def _get_cost(self, *args):
        """Return cost if parameters in params object match input args, else
        return None."""
        
        return None


class PositionIterator(opt.Iterator):
    
    def __init__(self, root_project_base_name,
                       worker_directory,
                       base_project,
                       counter,
                       objective_var,
                       logging="module",
                       restart=False,
                       clean_existing_dir=False,
                       violation_log_name = "violations.txt"):
        
        super(PositionIterator, self).__init__(root_project_base_name,
                                               worker_directory,
                                               base_project,
                                               counter,
                                               logging,
                                               restart,
                                               clean_existing_dir)
        
        self._tool_man = ToolManager()
        self._positioner = get_positioner(self._core, self._base_project)
        self._objective_var = objective_var
        self._violation_log_path = os.path.join(self._worker_directory,
                                                violation_log_name)
        
        return
    
    def get_popen_args(self, worker_project_path, *args):
        "Return the arguments to create a new process thread using Popen"
        
        popen_args = ["_dtocean-optim-pos",
                      worker_project_path]
        popen_args += [str(x) for x in args]
        
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
                self._log_violation(details, *args)
                return True
            
            raise RuntimeError(e)
        
        spacing_tool = self._tool_man.get_tool("Device Minimum Spacing Check")
        spacing_tool.configure(positions)
        
        try:
            
            self._tool_man.execute_tool(self._core,
                                        self._base_project,
                                        spacing_tool)
        
        except RuntimeError as e:
            
            details = str(e)
            
            if "Violation of the minimum distance constraint" in details:
                self._log_violation(details, *args)
                return True
            
            raise RuntimeError(e)
        
        return False
    
    def get_worker_cost(self, results):
        """Return the function cost based on the data read from the worker
        results file. Constraint violation should return np.nan"""
        
        flag = results["status"]
        
        if flag == "Exception":
            
            details = results["error"]
            
            if self._logging == "print":
                print flag
                print details
            elif self._logging == "module":
                module_logger.debug(flag)
                module_logger.debug(details)
            
            lcoe = np.nan
        
        elif flag == "Success":
            
            lcoe = results["results"][self._objective_var]
        
        else:
        
            raise RuntimeError("Unrecognised flag '{}'".format(flag))
        
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
        
        remove_retry(worker_project_path)
        
        return
    
    def _log_violation(self, details, *args):
        
        largs = [str(arg) for arg in args]
        largs.insert(0, details)
        log_str = ", ".join(largs) + "\n"
        
        with open(self._violation_log_path, "a") as f:
            f.write(log_str)
        
        return


class Main(object):
    
    def __init__(self, core=None,
                       project=None,
                       config_fname="config.yaml"):
        
        if core is None: core = Core()
        
        self.stop = False
        self._core = core
        self._project = project
        self._config_fname = config_fname
        self._worker_directory = None
        self._cma_main = None
        
        return
    
    def start(self, config):
        
        module_logger.info("Beginning position optimisation")
        
        self.stop = False
        self._worker_directory = config["worker_dir"]
        
        root_project_path = config['root_project_path']
        base_penalty = config["base_penalty"]
        n_threads = config["n_threads"]
        results_params = config["results_params"]
        objective = config["objective"]
        
        # Defaults
        clean_existing_dir = False
        max_simulations = None
        popsize = None
        timeout = None
        tolfun = None
        max_resample_loop_factor = None
        logging = "module"
        
        if "clean_existing_dir" in config:
            clean_existing_dir = config["clean_existing_dir"]
        
        if "max_simulations" in config:
            max_simulations = config["max_simulations"]
        
        if "popsize" in config:
            popsize = config["popsize"]
        
        if "timeout" in config:
            timeout = config["timeout"]
        
        if "tolfun" in config:
            tolfun = config["tolfun"]
        
        if "max_resample_factor" in config:
            max_resample_loop_factor = config["max_resample_factor"]
        
        if "logging" in config:
            logging = config["logging"]
        
        if self._project is None:
            project = self._core.load_project(root_project_path)
        else:
            project = self._project
        
        _, root_project_name = os.path.split(root_project_path)
        root_project_base_name, _ = os.path.splitext(root_project_name)
        
        fixed_params, ranges, x0s, nearest_ops = get_param_control(config,
                                                                   self._core,
                                                                   project)
        
        scaled_vars = [opt.NormScaler(x[0], x[1], y)
                                                for x, y in zip(ranges, x0s)]
        x0 = [scaled.x0 for scaled in scaled_vars]
        low_bound = [scaler.scaled(x[0])
                                    for x, scaler in zip(ranges, scaled_vars)]
        high_bound = [scaler.scaled(x[1])
                                    for x, scaler in zip(ranges, scaled_vars)]
        
        es = opt.init_evolution_strategy(x0,
                                         low_bound,
                                         high_bound,
                                         max_simulations=max_simulations,
                                         popsize=popsize,
                                         timeout=timeout,
                                         tolfun=tolfun)
        nh = opt.NoiseHandler(es.N, maxevals=[1, 1, 30])
        
        counter = PositionCounter()
        iterator = PositionIterator(root_project_base_name,
                                    self._worker_directory,
                                    project,
                                    counter,
                                    objective,
                                    logging=logging,
                                    clean_existing_dir=clean_existing_dir)
        
        # Store copy of config in worker directory for potential restart
        config_path = os.path.join(self._worker_directory, self._config_fname)
        dump_config(config, config_path)
        
        # Store the es object and counter search dict for potential restart
        opt.dump_outputs(self._worker_directory, es, iterator, nh)
        
        # Write the results params control file for workers
        results_params = list(set(results_params).union([objective]))
        dump_results_control(results_params, self._worker_directory)
        
        self._cma_main = opt.Main(
                            es,
                            self._worker_directory,
                            iterator,
                            scaled_vars,
                            nearest_ops,
                            nh=nh,
                            fixed_index_map=fixed_params,
                            base_penalty=base_penalty,
                            num_threads=n_threads,
                            max_resample_loop_factor=max_resample_loop_factor,
                            logging=logging)
        
        return
    
    def restart(self, worker_directory):
        
        module_logger.info("Restart position optimisation")
        
        self._worker_directory = worker_directory
        self.stop = False
        
        # Reload the config in the worker directory
        config_path = os.path.join(self._worker_directory, self._config_fname)
        config = load_config(config_path)
        
        # Reload outputs
        es, counter_dict, nh = opt.load_outputs(self._worker_directory)
    
        root_project_path = config['root_project_path']
        base_penalty = config["base_penalty"]
        n_threads = config["n_threads"]
        objective = config["objective"]
        
        # Defaults
        max_resample_loop_factor = None
        logging = "module"
        
        if "max_resample_factor" in config:
            max_resample_loop_factor = config["max_resample_factor"]
        
        if "logging" in config:
            logging = config["logging"]
        
        # Remove files above last recorded iteration
        if counter_dict:
            last_iter = max(counter_dict)
        else:
            last_iter = -1
            
        _, root_project_name = os.path.split(root_project_path)
        root_project_base_name, _ = os.path.splitext(root_project_name)
        
        yaml_pattern = '{}_*.yaml'.format(root_project_base_name)
        prj_pattern = '{}_*.prj'.format(root_project_base_name)
        
        clean_numbered_files_above(self._worker_directory,
                                   yaml_pattern,
                                   last_iter)
        clean_numbered_files_above(self._worker_directory,
                                   prj_pattern,
                                   last_iter)
        
        if self._project is None:
            project = self._core.load_project(root_project_path)
        else:
            project = self._project
        
        _, root_project_name = os.path.split(root_project_path)
        root_project_base_name, _ = os.path.splitext(root_project_name)
        
        fixed_params, ranges, x0s, nearest_ops = get_param_control(config,
                                                                   self._core,
                                                                   project)
        
        scaled_vars = [opt.NormScaler(x[0], x[1], y)
                                                for x, y in zip(ranges, x0s)]
        
        counter = PositionCounter(counter_dict)
        iterator = PositionIterator(root_project_base_name,
                                    self._worker_directory,
                                    project,
                                    counter,
                                    objective,
                                    logging=logging,
                                    restart=True)
        
        self._cma_main = opt.Main(
                            es,
                            self._worker_directory,
                            iterator,
                            scaled_vars,
                            nearest_ops,
                            nh=nh,
                            fixed_index_map=fixed_params,
                            base_penalty=base_penalty,
                            num_threads=n_threads,
                            max_resample_loop_factor=max_resample_loop_factor,
                            logging=logging)
        
        return
    
    def next(self):
        
        if self._cma_main.stop:
            module_logger.info("Position optimisation complete")
            self.stop = True
            return
        
        self._cma_main.next()
        opt.dump_outputs(self._worker_directory,
                         self._cma_main.es,
                         self._cma_main.iterator,
                         self._cma_main.nh)
        
        return
    
    def get_es(self):
        return self._cma_main.es
    
    def get_nhs(self):
        return self._cma_main.nh


def get_param_control(config, core, project):
    
    ranges = []
    x0s = []
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
        
        if "interp" in parameter:
            
            cinterp = parameter["interp"]
            
            if cinterp["type"] == "fixed":
                nearest_op = get_interp_fixed(cinterp["values"])
            elif  cinterp["type"] == "range":
                nearest_op = get_interp_range(prange, cinterp["delta"])
        
        else:
            
            nearest_op = None
        
        if "x0" in parameter:
            x0 = parameter["x0"]
        else:
            x0 = None
        
        ranges.append(prange)
        x0s.append(x0)
        nearest_ops.append(nearest_op)
    
    if not fixed_params: fixed_params = None
    
    return fixed_params, ranges, x0s, nearest_ops


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
    
    ruyaml = YAML()
    
    with open(config_path, "r") as stream:
        config = ruyaml.load(stream)
    
    return config


def load_config_template(config_name="config.yaml"):
    
    config_path = os.path.join(THIS_DIR, config_name)
    config = load_config(config_path)
    
    return config


def dump_config(config, config_path):
    
    ruyaml = YAML()
    
    with open(config_path, 'w') as stream:
        ruyaml.dump(config, stream)
    
    return


def dump_results_control(params,
                         worker_directory,
                         fname='results_control.txt'):
    
    dump_str = '\n'.join(params)
    fpath = os.path.join(worker_directory, fname)
    
    with open(fpath, 'w') as f:
        f.write(dump_str)
    
    return


def clean_numbered_files_above(directory, search_pattern, highest_valid):
    
    search_str = os.path.join(directory, search_pattern)
    file_paths = natsorted(glob.glob(search_str))
    file_numbers = map(extract_number, file_paths)
    
    paths_to_clean = [x for x, y in zip(file_paths, file_numbers)
                                                    if y > highest_valid]
    
    for path in paths_to_clean:
        remove_retry(path)
    
    return


def extract_number(f):
    s = re.findall("(\d+).", f)
    return int(s[0]) if s else -1
