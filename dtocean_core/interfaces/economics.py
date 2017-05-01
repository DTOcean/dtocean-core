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

from dtocean_economics.main import (get_discounted_cost,
                                    get_discounted_energy,
                                    lcoe)

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
                        'project.lifetime',
                        "project.electrical_economics_data",
                        "project.moorings_foundations_economics_data",
                        "project.installation_economics_data",
                        "project.capex_oandm",
                        "project.opex_per_year",
                        "project.energy_per_year",
                        'project.electrical_network_efficiency',
                        "project.annual_energy",
                        "project.number_of_devices",
                        "device.system_cost",
                        "device.power_rating",
                        'project.electrical_cost_estimate',
                        'project.moorings_cost_estimate',
                        'project.installation_cost_estimate',
                        'project.opex_estimate',
                        'project.annual_repair_cost_estimate',
                        'project.annual_array_mttf_estimate',
                        'project.electrical_network_efficiency'
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
                    'project.annual_array_mttf_estimate'
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
                  'year_energy': 'project.annual_energy',
                  'n_devices': 'project.number_of_devices',
                  "cost_breakdown": "project.cost_breakdown",
                  'capex_breakdown': 'project.capex_breakdown',
                  'LCOE_CAPEX': 'project.capex_lcoe',
                  'capex_total': 'project.capex_total',
                  'discount_rate': 'project.discount_rate',
                  'discounted_energy': 'project.discounted_energy',
                  'LCOE': 'project.lcoe',
                  'electrical_costs': 'project.electrical_economics_data',
                  'moorings_costs': "project.moorings_foundations_economics_data",
                  "installation_costs": "project.installation_economics_data",
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
                  "capex_oandm": "project.capex_oandm"
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

        # Discount rate (default to zero)
        if self.data.discount_rate is None:
            discount_rate = 0.0
        else:
            discount_rate = self.data.discount_rate
            
        # Total rated power
        total_rated_power = None
        
        if (self.data.n_devices is not None and
            self.data.power_rating is not None):
            
            total_rated_power = self.data.n_devices * self.data.power_rating
        
        ## COSTS
        
        # Collect extra capex costs
        capex_unit_cost = []
        capex_quantity = []
        capex_year = []     
        cap_costs_breakdown = {}
        
        if (self.data.device_cost is not None and
            self.data.n_devices is not None):
            
            capex_unit_cost.append(self.data.device_cost)
            capex_quantity.append(self.data.n_devices)
            capex_year.append(0)
            
            cap_costs_breakdown["Devices"] = self.data.device_cost * \
                                                        self.data.n_devices
            
        # Build capex cost dataframe
        capex_cost_raw = {'unitary_cost': capex_unit_cost,
                          'quantity': capex_quantity,
                          'project_year': capex_year}
            
        capex_costs = pd.DataFrame(capex_cost_raw)
        
        # Add electrical costs if available
        if self.data.electrical_costs is not None:
            
            electrical_costs = self.data.electrical_costs
            electrical_costs = electrical_costs.drop("Key Identifier", axis=1)
            
            name_map = {"Quantity": 'quantity',
                        "Cost": 'unitary_cost',
                        "Year": 'project_year'}
                        
            electrical_costs = electrical_costs.rename(columns=name_map)
            
            cap_costs_breakdown["Electrical Sub-Systems"] = (
                                    electrical_costs['unitary_cost'] * 
                                        electrical_costs['quantity']).sum()
                                
            capex_costs = pd.concat([capex_costs, electrical_costs])
            
        elif (total_rated_power is not None and
              self.data.electrical_estimate is not None):
            
            cost = total_rated_power * self.data.electrical_estimate
            
            raw_costs = {'quantity': [1],
                         'unitary_cost': [cost],
                         'project_year': [0]}
                         
            electrical_costs = pd.DataFrame(raw_costs)
            
            cap_costs_breakdown["Electrical Sub-Systems"] = cost
                                
            capex_costs = pd.concat([capex_costs, electrical_costs])
            
        # Add moorings costs if available
        if self.data.moorings_costs is not None:
            
            moorings_costs = self.data.moorings_costs
            moorings_costs = moorings_costs.drop("Key Identifier", axis=1)
            
            name_map = {"Quantity": 'quantity',
                        "Cost": 'unitary_cost',
                        "Year": 'project_year'}
                        
            moorings_costs = moorings_costs.rename(columns=name_map)

            cap_costs_breakdown["Mooring and Foundations"] = (
                                        moorings_costs['unitary_cost'] *
                                            moorings_costs['quantity']).sum()
                                
            capex_costs = pd.concat([capex_costs, moorings_costs])
            
        elif (total_rated_power is not None and
              self.data.moorings_estimate is not None):
            
            cost = total_rated_power * self.data.moorings_estimate
            
            raw_costs = {'quantity': [1],
                         'unitary_cost': [cost],
                         'project_year': [0]}
                         
            moorings_costs = pd.DataFrame(raw_costs)
            
            cap_costs_breakdown["Mooring and Foundations"] = cost
                                
            capex_costs = pd.concat([capex_costs, moorings_costs])
            
        # Add installation costs if available
        if self.data.installation_costs is not None:
            
            install_costs = self.data.installation_costs
            install_costs = install_costs.drop("Key Identifier", axis=1)
            
            name_map = {"Quantity": 'quantity',
                        "Cost": 'unitary_cost',
                        "Year": 'project_year'}
                        
            install_costs = install_costs.rename(columns=name_map)

            cap_costs_breakdown["Installation"] = (
                                        install_costs['unitary_cost'] *
                                            install_costs['quantity']).sum()
                                
            capex_costs = pd.concat([capex_costs, install_costs])
            
        elif (total_rated_power is not None and
              self.data.install_estimate is not None):
            
            cost = total_rated_power * self.data.install_estimate
            
            raw_costs = {'quantity': [1],
                         'unitary_cost': [cost],
                         'project_year': [0]}
                         
            install_costs = pd.DataFrame(raw_costs)
            
            cap_costs_breakdown["Installation"] = cost
                                
            capex_costs = pd.concat([capex_costs, install_costs])
            
        # And O&M Condition Monitering Capex
        if self.data.capex_oandm is not None:
            
            cost = self.data.capex_oandm
                        
            raw_costs = {'quantity': [1],
                         'unitary_cost': [cost],
                         'project_year': [0]}
                         
            oandm_costs = pd.DataFrame(raw_costs)
            
            cap_costs_breakdown["Condition Monitering"] = cost
                                
            capex_costs = pd.concat([capex_costs, oandm_costs]) 
            
        # Capex results
        if not capex_costs.empty:
            
            self.data.capex_total = (capex_costs['unitary_cost'] *
                                                capex_costs['quantity']).sum()
            
            self.data.discounted_capex = get_discounted_cost(capex_costs,
                                                             discount_rate)
                                                             
            # Record cost breakdown
            self.data.capex_breakdown = cap_costs_breakdown
            
        # Collect opex costs
        opex_costs = None

        if self.data.opex_per_year is not None:
            
            n_years = len(self.data.opex_per_year)
            costs = self.data.opex_per_year["Cost"].values
            
            opex_cost_raw = {'unitary_cost': costs,
                             'quantity': [1.] * n_years,
                             'project_year': range(n_years)}
                             
            opex_costs = pd.DataFrame(opex_cost_raw)
        
        # Build up estimates        
        elif self.data.lifetime is not None:
            
            annual_costs = 0.
            
            if (total_rated_power is not None and
                self.data.opex_estimate is not None):
                
                annual_costs += total_rated_power * self.data.opex_estimate
                
            if (self.data.annual_repair_cost_estimate is not None and
                self.data.annual_array_mttf_estimate is not None):
                
                year_mttf = self.data.annual_array_mttf_estimate / \
                                                                24. / 365.25
                failure_cost = self.data.annual_repair_cost_estimate / \
                                                                year_mttf
                
                annual_costs += failure_cost
                
            opex_unit_cost = [0.] + [annual_costs] * self.data.lifetime
            opex_quantity = [1] * (self.data.lifetime + 1)
            opex_year = range(self.data.lifetime + 1)
            
            opex_cost_raw = {'unitary_cost': opex_unit_cost,
                             'quantity': opex_quantity,
                             'project_year': opex_year}
                             
            opex_costs = pd.DataFrame(opex_cost_raw)
        
        # Opex results
        if opex_costs is not None:
            
            self.data.opex_total = (opex_costs['unitary_cost'] *
                                                opex_costs['quantity']).sum()
            
            self.data.discounted_opex = get_discounted_cost(opex_costs,
                                                            discount_rate)
            
        # CAPEX vs OPEX Breakdown
        if (self.data.capex_total is not None and 
            self.data.opex_total is not None):
            
            self.data.cost_breakdown = {"CAPEX": self.data.capex_total,
                                        "OPEX": self.data.opex_total}
                              
                              

        ## ENERGY
        
        # Create energy table
        energy_data = None

        # If no O&M results are given then use the basic design energy
        if (self.data.energy_per_year is not None and
            self.data.opex_per_year is not None):
            
            if self.data.network_efficiency is not None:
                net_coeff = self.data.network_efficiency * 1e3
            else:
                net_coeff = 1e3
            
            n_years = len(self.data.energy_per_year)
            energy_kws = self.data.energy_per_year["Energy"].values * net_coeff
            
            energy_raw = {'project_year': range(n_years),
                          'energy': energy_kws}
            energy_data = pd.DataFrame(energy_raw)
            
        elif (self.data.year_energy is not None and
              (self.data.opex_per_year is not None or
               self.data.lifetime is not None)):
                
            if self.data.opex_per_year is not None:
                n_years = len(self.data.opex_per_year)
            elif self.data.lifetime is not None:
                n_years = self.data.lifetime
            
            if self.data.network_efficiency is not None:
                net_coeff = self.data.network_efficiency
            else:
                net_coeff = 1.
                
            energy_kw = [0] + [self.data.year_energy * 1e3 * net_coeff] * \
                                                self.data.lifetime
            energy_year = range(self.data.lifetime + 1)
        
            energy_raw = {'project_year': energy_year,
                          'energy': energy_kw}
            energy_data = pd.DataFrame(energy_raw)
        
        # Calculate the discounted energy
        if energy_data is not None:        
        
            self.data.discounted_energy = get_discounted_energy(energy_data,
                                                                discount_rate)
                                                            
        if (self.data.discounted_capex is not None and
            self.data.discounted_energy is not None):
            
            self.data.LCOE_CAPEX = lcoe(self.data.discounted_capex,
                                        self.data.discounted_energy)
                                               
        if (self.data.discounted_opex is not None and
            self.data.discounted_energy is not None):
            
            self.data.LCOE_OPEX = lcoe(self.data.discounted_opex,
                                       self.data.discounted_energy)
        
        # Calculate final lcoe
        total_lcoe = 0.        
        
        if self.data.LCOE_CAPEX is not None:
            total_lcoe += self.data.LCOE_CAPEX
            
        if self.data.LCOE_OPEX is not None:
            total_lcoe += self.data.LCOE_OPEX
            
        if total_lcoe > 0: self.data.LCOE = total_lcoe

        return
