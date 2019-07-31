# -*- coding: utf-8 -*-

import os
import ast
import glob
import pickle
import logging

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
    
    def configure(self, config_path):
        
        config_dict = {"config_path": config_path}
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
        
        es = main(self._config["config_path"],
                  core=core,
                  project=project)
        
        self._post_process(core)
        
        return es
    
    def _post_process(self, core, extra_vars=None):
        
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
        
        if extra_vars is not None:
            extract_vars.extend(extra_vars)
        
        for var in extract_vars:
            pickle_dict[var] = []
        
        config = get_config(self._config["config_path"])
        
        root_project_path = config['root_project_path']
        sim_dir = config["worker_dir"]
        
        _, root_project_name = os.path.split(root_project_path)
        root_project_base_name, _ = os.path.splitext(root_project_name)
        sim_name_template = root_project_base_name + "_{}.{}"
        path_template = os.path.join(sim_dir, sim_name_template)
        
        read_params = config["parameters"].keys()
        
        for param in read_params:
            pickle_dict[param] = []
        
        search_str = os.path.join(sim_dir, '*.dat')
        n_sims = len(glob.glob(search_str))
        
        pickle_dict["sim_number"] = []
        
        for i in range(n_sims):
            
            pickle_dict["sim_number"].append(i)
            
            print "{} of {}".format(i, n_sims - 1)
            
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
        
        return
