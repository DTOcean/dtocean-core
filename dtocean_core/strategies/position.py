# -*- coding: utf-8 -*-

import os
import ast
import glob
import pickle
import logging

import pandas as pd

from . import Strategy
from .position_optimiser import get_config, main

# Set up logging
module_logger = logging.getLogger(__name__)


class AdvancedPosition(Strategy):
    
    """
    """
    
    @classmethod
    def get_name(cls):
        
        return "Advanced Positioning"
    
    def configure(self, **config_dict):
        
        # TODO: Add some validation of config_dict here
        self.set_config(config_dict)
        
        return
    
    def get_variables(self):
        
        set_vars = ['options.user_array_layout',
                    'project.rated_power']
        
        return set_vars
    
    def execute(self, core, project):
        
        # Check the project is active and record the simulation number
        sim_index = project.get_active_index()
        
        if sim_index is None:
            
            errStr = "Project has not been activated"
            raise RuntimeError(errStr)
        
        if "Default" not in project.get_simulation_titles():
            
            err_msg = ('The posisiton optimiser requires a simulation with '
                       'title "Default"')
            raise RuntimeError(err_msg)
        
        if project.get_simulation_title() != "Default":
            
            log_str = 'Setting active simulation to "Default"'
            module_logger.info(log_str)
            
            project.set_active_index(title="Default")
        
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
    
    def get_results_table(self):
        
        key_order = ["sim_number",
                     "array_orientation",
                     "delta_row",
                     "delta_col",
                     "n_nodes",
                     "t1",
                     "t2",
                     "project.number_of_devices",
                     "project.annual_energy",
                     "project.q_factor",
                     "project.lcoe_mode",
                     "project.capex_total",
                     "project.capex_breakdown",
                     "project.lifetime_opex_mode",
                     "project.lifetime_energy_mode"]
        
        root_project_path = self._config['root_project_path']
        sim_dir = self._config["worker_dir"]
        
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
                    
                    table_cols.append(col_name)
                    table_dict[col_name] = val_list
                
            else:
                
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
            
            sim_index = project.get_active_index()
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


def _get_root_project_base_name(root_project_path):
    
    _, root_project_name = os.path.split(root_project_path)
    root_project_base_name, _ = os.path.splitext(root_project_name)
    
    return root_project_base_name


def _get_sim_path_template(root_project_base_name, sim_dir):
    
    sim_name_template = root_project_base_name + "_{}.{}"
    sim_path_template = os.path.join(sim_dir, sim_name_template)
    
    return sim_path_template
