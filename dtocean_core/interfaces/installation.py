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
This module contains the package interface to the dtocean installation module.

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. module:: installation
   :platform: Windows
   :synopsis: Aneris interface for dtocean_core package
   
.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
                  Vincenzo Nava <vincenzo.nava@tecnalia.com>
                  Adam Collin <a.collin@ed.ac.uk>
"""

# Set up logging
import logging

module_logger = logging.getLogger(__name__)

import pickle

import numpy as np
import pandas as pd

from dtocean_installation.main import installation_main
from dtocean_installation.configure import get_operations_template
from dtocean_logistics.phases import EquipmentType

from aneris.boundary.interface import MaskVariable

from . import ModuleInterface
from ..utils.installation import (installation_phase_cost_output,
                                  installation_phase_time_result,
                                  find_marker_key_mf,
                                  installation_phase_date_result,
                                  installation_phase_date_result_timeseries)

from ..utils.install_electrical import (set_collection_points,
                                        set_cables,
                                        set_connectors,
                                        get_umbilical_terminations,
                                        set_cable_cp_references)


class InstallationInterface(ModuleInterface):
    
    '''Interface to the installation module
    
      Attributes:
        id_map (dict): Mapping of internal variable names to local variable
          names.
          
    '''
        
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Installation"
        
    @classmethod         
    def declare_weight(cls):
        
        return 4

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

        input_list  =  ["component.rov",
                        "component.divers",
                        "component.cable_burial",
                        "component.excavating",
                        "component.mattress_installation",
                        "component.rock_bags_installation",
                        "component.split_pipes_installation",
                        "component.hammer",
                        "component.drilling_rigs",
                        "component.vibro_driver",
                        "component.vessels",
                        "component.ports",
                        "component.port_locations",
                        "bathymetry.layers",
                        "corridor.layers",
                        "device.subsystem_installation",
                        "project.electrical_network",
                        "project.electrical_component_data",
                        "project.cable_routes",
                        "project.substation_props",
                        
                        MaskVariable("project.umbilical_cable_data",
                                      'device.system_type',
                                      ['Tidal Floating', 'Wave Floating']),
                        MaskVariable("project.umbilical_seabed_connection",
                                      'device.system_type',
                                      ['Tidal Floating', 'Wave Floating']),
                        
                        "project.moorings_foundations_network",
                        "project.foundations_component_data",
                        "project.foundations_soil_data",
                        
                        MaskVariable("project.moorings_line_data",
                                      'device.system_type',
                                      ['Tidal Floating', 'Wave Floating']),
                        MaskVariable("project.moorings_component_data",
                                      'device.system_type',
                                      ['Tidal Floating', 'Wave Floating']),
                                     
                        "project.layout",
                        "component.equipment_penetration_rates",
                        "component.installation_soil_compatibility",
                        "project.surface_laying_rate",
                        "project.split_pipe_laying_rate",
                        "project.loading_rate",
                        "project.grout_rate",
                        "project.fuel_cost_rate",
                        "project.port_percentage_cost",
                        "project.commissioning_time",
                        "project.cost_contingency",
                        "project.lease_area_entry_point",
                        "project.port_safety_factors",
                        "project.vessel_safety_factors",
                        "project.rov_safety_factors",
                        "project.divers_safety_factors",
                        "project.hammer_safety_factors",
                        "project.vibro_driver_safety_factors",
                        "project.cable_burial_safety_factors",
                        "project.split_pipe_safety_factors",
                        "device.system_type",
                        "device.system_length",
                        "device.system_width",
                        "device.system_height",
                        "device.system_mass",
                        "device.assembly_duration",
                        "device.load_out_method",
                        "device.transportation_method",
                        "device.bollard_pull",
                        "device.connect_duration",
                        "device.disconnect_duration",
                        "project.start_date",
                        "farm.wave_series_installation",
                        "farm.tidal_series_installation",
                        "farm.wind_series_installation",
                        "project.landfall_contruction_technique",
                        "site.projection",
                        "component.dry_mate_connectors",
                        "component.dynamic_cable",
                        "component.static_cable",
                        "component.wet_mate_connectors",
                        "component.collection_points",
                        "component.transformers",
                        "device.control_subsystem_installation",
                        "device.two_stage_assembly",
                        "project.selected_installation_tool",
                        "options.skip_phase"
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
        
        output_list = ["project.installation_completion_date",
                       "project.commissioning_date",
                       "project.port",
                       "project.port_distance",
                       "project.installation_journeys",
                       "project.installation_vessel_average_size",
                       "project.device_phase_installation_costs",
                       "project.device_phase_installation_cost_breakdown",
                       "project.device_phase_cost_class_breakdown",
                       "project.device_phase_installation_times",
                       "project.device_phase_installation_time_breakdown",
                       "project.device_phase_time_class_breakdown",
                       "project.electrical_phase_installation_costs",
                       "project.electrical_phase_installation_cost_breakdown",
                       "project.electrical_phase_cost_class_breakdown",
                       "project.electrical_phase_installation_times",
                       "project.electrical_phase_installation_time_breakdown",
                       "project.electrical_phase_time_class_breakdown",
                       "project.mooring_phase_installation_costs",
                       "project.mooring_phase_installation_cost_breakdown",
                       "project.mooring_phase_cost_class_breakdown",
                       "project.mooring_phase_installation_times",
                       "project.mooring_phase_installation_time_breakdown",
                       "project.mooring_phase_time_class_breakdown",
                       "project.installation_phase_cost_breakdown",
                       "project.installation_cost_class_breakdown",
                       "project.total_installation_cost",
                       "project.installation_phase_time_breakdown",
                       "project.installation_time_class_breakdown",
                       "project.total_installation_time",
                       "project.installation_economics_data",
                       "project.install_support_structure_dates",
                       "project.install_devices_dates",
                       "project.install_dynamic_cable_dates",
                       "project.install_export_cable_dates",
                       "project.install_array_cable_dates",
                       "project.install_surface_piercing_substation_dates",
                       "project.install_subsea_collection_point_dates",
                       "project.install_cable_protection_dates",
                       "project.install_driven_piles_dates",
                       "project.install_direct_embedment_dates",
                       "project.install_gravity_based_dates",
                       "project.install_pile_anchor_dates",
                       "project.install_drag_embedment_dates",
                       "project.install_suction_embedment_dates",
                       "project.install_support_structure_prep_time",
                       "project.install_devices_prep_time",
                       "project.install_dynamic_cable_prep_time",
                       "project.install_export_cable_prep_time",
                       "project.install_array_cable_prep_time",
                       "project.install_surface_piercing_substation_prep_time",
                       "project.install_subsea_collection_point_prep_time",
                       "project.install_cable_protection_prep_time",
                       "project.install_driven_piles_prep_time",
                       "project.install_direct_embedment_prep_time",
                       "project.install_gravity_based_prep_time",
                       "project.install_pile_anchor_prep_time",
                       "project.install_drag_embedment_prep_time",
                       "project.install_suction_embedment_prep_time",
                       "project.installation_plan"
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
                
        optional = ["project.electrical_network",
                    "project.electrical_component_data",
                    "project.cable_routes",
                    "project.substation_props",
                    "project.umbilical_cable_data",
                    "project.umbilical_seabed_connection",
                    "project.moorings_foundations_network",
                    "project.moorings_foundations_network",
                    "project.foundations_component_data",
                    "project.foundations_soil_data",     
                    "project.moorings_line_data",
                    "project.moorings_component_data",
                    "component.dry_mate_connectors",
                    "component.dynamic_cable",
                    "component.static_cable",
                    "component.wet_mate_connectors",
                    "component.collection_points",
                    "component.transformers",
                    "corridor.layers",
                    "project.landfall_contruction_technique",
                    "device.bollard_pull",
                    "device.control_subsystem_installation",
                    "device.two_stage_assembly",
                    "options.skip_phase"
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
                  
        id_map = {"rov": "component.rov",
                  "divers": "component.divers",
                  "cable_burial": "component.cable_burial",
                  "excavating": "component.excavating",
                  "mattresses": "component.mattress_installation",
                  "rock_bags": "component.rock_bags_installation",
                  "split_pipes": "component.split_pipes_installation",
                  "hammer": "component.hammer",
                  "drilling_rigs": "component.drilling_rigs",
                  "vibro_driver": "component.vibro_driver",
                  "vessels": "component.vessels",
                  "ports": "component.ports",
                  "port_locations": "component.port_locations",
                  "site": "bathymetry.layers",
                  "export": "corridor.layers",
                  "sub_device": "device.subsystem_installation",
                  "control_system": "device.control_subsystem_installation",
                  "electrical_network": "project.electrical_network" ,
                  "electrical_components": "project.electrical_component_data",
                  "cable_routes": "project.cable_routes",
                  "substations": "project.substation_props",
                  "umbilicals": "project.umbilical_cable_data",
                  "umbilical_terminations":
                          "project.umbilical_seabed_connection",
                  "landfall": "project.landfall_contruction_technique",
                  "mf_network": "project.moorings_foundations_network",
                  "foundations_data": "project.foundations_component_data",
                  "foundation_soil_layers": "project.foundations_soil_data",
                  "line_summary_data": "project.moorings_line_data",
                  "line_component_data": "project.moorings_component_data",
                  "penetration_rates":
                          "component.equipment_penetration_rates",
                  "installation_soil_compatibility": 
                          "component.installation_soil_compatibility",
                  "surface_laying_rate": "project.surface_laying_rate",
                  "split_pipe_laying_rate":
                          "project.split_pipe_laying_rate",
                  "loading_rate": "project.loading_rate",
                  "grout_rate": "project.grout_rate",
                  "fuel_cost_rate": "project.fuel_cost_rate",
                  "port_cost": "project.port_percentage_cost",
                  "commission_time": "project.commissioning_time",
                  "cost_contingency": "project.cost_contingency",
                  "port_safety_factors": "project.port_safety_factors",
                  "vessel_safety_factors": "project.vessel_safety_factors",
                  "rov_safety_factors": "project.rov_safety_factors",
                  "divers_safety_factors": "project.divers_safety_factors",
                  "hammer_safety_factors": "project.hammer_safety_factors",
                  "vibro_driver_safety_factors":
                      "project.vibro_driver_safety_factors",
                  "cable_burial_safety_factors":
                      "project.cable_burial_safety_factors",
                  "split_pipe_safety_factors":
                      "project.split_pipe_safety_factors",
                  "entry_point": "project.lease_area_entry_point",
                  "layout": "project.layout",
                  "system_type": "device.system_type",
                  "system_length": "device.system_length",
                  "system_width": "device.system_width",
                  "system_height": "device.system_height",
                  "system_mass": "device.system_mass",
                  "assembly_duration": "device.assembly_duration",
                  "load_out_method": "device.load_out_method",
                  "transportation_method": "device.transportation_method",
                  "bollard_pull": "device.bollard_pull",
                  "connect_duration": "device.connect_duration",
                  "disconnect_duration": "device.disconnect_duration",
                  "project_start_date": "project.start_date",
                  "wave_series": "farm.wave_series_installation",
                  "tidal_series": "farm.tidal_series_installation",
                  "wind_series": "farm.wind_series_installation",
                  "lease_utm_zone": "site.projection", 
                  "end_date": "project.installation_completion_date",
                  "commissioning_date": "project.commissioning_date",
                  "port": "project.port",
                  "port_distance": "project.port_distance",
                  "journeys": "project.installation_journeys",
                  "vessel_average_size":
                          "project.installation_vessel_average_size",
                  "elec_db_dry_mate": "component.dry_mate_connectors",
                  "elec_db_dynamic_cable": "component.dynamic_cable",
                  "elec_db_static_cable": "component.static_cable",
                  "elec_db_wet_mate": "component.wet_mate_connectors",
                  "elec_db_switchgear": "component.switchgear",
                  "elec_db_transformers": "component.transformers",
                  "device_component_costs":
                      "project.device_phase_installation_costs",
                  "device_component_cost_breakdown":
                      "project.device_phase_installation_cost_breakdown",
                  "device_cost_class_breakdown":
                      "project.device_phase_cost_class_breakdown",
                  "device_component_times":
                      "project.device_phase_installation_times",
                  "device_component_time_breakdown":
                      "project.device_phase_installation_time_breakdown",
                  "device_time_class_breakdown":
                      "project.device_phase_time_class_breakdown",
                  "electrical_component_costs": 
                      "project.electrical_phase_installation_costs",
                  "electrical_component_cost_breakdown":
                      "project.electrical_phase_installation_cost_breakdown",
                  "electrical_cost_class_breakdown":
                      "project.electrical_phase_cost_class_breakdown",
                  "electrical_component_times":
                      "project.electrical_phase_installation_times",
                  "electrical_component_time_breakdown":
                      "project.electrical_phase_installation_time_breakdown",
                  "electrical_time_class_breakdown":
                      "project.electrical_phase_time_class_breakdown",
                  "mooring_component_costs": 
                      "project.mooring_phase_installation_costs",
                  "mooring_component_cost_breakdown":
                      "project.mooring_phase_installation_cost_breakdown",
                  "mooring_cost_class_breakdown":
                      "project.mooring_phase_cost_class_breakdown",
                  "mooring_component_times":
                      "project.mooring_phase_installation_times",
                  "mooring_component_time_breakdown":
                      "project.mooring_phase_installation_time_breakdown",
                  "mooring_time_class_breakdown":
                      "project.mooring_phase_time_class_breakdown",
                  "total_phase_costs":
                      "project.installation_phase_cost_breakdown",
                  "total_class_costs":
                       "project.installation_cost_class_breakdown",
                  "total_costs":
                       "project.total_installation_cost",
                  "total_phase_times":
                      "project.installation_phase_time_breakdown",
                  "total_class_times":
                       "project.installation_time_class_breakdown",
                  "total_times":
                       "project.total_installation_time",
                  "installation_bom": "project.installation_economics_data",
                  "cable_tool": "project.selected_installation_tool", 
                  "skip_phase": "options.skip_phase",
                  "install_support_structure_dates":
                      "project.install_support_structure_dates",
                  "install_devices_dates": "project.install_devices_dates",
                  "install_dynamic_cable_dates":
                      "project.install_dynamic_cable_dates",        
                  "install_export_cable_dates":
                      "project.install_export_cable_dates",               
                  "install_array_cable_dates":
                      "project.install_array_cable_dates",               
                  "install_surface_piercing_substation_dates":
                      "project.install_surface_piercing_substation_dates",
                  "install_subsea_collection_point_dates":
                      "project.install_subsea_collection_point_dates",               
                  "install_cable_protection_dates":
                      "project.install_cable_protection_dates",               
                  "install_driven_piles_dates":
                      "project.install_driven_piles_dates",               
                  "install_direct_embedment_dates":
                      "project.install_direct_embedment_dates",
                  "install_gravity_based_dates":
                      "project.install_gravity_based_dates",
                  "install_pile_anchor_dates":
                      "project.install_pile_anchor_dates",
                  "install_drag_embedment_dates":
                      "project.install_drag_embedment_dates",
                  "install_suction_embedment_dates":
                      "project.install_suction_embedment_dates",
                  "install_support_structure_prep_time":
                      "project.install_support_structure_prep_time",
                  "install_devices_prep_time": 
                      "project.install_devices_prep_time",
                  "install_dynamic_cable_prep_time":
                      "project.install_dynamic_cable_prep_time",
                  "install_export_cable_prep_time":
                      "project.install_export_cable_prep_time",
                  "install_array_cable_prep_time":
                      "project.install_array_cable_prep_time",
                  "install_surface_piercing_substation_prep_time":
                      "project.install_surface_piercing_substation_prep_time",
                  "install_subsea_collection_point_prep_time":
                      "project.install_subsea_collection_point_prep_time",
                  "install_cable_protection_prep_time":
                      "project.install_cable_protection_prep_time",
                  "install_driven_piles_prep_time":
                      "project.install_driven_piles_prep_time",
                  "install_direct_embedment_prep_time":
                      "project.install_direct_embedment_prep_time",
                  "install_gravity_based_prep_time":
                      "project.install_gravity_based_prep_time",
                  "install_pile_anchor_prep_time":
                      "project.install_pile_anchor_prep_time",
                  "install_drag_embedment_prep_time":
                      "project.install_drag_embedment_prep_time",
                  "install_suction_embedment_prep_time":
                      "project.install_suction_embedment_prep_time",
                  "two_stage_assembly": "device.two_stage_assembly",
                  "plan": "project.installation_plan"
                  } 

        return id_map

    def connect(self, debug_entry=False,
                      export_data=True):
        
        '''The connect method is used to execute the external program and 
        populate the interface data store with values.
        
        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value
        
        '''
        
        # check that proj4 string is correctly formatted
        if not all(x in self.data.lease_utm_zone for x in ['utm', 'zone']): 

            errStr = ("Site projection not correctly defined. Must contain " +
                      "both 'utm' and 'zone' keys")

            raise ValueError(errStr)

        else:

            # could not get re search to work so using crude method between
            # two strings
            utm_zone = self.data.lease_utm_zone           
            zone = \
                utm_zone[utm_zone.find("zone=")+5:\
                         utm_zone.find(" +", utm_zone.find("zone=")+1)]

            zone = zone + ' U' # prepare for module

        input_dict = self.get_input_dict(self.data,
                                         self.data.site,
                                         self.data.system_type,
                                         self.data.layout,
                                         self.data.electrical_network,
                                         self.data.mf_network,
                                         zone)

        ### M&F
        if self.data.mf_network is not None:
            
            # call the m&f functions from the tools
            foundations_data = self.data.foundations_data
            
            if foundations_data is None:
                
                errStr = ("Complete moorings and foundations data has not "
                          "been provided.")
                raise ValueError(errStr)
            
            network = self.data.mf_network['nodes']
            device_association = []

            for item, value in foundations_data.iterrows():

                marker = value['Marker']
                device_association.append(
                        find_marker_key_mf(network, marker, 'foundation'))

            # give foundations a label
            foundation_labels = ['foundation' + str(n).zfill(3)
                                 for n
                                 in range(len(device_association))]

            foundations_zone = [zone]*len(device_association)
            
            # add device_association and foundation_labels to dataframe
            foundations_data["Device"] = device_association
            foundations_data["Foundation"] = foundation_labels
            foundations_data["UTM Zone"] = foundations_zone

            foundations_data = foundations_data.drop('Depth', axis = 1)

            foundations_df = foundations_data

            name_map = {"Type": "type [-]",
                        "Sub-Type": "subtype [-]",
                        "UTM X": "x coord [m]",
                        "UTM Y": "y coord [m]",
                        "UTM Zone": "zone [-]",
                        "Length": "length [m]",
                        "Width": "width [m]",
                        "Height": "height [m]",
                        "Installation Depth": "installation depth [m]",
                        "Dry Mass": "dry mass [kg]",
                        "Grout Type": "grout type [-]",
                        "Grout Volume": "grout volume [m3]",
                        "Device": "devices [-]",
                        "Foundation": "foundations [-]"}

            foundations_df = foundations_df.rename(columns=name_map)

            # Map wp4 to wp5 
            if "floating" in self.data.system_type.lower():
                
                append_this = ' anchor'
                
            else:
                
                append_this = ' foundation'
                
            foundations_df['type [-]'] = foundations_df['type [-]'].map(
                    {'pile': 'pile' + append_this,
                    'gravity': 'gravity' + append_this}
                    )

        else:

            # make empty data structures
            foundations = {'type [-]': {},
                           'subtype [-]': {},
                           'x coord [m]': {},
                           'y coord [m]': {},
                           'length [m]': {},
                           'width [m]': {},
                           'height [m]': {},
                           'installation depth [m]': {},
                           'dry mass [kg]': {},
                           'grout type [-]': {},
                           'grout volume [m3]': {},
                           'zone [-]': {},
                           'layer information (layer number, soil type, ' + 
                               'soil depth) [-,-,m]': {},
                           'devices [-]': {},
                           'foundations [-]': {}}
            
            foundations_df = pd.DataFrame(foundations)

        if "floating" in self.data.system_type.lower():

            # get first marker of each line id
            all_lines = \
                    self.data.line_component_data['Line Identifier'].unique()
        
            device_association = []
        
            for line in all_lines:
        
                marker = self.data.line_component_data[
                    self.data.line_component_data['Line Identifier'] == \
                    line].Marker.iloc[0]

                device_association.append(
                    find_marker_key_mf(network, marker, 'mooring'))

            # make table - then join on line identifier
            line_interm = pd.DataFrame({"Device": device_association, 
                                        "Line Identifier": all_lines})

            lines_df = pd.merge(self.data.line_summary_data, line_interm,
                                  on = 'Line Identifier', how ='inner')

            # set index
            ids = lines_df.index.tolist()
            ids = ['m' + str(val) for val in ids]
            lines_df.index = ids

            name_map = {"Device": "devices [-]",
                        "Line Identifier": "lines [-]",
                        "Type": "type [-]",
                        "Length": "length [m]",
                        "Dry Mass": "dry mass [kg]"}

            lines_df = lines_df.rename(columns=name_map)

        else:

            # make empty data structures
            empty_lines_df = {'devices [-]': [],
                              'lines [-]': [],
                              'component list [-]': [],
                              'type [-]': [],
                              'length [m]': [],
                              'dry mass [kg]': []}

            lines_df = pd.DataFrame(empty_lines_df)
            
        # Check if phases can be skipped:
        if self.data.skip_phase is None:
            skip_phase = False
        else:
            skip_phase = self.data.skip_phase

        if debug_entry:
            plan_only = True
        else:
            plan_only = False

        if export_data:
            
            arg_dict = {'lines_df': lines_df,
                        'foundations_df': foundations_df
                        }
            arg_dict.update(input_dict)
                        
            pickle.dump(arg_dict, open("installation_inputs.pkl", "wb" ))

        ### Call module
        installation_output = installation_main(
                                    input_dict["vessels_df"],
                                    input_dict["equipment"],
                                    input_dict["ports_df"],
                                    input_dict["phase_order_df"],
                                    input_dict["schedule_OLC"],
                                    input_dict["penetration_rate_df"],
                                    input_dict["laying_rate_df"],
                                    input_dict["other_rates_df"],
                                    input_dict["port_safety_factor_df"],
                                    input_dict["vessel_safety_factor_df"],
                                    input_dict["equipment_safety_factor_df"],
                                    input_dict["whole_area"],
                                    input_dict["metocean_df"],
                                    input_dict["device_df"],
                                    input_dict["sub_device_df"],
                                    input_dict["landfall_df"],
                                    input_dict["entry_point_df"],
                                    input_dict["layout_df"],
                                    input_dict["collection_point_df"],
                                    input_dict["dynamic_cable_df"],
                                    input_dict["static_cable_df"],
                                    input_dict["cable_route_df"],
                                    input_dict["connectors_df"],
                                    input_dict["external_protection_df"],
                                    input_dict["topology"],
                                    lines_df,
                                    foundations_df,
                                    plan_only=plan_only,
                                    skip_phase=skip_phase
                                    )
        
        if debug_entry: return

        if export_data:

            pickle.dump(
                installation_output, open("installation_outputs.pkl", "wb" ))

        ### Collect outputs
        
        ### Dates 
        self.data.end_date = installation_output['DATE']['End Date']
        self.data.commissioning_date =\
            installation_output['DATE']['Comissioning Date']

        ### Port data
        self.data.port = \
            str(installation_output['PORT']['Port Name & ID [-]'][0])
        self.data.port_distance = \
            installation_output['PORT']['Distance Port-Site [km]']

        ### Environmental output from wp5
        self.data.journeys = installation_output['ENVIRONMENTAL']\
                ['Number Vessels Installation [-]']

        self.data.vessel_average_size = \
                installation_output['ENVIRONMENTAL']['Vessel Mean Length [m]']

        ### Planning phases       
        self.data.plan = \
            installation_output['PLANNING']['List of Operations [-]']

        # Need to logic test as they will not always be present
        installed_phases = installation_output['OPERATION'].keys()

        # Collect data per phase
        cost_dict, time_dict = self._init_phase_dicts()
        
        ### Device phase
        if any('support structure' in phase for phase in installed_phases):
            
            values = installation_output['OPERATION'][
                                        'Installation of support structure']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_support_structure_prep_time = \
                values['TIME']['Preparation Time [h]']

            self.data.install_support_structure_dates = \
                installation_phase_date_result_timeseries(values)

            self._compile_phase(cost_dict,
                                time_dict,
                                'Support Structure',
                                phase_cost_dict,
                                phase_time_dict)

        if any('devices' in phase for phase in installed_phases):
            
            values = installation_output['OPERATION'][
                                            'Installation of devices']
                
            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_devices_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_devices_dates = \
                installation_phase_date_result_timeseries(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                'Device',
                                phase_cost_dict,
                                phase_time_dict)
                                      
        device_component_costs = pd.DataFrame(cost_dict)
        
        if device_component_costs.empty:
            
            device_component_costs = None
            device_component_cost_breakdown = None
            device_cost_class_breakdown = None
            
        else:

            device_component_costs = \
                            device_component_costs.set_index("Component")
            device_component_cost_breakdown = \
                            device_component_costs.sum(1).to_dict()
            device_cost_class_breakdown = device_component_costs.sum(
                                                 numeric_only=True).to_dict()
            device_component_costs = device_component_costs.reset_index()
                
        self.data.device_component_costs = device_component_costs
        self.data.device_component_cost_breakdown = \
                                        device_component_cost_breakdown
        self.data.device_cost_class_breakdown = \
                                        device_cost_class_breakdown
        
        device_component_times = pd.DataFrame(time_dict)
        
        if device_component_times.empty:
            
            device_component_times = None
            device_component_time_breakdown = None
            device_time_class_breakdown = None
            
        else:

            device_component_times = \
                                device_component_times.set_index("Component")
            device_component_time_breakdown = \
                                device_component_times.sum(1).to_dict()
            device_time_class_breakdown = device_component_times.sum(
                                                numeric_only=True).to_dict()
            device_component_times = device_component_times.reset_index()
                        
        self.data.device_component_times = device_component_times
        self.data.device_component_time_breakdown = \
                                        device_component_time_breakdown
        self.data.device_time_class_breakdown = \
                                        device_time_class_breakdown
                                        
        ### Electrical phase
        cost_dict, time_dict = self._init_phase_dicts()
        
        if any('dynamic' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                                            'Installation of dynamic cables']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_dynamic_cable_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_dynamic_cable_dates = \
                installation_phase_date_result_timeseries(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                'Dynamic Cables',
                                phase_cost_dict,
                                phase_time_dict)

        if any('export' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                                    'Installation of static export cables']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_export_cable_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_export_cable_dates = \
                installation_phase_date_result(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                'Export Cables',
                                phase_cost_dict,
                                phase_time_dict)

        if any('array' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                                    'Installation of static array cables']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_array_cable_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_array_cable_dates = \
                installation_phase_date_result_timeseries(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                'Inter-Array Cables',
                                phase_cost_dict,
                                phase_time_dict)

        if any('surface piercing' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                    'Installation of collection point (surface piercing)']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)

            self.data.install_surface_piercing_substation_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_surface_piercing_substation_dates = \
                installation_phase_date_result(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                'Collection Points',
                                phase_cost_dict,
                                phase_time_dict)
        
        ### TODO: UPDATE
        # Mat - you may wish to combine with the above
        if any('seabed' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                    'Installation of collection point (seabed)']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_subsea_collection_point_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_subsea_collection_point_dates = \
                installation_phase_date_result_timeseries(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                'Collection Points',
                                phase_cost_dict,
                                phase_time_dict)

        if any('cable protection' in phase for phase in installed_phases):

            values = installation_output['OPERATION']\
                ['Installation of external cable protection']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_cable_protection_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_cable_protection_dates = \
                installation_phase_date_result_timeseries(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                'External Cable Protection',
                                phase_cost_dict,
                                phase_time_dict)
            
        electrical_component_costs = pd.DataFrame(cost_dict)
        
        if electrical_component_costs.empty:
            
            electrical_component_costs = None
            electrical_component_cost_breakdown = None
            electrical_cost_class_breakdown = None
            
        else:

            electrical_component_costs = \
                            electrical_component_costs.set_index("Component")
            electrical_component_cost_breakdown = \
                            electrical_component_costs.sum(1).to_dict()
            electrical_cost_class_breakdown = electrical_component_costs.sum(
                                                 numeric_only=True).to_dict()
            electrical_component_costs = \
                            electrical_component_costs.reset_index()
                
        self.data.electrical_component_costs = electrical_component_costs
        self.data.electrical_component_cost_breakdown = \
                                        electrical_component_cost_breakdown
        self.data.electrical_cost_class_breakdown = \
                                        electrical_cost_class_breakdown
        
        electrical_component_times = pd.DataFrame(time_dict)
        
        if electrical_component_times.empty:
            
            electrical_component_times = None
            electrical_component_time_breakdown = None
            electrical_time_class_breakdown = None
            
        else:

            electrical_component_times = \
                            electrical_component_times.set_index("Component")
            electrical_component_time_breakdown = \
                            electrical_component_times.sum(1).to_dict()
            electrical_time_class_breakdown = electrical_component_times.sum(
                                                numeric_only=True).to_dict()
            electrical_component_times = \
                            electrical_component_times.reset_index()
                        
        self.data.electrical_component_times = electrical_component_times
        self.data.electrical_component_time_breakdown = \
                                        electrical_component_time_breakdown
        self.data.electrical_time_class_breakdown = \
                                        electrical_time_class_breakdown
                                        
        ### M&F phase
        cost_dict, time_dict = self._init_phase_dicts()
                                        
        if any('driven piles' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                        'Installation of driven piles anchors/foundations']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_driven_piles_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_driven_piles_dates = \
                installation_phase_date_result_timeseries(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                'Driven Piles',
                                phase_cost_dict,
                                phase_time_dict)

        if any('direct-embedment' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
               'Installation of mooring systems with direct-embedment anchors']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_direct_embedment_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_direct_embedment_dates = \
                installation_phase_date_result(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                "Direct-Embedment Anchors",
                                phase_cost_dict,
                                phase_time_dict)
            
        if any('gravity based' in phase for phase in installed_phases):
            
            values = installation_output['OPERATION'][
                                'Installation of gravity based foundations']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_gravity_based_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_gravity_based_dates = \
                installation_phase_date_result_timeseries(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                "Gravity Based Foundations",
                                phase_cost_dict,
                                phase_time_dict)
                
        if any('pile anchor' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                        'Installation of mooring systems with pile anchors']
                
            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            
            self.data.install_pile_anchor_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_pile_anchor_dates = \
                installation_phase_date_result_timeseries(values)
            
            self._compile_phase(cost_dict,
                                time_dict,
                                "Pile Anchors",
                                phase_cost_dict,
                                phase_time_dict)

        if any('drag-embedment' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                'Installation of mooring systems with drag-embedment anchors']
                
            self.data.install_drag_embedment_prep_time = \
                values['TIME']['Preparation Time [h]']
            
            self.data.install_drag_embedment_dates = \
                installation_phase_date_result_timeseries(values)

            self._compile_phase(cost_dict,
                                time_dict,
                                "Drag-Embedment Anchors",
                                phase_cost_dict,
                                phase_time_dict)

        if any('suction-embedment' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
              'Installation of mooring systems with suction-embedment anchors']
              
            self.data.install_suction_embedment_prep_time = \
                 values['TIME']['Preparation Time [h]']
              
            self.data.install_suction_embedment_dates = \
                installation_phase_date_result_timeseries(values)

            self._compile_phase(cost_dict,
                                time_dict,
                                "Suction-Caisson Anchors",
                                phase_cost_dict,
                                phase_time_dict)

        mooring_component_costs = pd.DataFrame(cost_dict)
        
        if mooring_component_costs.empty:
            
            mooring_component_costs = None
            mooring_component_cost_breakdown = None
            mooring_cost_class_breakdown = None
            
        else:

            mooring_component_costs = \
                            mooring_component_costs.set_index("Component")
            mooring_component_cost_breakdown = \
                            mooring_component_costs.sum(1).to_dict()
            mooring_cost_class_breakdown = mooring_component_costs.sum(
                                                 numeric_only=True).to_dict()
            mooring_component_costs = \
                            mooring_component_costs.reset_index()
                
        self.data.mooring_component_costs = mooring_component_costs
        self.data.mooring_component_cost_breakdown = \
                                        mooring_component_cost_breakdown
        self.data.mooring_cost_class_breakdown = \
                                        mooring_cost_class_breakdown
        
        mooring_component_times = pd.DataFrame(time_dict)
        
        if mooring_component_times.empty:
            
            mooring_component_times = None
            mooring_component_time_breakdown = None
            mooring_time_class_breakdown = None
            
        else:

            mooring_component_times = \
                            mooring_component_times.set_index("Component")
            mooring_component_time_breakdown = \
                            mooring_component_times.sum(1).to_dict()
            mooring_time_class_breakdown = mooring_component_times.sum(
                                                numeric_only=True).to_dict()
            mooring_component_times = \
                            mooring_component_times.reset_index()
                        
        self.data.mooring_component_times = mooring_component_times
        self.data.mooring_component_time_breakdown = \
                                        mooring_component_time_breakdown
        self.data.mooring_time_class_breakdown = \
                                        mooring_time_class_breakdown
                                        
                                        
        ### Cost agregation
        phase_costs = {}

        if device_component_cost_breakdown is not None:
            phase_costs["Devices"] = \
                            sum(device_component_cost_breakdown.values())
            
        if electrical_component_cost_breakdown is not None:
            phase_costs["Electrical Sub-Systems"] = \
                            sum(electrical_component_cost_breakdown.values())
            
        if mooring_component_cost_breakdown is not None:
            phase_costs["Mooring and Foundations"] = \
                            sum(mooring_component_cost_breakdown.values())
                                    
        if not phase_costs: phase_costs = None
        
        cost_classes = {'Equipment': 0.,
                        'Vessel': 0.,
                        'Port': 0.}
        record_classes = False
                    
        if device_cost_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in ['Equipment', 'Vessel', 'Port']:
                
                cost_classes[class_name] += \
                                    device_cost_class_breakdown[class_name]

        if electrical_cost_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in ['Equipment', 'Vessel', 'Port']:
                
                cost_classes[class_name] += \
                                    electrical_cost_class_breakdown[class_name]

        if mooring_cost_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in ['Equipment', 'Vessel', 'Port']:
                
                cost_classes[class_name] += \
                                    mooring_cost_class_breakdown[class_name]

        if not record_classes:
            
            cost_classes = None
            
        else:

            # Assert against module values
            assert np.isclose(cost_classes['Equipment'],
                              installation_output['COST'][
                                                'Total Equipment Cost [EUR]'])

            assert np.isclose(cost_classes['Vessel'],
                              installation_output['COST'][
                                                  'Total Vessel Cost [EUR]'])

            assert np.isclose(cost_classes['Port'],
                              installation_output['COST'][
                                                  'Total Port Cost [EUR]'])

        if phase_costs is not None and cost_classes is not None:
            
            total_phase_costs = sum(phase_costs.values())
            total_class_costs = sum(cost_classes.values())
            
            assert np.isclose(total_phase_costs, total_class_costs)

            total_costs = total_phase_costs

            assert np.isclose(total_costs,
                              installation_output['COST'][
                                          'Total Installation Cost [EUR]'])
            
        else:
            
            total_costs = None

        ### Contingency
        contingency = installation_output['COST'][
                                            'Total Contingency Costs [EUR]']

        if contingency:
            
            phase_costs['Contingency'] = contingency
            cost_classes['Contingency'] = contingency

            if total_costs is None:
                total_costs = contingency
            else:
                total_costs += contingency
                
        self.data.total_phase_costs = phase_costs
        self.data.total_class_costs = cost_classes
        self.data.total_costs = total_costs
            
        ### Time agregation
        phase_times = {}

        if device_component_time_breakdown is not None:
            phase_times["Devices"] = \
                            sum(device_component_time_breakdown.values())
            
        if electrical_component_time_breakdown is not None:
            phase_times["Electrical Sub-Systems"] = \
                            sum(electrical_component_time_breakdown.values())
            
        if mooring_component_time_breakdown is not None:
            phase_times["Mooring and Foundations"] = \
                            sum(mooring_component_time_breakdown.values())
                                    
        if not phase_times: phase_times = None
        
        time_classes = {'Preparation': 0.,
                        'Transit': 0.,
                        'Waiting': 0.,
                        'Operations': 0.}
        time_class_names = ['Preparation', 'Transit', 'Waiting', 'Operations']
        record_classes = False
                    
        if device_time_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in time_class_names:
                
                time_classes[class_name] += \
                                    device_time_class_breakdown[class_name]

        if electrical_time_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in time_class_names:
                
                time_classes[class_name] += \
                                    electrical_time_class_breakdown[class_name]

        if mooring_time_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in time_class_names:
                
                time_classes[class_name] += \
                                    mooring_time_class_breakdown[class_name]

        if not record_classes:
            
            time_classes = None
            
        else:

            # Assert against module values
            assert np.isclose(time_classes['Waiting'],
                              installation_output['TIME'][
                                                  'Total Waiting Time [h]'])

            assert np.isclose(time_classes['Preparation'],
                              installation_output['TIME'][
                                            'Total Preparation Time [h]'])

            assert np.isclose(time_classes['Transit'],
                              installation_output['TIME'][
                                              'Total Sea Transit Time [h]'])
            
            assert np.isclose(time_classes['Operations'],
                              installation_output['TIME'][
                                              'Total Sea Operation Time [h]'])

        if phase_times is not None and time_classes is not None:
            
            total_phase_times = sum(phase_times.values())
            total_class_times = sum(time_classes.values())
            
            assert np.isclose(total_phase_times, total_class_times)

            total_times = total_phase_times

            assert np.isclose(total_times,
                              installation_output['TIME'][
                                          'Total Installation Time [h]'])
            
        else:
            
            total_times = None
            
        self.data.total_phase_times = phase_times
        self.data.total_class_times = time_classes
        self.data.total_times = total_times
        
        ### BOM
        bom_dict = {"Key Identifier": phase_costs.keys(),
                    "Cost": phase_costs.values(),
                    "Quantity": [1] * len(phase_costs),
                    "Year": [0] * len(phase_costs)}

        bom_df = pd.DataFrame(bom_dict)
        
        self.data.installation_bom = bom_df
        
        ### outputs for Gantt chart - needs dates for each phase
        
        

        return
    
    @classmethod    
    def get_input_dict(cls, data,
                            bathymetry,
                            system_type,
                            array_layout,
                            electrical_network,
                            moorings_foundations_network,
                            zone):
        
        name_map = {"User/DDS": "dataframe"}

        ### Equipment
        name_map = {"ROV class": "ROV class [-]",
                    "Depth rating": "Depth rating [m]",
                    "Length": "Length [m]",
                    "Width": "Width [m]",
                    "Height": "Height [m]",
                    "Weight": "Weight [t]",
                    "Payload": "Payload [t]",
                    "Horse power": "Horse power [hp]",
                    "BP forward": "BP forward [kgf]",
                    "BP lateral": "BP lateral [kgf]",
                    "BP vertical": "BP vertical [kgf]",
                    "Manipulator number": "Manipulator number [-]",
                    "Manipulator grip force": "Manipulator grip force [N]",
                    "Manipulator wirst torque":
                        "Manipulator wirst torque [Nm]",
                    "AE footprint": "AE footprint [m^2]",
                    "AE weight": "AE weight [t]",
                    "AE supervisor": "AE supervisor [-]",
                    "AE technician": "AE technician [-]",
                    "ROV day rate": "ROV day rate [EURO/day]",
                    "Supervisor rate": "Supervisor rate [EURO/12h]",
                    "Technician rate": "Technician rate [EURO/12h]"
                    }

        rov_df = data.rov
        rov_df = rov_df.rename(columns=name_map)

        # divers
        name_map = {"Type diving": "	Type diving [-]",
                    "Max operating depth": "Max operating depth [m]",
                    "Deployment eq. footprint":
                        "Deployment eq. footprint [m^2]",
                    "Deployment eq. weight": "Deployment eq. weight [t]",
                    "Nr supervisors": "Nr supervisors [-]",
                    "Nr divers": "Nr divers [-]",
                    "Nr tenders": "Nr tenders [-]",
                    "Nr technicians": "Nr technicians [-]",
                    "Nr support technicians": "Nr support technicians [-]",
                    "Deployment eq. day rate":
                        "Deployment eq. day rate [EURO/day]",
                    "Supervisor day rate": "Supervisor day rate [EURO/day]",
                    "Divers day rate": "Divers day rate [EURO/day]",
                    "Tenders day rate	": "Tenders day rate [EURO/day]",
                    "Technicians day rate": "Technicians day rate [EURO/day]",
                    "Life support day rate":
                        "Life support day rate [EURO/day]",
                    "Total day rate": "Total day rate [EURO/day]"
                    }

        divers_df = data.divers
        divers_df = divers_df.rename(columns=name_map)
        
        # cable_burial
        name_map = {"Burial tool type": "Burial tool type [-]",
                    "Max operating depth": "Max operating depth [m]",
                    "Tow force required": "Tow force required [t]",
                    "Length": "Length [m]",
                    "Width": "Width [m]",
                    "Height": "Height [m]",
                    "Weight": "Weight [t]",
                    "Jetting capability": "Jetting capability [yes/no]",
                    "Ploughing capability": "Ploughing capability [yes/no]",
                    "Cutting capability": "Cutting capability [yes/no]",
                    "Jetting trench depth": "Jetting trench depth [m]",
                    "Ploughing trench depth": "Ploughing trench depth [m]",
                    "Cutting trench depth": "Cutting trench depth [m]",
                    "Max cable diameter": "Max cable diameter [mm]",
                    "Min cable bending radius":
                        "Min cable bending radius [m]",
                    "AE footprint": "AE footprint [m^2]",
                    "AE weight": "AE weight [t]",
                    "Burial tool day rate": "Burial tool day rate [EURO/day]",
                    "Personnel day rate": "Personnel day rate [EURO/12h]"
                    }
        
        cable_burial_df = data.cable_burial
        cable_burial_df = cable_burial_df.rename(columns=name_map)
        
        # Map boolean columns to yes/no
        yes_no_map = {True: "yes",
                      False: "no"}
        
        cable_burial_df = cable_burial_df.replace(
                                {"Jetting capability [yes/no]": yes_no_map,
                                 "Ploughing capability [yes/no]": yes_no_map,
                                 "Cutting capability [yes/no]": yes_no_map
                                 })
        
        # excavating
        name_map = {"Depth rating": "Depth rating [m]",
                    "Width": "Width [m]",
                    "Height": "Height [m]",
                    "Length or diameter": "Lenght or diameter[m]",
                    "Nozzle diameter": "Nozzle diameter [m]",
                    "Weight": "Weight [t]",
                    "Max pressure": "Max pressure [bar]",
                    "Max flow rate": "Max flow rate [bar]",
                    "Max torque": "Max torque [bar]",
                    "Thrust": "Thrust [t]",
                    "Propeller speed": "Propeller speed [rpm]",
                    "Excavator day rate": "Excavator day rate [EURO/day]",
                    "Personnel day rate": "Personnel day rate [EURO/12h]"
                    }

        excavating_df = data.excavating
        excavating_df = excavating_df.rename(columns=name_map)
        
        # mattresses
        name_map = {"Concrete resistance": "Concrete resistance [N/mm^2]",
                    "Concrete density": "Concrete density [kg/m^3]",
                    "Unit length": "Unit lenght [m]",
                    "Unit width": "Unit width [m]",
                    "Unit thickness": "Unit thickness [m]",
                    "Unit weight air": "Unit weight air [t]",
                    "Unit weight water": "Unit weight water [t]",
                    "Nr looped ropes": "Nr looped ropes [-]",
                    "Ropes diameter": "Ropes diameter [mm]",
                    "Cost per unit": "Cost per unit [EURO]"
                    }
        
        mattresses_df = data.mattresses
        mattresses_df = mattresses_df.rename(columns=name_map)
        
        # rock bags
        name_map = {"Weight": "Weight [t]",
                    "Particle diameter min": "Particle diameter min [mm]",
                    "Particle diameter max": "Particle diameter max [mm]",
                    "Mesh size": "Mesh size [mm]",
                    "Diameter": "Diameter [m]",
                    "Height": "Height [m]",
                    "Volume": "Volume [m^ 3]",
                    "Velocity unit": "Velocity unit [m/s]",
                    "Velocity grouped": "Velocity grouped [m/s]",
                    "Cost per unit": "Cost per unit [EURO]"
                    }

        rock_bags_df = data.rock_bags
        rock_bags_df = rock_bags_df.rename(columns=name_map)
        
        # split_pipes
        name_map = {"Material": "Material [-]",
                    "Unit weight air": "Unit weight air [kg]",
                    "Unit weight water": "Unit weight water [kg]",
                    "Unit length": "Unit length [mm]",
                    "Unit wall thickness": "Unit wall thichness [mm]",
                    "Unit inner diameter": "Unit inner diameter [mm]",
                    "Unit outer diameter": "Unit outer diameter [mm]",
                    "Max cable size": "Max cable size [mm]",
                    "Min bending radius": "Min bending radius [m]",
                    "Cost per unit": "Cost per unit [EURO]"
                    }

        split_pipes_df = data.split_pipes
        split_pipes_df = split_pipes_df.rename(columns=name_map)

        # hammer
        name_map = {"Depth rating": "Depth rating [m]",
                    "Length": "Length [m]",
                    "Weight in air": "Weight in air [t]",
                    "Min pile diameter": "Min pile diameter [mm]",
                    "Max pile diameter": "Max pile diameter [mm]",
                    "Max blow energy": "Max blow energy [kJ]",
                    "Min blow energy": "Min blow energy [kJ]",
                    "Blow rate at max blow energy":
                        "Blow rate at max blow energy [bl/min]",
                    "AE footprint": "AE footprint [m^2]",
                    "AE weight": "AE weight [t]",
                    "Hammer day rate": "Hammer day rate [EURO/day]",
                    "Personnel day rate": "Personnel day rate [EURO/12h]"
                    }

        hammer_df = data.hammer
        hammer_df = hammer_df.rename(columns=name_map)

        # drilling rigs
        name_map = {"Diameter": "Diameter [m]",
                    "Length": "Length [m]",
                    "Weight": "Weight [t]",
                    "Drilling diameter range": "Drilling diameter range [m]",
                    "Max drilling depth": "Max drilling depth [m]",
                    "Max water depth": "Max water depth [m]",
                    "Torque": "Torque [kNm]",
                    "Pull back": "Pull back [t]",
                    "AE footprint": "AE footprint [m^2]",
                    "AE weight": "AE weight [t]",
                    "Drill rig day rate": "Drill rig day rate [EURO/day]",
                    "Personnel day rate": "Personnel day rate [EURO/day]"
                    }

        drilling_rigs_df = data.drilling_rigs
        drilling_rigs_df = drilling_rigs_df.rename(columns=name_map)

        # vibro driver
        name_map = {"Width": "Width [m]",
                    "Length": "Length [m]",
                    "Height": "Height [m]",
                    "Vibro driver weight": "Vibro driver weight [m]",
                    "Clamp weight": "Clamp weight [m]",
                    "Eccentric moment": "Eccentric moment [m.kg]",
                    "Max frequency": "Max frequency [hz]",
                    "Max centrifugal force": "Max centrifugal force [kN]",
                    "Max line pull": "Max line pull [kN]",
                    "Min pile diameter": "Min pile diameter [mm]",
                    "Max pile diameter": "Max pile diameter [mm]",
                    "Max pile weight": "Max pile weight [t]",
                    "Power": "Power [kW]",
                    "Oil flow": "Oil flow [l/min]",
                    "AE footprint": "AE footprint [m^2]",
                    "AE weight": "AE weight [t]",
                    "Vibro diver day rate": "Vibro diver day rate [EURO/day]",
                    "Personnel day rate": "Personnel day rate [EURO/day]"
                    }

        vibro_driver_df = data.vibro_driver
        vibro_driver_df = vibro_driver_df.rename(columns=name_map)

        ### make equipment class here
        # Divide cable burial equipments per trenching capabilities
        jetting_trenchers = (
            cable_burial_df[
                cable_burial_df['Jetting capability [yes/no]'] == 'yes'])
        plough_trenchers = (
            cable_burial_df[
                cable_burial_df['Ploughing capability [yes/no]'] == 'yes'])
        cutting_trenchers = (
            cable_burial_df[
                cable_burial_df['Cutting capability [yes/no]'] == 'yes'])
        
        equipment = {'rov': EquipmentType("rov", rov_df),
                     'divers': EquipmentType("divers", divers_df),
                     'jetter': EquipmentType("jetter", jetting_trenchers),
                     'plough': EquipmentType("plough", plough_trenchers),
                     'cutter': EquipmentType("cutter", cutting_trenchers),
                     'cable burial': EquipmentType("cable burial",
                                                   cable_burial_df),
                     'excavating': EquipmentType("excavating", excavating_df),
                     'mattress': EquipmentType("mattress", mattresses_df),
                     'rock filter bags': EquipmentType("rock_filter_bags",
                                                       rock_bags_df),
                     'split pipe': EquipmentType("split pipe",
                                                 split_pipes_df),
                     'hammer': EquipmentType("hammer", hammer_df),
                     'drilling rigs': EquipmentType("drilling rigs",
                                                    drilling_rigs_df),
                     'vibro driver': EquipmentType("vibro driver",
                                                   vibro_driver_df)
                     }
                     
        
        ### Ports
        name_map = {"Name": "Name [-]",
                    "Country": "Country [-]",
#                    "UTM x": "UTM x [m]",
#                    "UTM y": "UTM y [m]",
                    "UTM zone": "UTM zone [-]",
                    "Type of terminal": "Type of terminal [Quay/Dry-dock]",
                    "Entrance width": "Entrance width [m]",
                    "Terminal length": "Terminal length [m]",
                    "Terminal load bearing": "Terminal load bearing [t/m^2]",
                    "Terminal draught": "Terminal draught [m]",
                    "Terminal area": "Terminal area [m^2]",
                    "Max gantry crane lift capacity":
                        "Max gantry crane lift capacity [t]",
                    "Max tower crane lift capacity":
                        "Max tower crane lift capacity [t]",
                    "Jacking capability": "Jacking capability [yes/no]"
                    }

        ports_df = data.ports
        ports_df = ports_df.rename(columns=name_map)
        
        port_locations = data.port_locations
        port_x = []
        port_y = []
        port_names = []

        for name, point in port_locations.iteritems():
            
            port_names.append(name)
            xy = list(point.coords)[0]
            port_x.append(xy[0])
            port_y.append(xy[1])
            
        port_location_dict = {"Name [-]": port_names,
                              "UTM x [m]": port_x,
                              "UTM y [m]": port_y}
        port_location_df = pd.DataFrame(port_location_dict)
        
        ports_df = pd.merge(ports_df, port_location_df, on="Name [-]")
        
        ports_df = ports_df.replace(
                                {"Jacking capability [yes/no]": yes_no_map})

        ### Vessels
        name_map = {"Vessel class": "Vessel class [-]",
                    "Vessel type": "Vessel type [-]",
                    "Gross tonnage": "Gross tonnage [ton]",
                    "Length": "Length [m]",
                    "Beam": "Beam [m]",
                    "Min. draft": "Min. draft [m]",
                    "Max. draft": "Max. draft [m]",
                    "Travel range": "Travel range [km]",
                    "Engine size": "Engine size [BHP]",
                    "Fuel tank": "Fuel tank [m^3]",
                    "Consumption": "Consumption [l/h]",
                    "Consumption towing": "Consumption towing [l/h]",
                    "Deck space": "Deck space [m^2]",
                    "Deck loading": "Deck loading [t/m^2]",
                    "Max. cargo": "Max. cargo [t]",
                    "Transit speed": "Transit speed [m/s]",
                    "Max. Speed": "Max. Speed [m/s]",
                    "Bollard pull": "Bollard pull [t]",
                    "Crew size": "Crew size [-]",
                    "External  personnel": "External  personnel [-]",
                    "OLC: Transit maxHs": "OLC: Transit maxHs [m]",
                    "OLC: Transit maxTp": "OLC: Transit maxTp [s]",
                    "OLC: Transit maxCs": "OLC: Transit maxCs [m/s]",
                    "OLC: Transit maxWs": "OLC: Transit maxWs [m/s]",
                    "OLC: Towing maxHs": "OLC: Towing maxHs [m]",
                    "OLC: Towing maxTp": "OLC: Towing maxTp [s]",
                    "OLC: Towing maxCs": "OLC: Towing maxCs [knots]",
                    "OLC: Towing maxWs": "OLC: Towing maxWs [m/s]",
                    "OLC: Jacking maxHs": "OLC: Jacking maxHs [m]",
                    "OLC: Jacking maxTp": "OLC: Jacking maxTp [s]",
                    "OLC: Jacking maxCs": "OLC: Jacking maxCs [m/s]",
                    "OLC: Jacking maxWs": "OLC: Jacking maxWs [m/s]",
                    "Crane capacity": "Crane capacity [t]",
                    "Crane radius": "Crane radius [m]",
                    "Turntable number": "Turntable number [-]",
                    "Turntable loading": "Turntable loading [t]",
                    "Turntable outer diameter":
                        "Turntable outer diameter [m]",
                    "Turntable inner diameter":
                        "Turntable inner diameter [m]",
                    "Turntable height": "Turntable height [m]",
                    "Cable splice": "Cable splice [yes/no]",
                    "Ground out capabilities":
                        "Ground out capabilities [yes/no]",
                    "DP": "DP [-]",
                    "Rock storage capacity": "Rock storage capacity [t]",
                    "Max dumping depth": "Max dumping depth [m]",
                    "Max dumping capacity": "Max dumping capacity [t/h]",
                    "Fall pipe diameter": "Fall pipe diameter [mm]",
                    "Diving moonpool": "Diving moonpool [yes/no]",
                    "Diving depth": "Diving depth [m]",
                    "Diving capacity": "Diving capacity [-]",
                    "ROV inspection": "ROV inspection [yes/no]",
                    "ROV inspection max depth":
                        "ROV inspection max depth [m]",
                    "ROV workclass": "ROV workclass [yes/no]",
                    "ROV workclass max depth": "ROV workclass max depth [m]",
                    "JackUp leg length": "JackUp leg lenght [m]",
                    "JackUp leg diameter": "JackUp leg diameter [m]",
                    "JackUp max water depth": "JackUp max water depth [m]",
                    "JackUp speed Up": "JackUp speed Up [m/min]",
                    "JackUp speed down": "JackUp speed down [m/min]",
                    "JackUp max payload": "JackUp max payload [t]",
                    "Mooring number  winches": "Mooring number  winches [-]",
                    "Mooring line pull": "Mooring line pull [t]",
                    "Mooring wire length": "Mooring wire lenght [m]",
                    "Mooring number anchors": "Mooring number anchors [-]",
                    "Mooring anchor weight": "Mooring anchor weight [t]",
                    "AH drum capacity": "AH drum capacity [m]",
                    "AH wire size": "AH wire size [mm]",
                    "AH winch rated pull": "AH winch rated pull [t]",
                    "AH winch break load": "AH winch break load [t]",
                    "Dredge depth": "Dredge depth [m]",
                    "Dredge type": "Dredge type [-]",
                    "Mob time": "Mob time [h]",
                    "Mob percentage": "Mob percentage [%]",
                    "Op min Day Rate": "Op min Day Rate [EURO/day]",
                    "Op max Day Rate": "Op max Day Rate [EURO/day]"
                    }

        vessels_df = data.vessels
        vessels_df = vessels_df.rename(columns=name_map)
        
        # Map boolean columns to yes/no
        cable_burial_df = cable_burial_df.replace(
                            {"Cable splice [yes/no]": yes_no_map,
                             "Ground out capabilities [yes/no]": yes_no_map,
                             "Diving moonpool [yes/no]": yes_no_map,
                             "ROV inspection [yes/no]": yes_no_map,
                             "ROV workclass [yes/no]": yes_no_map
                             })

        ### Site
        site_df_unsort = bathymetry.to_dataframe()
        site_df = site_df_unsort.unstack(level = 'layer')
        site_df = site_df.swaplevel(1, 1, axis = 1)
        site_df = site_df.sortlevel(1, axis = 1)

        site_df = site_df.reset_index()

        site_df.columns = [' '.join(col).strip()
                                        for col in site_df.columns.values]

        mapping = {"x":"x","y":"y"}

        for i in range (3,(len(site_df.columns))):
            split_name = site_df.columns.values[i].split()
            if split_name[0] == "sediment":
                mapping[site_df.columns.values[i]]= "layer {} type".format(
                                                                split_name[2])  
            elif split_name[0] == "depth":
                mapping[site_df.columns.values[i]]= "layer {} start".format(
                                                                split_name[2]) 

        site_df = site_df.rename(columns=mapping)
        
        # drop all layers above 1 for now
        layer_cols = [col for col in site_df.columns if 'layer' in col]

        if len(layer_cols) > 2:

            #drop cols greater than 1
            n_layers = len(layer_cols)/2
            layer_start_remove = ['layer ' + str(layer) + ' start' 
                                    for layer in range(2, n_layers+1)]
            layer_type_remove = ['layer ' + str(layer) + ' type' 
                                    for layer in range(2, n_layers+1)]
            layer_remove = layer_start_remove + layer_type_remove
            site_df.drop(layer_remove)

        # Convert soil types to short codes
        soil_map = {'loose sand': 'ls',
                    'medium sand': 'ms',
                    'dense sand': 'ds',
                    'very soft clay': 'vsc',
                    'soft clay': 'sc',
                    'firm clay': 'fc',
                    'stiff clay': 'stc',
                    'hard glacial till': 'hgt',
                    'cemented': 'cm',
                    'soft rock coral': 'src',
                    'hard rock': 'hr',
                    'gravel cobble': 'gc'}

        site_df["layer 1 type"] = \
            site_df["layer 1 type"].map(soil_map)

        name_map = {
            "x": "x coord [m]",
            "y": "y coord [m]",
            # "zone": "zone [-]",
            "depth layer 1": "bathymetry [m]",
            "layer 1 type": "soil type [-]"
            }

        site_df = site_df.rename(columns=name_map)

        site_zone = [zone]*len(site_df)
        site_df.loc[:, 'zone [-]'] = pd.Series(site_zone)
        
        ### Export
        if data.export is not None:
        
            export_df_unsort = data.export.to_dataframe()
            export_df = export_df_unsort.unstack(level = 'layer')
            export_df = export_df.swaplevel(1, 1, axis = 1)
            export_df = export_df.sortlevel(1, axis = 1)
    
            export_df = export_df.reset_index()
    
            export_df.columns = [' '.join(col).strip()
                                        for col in export_df.columns.values]
    
            mapping = {"x":"x","y":"y"}
    
            for i in range (3,(len(export_df.columns))):
                split_name = export_df.columns.values[i].split()
                if split_name[0] == "sediment":
                    mapping[export_df.columns.values[i]] = \
                                        "layer {} type".format(split_name[2])  
                elif split_name[0] == "depth":
                    mapping[export_df.columns.values[i]] = \
                                        "layer {} start".format(split_name[2]) 
    
            export_df = export_df.rename(columns=mapping)
            
            # drop all layers above 1 for now
            layer_cols = [col for col in export_df.columns if 'layer' in col]
    
            if len(layer_cols) > 2:
    
                #drop cols greater than 1
                n_layers = len(layer_cols)/2
                layer_start_remove = ['layer ' + str(layer) + ' start' 
                                        for layer in range(2, n_layers+1)]
                layer_type_remove = ['layer ' + str(layer) + ' type' 
                                        for layer in range(2, n_layers+1)]
                layer_remove = layer_start_remove + layer_type_remove
                export_df.drop(layer_remove)
    
            # Convert soil types to short codes
            soil_map = {'loose sand': 'ls',
                        'medium sand': 'ms',
                        'dense sand': 'ds',
                        'very soft clay': 'vsc',
                        'soft clay': 'sc',
                        'firm clay': 'fc',
                        'stiff clay': 'stc',
                        'hard glacial till': 'hgt',
                        'cemented': 'cm',
                        'soft rock coral': 'src',
                        'hard rock': 'hr',
                        'gravel cobble': 'gc'}
    
            export_df["layer 1 type"] = \
                export_df["layer 1 type"].map(soil_map)
    
            name_map = {
                "x": "x coord [m]",
                "y": "y coord [m]",
                # "zone": "zone [-]",
                "depth layer 1": "bathymetry [m]",
                "layer 1 type": "soil type [-]"
                }
    
            export_df = export_df.rename(columns=name_map)
    
            export_zone = [zone]*len(export_df)
            export_df.loc[:, 'zone [-]'] = pd.Series(export_zone)
    
            # merge export and site data
            whole_area = export_df.append(site_df)
            whole_area = whole_area.reset_index(drop=True)
            
        else:
            
            whole_area = site_df
            
        # Switch sign on depths
        whole_area["bathymetry [m]"] = - whole_area["bathymetry [m]"]

        ### Metocean
        wave_series_df = data.wave_series
        tidal_series = data.tidal_series
        wind_series = data.wind_series
        
        tidal_series_df = tidal_series.to_frame(name="Cs")
        wind_series_df = wind_series.to_frame(name="Ws")

        # merge these on datetime index
        metocean_df = pd.merge(
            wave_series_df, tidal_series_df, how ='left', left_index=True, 
            right_index=True)

        metocean_df = pd.merge(
            metocean_df, wind_series_df, how = 'left', left_index=True,
            right_index=True)
            
        year = metocean_df.index.year
        month = metocean_df.index.month
        day = metocean_df.index.day
        hour = metocean_df.index.hour
        
        metocean_df.loc[:, 'year'] = year
        metocean_df.loc[:, 'month'] = month
        metocean_df.loc[:, 'day'] = day
        metocean_df.loc[:, 'hour'] = hour
        
        metocean_df.reset_index(inplace = True)
        metocean_df.drop('DateTime', axis = 1, inplace = True)

        name_map = {
            "year": "year [-]",
            "month": "month [-]",
            "day": "day [-]",
            "hour": "hour [-]",
            "Hs": "Hs [m]",
            "Tp": "Tp [s]",
            "Ws": "Ws [m/s]",
            "Cs": "Cs [m/s]"
            }

        metocean_df = metocean_df.rename(columns=name_map)

        ### Device
        # get sub system list from sub systems var
        sub_system_list = []

        name_map = {"Prime Mover": "A",
                    "PTO": "B",
                    "Support Structure": "D"}

        sub_systems = data.sub_device
        sub_systems = sub_systems.rename(index=name_map)
        
        if data.control_system is not None:
            
            control_system = data.control_system
            control_system = control_system.rename(
                                               index={"Control System": "C"})
            
            sub_systems = pd.concat([sub_systems, control_system])
        
        # place limitation - A, B, C must be assembled at Port.
        restricted_stages = "[A,B,C"

        if data.two_stage_assembly:
            sub_assembly_strategy = restricted_stages + "],D"
        else:
            sub_assembly_strategy = restricted_stages + ",D]"

        sub_assembly_strategy = "({})".format(sub_assembly_strategy)

        # map device type to required strings        
        if 'floating' in system_type.lower():

            device_type ='float'

        else:

            device_type = 'fixed'

        if 'tidal' in system_type.lower():

            device_type = device_type + ' TEC'

        else:

            device_type = device_type + ' WEC'
            
        # Check a bollard pull has been given when towed
        if data.transportation_method == "Tow" and data.bollard_pull is None:
            
            errStr = ("If device is towed fo deployment, a bollard pull value "
                      "must be given.")
            raise ValueError(errStr)
            
        # Get installation limits from subsystems
        max_hs = sub_systems["Max Hs"].max()
        max_tp = sub_systems["Max Tp"].max()
        max_ws = sub_systems["Max Wind Velocity"].max()
        max_cs = sub_systems["Max Current Velocity"].max()

        device_dict = {
            "Type": device_type,
            "Length": data.system_length,
            "Width": data.system_width,
            "Height": data.system_height,
            "Dry Mass": data.system_mass,
            "Sub-System List": sub_system_list,
            "Assembly Strategy": sub_assembly_strategy,
            "Assembly Duration": data.assembly_duration,
            "Load Out": data.load_out_method.lower(),
            "Transportation Method": data.transportation_method.lower(),
            "Bollard Pull": data.bollard_pull,
            "Connect Duration": data.connect_duration,
            "Disconnect Duration": data.disconnect_duration,
            "Max Hs": max_hs,
            "Max Tp": max_tp,
            "Max Wind Speed": max_ws,
            "Max Current Speed": max_cs,
            "Project Start Date": data.project_start_date
            }

        device_df = pd.DataFrame(device_dict)

        name_map = {
            "Type": "type [-]",
            "Length": "length [m]",
            "Width": "width [m]",
            "Height": "height [m]",
            "Dry Mass": "dry mass [kg]",
            "Sub-System List": "sub system list [-]",
            "Assembly Strategy": "assembly strategy [-]",
            "Assembly Duration": "assembly duration [h]",
            "Load Out": "load out [-]",
            "Transportation Method": "transportation method [-]",
            "Bollard Pull": "bollard pull [t]",
            "Connect Duration": "connect duration [h]",
            "Disconnect Duration": "disconnect duration [h]",
            "Max Hs": "max Hs [m]",
            "Max Tp": "max Tp [s]",
            "Max Wind Speed": "max wind speed [m/s]",
            "Max Current Speed": "max current speed [m/s]",
            "Project Start Date": "Project start date [-]"
            }

        device_df = device_df.rename(columns=name_map)

        ### Subdevice
        name_map = {
            "Length": "length [m]",
            "Width": "width [m]",
            "Height": "height [m]",
            "Dry Mass": "dry mass [kg]"}

        sub_device_df = sub_systems[name_map.keys()]
        sub_device_df = sub_device_df.rename(columns=name_map)

        ### Rates
        # Equipment penetration rate
        name_map = {
            "Loose Sand": "ls",
            "Medium Sand": "ms",
            "Dense Sand": "ds",
            "Very Soft Clay": "vsc",
            "Soft Clay": "sc",
            "Firm Clay": "fc",
            "Stiff Clay": "stc",
            "Hard Glacial Till": "hgt",
            "Cemented": "cm",
            "Soft Rock Coral": "src",
            "Hard Rock": "hr",
            "Gravel Cobble": "gc"
            }

        penetration_rate_df = data.penetration_rates
        penetration_rate_df = penetration_rate_df.rename(columns=name_map)

        # Installation soil compatibility/laying rate
        name_map = {
            "Loose Sand": "ls",
            "Medium Sand": "ms",
            "Dense Sand": "ds",
            "Very Soft Clay": "vsc",
            "Soft Clay": "sc",
            "Firm Clay": "fc",
            "Stiff Clay": "stc",
            "Hard Glacial till": "hgt",
            "Cemented": "cm",
            "Soft Rock Coral": "src",
            "Hard Rock": "hr",
            "Gravel Cobble": "gc"
            }

        laying_rate_df = data.installation_soil_compatibility
        laying_rate_df = laying_rate_df.rename(columns=name_map)

        index_map = {"Ploughing": "Ploughing [m/h]",
                     "Jetting": "Jetting [m/h]",
                     "Cutting": "Cutting [m/h]",
                     "Dredging": "Dredging [m/h]"
                     }
        
        laying_rate_df = laying_rate_df.rename(index = index_map)

        # other rates
        vals = [data.surface_laying_rate,
                data.split_pipe_laying_rate,
                data.loading_rate,
                data.grout_rate,       
                data.fuel_cost_rate,
                data.port_cost,
                data.commission_time,
                data.cost_contingency]

        idx = ['Surface laying [m/h]',
               'Installation of iron cast split pipes [m/h]',
               'Loading rate [m/h]',
               'Grout rate [m3/h]',
               'Fuel cost rate [EUR/l]',
               'Port percentual cost [%]',
               'Comissioning time [weeks]',
               'Cost Contingency [%]'
               ]

        other_rates_df = pd.DataFrame({"Default values": vals}, index = idx)

        ### Safety factors
        # port
        name_map = {
            "Parameter": "Port parameter and unit [-]",
            "Safety Factor": "Safety factor (in %) [-]"
            }

        port_safety_factor_df = data.port_safety_factors.reset_index()
        port_safety_factor_df = port_safety_factor_df.rename(columns=name_map)
        
        # vessel
        name_map = {
            "Parameter": "Vessel parameter and unit [-]",
            "Safety Factor": "Safety factor (in %) [-]"
            }

        vessel_safety_factor_df = data.vessel_safety_factors.reset_index()
        vessel_safety_factor_df = vessel_safety_factor_df.rename(
            columns=name_map)

        # equipment
        equipment_tables = [data.rov_safety_factors,
                            data.divers_safety_factors,
                            data.hammer_safety_factors,
                            data.vibro_driver_safety_factors,
                            data.cable_burial_safety_factors,
                            data.split_pipe_safety_factors]
                            
        type_ids = ['rov',
                    'divers',
                    'hammer',
                    'vibro_driver',
                    'cable_burial',
                    'split_pipe']
        
        column_map = {"Parameter": "Equipment parameter and unit [-]",
                      "Safety Factor": "Safety factor (in %) [-]",
                      }
                      
        mapped_tables = []
        
        for type_id, equipment_table in zip(type_ids, equipment_tables):
            
            equipment_table = equipment_table.reset_index()
            equipment_table = equipment_table.rename(columns=column_map)
            equipment_table["Equipment type id [-]"] = type_id
            mapped_tables.append(equipment_table)
        
        equipment_safety_factor_df = pd.concat(mapped_tables,
                                               ignore_index=True)
        
        ### Configuration options
        # Installation order
        device_order_dict = {
             u'Default order': {12: 0,
                                13: 1},
             u'id': {12: u'S_structure',
                     13: u'Device'},
             u'logistic phases group': {
                      12: u'Installation of devices',
                      13: u'Installation of devices'}}
                      
        device_order_df = pd.DataFrame(device_order_dict)
        
        device_order_increment = 0
        phase_order_tables = []
        
        if electrical_network is not None:

            # Increment the device installation order
            device_order_increment += 4

            electrical_order_dict = {
                 u'Default order': {0: 1,
                                    1: 3,
                                    2: 4,
                                    3: 0,
                                    4: 2,
                                    5: 4},
                 u'id': {0: u'E_export',
                         1: u'E_array',
                         2: u'E_external',
                         3: u'E_cp_seabed',
                         4: u'E_cp_surface',
                         5: u'E_dynamic'},
                 u'logistic phases group': {
                      0: u'Installation of electrical infrastructure',
                      1: u'Installation of electrical infrastructure',
                      2: u'Installation of static cable external protection',
                      3: u'Installation of electrical infrastructure',
                      4: u'Installation of electrical infrastructure',
                      5: u'Installation of electrical infrastructure'}}
                          
            electrical_order_df = pd.DataFrame(electrical_order_dict)
            phase_order_tables.append(electrical_order_df)
            
        if moorings_foundations_network is not None:

            # Increment the device installation order
            device_order_increment += 1

            mf_order_dict = {
             u'Default order': {6: 0,
                                7: 0,
                                8: 0,
                                9: 0,
                                10: 0,
                                11: 0},
             u'id': {6: u'Driven',
                     7: u'Gravity',
                     8: u'M_pile',
                     9: u'M_drag',
                     10: u'M_direct',
                     11: u'M_suction'},
             u'logistic phases group': {
                      6: u'Installation of moorings & foundations',
                      7: u'Installation of moorings & foundations',
                      8: u'Installation of moorings & foundations',
                      9: u'Installation of moorings & foundations',
                      10: u'Installation of moorings & foundations',
                      11: u'Installation of moorings & foundations'}}
                          
            mf_order_df = pd.DataFrame(mf_order_dict)
            phase_order_tables.append(mf_order_df)
            
        # Increment the order of device installation
        if device_order_increment > 4: device_order_increment = 4

        device_order_df['Default order'] += device_order_increment
        phase_order_tables.append(device_order_df)
        
        # Joint the tables
        phase_order_tables = [x for x in phase_order_tables if x is not None]
        phase_order_df = pd.concat(phase_order_tables)
        phase_order_df = phase_order_df.reindex()

        # Entry point
        entry_point_data = {'x coord [m]': data.entry_point.x,
                            'y coord [m]': data.entry_point.y,
                            'zone [-]': zone}

        entry_point_df = pd.DataFrame(entry_point_data, index = [0])

#        entry_point_df.reset_index(inplace = True )

        # schedule OLC
        schedule_OLC = get_operations_template()
                
        ### Hydrodynamics                            
        device, x, y  = zip(*[(key.lower(), item.x, item.y)
                            for key, item in array_layout.items()])      
        
        layout_dict = {'Device': device,
                       'UTM X': x,
                       'UTM Y': y}

        layout_df = pd.DataFrame(layout_dict)
        
        name_map = {"Device": "device [-]",
                    "UTM X": "x coord [m]",
                    "UTM Y": "y coord [m]"}

        layout_df = layout_df.rename(columns=name_map)

        layout_zone = [zone]*len(layout_df)
        layout_df.loc[:, 'zone [-]'] = pd.Series(layout_zone)

        index = layout_df.index.tolist()
        index = ['d' + str(val) for val in index]
        layout_df.index = index

        ### Electrical
        topology = 'type 1' # to be mapped from wp3

        if electrical_network is not None:
            
            if data.export is None:
                
                errStr = ("Cable corridor bathymetry must be provided"
                          " if electrical network is set")
                raise ValueError(errStr)
            
            elec_network_design = electrical_network['nodes']
            elec_hierarchy = electrical_network['topology']

            elec_component_data_df = data.electrical_components
            elec_substation_data = data.substations
            elec_static_cables_df = data.elec_db_static_cable
            elec_dynamic_cables_df = data.elec_db_dynamic_cable
            elec_dry_mate_df = data.elec_db_dry_mate
            elec_wet_mate_df = data.elec_db_wet_mate
            cable_route_df = data.cable_routes
            landfall = data.landfall
            
            data_missing = False
            
            if elec_component_data_df is None: data_missing = True
            if elec_substation_data is None: data_missing = True
            if elec_static_cables_df is None: data_missing = True
            if elec_dry_mate_df is None: data_missing = True
            if elec_wet_mate_df is None: data_missing = True
            if cable_route_df is None: data_missing = True
            if landfall is None: data_missing = True
            
            if data_missing:
                
                errStr = ("Complete electrical network data has not been "
                          "provided.")
                raise ValueError(errStr)
            
            collection_point_df = set_collection_points(elec_component_data_df,
                                                        elec_network_design,
                                                        elec_hierarchy,
                                                        elec_substation_data)

            cp_zone = [zone]*len(collection_point_df)
            collection_point_df.loc[:, 'Zone'] = pd.Series(cp_zone)

            name_map = {"Downstream Interface Type": "downstream ei type [-]",
                        "Pigtail Cable Mass":
                                "pigtails cable dry mass [kg/m]",
                        "Downstream Interface Marker": "downstream ei id [-]",
                        "Upstream Interface Marker": "upstream ei id [-]",
                        "N Pigtails": "nr pigtails [-]",
                        "Pigtail Total Mass": "pigtails total dry mass [kg]",
                        "Height": "height [m]",
                        "Width": "width [m]",
                        "Length": "length [m]",
                        "Upstream Interface Type": "upstream ei type [-]",
                        "Mass": "dry mass [kg]",
                        "X Coord": "x coord [m]",
                        "Y Coord": "y coord [m]",
                        "Pigtail Length": "pigtails length [m]",
                        "Type": "type [-]",
                        "Pigail Diameter": "pigtails diameter [mm]",
                        "Zone": "zone [-]"}

            collection_point_df = collection_point_df.rename(columns=name_map)

            static_cable_df = set_cables(elec_component_data_df,
                                         elec_network_design,
                                         elec_hierarchy,
                                         elec_static_cables_df,
                                         'static')

            static_cable_df = set_cable_cp_references(static_cable_df,
                                                      collection_point_df)

            name_map = {"Type": "type [-]",
                        "Length": "length [m]",
                        "Upstream Interface Marker": "upstream ei id [-]",
                        "Downstream Interface Marker": "downstream ei id [-]",
                        "Upstream Interface Type": "upstream ei type [-]",
                        "Downstream Interface Type": "downstream ei type [-]",
                        "Upstream Component Type":
                            "upstream termination type [-]",
                        "Upstream Component Id": "upstream termination id [-]",
                        "Downstream Component Type":
                            "downstream termination type [-]",
                        "Downstream Component Id":
                            "downstream termination id [-]",
                        "Mass": "dry mass [kg/m]",
                        "Diameter": "diameter [mm]",
                        "MBR": "MBR [m]",
                        "MBL": "MBL [N]",
                        "Total Mass": "total dry mass [kg]"}

            static_cable_df = static_cable_df.rename(columns=name_map)

            trenching = [[data.cable_tool.lower()]]*len(static_cable_df)
            static_cable_df.loc[:, 'trench type [-]'] = pd.Series(trenching)
            static_cable_df = static_cable_df.set_index('Marker')
            static_cable_df.index.name = 'id [-]'

            if 'floating' in system_type.lower():
                
                if data.umbilical_terminations is None:
                    
                    errStr = ("The umbilical seabed connection points must be "
                              "provided for electrical network installation "
                              "of floating devices")
                    raise ValueError(errStr)

                dynamic_cable_df = set_cables(elec_component_data_df,
                                              elec_network_design,
                                              elec_hierarchy,
                                              elec_dynamic_cables_df,
                                              'dynamic')

                umbilical_ends = {name.lower(): val for name, val in
                                      data.umbilical_terminations.items()}

                terminations = get_umbilical_terminations(
                                    electrical_network['nodes'],
                                    umbilical_ends,
                                    dynamic_cable_df,
                                    layout_df)

                dynamic_cable_df = pd.merge(dynamic_cable_df,
                                            terminations,
                                            on=['Marker'])
                    
                dynamic_cable_df = set_cable_cp_references(dynamic_cable_df,
                                                           collection_point_df)

                name_map = {"Type": "type [-]",
                            "Length": "length [m]",
                            "Upstream Interface Marker": "upstream ei id [-]",
                            "Downstream Interface Marker":
                            "downstream ei id [-]",
                            "Upstream Interface Type": "upstream ei type [-]",
                            "Downstream Interface Type":
                            "downstream ei type [-]",
                            "Upstream Component Type":
                                "upstream termination type [-]",
                            "Upstream Component Id":
                            "upstream termination id [-]",
                            "Downstream Component Type":
                                "downstream termination type [-]",
                            "Downstream Component Id":
                                "downstream termination id [-]",
                            "Mass": "dry mass [kg/m]",
                            "Diameter": "diameter [mm]",
                            "MBR": "MBR [m]",
                            "MBL": "MBL [N]",
                            "Total Mass": "total dry mass [kg]",
                            'Upstream UTM X' :
                                'upstream termination x coord [m]',
                            'Upstream UTM Y' :
                                'upstream termination y coord [m]',
                            'Downstream UTM X' :
                                'downstream termination x coord [m]',
                            'Downstream UTM Y' :
                                'downstream termination y coord [m]'}

                dynamic_cable_df = dynamic_cable_df.rename(columns=name_map)

                dynamic_cable_zone = [zone]*len(dynamic_cable_df)

                dynamic_cable_df.loc[:, 'downstream termination zone [-]'] = \
                    pd.Series(dynamic_cable_zone)

                dynamic_cable_df.loc[:, 'upstream termination zone [-]'] = \
                    pd.Series(dynamic_cable_zone)
                                    
                ### TODO: UPDATE
                # If wp4 runs this data can be added
                buoyancy_number = []*len(dynamic_cable_df)
                buoyancy_diameter = []*len(dynamic_cable_df)
                buoyancy_length = []*len(dynamic_cable_df)
                buoyancy_weight = []*len(dynamic_cable_df)
                cable_weight = [1]*len(dynamic_cable_df)
                
                dynamic_cable_df.loc[:, 'buoyancy number [-]'] = \
                    pd.Series(buoyancy_number)
                
                dynamic_cable_df.loc[:, 'buoyancy length [m]'] = \
                    pd.Series(buoyancy_length)
                
                dynamic_cable_df.loc[:, 'buoyancy weigth [kg]'] = \
                    pd.Series(buoyancy_weight)
                
                dynamic_cable_df.loc[:, 'buoyancy diameter [mm]'] = \
                    pd.Series(buoyancy_diameter)
                
                dynamic_cable_df.loc[:, 'dry mass [kg/m]'] = \
                    pd.Series(cable_weight)

            else:

                dynamic_cable = {"dry mass [kg/m]": {},
                                 "total dry mass [kg]": {},
                                 "length [m]": {},
                                 "diameter [mm]": {},
                                 "MBR [m]": {},
                                 "MBL [N]": {},
                                 "upstream termination type [-]": {},
                                 "upstream termination id [-]": {},
                                 "upstream termination x coord [m]": {},
                                 "upstream termination y coord [m]": {},
                                 "upstream termination zone [-]": {},
                                 "downstream termination type [-]": {},
                                 "downstream termination id [-]": {},
                                 "downstream termination x coord [m]": {},
                                 "downstream termination y coord [m]": {},
                                 "downstream termination zone [-]": {},
                                 "upstream ei type [-]": {},
                                 "upstream ei id [-]": {},
                                 "downstream ei type [-]": {},
                                 "downstream ei id [-]": {},
                                 "buoyancy number [-]": {},
                                 "buoyancy diameter [mm]": {},
                                 "buoyancy length [m]": {},
                                 "buoyancy weigth [kg]": {}} # typo in wp5
    
                dynamic_cable_df = pd.DataFrame(dynamic_cable, dtype = object)

            name_map = {"Burial Depth": "burial depth [m]",
                        "Split Pipe": "split pipe [-]",
                        "UTM X": "x coord [m]",
                        "UTM Y": "y coord [m]",
                        "Depth": 'bathymetry [m]',
                        "Sediment": 'soil type [-]',
                        "Marker": "static cable id [-]",
                        }

            cable_route_df = data.cable_routes.rename(columns=name_map)

            cable_zone = [zone]*len(data.cable_routes)
            cable_route_df['zone [-]'] = cable_zone
            cable_route_df['bathymetry [m]'] = \
                                            - cable_route_df['bathymetry [m]']

            connector_db = elec_dry_mate_df.append(elec_wet_mate_df)

            connectors_df = \
                set_connectors(elec_component_data_df, connector_db)

            connectors_df.index.name = 'id [-]'

            name_map = {"Demating Force": "demating force [N]",
                        "Height": "height [m]",
                        "Length": "lenght [m]",
                        "Mass": "dry mass [kg]",
                        "Mating Force": "mating force [N]",
                        "Width": "width [m]"
                        }

            connectors_df = connectors_df.rename(columns=name_map)

            external_protection = {"protection type [-]": {},
                                   "x coord [m]": {},
                                   "y coord [m]": {},
                                   "zone [-]": {}}

            external_protection_df = \
                    pd.DataFrame(external_protection, dtype = object)
                    
            ### Landfall
            technique_map = {"Horizontal Directional Drilling": "HDD",
                             "Open Cut Trenching": "OCT"}
            technique = technique_map[landfall]
            
            landfall_dict = {"method [-]": [technique]}
            landfall_df = pd.DataFrame(landfall_dict)

        else:

            # make empty data structures
            collection_point = {"type [-]": {},
                                 "x coord [m]": {},
                                 "y coord [m]": {},
                                 "zone [-]": {},
                                 "length [m]": {},
                                 "width [m]": {},
                                 "height [m]": {},
                                 "dry mass [kg]": {},
                                 "upstream ei type [-]": {},
                                 "upstream ei id [-]": {},
                                 "downstream ei type [-]": {},
                                 "downstream ei id [-]": {},
                                 "nr pigtails [-]": {},
                                 "pigtails length [m]": {},
                                 "pigtails diameter [mm]": {},
                                 "pigtails cable dry mass [kg/m]": {},
                                 "pigtails total dry mass [kg]": {}}

            collection_point_df = pd.DataFrame(collection_point)

            dynamic_cable = {"dry mass [kg/m]": {},
                             "total dry mass [kg]": {},
                             "length [m]": {},
                             "diameter [mm]": {},
                             "MBR [m]": {},
                             "MBL [N]": {},
                             "upstream termination type [-]": {},
                             "upstream termination id [-]": {},
                             "upstream termination x coord [m]": {},
                             "upstream termination y coord [m]": {},
                             "upstream termination zone [-]": {},
                             "downstream termination type [-]": {},
                             "downstream termination id [-]": {},
                             "downstream termination x coord [m]": {},
                             "downstream termination y coord [m]": {},
                             "downstream termination zone [-]": {},
                             "upstream ei type [-]": {},
                             "upstream ei id [-]": {},
                             "downstream ei type [-]": {},
                             "downstream ei id [-]": {},
                             "buoyancy number [-]": {},
                             "buoyancy diameter [mm]": {},
                             "buoyancy length [m]": {},
                             "buoyancy weigth [kg]": {}}

            dynamic_cable_df = pd.DataFrame(dynamic_cable, dtype = object)

            static_cable = {"type [-]": {},
                            "dry mass [kg/m]": {},
                            "total dry mass [kg]": {},
                            "length [m]": {},
                            "diameter [mm]": {},
                            "MBR [m]": {},
                            "MBL [N]": {},
                            "upstream termination type [-]": {},
                            "upstream termination id [-]": {},
                            "upstream ei type [-]": {},
                            "upstream ei id [-]": {},
                            "downstream termination type [-]": {},
                            "downstream termination id [-]": {},
                            "downstream ei type [-]": {},
                            "downstream ei id [-]": {},
                            "trench type [-]": {}}

            static_cable_df = pd.DataFrame(static_cable, dtype = object)

            cable_route = {"static cable id [-]": {},
                           "x coord [m]": {},
                           "y coord [m]": {},
                           "zone [-]": {},
                           "soil type [-]": {},
                           "bathymetry [m]": {},
                           "burial depth [m]": {},
                           "split pipe [-]": {}}

            cable_route_df = pd.DataFrame(cable_route, dtype = object)

            connectors = {"type [-]": {},
                          "dry mass [kg]": {},
                          "lenght [m]": {},
                          "width [m]": {},
                          "height [m]": {},
                          "mating force [N]": {},
                          "demating force [N]": {}}

            connectors_df = pd.DataFrame(connectors)

            external_protection = {"protection type [-]": {},
                                   "x coord [m]": {},
                                   "y coord [m]": {},
                                   "zone [-]": {}}

            external_protection_df = \
                    pd.DataFrame(external_protection, dtype = object)

            topology = None
            landfall_df = None
            
        arg_dict = {'equipment': equipment,
                    'ports_df': ports_df,
                    'phase_order_df': phase_order_df,
                    'vessels_df': vessels_df,
                    'schedule_OLC': schedule_OLC,
                    'penetration_rate_df': penetration_rate_df,
                    'laying_rate_df': laying_rate_df,
                    'other_rates_df': other_rates_df,
                    'port_safety_factor_df': port_safety_factor_df,
                    'vessel_safety_factor_df': vessel_safety_factor_df,
                    'equipment_safety_factor_df':
                        equipment_safety_factor_df,
                    'whole_area': whole_area,
                    'metocean_df': metocean_df,
                    'device_df': device_df,
                    'sub_device_df': sub_device_df,
                    'landfall_df': landfall_df,
                    'entry_point_df': entry_point_df,
                    'layout_df': layout_df,
                    'collection_point_df': collection_point_df,
                    'dynamic_cable_df': dynamic_cable_df,
                    'static_cable_df': static_cable_df,
                    'cable_route_df': cable_route_df,
                    'connectors_df': connectors_df,
                    'external_protection_df': external_protection_df,
                    'topology': topology}
                    
        return arg_dict
        
    def _init_phase_dicts(self):
        
        cost_dict = {"Component": [],
                     "Equipment": [],
                     "Port": [],
                     "Vessel": []}

        time_dict = {"Component": [],
                     "Preparation": [],
                     "Operations": [],
                     "Transit": [],
                     "Waiting": []}

        return cost_dict, time_dict
        
    def _compile_phase(self, cost_dict,
                             time_dict,
                             phase_name,
                             phase_cost_dict,
                             phase_time_dict):
        
        cost_dict["Component"].append(phase_name)
        cost_dict["Equipment"].append(phase_cost_dict['Equipment'])
        cost_dict["Port"].append(phase_cost_dict['Port'])
        cost_dict["Vessel"].append(phase_cost_dict['Vessel'])
        
        time_dict["Component"].append(phase_name)
        time_dict["Preparation"].append(phase_time_dict['Prep'])
        time_dict["Operations"].append(phase_time_dict['Sea'])
        time_dict["Transit"].append(phase_time_dict['Transit'])
        time_dict["Waiting"].append(phase_time_dict['Wait'])
        
        return
        
