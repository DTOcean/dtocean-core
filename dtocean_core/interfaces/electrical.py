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
This module contains the package interface to the dtocean electrical sub
systems module.

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. module:: electrical
   :platform: Windows
   :synopsis: Aneris interface for dtocean_core package
   
.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
                  Vincenzo Nava <vincenzo.nava@tecnalia.com>
"""

# Set up logging
import logging

module_logger = logging.getLogger(__name__)

import pickle

import numpy as np
import pandas as pd

from dtocean_electrical.main import Electrical
from dtocean_electrical.inputs import (ElectricalComponentDatabase,
                                       ElectricalMachineData,
                                       ElectricalArrayData,
                                       ConfigurationOptions,
                                       ElectricalSiteData,
                                       ElectricalExportData
                                       )

from aneris.boundary.interface import MaskVariable

from . import ModuleInterface
from ..utils.hydrodynamics import bearing_to_radians
from ..utils.electrical import sanitise_network
from ..utils.network import find_marker_key


class ElectricalInterface(ModuleInterface):
    
    '''Interface to the electrical sub systems module
    
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
        
        return "Electrical Sub Systems"
        
    @classmethod         
    def declare_weight(cls):
        
        return 2

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

        input_list  =  ['component.static_cable',
                        'component.dynamic_cable',
                        'component.wet_mate_connectors',
                        'component.dry_mate_connectors',
                        'component.transformers',
                        'component.collection_points',
                        'component.collection_point_cog',
                        'component.collection_point_foundations',
                        'component.switchgear',
                        'component.power_quality',
                        'bathymetry.layers',
                        'farm.max_seabed_temp',
                        'farm.max_soil_resistivity',
                        'farm.max_surface_current_10_year',
                        'farm.nogo_areas',
                        'farm.direction_of_max_surface_current',
                        'farm.wave_direction_100_year',
                        'farm.shipping_hist',
                        'corridor.layers',
                        'corridor.max_seabed_temp',
                        'corridor.max_soil_resistivity',
                        'corridor.tidal_current_flow',
                        'corridor.nogo_areas',
                        'corridor.tidal_current_direction',
                        'corridor.wave_direction',
                        'corridor.shipping_hist',
                        'corridor.landing_point',
                        'project.layout',
                        'project.mean_power_hist_per_device',
                        'project.annual_energy',
                        'project.main_direction',
                        'device.system_type',
                        'device.power_rating',
                        'device.voltage',
                        'device.connector_type',
                        'device.prescribed_footprint_radius',
                        'device.footprint_coords',
                        'device.power_factor',
                        'device.constant_power_factor',
                        
                         MaskVariable('device.system_draft',
                                      'device.system_type',
                                      ['Tidal Floating', 'Wave Floating']),

                         MaskVariable('device.umbilical_type',
                                      'device.system_type',
                                      ['Tidal Floating', 'Wave Floating']),

                         MaskVariable('device.umbilical_connection_point',
                                      'device.system_type',
                                      ['Tidal Floating', 'Wave Floating']),
                                      
                         MaskVariable('project.umbilical_safety_factor',
                                      'device.system_type',
                                      ['Tidal Floating', 'Wave Floating']),
                                      
                        'project.network_configuration',
                        'project.export_target_burial_depth',
                        'project.target_burial_depth',
                        'project.devices_per_string',
                        'project.equipment_gradient_constraint',
                        'component.installation_soil_compatibility',
                        'project.export_voltage',
                        'project.voltage_limit_min',
                        'project.voltage_limit_max',
                        'project.onshore_infrastructure_cost',
                        'project.onshore_losses',
                        'project.offshore_reactive_limit',
                        'project.ac_power_flow',
                        'project.control_signal_type',
                        'project.control_signal_cable',
                        'project.control_signal_channels',
                        'options.user_installation_tool',
                        'constants.gravity'
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
        
        output_list = ['project.annual_energy',
                       'project.array_efficiency',
                       'project.electrical_network',
                       'project.electrical_component_data',
                       'project.electrical_economics_data',
                       'project.cable_routes',
                       'project.substation_props',
                       'project.substation_layout',
                       'project.substation_cog',
                       'project.substation_foundation_location',
                       'device.umbilical_type',
                       'project.umbilical_cable_data',
                       'project.umbilical_seabed_connection',
                       'project.selected_installation_tool',
                       'project.electrical_network_efficiency'
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
                
        optional = [ 'component.installation_soil_compatibility',
                     'corridor.nogo_areas',
                     'project.export_target_burial_depth',
                     'project.export_voltage',
                     'device.constant_power_factor',
                     'device.footprint_coords',
                     'device.power_factor',
                     'device.prescribed_footprint_radius',
                     'device.umbilical_type',
                     'project.ac_power_flow',
                     'project.control_signal_cable',
                     'project.control_signal_channels',
                     'project.control_signal_type',
                     'project.devices_per_string',
                     'project.main_direction',
                     'farm.nogo_areas',
                     'project.offshore_reactive_limit',
                     'project.onshore_infrastructure_cost',
                     'project.onshore_losses',
                     'project.target_burial_depth',
                     'project.voltage_limit_max',
                     'project.voltage_limit_min',
                     'options.user_installation_tool'                    
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
                  
        id_map = {"bathymetry" : "bathymetry.layers", 
                  "nogo_areas": "farm.nogo_areas",
                  "current_dir": "farm.direction_of_max_surface_current",
                  "max_surf_current":  "farm.max_surface_current_10_year",
                  "wave_dir":"farm.wave_direction_100_year",
                  "device_type": "device.system_type", 
                  "power_rating": "device.power_rating",
                  "layout": "project.layout",
                  "annual_energy": "project.annual_energy",
                  "static_cable": "component.static_cable",
                  "dynamic_cable": "component.dynamic_cable",
                  "wet_mate_connectors": "component.wet_mate_connectors",
                  "dry_mate_connectors": "component.dry_mate_connectors",
                  "transformers": "component.transformers",
                  "collection_points": "component.collection_points",
                  "collection_point_cog": "component.collection_point_cog",
                  "collection_point_foundations": 
                                  "component.collection_point_foundations",
                  "switchgear": "component.switchgear",
                  "power_quality": "component.power_quality",
                  "max_temp": "farm.max_seabed_temp",
                  "max_soil_res": "farm.max_soil_resistivity",
                  "shipping_hist": "farm.shipping_hist",     
                  "voltage": "device.voltage",
                  "offshore_reactive_limit": "project.offshore_reactive_limit",
                  "network_configuration": "project.network_configuration",           
                  "ac_power_flow": "project.ac_power_flow",
                  "target_burial_depth": "project.target_burial_depth", 
                  "devices_per_string": "project.devices_per_string",
                  "corridor_current_dir": "corridor.tidal_current_direction",
                  "corridor_nogo_areas": "corridor.nogo_areas",
                  "corridor_max_surf_current": "corridor.tidal_current_flow",    
                  "corridor_wave_dir": "corridor.wave_direction",
                  "corridor_shipping_hist": "corridor.shipping_hist",
                  "corridor_target_burial_depth":
                      "project.export_target_burial_depth",
                  "corridor_landing_point": "corridor.landing_point",
                  "export_strata": "corridor.layers",
                  "corridor_max_temp": "corridor.max_seabed_temp",
                  "corridor_max_soil_res": "corridor.max_soil_resistivity",     
                  "corridor_voltage": "project.export_voltage",
                  "equipment_gradient_constraint" :
                      "project.equipment_gradient_constraint",
                  "installation_soil_compatibility" :
                      "component.installation_soil_compatibility",
                  "control_signal_type": "project.control_signal_type",
                  "control_signal_cable": "project.control_signal_cable",
                  "control_signal_channels": "project.control_signal_channels",
                  "min_voltage": "project.voltage_limit_min",
                  "max_voltage": "project.voltage_limit_max",
                  "footprint_radius" : "device.prescribed_footprint_radius",
                  "footprint_coords" : "device.footprint_coords",
                  "onshore_infrastructure_cost" :
                      "project.onshore_infrastructure_cost",
                  "onshore_losses" : "project.onshore_losses",
                  "mean_power_hist_per_device" :
                      "project.mean_power_hist_per_device",
                  "electrical_network" : "project.electrical_network",
                  "electrical_component_data" :
                      "project.electrical_component_data",
                  "electrical_economics_data":
                      "project.electrical_economics_data",
                  "cables_routes" : "project.cable_routes",
                  "substation_props" : "project.substation_props",
                  "power_factor": "device.power_factor",
                  "constant_power_factor" : "device.constant_power_factor",
                  "umbilical_cables" : "project.umbilical_cable_data",
                  "dev_umbilical_point": "device.umbilical_connection_point",
                  "system_draft": 'device.system_draft',
                  "umbilical_sf": "project.umbilical_safety_factor",
                  "main_direction": "project.main_direction",
                  'substation_layout': 'project.substation_layout',
                  'substation_cog': 'project.substation_cog',
                  'substation_foundations':
                      'project.substation_foundation_location',
                  "seabed_connection": "project.umbilical_seabed_connection",
                  'array_efficiency': 'project.array_efficiency',
                  "device_connector_type": "device.connector_type",
                  "umbilical_type": "device.umbilical_type",
                  "users_tool": "options.user_installation_tool",
                  "selected_tool": "project.selected_installation_tool",
                  "gravity": "constants.gravity",
                  'network_efficiency': 'project.electrical_network_efficiency'
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
                                               
        input_dict = self.get_input_dict(self.data)
                                       
        if debug_entry: return

        if export_data:
            pickle.dump(input_dict, open("electrical_inputs.pkl", "wb" ))
        
        elec = Electrical(input_dict["site_data"],
                          input_dict["array_data"],
                          input_dict["export_data"],
                          input_dict["options"],
                          input_dict["database"])
        solution, installation_tool = elec.run_module()
        
        if export_data:
            pickle.dump(solution, open("electrical_outputs.pkl", "wb" ))
                        
        # Convert to MWh 
        annual_energy_togrid = solution.annual_yield / 1e6
        network_efficiency = annual_energy_togrid / self.data.annual_energy
                                                    
        # Protect from stupid answers
        if network_efficiency > 1:
            
            logMsg = ("Annual output has increased to {} MWh from {} MWh "
                      "resulting in a network efficiency of {}. Capping at "
                      "1").format(annual_energy_togrid,
                                  self.data.annual_energy,
                                  network_efficiency)
            module_logger.warning(logMsg)
            
            self.data.network_efficiency = 1.
            
        else:
            
            self.data.network_efficiency = network_efficiency
        
        self.data.network_efficiency
        
        name_map = {"db ref" : "Key Identifier",
                    "cost" : "Cost",
                    "quantity" : "Quantity",
                    "year" : "Year"
                    }

        self.data.electrical_economics_data = \
                        solution.economics_data.rename(columns=name_map)
                        
        self.data.array_efficiency = solution.annual_efficiency
                        
        sane_hier = sanitise_network(solution.hierarchy)
        sane_bom = sanitise_network(solution.network_design)

        # Collect installation tool
        self.data.selected_tool = installation_tool

        # Build network dictionary
        raw_network = {"topology": sane_hier,
                       "nodes": sane_bom}

        self.data.electrical_network = raw_network
        
        # Build supplementary data
        name_map = {"db ref" : "Key Identifier",
                    "install_type" : "Installation Type",
                    "quantity" : "Quantity",
                    "utm_x" :  "UTM X",
                    "utm_y" : "UTM Y",
                    "marker" : "Marker"
                    }
                     
        self.data.electrical_component_data = solution.b_o_m.rename(
                                                            columns=name_map) 
                                                            
        name_map = {"db ref" : "Key Identifier",
                    "burial_depth" : "Burial Depth",
                    "split pipe" : "Split Pipe",
                    "x":  "UTM X",
                    "y": "UTM Y",
                    'layer 1 start': "Depth",
                    'layer 1 type': "Sediment",
                    "marker" : "Marker"
                    }
                     
        self.data.cables_routes = solution.cable_routes.rename(
                                                            columns=name_map)
                
        if solution.collection_points:
            
            substation_props_df = solution.collection_points_design
            new_headers = [x.title() for x in
                                        substation_props_df.columns.values]
            substation_props_df.columns = new_headers
                    
            # Create indentifiers
            n_arrays = 0
                   
            for index, row in substation_props_df.iterrows():
                
                if "Radial" in self.data.network_configuration:
                    
                    if n_arrays > 0:
                        
                        errStr = ("Only one 'array' type substation may be "
                                  "specified")
                        raise ValueError(errStr)
                        
                    sub_id = "array"
                    n_arrays += 1
                
                elif row["Type"] == 'subsea':
                    
                    sub_id = find_marker_key(sane_bom,
                                             row["Marker"],
                                             return_top_key=True).lower()
                    
                    if sub_id is None:
                        
                        errStr = ("No substation found with marker "
                                  "'{}'").format(row["Marker"])
                        raise ValueError(errStr)
                    
                elif row["Type"] == 'array':
                    
                    if n_arrays > 0:
                        
                        errStr = ("Only one 'array' type substation may be "
                                  "specified")
                        raise ValueError(errStr)
                        
                    sub_id = "array"
                    n_arrays += 1
                    
                else:
                    
                    errStr = ("Unrecognised substation type: "
                              "'{}'").format(row["Type"])
                    raise ValueError(errStr)
                    
                substation_props_df.loc[index,
                                        'Substation Identifier'] = sub_id
                    
            # Break out positional variables
            sub_ids = substation_props_df['Substation Identifier']
            origin = substation_props_df.pop("Origin")
            cog = substation_props_df.pop("Centre_Of_Gravity")
            foundations = substation_props_df.pop("Foundation Locations")
            
            raw_origin_dict = {}
            raw_cog_dict = {}
            raw_found_dict = {}
            
            for i, sub_id in enumerate(sub_ids):
                
                raw_origin_dict[sub_id] = origin.ix[i]
                raw_cog_dict[sub_id] = cog.ix[i]
                raw_found_dict[sub_id] = [foundations.ix[i]]
            
            self.data.substation_props = substation_props_df
            self.data.substation_layout = raw_origin_dict
            self.data.substation_cog = raw_cog_dict
            self.data.substation_foundations = raw_found_dict
            
        if solution.umbilical_cables:
            
            umbilical_cables = solution.umbilical_cable_design
            
            device_ids = umbilical_cables["device"].values
            seabed_points = umbilical_cables.pop("seabed_connection_point")
            umbilical_cables = umbilical_cables.drop("device", axis=1)

            name_map = {
                "db ref": "Key Identifier",
                "length": "Length",
                "marker": "Marker"
                }
        
            umbilical_cables = umbilical_cables.rename(columns=name_map)
            
            # Fake missing columns                                                
            umbilical_cables["Dry Mass"] = np.nan
            umbilical_cables["Required Floatation"] = np.nan
            umbilical_cables["Floatation Length"] = np.nan
            
            # Store all umbilical cable data
            self.data.umbilical_cables = umbilical_cables
            
            # Get the type of the first cable
            all_ids = umbilical_cables["Key Identifier"]
            self.data.umbilical_type = all_ids[0]
            
            seabed_point_dict = {}
            
            for dev_id, point in zip(device_ids,
                                     seabed_points.values):

                seabed_point_dict[dev_id.title()] = point

            self.data.seabed_connection = seabed_point_dict
            
    @classmethod    
    def get_input_dict(cls, data):
        
#    class ElectricalSiteData(object):
#    
#        '''Define the electrical systems site data object. This includes all
#        geotechnical and geophysical data.
#        
#        Args:
#            bathymetry (pd.dataframe) [m]: the vertical profile of the sea bottom
#                and geotechnical layers at each (given) UTM coordinate within the
#                lease area; expressed as [id,i,j,x,y,layer1depth,layer1type,..,..,
#                layerNdepth, layerNtype], where: i and j are local indices; x,y are
#                grid coordinates and layerndepth, laterntype define the start depth
#                and the type of layer n (from n=1:N).
#            exclusion_zones (list) [-]: list containing the UTM coordinates of the
#                                        exclusion zone polygons within the lease
#                                        area.
#            max_temp (float) [degrees C]: the maximum seabed temperature recorded in
#                                          the lease area.
#            max_soil_res (float) [K.m/W]: the maximum soil resistivity recorded in
#                                          the lease area.
#            tidal_current_direction (float) [rad]: the tidal stream current
#                                                   prevalent direction in the lease
#                                                   area.
#            tidal_current_flow (float) [m/s]: maximum tidal stream current velocity
#                                              in the lease area.
#            wave_direction (float) [rad]: the prevalent wave direction in the lease
#                                          area.
#            shipping (numpy.ndarray) [-]: histogram of shipping activity in the
#                                          lease area; expressed as [val1, val2]
#                                          where: val1 is the bin edge of the vessel
#                                          deadweight (T) val2 is the frequency (pc)
            
        renaming_bathymetry = {"loose sand" : "ls",
                               "medium sand" : "ms",
                               "dense sand" : "ds",
                               "very soft clay" : "vsc",
                               "soft clay" : "sc",
                               "firm clay" : "fc",
                               "stiff clay" : "stc",
                               "hard glacial till" : "hgt",
                               "cemented" : "c",
                               "soft rock coral" : "src",
                               "hard rock" : "hr",
                               "gravel cobble" : "gc"                            
                               }

        bathymetry_pd_unsort = data.bathymetry.to_dataframe()
        bathymetry_pd = bathymetry_pd_unsort.unstack(level='layer')
        bathymetry_pd = bathymetry_pd.swaplevel(1, 1, axis=1)
        bathymetry_pd = bathymetry_pd.sortlevel(1, axis=1)

        cartesian_product_index = bathymetry_pd.index.labels
        
        bathymetry = bathymetry_pd.reset_index()
        bathymetry.insert(0,'i',cartesian_product_index[0].astype(np.int64))
        bathymetry.insert(1,'j',cartesian_product_index[1].astype(np.int64))
        bathymetry.insert(0,'id',bathymetry.index)
        
        bathymetry.columns = [' '.join(col).strip()
                                        for col in bathymetry.columns.values]
    
        mapping = {"id":"id","i":"i","j":"j","x":"x","y":"y"}
    
        for i in range (5,(len(bathymetry.columns))):
            split_name = bathymetry.columns.values[i].split()
            if split_name[0] == "sediment":
                mapping[bathymetry.columns.values[i]]= "layer {} type".format(
                                                                split_name[2])  
            elif split_name[0] == "depth":
                mapping[bathymetry.columns.values[i]]= "layer {} start".format(
                                                                split_name[2]) 
        
        bathymetry = bathymetry.rename(columns=mapping)
        
        bathymetry = bathymetry.replace(to_replace = renaming_bathymetry)

        # Convert the directions from bearings to radians
        site_current_dir = bearing_to_radians(data.current_dir)
        site_wave_dir = bearing_to_radians(data.wave_dir)

        # Only use bin ends for shipping history
        shipping_hist = []
        full_bins = data.shipping_hist["bins"]
        
        for i, value in enumerate(data.shipping_hist["values"]):
            bin_edge = [full_bins[i+1], value]
            shipping_hist.append(bin_edge)
                        
        site = ElectricalSiteData(bathymetry,
                                  data.nogo_areas,
                                  data.max_temp,
                                  data.max_soil_res,
                                  site_current_dir,
                                  data.max_surf_current,
                                  site_wave_dir,
                                  shipping_hist)
        
#    class ElectricalExportData(object):
#        
#        '''Define the electrical systems export data object. This includes all
#        geotechnical and geophysical data.
#    
#        Args:
#            bathymetry (pd.dataframe) [m]: the vertical profile of the sea bottom
#                and geotechnical layers at each (given) UTM coordinate within the
#                export area; expressed as [id,i,j,x,y,layer1depth,layer1type,..,..,
#                layerNdepth, layerNtype], where: i and j are local indices; x,y are
#                grid coordinates and layerndepth, laterntype define the start depth
#                and the type of layer n (from n=1:N).
#            exclusion_zones (list) [-]: list containing the UTM coordinates of the
#                exclusion zone polygons within the export area.
#            max_temp (float) [degrees C]: the maximum seabed temperature recorded 
#                in the export area.
#            max_soil_res (float) [K.m/W]: the maximum soil resistivity recorded in
#                the export area.
#            tidal_current_direction (float) [rad]: the tidal stream current
#                prevalent direction in the export area.
#            tidal_current_flow (float) [m/s]: maximum tidal stream current velocity
#                in the export area.
#            wave_direction (float) [rad]: the prevalent wave direction in the
#                export area.
#            shipping (numpy.ndarray) [-]: histogram of shipping activity in the
#                export area; expressed as [val1, val2] where: val1 is the bin edge
#                of the vessel deadweight (T) val2 is the frequency (pc).
                                          
        export_bathymetry_pd_unsort = data.export_strata.to_dataframe()
        export_bathymetry_pd = export_bathymetry_pd_unsort.unstack(
                                                                level='layer')
        export_bathymetry_pd = export_bathymetry_pd.swaplevel(1, 1, axis=1)
        export_bathymetry_pd = export_bathymetry_pd.sortlevel(1, axis=1)
        
        export_cartesian_product_index = export_bathymetry_pd.index.labels
        
        export_bathymetry=export_bathymetry_pd.reset_index()
        export_bathymetry.insert(0,
                                 'i',
                                 export_cartesian_product_index[0].astype(
                                                                    np.int64))
        export_bathymetry.insert(1,
                                 'j',
                                 export_cartesian_product_index[1].astype(
                                                                    np.int64))
        export_bathymetry.insert(0,'id',export_bathymetry.index)
        
        export_bathymetry.columns = [' '.join(col).strip()
                                for col in export_bathymetry.columns.values]
    
        export_mapping = {"id":"id","i":"i","j":"j","x":"x","y":"y"}
    
        for i in range (5,(len(export_bathymetry.columns))):
            split_name = export_bathymetry.columns.values[i].split()
            if split_name[0] == "sediment":
                export_mapping[export_bathymetry.columns.values[i]] = \
                                        "layer {} type".format(split_name[2])  
            elif split_name[0] == "depth":
                export_mapping[export_bathymetry.columns.values[i]] = \
                                        "layer {} start".format(split_name[2]) 

        export_bathymetry = export_bathymetry.rename(columns=export_mapping)
        
        export_bathymetry = export_bathymetry.replace(
                                              to_replace=renaming_bathymetry)
        
        # Convert the directions from bearings to radians
        export_current_dir = bearing_to_radians(data.corridor_current_dir)
        export_wave_dir = bearing_to_radians(data.corridor_wave_dir)

        # Only use bin ends for shipping history
        export_shipping_hist = []
        full_bins = data.corridor_shipping_hist["bins"]
        
        for i, value in enumerate(data.corridor_shipping_hist["values"]):
            bin_edge = [full_bins[i+1], value]
            export_shipping_hist.append(bin_edge)

        export = ElectricalExportData(export_bathymetry,
                                      data.corridor_nogo_areas,
                                      data.corridor_max_temp,
                                      data.corridor_max_soil_res,
                                      export_current_dir,
                                      data.corridor_max_surf_current,
                                      export_wave_dir,
                                      export_shipping_hist)
                                      
#    class ElectricalMachineData(object):
#    
#        '''Container class to carry the OEC device object.
#    
#        Args:
#            technology (str) [-]: floating or fixed
#            power (float) [W]: OEC rated power output
#            voltage (float) [V]: OEC rated voltage at point of network connection
#            connection (str) [-]: Type of connection, either 'wet-mate', 'dry-mate'
#                or 'hard-wired'.
#            variable_power_factor (list) [-]: List of tuples for OEC power factor;
#                                     val1 = power in pu, val2 = pf.
#            constant_power_factor (float) [-]: A power factor value to be applied
#                at every point of analysis.
#            footprint_radius (float) [m]: The device footprint defined by radius.
#            footprint_coords (list) [m]: The device footprint by utm [x,y,z]
#                coordinates.
#            connection_point (tuple) [m]: Location of electrical connection, as
#                (x, y, z) coordinates in local coordinate system.
#            equilibrium_draft (float) [m]: Device equilibrium draft without mooring
#                system.
                                  
        if "floating" in data.device_type.lower():
            dev_type = "floating"
            umbilical_connection = data.dev_umbilical_point
        else: 
            dev_type = "fixed"   
            umbilical_connection = None

        # Translate connector type
#        translate_connector = {"Wet-Mate"  : 1,
#                               "Dry-Mate"  : 2,
#                               "Hard-Wired" : 3}
#        device_connector_int = translate_connector[
#                                            data.device_connector_type]
                                            
        power_rating_watts = data.power_rating * 1.e6
        
        if data.power_factor is not None:
            variable_power_factor = data.power_factor.tolist()
        else:
            variable_power_factor = None
                
        machine = ElectricalMachineData(
                                    dev_type,
                                    power_rating_watts,
                                    data.voltage,
                                    data.device_connector_type.lower(),
                                    variable_power_factor,
                                    data.constant_power_factor,
                                    data.footprint_radius,
                                    data.footprint_coords, #implent either... or... 
                                    umbilical_connection,
                                    data.system_draft)

#    class ElectricalArrayData(object):
#                                        
#        '''Container class to carry the array object. This inherets the machine.
#    
#        Args:
#            ElectricalMachineData (class) [-]: class containing the machine
#                                               specification
#            landing_point (tuple) [m]: UTM coordinates of the landing areas;
#                                       expressed as [x,y, id]
#            layout (dict) [m]: OEC layout in dictionary from WP2;
#                               key = device id,
#                               value = UTM coordinates, as [x,y,z]
#            n_devices (int) [-]: the number of OECs in the array.
#            array_output (numpy.ndarray) [pc]: the total array power output in
#                histogram form.
#            control_signal_type (str) [-]: the type of control signal used in the
#                                           array, accepts 'fibre optic'.
#            control_signal_cable (bool) [-]: defines if the control signal is to 
#                                             packaged in the power cable (True) or
#                                             not (False)
#            control_signal_channels (int) [-]: defines the number of control signal
#                                               pairs per device
#            voltage_limit_min (float) [pu]: the minimum voltage allowed in the
#                                            offshore network
#            voltage_limit_max (float) [pu]: the maximum voltage allowed in the
#                                            offshore network
#            offshore_reactive_limit (list) [-]: the target power factor at the
#                                                offshore collection point. This is
#                                                a list of pairs: val1 = power [pu],
#                                                val2 = reactive power [pu]
#            onshore_infrastructure_cost (float) [E]:C ost of the onshore
#                infrastructure, for use in LCOE calculation.
#            onshore_losses (float) [pc]: Electrical losses of the onshore
#                infrastructure, entered as percentage of annual energy yield.
#            orientation_angle (float) [degree]: Device orientation angle.
                                    
        occurrences = []
        
        mean_power_hist = data.mean_power_hist_per_device.values()
        
        for item in mean_power_hist:
            
            values = np.array(item["values"])
            bins = np.array(item["bins"])
            
            occurrence = values * (bins[1:] - bins[:-1])
            occurrences.append(occurrence)

        array_output = np.array([sum(x) / len(occurrences)
                                                for x in zip(*occurrences)])
            
        if not np.isclose(sum(array_output), 1):
            
            # Forcibly normalise the power outputs
            given_occurance = sum(array_output)

            logmsg = ("Sum of given power histogram is {}. Forcibly "
                      "normalising to unity").format(given_occurance)
            module_logger.warn(logmsg)
            
            array_output = array_output / given_occurance
            
        assert np.isclose(sum(array_output), 1)
            
        layout_dict = {key.capitalize() : list(item.coords)[0]
                        for key, item in data.layout.items()}
                            
        corr_land_point = list(data.corridor_landing_point.coords)[0]

        # Build optional arguments        
        opt_args = {}
        
        if data.onshore_infrastructure_cost is not None:
            opt_args["onshore_infrastructure_cost"] = \
                                        data.onshore_infrastructure_cost
                                        
        if data.onshore_losses is not None:
            opt_args["onshore_losses"] = data.onshore_losses
            
        if data.control_signal_type is not None:
            opt_args["control_signal_type"] = data.control_signal_type
            
        if data.control_signal_cable is not None:
            opt_args["control_signal_cable"] = data.control_signal_cable
            
        if data.control_signal_channels is not None:
            opt_args["control_signal_channels"] = \
                                        data.control_signal_channels
                                        
        if data.min_voltage is not None:
            opt_args["voltage_limit_min"] = data.min_voltage
            
        if data.max_voltage is not None:
            opt_args["voltage_limit_max"] = data.max_voltage
            
        if data.offshore_reactive_limit is not None:
            opt_args["offshore_reactive_limit"] = \
                                        data.offshore_reactive_limit
                                        
        if data.main_direction is not None:
            opt_args["orientation_angle"] = data.main_direction
        
        array = ElectricalArrayData(machine,
                                    corr_land_point,
                                    layout_dict,
                                    len(layout_dict),
                                    array_output,
                                    **opt_args)
                                    
#    class ConfigurationOptions(object):
#    
#        '''Container class for the configuration options defined in the core. These
#        can be specificed by the user at GUI interface or by the core during the
#        global optimisation process.
#        
#        Args:
#            network_configuration (list, str) [-]: list of networks to evaluate:
#                radial or star.
#            export_voltage (float) [V]: export cable voltage.
#            export_cables (int) [-]: number of export cables.
#            ac_power_flow (Bool) [-]: run full ac power flow (True) or dc (False).
#            target_burial_depth_array (float) [m]: array cable burial depth.
#            target_burial_depth_export (float) [m]: export cable burial depth.
#            connector_type (string) [-]: 'wet mate' or 'dry mate'. This will be
#                applied to all connectors.
#            collection_point_type (string) [-]: 'subsea' or 'surface'. This will be
#                applied to all collection points.
#            devices_per_string (int) [-]: number of devices per string.
#            equipment_gradient_constraint (float) [deg]: the maximum seabed
#                gradient considered by the cable routing analysis.
#            equipment_soil_compatibility (pd.DataFrame) [m/s]: the equipment soil
#                installation compatibility matrix.
#            umbilical_safety_factor (float) [-]: Umbilical safety factor from
#                DNV-RP-F401.
#
                                
        if "floating" in data.device_type.lower():
            safety_factor = data.umbilical_sf
        else:
            safety_factor = None
            
        # Make columns lower case on installation_soil_compatibility table
        renaming_columns = {"loose sand" : "ls",
                            "medium sand" : "ms",
                            "dense sand" : "ds",
                            "very soft clay" : "vsc",
                            "soft clay" : "sc",
                            "firm clay" : "fc",
                            "stiff clay" : "stc",
                            "hard glacial till" : "hgt",
                            "cemented" : "c",
                            "soft rock coral" : "src",
                            "hard rock" : "hr",
                            "gravel cobble" : "gc"                            
                            }

        up_cols = data.installation_soil_compatibility.columns
        low_cols = [x.lower() for x in up_cols]
        columns_renamed = [renaming_columns[x] for x in low_cols]
        data.installation_soil_compatibility.columns = columns_renamed       

        options = ConfigurationOptions(
                                    [data.network_configuration],
                                    data.corridor_voltage,
                                    None,
                                    data.ac_power_flow,
                                    data.target_burial_depth,
                                    data.corridor_target_burial_depth,
                                    None,
                                    None,
                                    data.devices_per_string,
                                    data.equipment_gradient_constraint,
                                    data.installation_soil_compatibility,
                                    data.users_tool,
                                    safety_factor,
                                    data.gravity,
                                    data.umbilical_type,
                                    )
        
        database = cls.get_component_database(
                                       data.static_cable,
                                       data.dynamic_cable,
                                       data.wet_mate_connectors,
                                       data.dry_mate_connectors,
                                       data.transformers,
                                       data.collection_points,
                                       data.collection_point_cog,
                                       data.collection_point_foundations,
                                       data.switchgear,
                                       data.power_quality)
        
        input_dict = {"site_data": site, 
                      "array_data": array, 
                      "export_data": export, 
                      "options": options, 
                      "database": database
                      }
        
        return input_dict
    
    @classmethod
    def get_component_database(cls, static_cable,
                                    dynamic_cable,
                                    wet_mate_connectors,
                                    dry_mate_connectors,
                                    transformers,
                                    collection_points,
                                    collection_point_cog,
                                    collection_point_foundations,
                                    switchgear,
                                    power_quality):
        
        name_map = {"Key Identifier": "id",
                    "Number of Conductors": "n",
                    "Rated Voltage": "v_rate",
                    "Rated Current in Air": "a_air",
                    "Rated Current if Buried": "a_bury",
                    "Rated Current in J Tube": "a_jtube",
                    "DC Resistance": "r_dc",
                    "AC Resistance": "r_ac",
                    "Inductive Reactance": "xl",
                    "Capacitance": "c",
                    "Colour": "colour",
                    "Dry Mass": "dry_mass",
                    "Wet Mass": "wet_mass",
                    "Diameter": "diameter",
                    "Minimum Bend Radius": "mbr",
                    "Minimum Break Load": "mbl",
                    "Fibre": "fibre",
                    "Cost": "cost",
                    "Max Temperature": "max_operating_temp",
                    "Environmental Impact": "environmental_impact"}
        
        static_cable_df = static_cable
        static_cable_df = static_cable_df.rename(columns=name_map)
        
        dynamic_cable_df = dynamic_cable
        dynamic_cable_df.drop(["Environmental Impact"],
                              1)
        dynamic_cable_df = dynamic_cable_df.rename(columns=name_map)
        
        name_map = { "Key Identifier" : "id",
                     "Number Of Contacts" : "n",
                     "Rated Voltage" : "v_rate",
                     "Rated Current" : "a_rate",
                     "Dry Mass" : "dry_mass",
                     "Height" : "height",
                     "Width" : "width",
                     "Depth" : "depth",
                     "Mating" : "mating",
                     "Demating" : "demating",
                     "Colour" : "colour",
                     "Outer Coating" : "outer_coating",
                     "Fibre" : "fibre",
                     "Cost" : "cost",
                     "Max Water Depth" : "max_water_depth",
                     "Min Temperature" : "min_temperature",
                     "Max Temperature" : "max_temperature"}
                     
        wet_mate_connectors_df = wet_mate_connectors
        
        # Calculate mean of CSA values
        wet_mate_connectors_df["cable_csa"] = \
                wet_mate_connectors_df[["Min Cable CSA",
                                        "Max Cable CSA" ]].mean(axis=1)
    
        wet_mate_connectors_df.drop([
                            "Min Cable CSA",
                            "Max Cable CSA",
                            "Environmental Impact"],
                            1)
        wet_mate_connectors_df = wet_mate_connectors_df.rename(
                                                            columns=name_map)
        
        dry_mate_connectors_df = dry_mate_connectors
        
        # Calculate mean of CSA values
        dry_mate_connectors_df["cable_csa"] = \
                wet_mate_connectors_df[["Min Cable CSA",
                                        "Max Cable CSA" ]].mean(axis=1)
    
        dry_mate_connectors_df.drop([
                            "Min Cable CSA",
                            "Max Cable CSA",
                            "Environmental Impact"],
                            1)
        dry_mate_connectors_df = dry_mate_connectors_df.rename(
                                                            columns=name_map)
        
        name_map = { "Key Identifier" : "id",
                     "Windings" : "windings",
                     "Rating" : "rating",
                     "V1" : "v1",
                     "V2" : "v2",
                     "V3" : "v3",
                     "Dry Mass" : "dry_mass",
                     "Height" : "height",
                     "Width" : "width",
                     "Depth" : "depth",
                     "Colour" : "colour",
                     "Outer Coating" : "outer_coating",
                     "Cost" : "cost",
                     "Cooling" : "cooling",
                     "Max Water Depth" : "max_water_depth",
                     "Min Temperature" : "min_temperature",
                     "Max Temperature" : "max_temperature",
                     "Impedance" : "impedance"}
                     
        transformers_df = transformers
        transformers_df.drop(["Environmental Impact"],
                             1)
        transformers_df = transformers_df.rename(columns=name_map)
        
        name_map = { "Key Identifier" : "id",
                     "Input" : "input",
                     "Output" : "output",
                     "Input Connector" : "input_connector",
                     "Output Connector" : "output_connector",
                     "V1" : "v1",
                     "V2" : "v2",
                     "Rated Current" : "a_rate",
                     "Dry Mass" : "dry_mass",
                     "Wet Mass" : "wet_mass",
                     "Height" : "height",
                     "Width" : "width",
                     "Depth" : "depth",
                     "Colour" : "colour",
                     "Outer Coating" : "outer_coating",
                     "Foundation" : "foundation",
                     "Busbar" : "busbar",
                     "Cost" : "cost",
                     "Cooling" : "cooling",
                     "Max Water Depth" : "max_water_depth",
                     "Fibre" : "fibre",
                     "Operating Environment" : "operating_environment",
                     "Min Temperature" : "min_temperature",
                     "Max Temperature" : "max_temperature",
                     "Wet Frontal Area": "wet_frontal_area",
                     "Dry Frontal Area": "dry_frontal_area",
                     "Wet Beam Area": "wet_beam_area",
                     "Dry Beam Area": "dry_beam_area",
                     "Orientation Angle": "orientation_angle"
                     }
                     
        collection_points_df = collection_points
        collection_points_df.drop(["Environmental Impact"],
                                  1)
        collection_points_df = collection_points_df.rename(columns=name_map)
        collection_points_df = collection_points_df.set_index("id")

        # Build in centre of gravity
        cog_dict = collection_point_cog
        cog_df = pd.DataFrame(cog_dict.items(),
                              columns=["id", "gravity_centre"])
        cog_df = cog_df.set_index("id")
                              
        # Build in foundation locations
        found_dict = collection_point_foundations
        found_df = pd.DataFrame(found_dict.items(),
                                columns=["id", "foundation_loc"])
        found_df = found_df.set_index("id")
        
        collection_points_df = pd.concat([collection_points_df,
                                          cog_df,
                                          found_df],
                                          axis=1)
                                         
        collection_points_df = collection_points_df.reset_index()
        
        name_map = { "Key Identifier"  : "id",
                     "Rated Voltage"  : "v_rate",
                     "Rated Current"  : "a_rate",
                     "Dry Mass"  : "dry_mass",
                     "Height"  : "height",
                     "Width"  : "width",
                     "Depth"  : "depth",
                     "Max Water Depth"  : "max_water_depth",
                     "Operating Environment"  : "operating_environment",
                     "Outer Coating"  : "outer_coating",
                     "Colour"  : "colour",
                     "Min Temperature"  : "min_temperature",
                     "Max Temperature"  : "max_temperature",
                     "Cost"  : "cost"}
        
        switchgear_df = switchgear
        switchgear_df.drop(["Environmental Impact"],
                           1)
        switchgear_df = switchgear_df.rename(columns=name_map)
        
        name_map = { "Key Identifier"  :  "id",
                     "Rated Voltage"  :  "v_rate",
                     "Reactive Power"  :  "reactive_power",
                     "N Control"  :  "n_control",
                     "Var Per Step"  : "var_per_step",
                     "Dry Mass"  :  "dry_mass",
                     "Operating Environment"  :  "operating_environment",
                     "Height"  :  "height",
                     "Width"  :  "width",
                     "Depth"  :  "depth",
                     "Cooling"  :  "cooling",
                     "Outer Coating"  :  "outer_coating",
                     "Colour"  :  "colour",
                     "Min Temperature"  :  "min_temperature",
                     "Max Temperature"  :  "max_temperature",
                     "Max Water Depth"  :  "max_water_depth",
                     "Cost"  :  "cost"}
                     
        power_quality_df = power_quality
        power_quality_df.drop(["Environmental Impact"],
                              1)
        power_quality_df = power_quality_df.rename(columns=name_map)      

        database = ElectricalComponentDatabase(static_cable_df,
                                               dynamic_cable_df,
                                               wet_mate_connectors_df,
                                               wet_mate_connectors_df,
                                               transformers_df,
                                               collection_points_df,
                                               switchgear_df,
                                               power_quality_df)
        
        return database

