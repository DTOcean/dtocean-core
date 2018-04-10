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

"""
This module contains the package interface to the dtocean economics functions.

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. module:: economics
   :platform: Windows
   :synopsis: Aneris interface for dtocean_core package
   
.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

import numpy as np
import pandas as pd

from dtocean_economics import main
from dtocean_economics.preprocessing import (estimate_cost_per_power,
                                             estimate_energy,
                                             estimate_opex,
                                             make_phase_bom)

from . import ThemeInterface
from ..utils.stats import EstimatedDistribution


class EconomicInterface(ThemeInterface):
    
    '''Interface to the economics thematic functions.
    '''

    def __init__(self):
        
        super(EconomicInterface, self).__init__()
        
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Economics"
        
    @classmethod         
    def declare_weight(cls):
        
        return 1

    @classmethod         
    def declare_inputs(cls):
        
        '''A class method to declare all the variables required as inputs by
        this interface. 
        
        Returns:
          list: List of inputs identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example::
          
              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        '''

        input_list  =  ["device.system_cost",
                        "project.number_of_devices",
                        "project.electrical_economics_data",
                        "project.moorings_foundations_economics_data",
                        "project.installation_economics_data",
                        "project.capex_oandm",
                        "project.opex_per_year",
                        "project.energy_per_year",
                        'project.electrical_network_efficiency',
                        'project.lifetime',
                        "project.discount_rate",
                        "project.externalities_capex",
                        "project.externalities_opex",
                        'project.electrical_cost_estimate',
                        'project.moorings_cost_estimate',
                        'project.installation_cost_estimate',
                        'project.opex_estimate',
                        'project.annual_repair_cost_estimate',
                        'project.annual_array_mttf_estimate',
                        'project.electrical_network_efficiency',
                        "project.annual_energy",
                        'project.estimate_energy_record'
                        ]
                                                
        return input_list

    @classmethod        
    def declare_outputs(cls):
        
        '''A class method to declare all the output variables provided by
        this interface.
        
        Returns:
          list: List of output identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example::
          
              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        '''
        
        output_list = ["project.economics_metrics",
                       "project.lcoe_mean",
                       "project.lcoe_mode",
                       "project.lcoe_interval_lower",
                       "project.lcoe_interval_upper",
                       "project.capex_lcoe_mean",
                       "project.capex_lcoe_mode",
                       "project.capex_lcoe_interval_lower",
                       "project.capex_lcoe_interval_upper",
                       "project.opex_lcoe_mean",
                       "project.opex_lcoe_mode",
                       "project.opex_lcoe_interval_lower",
                       "project.opex_lcoe_interval_upper",
                       "project.opex_mean",
                       "project.opex_mode",
                       "project.opex_interval_lower",
                       "project.opex_interval_upper",
                       "project.discounted_opex_mean",
                       "project.discounted_opex_mode",
                       "project.discounted_opex_interval_lower",
                       "project.discounted_opex_interval_upper",
                       "project.exported_energy_mean",
                       "project.exported_energy_mode",
                       "project.exported_energy_interval_lower",
                       "project.exported_energy_interval_upper",
                       "project.discounted_energy_mean",
                       "project.discounted_energy_mode",
                       "project.discounted_energy_interval_lower",
                       "project.discounted_energy_interval_upper",
                       "project.capex_total",
                       "project.discounted_capex",
                       "project.cost_breakdown",
                       "project.capex_breakdown",
                       "project.capex_lcoe_breakdown",
                       "project.opex_breakdown",
                       "project.opex_lcoe_breakdown",
                       "project.lcoe_pdf"]
        
        return output_list
        
    @classmethod        
    def declare_optional(cls):
        
        '''A class method to declare all the variables which should be flagged
        as optional.
        
        Returns:
          list: List of optional variable identifiers
        
        Note:
          Currently only inputs marked as optional have any logical effect.
          However, this may change in future releases hence the general
          approach.
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the declare_inputs output. For example::
          
              optional = ["My:first:variable",
                         ]
        '''
        
        optional = ["device.system_cost",
                    "project.number_of_devices",
                    'project.electrical_network_efficiency',
                    "project.electrical_economics_data",
                    "project.moorings_foundations_economics_data",
                    "project.installation_economics_data",
                    "project.opex_per_year",
                    "project.energy_per_year",
                    "project.capex_oandm",
                    'project.lifetime',
                    "project.discount_rate",
                    "project.externalities_capex",
                    "project.externalities_opex",
                    'project.electrical_cost_estimate',
                    'project.moorings_cost_estimate',
                    'project.installation_cost_estimate',
                    'project.opex_estimate',
                    'project.annual_repair_cost_estimate',
                    'project.annual_array_mttf_estimate',
                    "project.annual_energy",
                    'project.estimate_energy_record'
                    ]
               
        return optional
        
    @classmethod 
    def declare_id_map(self):
        
        '''Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.
        
        Returns:
          dict: Mapping of local to data description variable identifiers 
        
        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example::
          
              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }
        
        '''
                  
        id_map = {'device_cost': 'device.system_cost',
                  'annual_energy': 'project.annual_energy',
                  'n_devices': 'project.number_of_devices',
                  'discount_rate': 'project.discount_rate',
                  'electrical_bom': 'project.electrical_economics_data',
                  'moorings_bom':
                      "project.moorings_foundations_economics_data",
                  "installation_bom": "project.installation_economics_data",
                  "capex_oandm": "project.capex_oandm",
                  "opex_per_year": "project.opex_per_year",
                  "energy_per_year": "project.energy_per_year",
                  'network_efficiency':
                      'project.electrical_network_efficiency',
                  "lifetime": 'project.lifetime',
                  
                  "electrical_estimate": 'project.electrical_cost_estimate',
                  "moorings_estimate": 'project.moorings_cost_estimate',
                  "install_estimate": 'project.installation_cost_estimate',
                  "opex_estimate": 'project.opex_estimate',
                  "annual_repair_cost_estimate":
                      'project.annual_repair_cost_estimate',
                  "annual_array_mttf_estimate":
                      'project.annual_array_mttf_estimate',
                  "estimate_energy_record": 'project.estimate_energy_record',
                  
                  "economics_metrics": "project.economics_metrics",
                  "lcoe_mean": "project.lcoe_mean",
                  "lcoe_mode": "project.lcoe_mode",
                  "lcoe_lower": "project.lcoe_interval_lower",
                  "lcoe_upper": "project.lcoe_interval_upper",
                  "capex_lcoe_mean": "project.capex_lcoe_mean",
                  "capex_lcoe_mode": "project.capex_lcoe_mode",
                  "capex_lcoe_lower": "project.capex_lcoe_interval_lower",
                  "capex_lcoe_upper": "project.capex_lcoe_interval_upper",
                  "opex_lcoe_mean": "project.opex_lcoe_mean",
                  "opex_lcoe_mode": "project.opex_lcoe_mode",
                  "opex_lcoe_lower": "project.opex_lcoe_interval_lower",
                  "opex_lcoe_upper": "project.opex_lcoe_interval_upper",
                  "opex_mean": "project.opex_mean",
                  "opex_mode": "project.opex_mode",
                  "opex_lower": "project.opex_interval_lower",
                  "opex_upper": "project.opex_interval_upper",
                  "discounted_opex_mean": "project.discounted_opex_mean",
                  "discounted_opex_mode": "project.discounted_opex_mode",
                  "discounted_opex_lower":
                      "project.discounted_opex_interval_lower",
                  "discounted_opex_upper":
                      "project.discounted_opex_interval_upper",
                  "exported_energy_mean": "project.exported_energy_mean",
                  "exported_energy_mode": "project.exported_energy_mode",
                  "exported_energy_lower":
                      "project.exported_energy_interval_lower",
                  "exported_energy_upper":
                      "project.exported_energy_interval_upper",
                  "discounted_energy_mean": "project.discounted_energy_mean",
                  "discounted_energy_mode": "project.discounted_energy_mode",
                  "discounted_energy_lower":
                      "project.discounted_energy_interval_lower",
                  "discounted_energy_upper":
                      "project.discounted_energy_interval_upper",
                  "capex_total": "project.capex_total",
                  "discounted_capex": "project.discounted_capex",
                  "cost_breakdown": "project.cost_breakdown",
                  'capex_breakdown': "project.capex_breakdown",
                  "capex_lcoe_breakdown": "project.capex_lcoe_breakdown",
                  'opex_breakdown': "project.opex_breakdown",
                  "opex_lcoe_breakdown": "project.opex_lcoe_breakdown",
                  "lcoe_pdf": "project.lcoe_pdf",
                  "externalities_capex": "project.externalities_capex",
                  "externalities_opex": "project.externalities_opex"
                  }
                  
        return id_map
                 
    def connect(self, debug_entry=False):
        
        '''The connect method is used to execute the external program and 
        populate the interface data store with values.
        
        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value
        
        '''
        
        bom_cols = ['phase', 'quantity', 'unitary_cost', 'project_year']
        
        # CAPEX Dataframes
        device_bom = pd.DataFrame(columns=bom_cols)
        electrical_bom = pd.DataFrame(columns=bom_cols)
        moorings_bom = pd.DataFrame(columns=bom_cols)
        installation_bom = pd.DataFrame(columns=bom_cols)
        capex_oandm_bom = pd.DataFrame(columns=bom_cols)
        externalities_bom = pd.DataFrame(columns=bom_cols)
        
        opex_bom = pd.DataFrame()
        energy_record = pd.DataFrame()
                    
        # Prepare costs
        if (self.data.n_devices is not None and
            self.data.device_cost is not None):
            
            quantities = [self.data.n_devices]
            costs = [self.data.device_cost]
            years = [0]
            
            device_bom = make_phase_bom(quantities,
                                        costs,
                                        years,
                                        "Devices")
        
        if self.data.electrical_bom is not None:
            
            electrical_bom = self.data.electrical_bom.drop("Key Identifier",
                                                           axis=1)
            
            name_map = {"Quantity": 'quantity',
                        "Cost": 'unitary_cost',
                        "Year": 'project_year'}
                    
            electrical_bom = electrical_bom.rename(columns=name_map)
            electrical_bom["phase"] = "Electrical Sub-Systems"
            
        elif self.data.electrical_estimate is not None:
                        
            electrical_bom = estimate_cost_per_power(
                                            1,
                                            self.data.electrical_estimate,
                                            "Electrical Sub-Systems")
            
        if self.data.moorings_bom is not None:
            
            moorings_bom = self.data.moorings_bom.drop("Key Identifier",
                                                       axis=1)
            
            name_map = {"Quantity": 'quantity',
                        "Cost": 'unitary_cost',
                        "Year": 'project_year'}
                        
            moorings_bom = moorings_bom.rename(columns=name_map)
            moorings_bom["phase"] = "Mooring and Foundations"
            
        elif self.data.moorings_estimate is not None:
                        
            moorings_bom = estimate_cost_per_power(
                                            1,
                                            self.data.moorings_estimate,
                                            "Mooring and Foundations")         
            
        if self.data.installation_bom is not None:
                    
            installation_bom = self.data.installation_bom.drop(
                                                            "Key Identifier",
                                                            axis=1)
            
            name_map = {"Quantity": 'quantity',
                        "Cost": 'unitary_cost',
                        "Year": 'project_year'}
                        
            installation_bom = installation_bom.rename(columns=name_map)
            installation_bom["phase"] = "Installation"
            
        elif self.data.install_estimate is not None:
                        
            installation_bom = estimate_cost_per_power(
                                            1,
                                            self.data.install_estimate,
                                            "Installation")
        
        if self.data.capex_oandm is not None:
            
            quantities = [1]
            costs = [self.data.capex_oandm]
            years = [0]
            
            capex_oandm_bom = make_phase_bom(quantities,
                                             costs,
                                             years,
                                             "Condition Monitoring")
            
        if self.data.externalities_capex is not None:
            
            quantities = [1]
            costs = [self.data.externalities_capex]
            years = [0]
            
            capex_oandm_bom = make_phase_bom(quantities,
                                             costs,
                                             years,
                                             "Externalities")
            
        # Combine the capex dataframes
        capex_bom = pd.concat([device_bom,
                               electrical_bom,
                               moorings_bom,
                               installation_bom,
                               capex_oandm_bom,
                               externalities_bom],
                               ignore_index=True)
            
        if self.data.opex_per_year is not None:
            
            opex_bom = self.data.opex_per_year.copy()
            opex_bom.index.name = 'project_year'
            opex_bom = opex_bom.reset_index()
            
        elif (self.data.lifetime is not None and
              (self.data.opex_estimate is not None or
               (self.data.annual_repair_cost_estimate is not None and
                self.data.annual_array_mttf_estimate is not None))):
            
            opex_bom = estimate_opex(self.data.lifetime,
                                     1,
                                     self.data.opex_estimate,
                                     self.data.annual_repair_cost_estimate,
                                     self.data.annual_array_mttf_estimate)
            
        # Add OPEX externalities
        if not opex_bom.empty and self.data.externalities_opex is not None:
        
            opex_bom = opex_bom.set_index('project_year')
            opex_bom += self.data.externalities_opex
            opex_bom = opex_bom.reset_index()
            
        # Prepare energy
        if self.data.network_efficiency is not None:
            net_coeff = self.data.network_efficiency  * 1e3
        else:
            net_coeff = 1e3
        
        if self.data.energy_per_year is not None:

            energy_record = self.data.energy_per_year.copy()
            energy_record = energy_record * net_coeff
            energy_record.index.name = 'project_year'
            energy_record = energy_record.reset_index()
                        
        elif (self.data.estimate_energy_record and 
              self.data.lifetime is not None and
              self.data.annual_energy is not None):
            
            energy_record = estimate_energy(self.data.lifetime,
                                            self.data.annual_energy,
                                            net_coeff)
            
        if debug_entry: return
        
        result = main(capex_bom,
                      opex_bom,
                      energy_record,
                      self.data.discount_rate)        

        self.data.capex_total = result["CAPEX"]
        self.data.discounted_capex = result["Discounted CAPEX"]
        self.data.capex_breakdown = result["CAPEX breakdown"]
        
        # Build metrics table if possible
        n_rows = None
        
        if not opex_bom.empty:
            n_rows = len(opex_bom.columns) - 1
        elif not energy_record.empty:
            n_rows = len(energy_record.columns) - 1
        else:
            return
                    
        table_cols = ["LCOE",
                      "LCOE CAPEX",
                      "LCOE OPEX",
                      "OPEX",
                      "Discounted OPEX",
                      "Energy",
                      "Discounted Energy"]
            
        metrics_dict = {}
            
        for col_name in table_cols:
                        
            if result[col_name] is not None:
                values = result[col_name].values
                if "Energy" in col_name: values /= 1e3
            else:
                values = [None] * n_rows
            
            metrics_dict[col_name] = values

        metrics_table = pd.DataFrame(metrics_dict)
        
        self.data.economics_metrics = metrics_table
        
        # Do stats on the metrics
        args_table = {"LCOE": "lcoe",
                      "LCOE CAPEX": "capex_lcoe",
                      "LCOE OPEX": "opex_lcoe",
                      "OPEX": "opex",
                      "Discounted OPEX": "discounted_opex",
                      "Energy": "exported_energy",
                      "Discounted Energy": "discounted_energy"}
        
        for key, arg_root in args_table.iteritems():
                        
            if metrics_table[key].isnull().any(): continue
        
            data = metrics_table[key].values
            
            mean = None
            mode = None
            lower = None
            upper = None
            
            # Catch one or two data points
            if len(data) == 1:
                
                mean = data[0]
                mode = data[0]
                
            elif len(data) == 2:
                
                mean = data.mean()
                
            else:
                
                try:
            
                    distribution = EstimatedDistribution(data)
                    mean = distribution.mean()
                    mode = distribution.mode()
                    
                    intervals = distribution.confidence_interval(95)
                    lower = intervals[0]
                    upper = intervals[1]
                    
                except np.linalg.LinAlgError:
                    
                    mean = data.mean()
            
            arg_mean = "{}_mean".format(arg_root)
            arg_mode = "{}_mode".format(arg_root)
            arg_lower = "{}_lower".format(arg_root)
            arg_upper = "{}_upper".format(arg_root)
            
            self.data[arg_mean] = mean
            self.data[arg_mode] = mode                        
            self.data[arg_lower] = lower
            self.data[arg_upper] = upper
            
        # CAPEX vs OPEX Breakdown and OPEX Breakdown if externalities
        if self.data.opex_mode is not None:
                        
            breakdown = {"CAPEX": result["CAPEX"],
                         "OPEX": self.data.opex_mode}
            
            self.data.cost_breakdown = breakdown
                        
            if self.data.externalities_opex is not None:
                
                total_external = self.data.externalities_opex * len(opex_bom)
                total_maintenance = self.data.opex_mode - total_external
                
                self.data.opex_breakdown = {"Maintenance": total_maintenance,
                                            "Externalities": total_external}
                
        # LCOE Breakdowns
        discounted_energy_mode = self.data.discounted_energy_mode
        discounted_opex_mode = self.data.discounted_opex_mode
        
        if discounted_energy_mode is not None:
            
            if self.data.capex_breakdown is not None:
        
                capex_lcoe_breakdown = {}
                
                for k, v in self.data.capex_breakdown.iteritems():
                    
                    capex_lcoe_breakdown[k] = round(
                                            v / discounted_energy_mode / 10,
                                            2)
                    
                self.data.capex_lcoe_breakdown = capex_lcoe_breakdown
            
            if (discounted_opex_mode is not None and
                self.data.externalities_opex is not None):
                                
                years = range(1, len(opex_bom) + 1)
                
                discounted_externals = [self.data.externalities_opex /
                                       (1 + self.data.discount_rate) ** i
                                                               for i in years]
                
                discounted_external = np.array(discounted_externals).sum()
                discounted_maintenance = discounted_opex_mode - \
                                                        discounted_external
                
                lcoe_maintenance = round(
                        discounted_maintenance / discounted_energy_mode / 10,
                        2)
                lcoe_external = round(
                        discounted_external / discounted_energy_mode / 10,
                        2)
                    
                self.data.opex_lcoe_breakdown = {
                                            "Maintenance": lcoe_maintenance,
                                            "Externalities": lcoe_external}

        # LCOE distribution
        if (metrics_table["LCOE"].isnull().any() or
            len(metrics_table["LCOE"])) < 3: return
        
        data = metrics_table["LCOE"].values
        
        try:
            distribution = EstimatedDistribution(data)
        except np.linalg.LinAlgError:
            return
        
        dist_min = data.min()
        dist_max = data.max()
        dist_stop = (dist_max - dist_min) / 2.
        
        while (distribution.pdf(dist_min)[0] > 1e-3 and
               dist_min > data.min() - dist_stop): dist_min -= 0.01
            
        while (distribution.pdf(dist_max)[0] > 1e-3 and
               dist_max < data.max() + dist_stop): dist_max += 0.01
        
        x = np.linspace(dist_min, dist_max, 500)
        probabilities = distribution.pdf(x)
        
        self.data.lcoe_pdf = np.array((x, probabilities)).T

        return
