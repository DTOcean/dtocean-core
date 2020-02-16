# -*- coding: utf-8 -*-

import os
import ast
import glob
import math
import types
import pickle
import logging
import threading

import pandas as pd
import yaml
from natsort import natsorted

from . import Strategy
from .position_optimiser import (dump_config,
                                 load_config,
                                 load_config_template,
                                 Main)
from .position_optimiser.iterator import get_positioner, iterate
from ..menu import ModuleMenu
from ..pipeline import Tree

# Set up logging
module_logger = logging.getLogger(__name__)


class MainThread(threading.Thread):
    
    def __init__(self, main,
                       config,
                       log_interval=100,
                       wait_interval=1):
        
        super(MainThread, self).__init__(name="MainThread")
        self._main = main
        self._config = config
        self._log_interval = log_interval
        self._wait_interval = wait_interval
        self._stop_event = threading.Event()
        self._continue_event = threading.Event()
        self._continue_event.set()
        
        self._stopped = False
        self._paused = False
    
    @property
    def stopped(self):
        return self._stopped
    
    @property
    def paused(self):
        return self._paused
    
    def _set_stopped(self, state=True):
        
        if not state:
            err_msg = "Stopped state may only be set to True"
            raise ValueError(err_msg)
        
        log_msg = "Thread stopped"
        module_logger.info(log_msg)
        
        try:
            self._exit_hook()
        except Exception as e:
            log_msg = ("Exit hook threw {}: "
                       "{}").format(type(e).__name__, str(e))
            module_logger.warning(log_msg)
        
        self._stopped = True
        
        return
    
    def _set_paused(self, state):
        
        if state:
            state_msg = "paused"
        else:
            state_msg = "resumed"
        
        log_msg = "Thread {}".format(state_msg)
        module_logger.info(log_msg)
        
        self._paused = state
        
        return
    
    def stop(self):
        
        if self._stop_event.is_set(): return
        
        log_msg = "Stopping thread..."
        module_logger.info(log_msg)
        
        self._stop_event.set()
        
        if not self._continue_event.is_set():
            self._continue_event.set()
        
        return
    
    def pause(self):
        
        if (self._stop_event.is_set() or
            not self._continue_event.is_set()): return
        
        log_msg = "Pausing thread..."
        module_logger.info(log_msg)
        
        self._continue_event.clear()
        
        return
    
    def resume(self):
        
        if (self._stop_event.is_set() or
            self._continue_event.is_set()): return
        
        log_msg = "Resuming thread..."
        module_logger.info(log_msg)
        
        self._continue_event.set()
        
        return
    
    def _exit_hook(self):
        return
    
    def set_exit_hook(self, func):
        
        method = _method_decorator(func)
        self._exit_hook = types.MethodType(method, self)
        
        return
    
    def clear_exit_hook(self):
        
        def empty():
            return
        
        method = _method_decorator(empty)
        self._exit_hook = types.MethodType(method, self)
        
        return
    
    def run(self):
        
        continue_event_state = self._continue_event.is_set()
        
        while not self._main.stop:
            
            if (self._continue_event.is_set() != continue_event_state and 
                not self._continue_event.is_set()):
                
                self._set_paused(True)
                continue_event_state = self._continue_event.is_set()
            
            self._continue_event.wait()
            
            if (self._continue_event.is_set() != continue_event_state and
                self._continue_event.is_set()):
                
                self._set_paused(False)
                continue_event_state = self._continue_event.is_set()
            
            if self._stop_event.is_set():
                self._set_stopped()
                return
            
            self._main.next()
        
        _post_process(self._config, self._log_interval)
        self._set_stopped()
        
        return
    
    def get_es(self):
        
        if self.stopped:
            result = self._main.get_es()
        else:
            result = None
        
        return result

class AdvancedPosition(Strategy):
    
    """
    """
    
    @classmethod
    def get_name(cls):
        
        return "Advanced Positioning"
    
    def configure(self, **config_dict):
        
        _, status = self.get_config_status(config_dict)
        
        if status == 0:
            
            err_msg = ("Required keys are missing from the configuration "
                       "dictionary.")
            raise ValueError(err_msg)
        
        self.set_config(config_dict)
        
        return
    
    def get_variables(self):
        
        set_vars = ['options.user_array_layout',
                    'project.rated_power']
        
        return set_vars
    
    def execute(self, core, project):
        
        self._prepare_project(core, project)
        main = Main(core=core, project=project)
        
        _, work_dir_status = self.get_worker_directory_status(self._config)
        _, optim_status = self.get_optimiser_status(self._config)
        
        if work_dir_status == 0 and optim_status == 2:
            
            log_str = 'Attempting restart of incomplete strategy'
            module_logger.info(log_str)
            
            main.restart(self._config["worker_dir"])
        
        else:
            
            main.start(self._config)
        
        while not main.stop:
            main.next()
        
        es = main.get_es()
        self._post_process()
        
        return es
    
    def execute_threaded(self, core, project):
        
        self._prepare_project(core, project)
        main = Main(core=core, project=project)
        
        _, work_dir_status = self.get_worker_directory_status(self._config)
        _, optim_status = self.get_optimiser_status(self._config)
        
        if work_dir_status == 0 and optim_status == 2:
            
            log_str = 'Attempting restart of incomplete strategy'
            module_logger.info(log_str)
            
            main.restart(self._config["worker_dir"])
        
        else:
            
            main.start(self._config)
        
        thread = MainThread(main,
                            self._config)
        
        thread.start()
        
        return thread
    
    def _post_process(self, log_interval=100):
        
        _post_process(self._config, log_interval)
        
        return
    
    @classmethod
    def get_results_table(cls, config):
        
        key_order = ["sim_number"]
        key_order.append(config["objective"])
        key_order.extend(["array_orientation",
                          "delta_row",
                          "delta_col",
                          "n_nodes",
                          "t1",
                          "t2"])
        
        params_set = set(config["results_params"])
        params_set = params_set.difference([config["objective"]])
        key_order.extend(list(params_set))
        
        conversion_map = {"array_orientation": math.degrees}
        
        root_project_path = config['root_project_path']
        sim_dir = config["worker_dir"]
        
        root_project_base_name = _get_root_project_base_name(root_project_path)
        
        pickle_name = "{}_results.pkl".format(root_project_base_name)
        pickle_path = os.path.join(sim_dir, pickle_name)
        
        pickle_dict = pickle.load(open(pickle_path, 'rb'))
        
        table_dict = {}
        table_cols = []
        
        for key in key_order:
            
            value = pickle_dict[key]
            
            if not value:
                
                table_cols.append(key)
                table_dict[key] = value
                
            elif isinstance(value[0], dict):
                
                ref_dict = value[0]
                template = "{} [{}]"
                
                for ref_key in ref_dict:
                    
                    col_name = template.format(key, ref_key)
                    val_list = [x[ref_key] for x in value]
                    
                    if key in conversion_map:
                        val_list = [conversion_map[key](x) for x in val_list]
                    
                    table_cols.append(col_name)
                    table_dict[col_name] = val_list
                
            else:
                
                if key in conversion_map:
                    value = [conversion_map[key](x) for x in value]
                
                table_cols.append(key)
                table_dict[key] = value
        
        return pd.DataFrame(table_dict, columns=table_cols)
    
    def load_simulations(self, core,
                               project,
                               sim_numbers,
                               sim_titles=None):
        
        self.restart()
        
        root_project_path = self._config['root_project_path']
        sim_dir = self._config["worker_dir"]
        positioner = None
        
        root_project_base_name = _get_root_project_base_name(root_project_path)
        path_template = _get_sim_path_template(root_project_base_name, sim_dir)
        
        for i, n in enumerate(sim_numbers):
            
            prj_file_path = path_template.format(n, 'prj')
            
            if not os.path.isfile(prj_file_path):
                
                if positioner is None:
                    positioner = get_positioner(core, project)
                
                src_project = project._to_project()
                
                prj_base_path, _ = os.path.splitext(prj_file_path)
                yaml_file_path = "{}.yaml".format(prj_base_path)
                
                with open(yaml_file_path, "r") as stream:
                    results = yaml.load(stream, Loader=yaml.FullLoader)
                
                params = results["params"]
                
                array_orientation = params["theta"]
                delta_row = params["dr"]
                delta_col = params["dc"]
                n_nodes = params["n_nodes"]
                t1 = params["t1"]
                t2 = params["t2"]
                
                iterate(core,
                        src_project,
                        positioner,
                        array_orientation,
                        delta_row,
                        delta_col,
                        n_nodes,
                        t1,
                        t2)
                
                core.dump_project(src_project, prj_file_path)
            
            else:
                
                src_project = core.load_project(prj_file_path)
            
            if sim_titles is not None:
                sim_title = sim_titles[i]
            else:
                sim_title = "Simulation {}".format(n)
            
            core.import_simulation(src_project,
                                   project,
                                   dst_sim_title=sim_title)
            
            self.add_simulation_title(sim_title)
        
        return
    
    @classmethod
    def remove_simulations(cls, core,
                                project,
                                sim_titles=None,
                                exclude_default=True):
        
        """Convenience method for removing either all simulations in a project,
        excluding the 'Default' simulation (by default - hah), or removing
        the simulations with titles given in sim_titles.
        """
        
        if sim_titles is None:
            
            sim_titles = project.get_simulation_titles()
            if exclude_default: sim_titles.remove("Default")
        
        for sim_title in sim_titles:
            core.remove_simulation(project, sim_title=sim_title)
        
        return
    
    @classmethod
    def load_config(cls, config_path):
        
        config = load_config(config_path)
        
        return config
    
    def dump_config(self, config_path):
        
        dump_config(self._config, config_path)
        
        return
    
    @classmethod
    def export_config_template(cls, export_path):
        
        config = load_config_template()
        dump_config(config, export_path)
        
        return
    
    @classmethod
    def get_config_status(cls, config):
        
        required_keys = ["root_project_path",
                         "worker_dir",
                         "base_penalty",
                         "n_threads",
                         "parameters",
                         "objective",
                         "results_params"]
        
        required_filled = [bool(config[x]) if x in config else False
                                                       for x in required_keys]
        
        if not all(required_filled):
            
            status_str = "Configuration incomplete"
            status_code = 0
        
        else:
            
            status_str = "Configuration complete"
            status_code = 1
        
        return status_str, status_code
    
    @classmethod
    def get_project_status(cls, core, project):
        
        module_menu = ModuleMenu()
        
        sim_index = project.get_active_index()
        active_modules = module_menu.get_active(core, project)
        required_modules = ["Hydrodynamics",
                            "Operations and Maintenance"]
        
        if sim_index is None:
            
            status_strs = ["Project has not been activated"]
            status_code = 0
        
        elif not set(required_modules) <= set(active_modules):
            
            status_strs = []
            
            for missing in set(required_modules) - set(active_modules):
                
                status_str = ("Project does not contain the {} "
                              "module").format(missing)
                status_strs.append(status_str)
                
            status_code = 0
        
        elif "Default" not in project.get_simulation_titles():
            
            status_strs = [('The position optimiser requires a simulation'
                           ' with title "Default"')]
            status_code = 0
        
        else:
            
            status_strs = ["Project ready"]
            status_code = 1
        
        return status_strs, status_code
    
    @classmethod
    def get_worker_directory_status(cls, config):
        
        worker_directory = config["worker_dir"]
        
        status_str = None
        status_code = None
        
        if os.path.isdir(worker_directory):
            
            if len(os.listdir(worker_directory)) == 0:
                
                status_str = "Worker directory empty"
                status_code = 1
            
            elif not config['clean_existing_dir']:
                
                status_str = "Worker directory contains files"
                status_code = 0
        
        else:
            
            status_str = "Worker directory does not yet exist"
            status_code = 1
        
        return status_str, status_code
    
    @classmethod
    def get_optimiser_status(cls, config):
        
        root_project_path = config['root_project_path']
        worker_directory = config["worker_dir"]
        
        status_str = None
        status_code = None
        
        if os.path.isdir(worker_directory):
            
            _, root_project_name = os.path.split(root_project_path)
            root_project_base_name, _ = os.path.splitext(root_project_name)
            pickle_name = "{}_results.pkl".format(root_project_base_name)
            
            results_path = os.path.join(worker_directory, pickle_name)
            
            if os.path.isfile(results_path):
                
                status_str = "Optimisation complete"
                status_code = 1
            
            else:
                
                status_str = ("Optimisation incomplete (restart may be "
                              "possible)")
                status_code = 2
        
        return status_str, status_code
    
    def _prepare_project(self, core, project):
        
        # Check the project is active and record the simulation number
        status_strs, status_code = self.get_project_status(core,
                                                           project)
        
        if status_code == 0:
            status_str = "\n".join(status_strs)
            raise RuntimeError(status_str)
        
        if project.get_simulation_title() != "Default":
            
            log_str = 'Setting active simulation to "Default"'
            module_logger.info(log_str)
            
            project.set_active_index(title="Default")
        
        log_str = 'Attempting to reset simulation level'
        module_logger.info(log_str)
        
        tree = Tree()
        hydro_branch = tree.get_branch(core, project, "Hydrodynamics")
        hydro_branch.reset(core, project)
        
        return


def _method_decorator(func):
    
    def wrapper(self):
        func()
    
    return wrapper


def _get_root_project_base_name(root_project_path):
    
    _, root_project_name = os.path.split(root_project_path)
    root_project_base_name, _ = os.path.splitext(root_project_name)
    
    return root_project_base_name


def _get_sim_path_template(root_project_base_name, sim_dir):
    
    sim_name_template = root_project_base_name + "_{}.{}"
    sim_path_template = os.path.join(sim_dir, sim_name_template)
    
    return sim_path_template


def _post_process(config, log_interval=100):
    
    msg_str = "Beginning post-processing of simulations"
    module_logger.info(msg_str)
    
    pickle_dict = {}
    
    param_map = {"array_orientation": "theta",
                 "delta_row": "dr",
                 "delta_col": "dc",
                 "n_nodes": "n_nodes",
                 "t1": "t1",
                 "t2": "t2"}
    
    sim_dir = config["worker_dir"]
    root_project_path = config['root_project_path']
    root_project_base_name = _get_root_project_base_name(root_project_path)
    
    yaml_pattern = '{}_*.yaml'.format(root_project_base_name)
    search_str = os.path.join(sim_dir, yaml_pattern)
    yaml_file_paths = natsorted(glob.glob(search_str))
    n_sims = len(yaml_file_paths)
    
    read_params = config["parameters"].keys()
    
    for param in read_params:
        pickle_dict[param] = []
    
    extract_vars = set(config["results_params"])
    extract_vars = extract_vars.union([config["objective"]])
    extract_vars = list(extract_vars)
    
    for var in extract_vars:
        pickle_dict[var] = []
    
    pickle_dict["sim_number"] = []
    
    for i, yaml_file_path in enumerate(yaml_file_paths):
        
        if (i + 1) % log_interval == 0:
            
            msg_str = "Processed {} of {} simulations".format(i + 1,
                                                              n_sims)
            module_logger.info(msg_str)
        
        with open(yaml_file_path, "r") as stream:
            results = yaml.load(stream, Loader=yaml.FullLoader)
        
        flag = results["status"]
        
        if flag == "Exception": continue
        
        param_values = results["params"]
        
        sim_num_dat = yaml_file_path.split("_")[-1]
        sim_num = int(os.path.splitext(sim_num_dat)[0])
        
        data_values = results["results"]
        
        if set(data_values) != set(extract_vars): continue
        
        pickle_dict["sim_number"].append(sim_num)
        
        for param in read_params:
            param_value = param_values[param_map[param]]
            pickle_dict[param].append(param_value)
        
        for var_name in extract_vars:
            data_value = data_values[var_name]
            pickle_dict[var_name].append(data_value)
    
    pickle_name = "{}_results.pkl".format(root_project_base_name)
    pickle_path = os.path.join(sim_dir, pickle_name)
    pickle.dump(pickle_dict, open(pickle_path, 'wb'))
    
    msg_str = "Post-processing complete"
    module_logger.info(msg_str)
    
    return


def _post_process_legacy(core, config, log_interval=100):
    
    msg_str = "Beginning post-processing of simulations"
    module_logger.info(msg_str)
    
    pickle_dict = {}
    
    param_map = {"array_orientation": "theta",
                 "delta_row": "dr",
                 "delta_col": "dc",
                 "n_nodes": "n_nodes",
                 "t1": "t1",
                 "t2": "t2"}
    
    extract_vars = ["project.number_of_devices",
                    "project.annual_energy",
                    "project.q_factor",
                    "project.lcoe_mode",
                    "project.capex_total",
                    "project.capex_breakdown",
                    "project.lifetime_opex_mode",
                    "project.lifetime_energy_mode"]
    
    for var in extract_vars:
        pickle_dict[var] = []
    
    root_project_path = config['root_project_path']
    sim_dir = config["worker_dir"]
    
    root_project_base_name = _get_root_project_base_name(root_project_path)
    path_template = _get_sim_path_template(root_project_base_name, sim_dir)
    
    read_params = config["parameters"].keys()
    
    for param in read_params:
        pickle_dict[param] = []
    
    search_str = os.path.join(sim_dir, '*.dat')
    dat_file_paths = natsorted(glob.glob(search_str))
    n_sims = len(dat_file_paths)
    
    pickle_dict["sim_number"] = []
    
    for i, dat_file_path in enumerate(dat_file_paths):
        
        if (i + 1) % log_interval == 0:
            
            msg_str = "Processed {} of {} simulations".format(i + 1,
                                                              n_sims)
            module_logger.info(msg_str)
        
        with open(dat_file_path, "r") as f:
            lines = f.read().splitlines()
        
        flag = lines[2]
        
        if flag == "Exception": continue
        
        params_line = lines[0]
        
        param_values = {b.split(":")[0].strip():
                            ast.literal_eval(b.split(":")[1].strip())
                                for b in params_line.split(";")}
        
        sim_num_dat = dat_file_path.split("_")[-1]
        sim_num = int(os.path.splitext(sim_num_dat)[0])
        
        prj_file_path = path_template.format(sim_num, 'prj')
        project = core.load_project(prj_file_path)
        
        if core.has_data(project, "project.lcoe_mode"):
            
            pickle_dict["sim_number"].append(sim_num)
            
            for param in read_params:
                param_value = param_values[param_map[param]]
                pickle_dict[param].append(param_value)
            
            for var_name in extract_vars:
                data_value = core.get_data_value(project, var_name)
                pickle_dict[var_name].append(data_value)
        
        else:
            
            continue
    
    pickle_name = "{}_results.pkl".format(root_project_base_name)
    pickle_path = os.path.join(sim_dir, pickle_name)
    pickle.dump(pickle_dict, open(pickle_path, 'wb'))
    
    msg_str = "Post-processing complete"
    module_logger.info(msg_str)
    
    return
