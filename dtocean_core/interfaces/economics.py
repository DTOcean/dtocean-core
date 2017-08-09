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

import pandas as pd

from dtocean_economics import main
from dtocean_economics.preprocessing import (estimate_cost_per_power,
                                             estimate_energy,
                                             estimate_opex,
                                             make_phase_bom)

from . import ThemeInterface


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

        input_list  =  ["project.discount_rate",
                        "device.system_cost",
                        "project.number_of_devices",
                        "project.electrical_economics_data",
                        "project.moorings_foundations_economics_data",
                        "project.installation_economics_data",
                        "project.capex_oandm",
                        "project.opex_per_year",
                        "project.energy_per_year",
                        'project.electrical_network_efficiency',
                        'project.lifetime',
                        "device.power_rating",
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
        
        output_list = ["project.lcoe",
                       "project.capex_lcoe",
                       "project.opex_lcoe",
                       "project.cost_breakdown",
                       "project.capex_total",
                       "project.discounted_capex",
                       "project.capex_breakdown",
                       "project.opex_total",
                       "project.discounted_opex",
                       "project.discounted_energy"
                       ]
        
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
        
        optional = ["device.power_rating",
                    "device.system_cost",
                    "project.number_of_devices",
                    "project.annual_energy",
                    'project.electrical_network_efficiency',
                    "project.electrical_economics_data",
                    "project.moorings_foundations_economics_data",
                    "project.installation_economics_data",
                    "project.opex_per_year",
                    "project.energy_per_year",
                    "project.capex_oandm",
                    "project.discount_rate",
                    'project.lifetime',
                    'project.electrical_cost_estimate',
                    'project.moorings_cost_estimate',
                    'project.installation_cost_estimate',
                    'project.opex_estimate',
                    'project.annual_repair_cost_estimate',
                    'project.annual_array_mttf_estimate',
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
                  
        id_map = {
                  'device_cost': 'device.system_cost',
                  "power_rating": "device.power_rating",
                  'annual_energy': 'project.annual_energy',
                  'n_devices': 'project.number_of_devices',
                  "cost_breakdown": "project.cost_breakdown",
                  'capex_breakdown': 'project.capex_breakdown',
                  'LCOE_CAPEX': 'project.capex_lcoe',
                  'capex_total': 'project.capex_total',
                  'discount_rate': 'project.discount_rate',
                  'discounted_energy': 'project.discounted_energy',
                  'LCOE': 'project.lcoe',
                  'electrical_bom': 'project.electrical_economics_data',
                  'moorings_bom': "project.moorings_foundations_economics_data",
                  "installation_bom": "project.installation_economics_data",
                  'discounted_capex': "project.discounted_capex",
                  'discounted_opex': "project.discounted_opex",
                  'LCOE_OPEX': "project.opex_lcoe",
                  'opex_total': "project.opex_total",
                  "lifetime": 'project.lifetime',
                  "electrical_estimate": 'project.electrical_cost_estimate',
                  "moorings_estimate": 'project.moorings_cost_estimate',
                  "install_estimate": 'project.installation_cost_estimate',
                  "opex_estimate": 'project.opex_estimate',
                  "annual_repair_cost_estimate":
                      'project.annual_repair_cost_estimate',
                  "annual_array_mttf_estimate":
                      'project.annual_array_mttf_estimate',
                  'network_efficiency': 'project.electrical_network_efficiency',
                  "opex_per_year": "project.opex_per_year",
                  "energy_per_year": "project.energy_per_year",
                  "capex_oandm": "project.capex_oandm",
                  "estimate_energy_record": 'project.estimate_energy_record'
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
        
        device_bom = pd.DataFrame(columns=bom_cols)
        electrical_bom = pd.DataFrame(columns=bom_cols)
        moorings_bom = pd.DataFrame(columns=bom_cols)
        installation_bom = pd.DataFrame(columns=bom_cols)
        capex_oandm_bom = pd.DataFrame(columns=bom_cols)
        
        opex_bom = pd.DataFrame(columns=bom_cols)
        energy_record = pd.DataFrame(columns=["energy", 'project_year'])
        
        # Shortcut for total power
        total_rated_power = None
        
        if (self.data.n_devices is not None and
            self.data.power_rating is not None):
            
            total_rated_power = self.data.n_devices * self.data.power_rating
                    
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
            
        elif (total_rated_power is not None and
              self.data.electrical_estimate is not None):
                        
            electrical_bom = estimate_cost_per_power(
                                            total_rated_power,
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
            
        elif (total_rated_power is not None and
              self.data.moorings_estimate is not None):
                        
            moorings_bom = estimate_cost_per_power(
                                            total_rated_power,
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
            
        elif (total_rated_power is not None and
              self.data.install_estimate is not None):
                        
            installation_bom = estimate_cost_per_power(
                                            total_rated_power,
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
            
        # Combine the capex dataframes
        capex_bom = pd.concat([device_bom,
                               electrical_bom,
                               moorings_bom,
                               installation_bom,
                               capex_oandm_bom],
                              ignore_index=True)
            
        if self.data.opex_per_year is not None:
            
            n_years = len(self.data.opex_per_year)
            costs = self.data.opex_per_year["Cost"].values
            years = self.data.opex_per_year.index.values
            
            opex_cost_raw = {'unitary_cost': costs,
                             'quantity': [1.] * n_years,
                             'project_year': years}
                             
            opex_bom = pd.DataFrame(opex_cost_raw)
            
        elif (self.data.lifetime is not None and
              ((total_rated_power is not None and 
                self.data.opex_estimate is not None) or
               (self.data.annual_repair_cost_estimate is not None and
                self.data.annual_array_mttf_estimate is not None))):
            
            opex_bom = estimate_opex(self.data.lifetime,
                                     total_rated_power,
                                     self.data.opex_estimate,
                                     self.data.annual_repair_cost_estimate,
                                     self.data.annual_array_mttf_estimate)
            
        # Prepare energy
        if self.data.network_efficiency is not None:
            net_coeff = self.data.network_efficiency  * 1e3
        else:
            net_coeff = 1e3
        
        if self.data.energy_per_year is not None:
            
            energy_kws = self.data.energy_per_year["Energy"].values * \
                                                                    net_coeff
            years = self.data.energy_per_year.index.values
            
            energy_raw = {'project_year': years,
                          'energy': energy_kws}
            energy_record = pd.DataFrame(energy_raw)
            
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

        # CAPEX
        self.data.capex_total = result["CAPEX"]
        self.data.discounted_capex = result["Discounted CAPEX"]
        self.data.capex_breakdown = result["CAPEX breakdown"]
            
        # OPEX
        self.data.opex_total = result["OPEX"]
        self.data.discounted_opex = result["Discounted OPEX"]
            
        # CAPEX vs OPEX Breakdown
        self.data.cost_breakdown = result["Total cost breakdown"]
                              
        # Energy
        self.data.discounted_energy = result["Discounted Energy"]
        
        # LCOE
        self.data.LCOE_CAPEX = result["LCOE CAPEX"]
        self.data.LCOE_OPEX = result["LCOE OPEX"]
        self.data.LCOE = result["LCOE"]

        return
