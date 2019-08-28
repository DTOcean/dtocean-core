# -*- coding: utf-8 -*-

import os
import ast
import glob
import math
import pickle
import logging

import pandas as pd

from . import Strategy
from .position_optimiser import (dump_config,
                                 load_config,
                                 load_config_template,
                                 main)
from ..menu import ModuleMenu
from ..pipeline import Tree

# Set up logging
module_logger = logging.getLogger(__name__)


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
        
        es = main(self._config,
                  core=core,
                  project=project)
        
        self._post_process(core)
        
        return es
    
    def _post_process(self, core,
                            log_interval=100):
        
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
        
        root_project_path = self._config['root_project_path']
        sim_dir = self._config["worker_dir"]
        
        root_project_base_name = _get_root_project_base_name(root_project_path)
        path_template = _get_sim_path_template(root_project_base_name, sim_dir)
        
        read_params = self._config["parameters"].keys()
        
        for param in read_params:
            pickle_dict[param] = []
        
        search_str = os.path.join(sim_dir, '*.dat')
        n_sims = len(glob.glob(search_str))
        
        pickle_dict["sim_number"] = []
        
        for i in range(n_sims):
            
            if (i + 1) % log_interval == 0:
                
                msg_str = "Processed {} of {} simulations".format(i + 1,
                                                                  n_sims)
                module_logger.info(msg_str)
            
            dat_file_path = path_template.format(i, 'dat')
            
            with open(dat_file_path, "r") as f:
                lines = f.read().splitlines()
            
            flag = lines[2]
            
            if flag == "Exception": continue
            
            params_line = lines[0]
            
            param_values = {b.split(":")[0].strip():
                                ast.literal_eval(b.split(":")[1].strip())
                                    for b in params_line.split(";")}
            
            prj_file_path = path_template.format(i, 'prj')
            project = core.load_project(prj_file_path)
            
            if core.has_data(project, "project.lcoe_mode"):
                
                pickle_dict["sim_number"].append(i)
                
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
    
    @classmethod
    def get_results_table(cls, config):
        
        key_order = ["sim_number",
                     "project.lcoe_mode",
                     "array_orientation",
                     "delta_row",
                     "delta_col",
                     "n_nodes",
                     "t1",
                     "t2",
                     "project.number_of_devices",
                     "project.annual_energy",
                     "project.q_factor",
                     "project.capex_total",
                     "project.capex_breakdown",
                     "project.lifetime_opex_mode",
                     "project.lifetime_energy_mode"]
        
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
            
            if isinstance(value[0], dict):
                
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
        
        root_project_base_name = _get_root_project_base_name(root_project_path)
        path_template = _get_sim_path_template(root_project_base_name, sim_dir)
        
        for i, n in enumerate(sim_numbers):
            
            prj_file_path = path_template.format(n, 'prj')
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
    def get_config_status(self, config):
        
        required_keys = ["root_project_path",
                         "worker_dir",
                         "base_penalty",
                         "n_threads",
                         "parameters"]
        
        required_filled = [bool(config[x]) for x in required_keys]
        
        if not all(required_filled):
            
            status_str = "Configuration incomplete"
            status_code = 0
        
        else:
            
            status_str = "Configuration complete"
            status_code = 1
        
        return status_str, status_code
    
    @classmethod
    def get_project_status(self, core, project):
        
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

def _get_root_project_base_name(root_project_path):
    
    _, root_project_name = os.path.split(root_project_path)
    root_project_base_name, _ = os.path.splitext(root_project_name)
    
    return root_project_base_name


def _get_sim_path_template(root_project_base_name, sim_dir):
    
    sim_name_template = root_project_base_name + "_{}.{}"
    sim_path_template = os.path.join(sim_dir, sim_name_template)
    
    return sim_path_template
