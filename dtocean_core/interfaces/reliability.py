# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2018 Mathew Topper
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
This module contains the package interface to the dtocean reliability
module.

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. module:: reliability
   :platform: Windows
   :synopsis: Aneris interface for dtocean_core package
   
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os
import pickle
import logging
import pkg_resources
from packaging.version import Version

from polite.paths import Directory, ObjDirectory, UserDataDirectory
from polite.configuration import ReadINI
from dtocean_reliability.main import Variables, Main

from . import ThemeInterface
from ..utils.reliability import get_component_dict, read_RAM
from ..utils.maintenance import (get_user_network,
                                 get_user_compdict)

# Check module version
pkg_title = "dtocean-reliability"
min_version = "1.1.dev0"
version = pkg_resources.get_distribution(pkg_title).version

if not Version(version) >= Version(min_version):
    
    err_msg = ("Installed {} is too old! At least version {} is required, but "
               "version {} is installed").format(pkg_title,
                                                 version,
                                                 min_version)
    raise ImportError(err_msg)

# Set up logging
module_logger = logging.getLogger(__name__)


class ReliabilityInterface(ThemeInterface):
    
    '''Interface to the reliability theme.
          
    '''

    def __init__(self):
        
        super(ReliabilityInterface, self).__init__()
        
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Reliability"
        
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

        input_list  =  ["device.system_type",
                        'device.subsystem_failure_rates',
                        'device.control_subsystem_failure_rates',
                        "project.layout",
                        "project.electrical_network",
                        "project.network_configuration",
                        "project.moorings_foundations_network",
                        "project.lifetime",
                        "project.mttfreq",
                        
                        "component.static_cable_NCFR",
                        "component.dynamic_cable_NCFR",
                        "component.dry_mate_connectors_NCFR",
                        "component.wet_mate_connectors_NCFR",
                        "component.collection_points_NCFR",
                        "component.transformers_NCFR",
                        "component.static_cable_CFR",
                        "component.dynamic_cable_CFR",
                        "component.dry_mate_connectors_CFR",
                        "component.wet_mate_connectors_CFR",
                        "component.collection_points_CFR",
                        "component.transformers_CFR",
                        "component.foundations_anchor_NCFR",
                        "component.foundations_pile_NCFR",
                        "component.foundations_anchor_CFR",
                        "component.foundations_pile_CFR",
                        "component.moorings_chain_NCFR",
                        "component.moorings_forerunner_NCFR",
                        "component.moorings_rope_NCFR",
                        "component.moorings_shackle_NCFR",
                        "component.moorings_swivel_NCFR",
                        "component.moorings_chain_CFR",
                        "component.moorings_forerunner_CFR",
                        "component.moorings_rope_CFR",
                        "component.moorings_shackle_CFR",
                        "component.moorings_swivel_CFR"
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
        
        output_list = ["project.mttf",
                       "project.mttf_test",
                       "project.rsystime",
                       "project.export_cable_reliability",
                       "project.substation_reliability",
                       "project.hub_reliability",
                       "project.interarray_cable_reliability",
                       "project.umbilical_cable_reliability",
                       "project.moorings_reliability"]
        
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
        optional = [
                   'device.subsystem_failure_rates',
                   'device.control_subsystem_failure_rates',
                   "project.layout",
                   "project.electrical_network",
                   "project.network_configuration",
                   "project.moorings_foundations_network",
                   "project.mttfreq",
                   "component.collection_points_NCFR",
                   "component.dry_mate_connectors_NCFR",
                   "component.dynamic_cable_NCFR",
                   "component.static_cable_NCFR",
                   "component.transformers_NCFR",
                   "component.wet_mate_connectors_NCFR",
                   "component.collection_points_CFR",
                   "component.dry_mate_connectors_CFR",
                   "component.dynamic_cable_CFR",
                   "component.static_cable_CFR",
                   "component.transformers_CFR",
                   "component.wet_mate_connectors_CFR",
                   "component.moorings_chain_NCFR",
                   "component.foundations_anchor_NCFR",
                   "component.moorings_forerunner_NCFR",
                   "component.foundations_pile_NCFR",
                   "component.moorings_rope_NCFR",
                   "component.moorings_shackle_NCFR",
                   "component.moorings_swivel_NCFR",
                   "component.moorings_chain_CFR",
                   "component.foundations_anchor_CFR",
                   "component.moorings_forerunner_CFR",
                   "component.foundations_pile_CFR",
                   "component.moorings_rope_CFR",
                   "component.moorings_shackle_CFR",
                   "component.moorings_swivel_CFR"
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
                  
        id_map = {"array_layout": "project.layout",
                  "device_type_user": "device.system_type",
                  'subsystem_failure_rates': 'device.subsystem_failure_rates',
                  'control_subsystem_failure_rates':
                      'device.control_subsystem_failure_rates',
                  "network_configuration_user":
                      "project.network_configuration",
                  "mission_time": "project.lifetime",
                  "expected_mttf": "project.mttfreq",
                  "moor_found_network":
                      "project.moorings_foundations_network",
                  "electrical_network": "project.electrical_network",
                  "collection_points_NCFR":
                      "component.collection_points_NCFR",
                  "dry_mate_connectors_NCFR":
                      "component.dry_mate_connectors_NCFR",
                  "dynamic_cable_NCFR": "component.dynamic_cable_NCFR",
                  "static_cable_NCFR": "component.static_cable_NCFR",
                  "transformers_NCFR": "component.transformers_NCFR",
                  "wet_mate_connectors_NCFR":
                      "component.wet_mate_connectors_NCFR",
                  "collection_points_CFR": "component.collection_points_CFR",
                  "dry_mate_connectors_CFR":
                      "component.dry_mate_connectors_CFR",
                  "dynamic_cable_CFR": "component.dynamic_cable_CFR",
                  "static_cable_CFR": "component.static_cable_CFR",
                  "transformers_CFR": "component.transformers_CFR",
                  "wet_mate_connectors_CFR":
                      "component.wet_mate_connectors_CFR",
                  "moorings_chain_NCFR": "component.moorings_chain_NCFR",
                  "foundations_anchor_NCFR":
                      "component.foundations_anchor_NCFR",
                  "moorings_forerunner_NCFR":
                      "component.moorings_forerunner_NCFR",
                  "foundations_pile_NCFR": "component.foundations_pile_NCFR",
                  "moorings_rope_NCFR": "component.moorings_rope_NCFR",
                  "moorings_shackle_NCFR": "component.moorings_shackle_NCFR",
                  "moorings_swivel_NCFR": "component.moorings_swivel_NCFR",
                  "moorings_chain_CFR": "component.moorings_chain_CFR",
                  "foundations_anchor_CFR": "component.foundations_anchor_CFR",
                  "moorings_forerunner_CFR":
                      "component.moorings_forerunner_CFR",
                  "foundations_pile_CFR": "component.foundations_pile_CFR",
                  "moorings_rope_CFR": "component.moorings_rope_CFR",
                  "moorings_shackle_CFR": "component.moorings_shackle_CFR",
                  "moorings_swivel_CFR": "component.moorings_swivel_CFR",
                  
                  "mttf": "project.mttf",
                  "mttf_test": "project.mttf_test",
                  "rsystime": "project.rsystime",
                  "export_cable_reliability":
                      "project.export_cable_reliability" ,
                  "substation_reliability": "project.substation_reliability" ,
                  "hub_reliability": "project.hub_reliability",
                  "inter_cable_reliability":
                      "project.interarray_cable_reliability",
                  "umbilical_cable_reliability":
                      "project.umbilical_cable_reliability",
                  "moorings_reliability": "project.moorings_reliability"
                  }
                  
        return id_map
                 
    def connect(self, debug_entry=False, export_data=True):
        
        '''The connect method is used to execute the external program and 
        populate the interface data store with values.
        
        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value
        
        '''
        
        system_type_map = {"Tidal Floating": "tidefloat",
                           "Tidal Fixed": "tidefixed",
                           "Wave Floating": "wavefloat",
                           "Wave Fixed": "wavefixed"
                           }
        system_type = system_type_map[self.data.device_type_user]

        input_dict = self.get_input_dict(self.data,
                                         self.data.network_configuration_user)
        
        if input_dict is None: return
        
        mission_time_hours = self.data.mission_time * 365. * 24. 
                
        if self.data.expected_mttf is None:
            mttfreq_hours = None
        else:
            mttfreq_hours = self.data.expected_mttf * 365. * 24.
        
        input_dict["system_type"] = system_type
        input_dict["mission_time_hours"] = mission_time_hours
        input_dict["mttfreq_hours"] = mttfreq_hours
            
        if export_data:
            
            userdir = UserDataDirectory("dtocean_core", "DTOcean", "config")
                    
            if userdir.isfile("files.ini"):
                configdir = userdir
            else:
                configdir = ObjDirectory("dtocean_core", "config")
            
            files_ini = ReadINI(configdir, "files.ini")
            files_config = files_ini.get_config()
            
            appdir_path = userdir.get_path("..")
            debug_folder = files_config["debug"]["path"]
            debug_path = os.path.join(appdir_path, debug_folder)
            debugdir = Directory(debug_path)
            debugdir.makedir()

            pkl_path = debugdir.get_path("reliability_inputs.pkl")
            pickle.dump(input_dict, open(pkl_path, "wb"))
                        
        input_variables = Variables(input_dict["mission_time_hours"],
                                    input_dict["system_type"],
                                    input_dict["compdict"], 
                                    input_dict["mttfreq_hours"], 
                                    input_dict["network_configuration"],
                                    input_dict["electrical_network_hier"], 
                                    input_dict["electrical_network_bom"],
                                    input_dict["moor_found_network_hier"], 
                                    input_dict["moor_found_network_bom"],
                                    input_dict["user_hier"],
                                    input_dict["user_bom"])
                                
        main = Main(input_variables)    
                       
        if debug_entry: return
        
        year_hours = 24. * 365.25
            
        mttf, self.data.rsystime = main()
        
        self.data.mttf = mttf / year_hours
        self.data.mttf_test = main.mttfpass
        
        if self.data.network_configuration_user == "Radial":
            network_configuration = "radial"
        elif self.data.network_configuration_user == "Star":
            network_configuration = "multiplehubs"
        else:
            network_configuration = None
            
        ram_df = read_RAM(main.rsubsysvalues2,
                          main.rsubsysvalues3,
                          network_configuration)
        
        metrics_map = {"system id [-]": "System ID",
                       "failure rate [1/10^6 hours]": "Failure Rate",
                       "MTTF [hours]": "MTTF"}
                        
        if self.data.electrical_network is not None:
        
            metrics = ram_df[(ram_df["system id [-]"] == "-") &
                             (ram_df["subsystem id [-]"] == "Substation")]
            failure_rate = metrics["failure rate [1/10^6 hours]"].iloc[0]
            mttf = metrics["MTTF [hours]"].iloc[0] / year_hours
            
            self.data.substation_reliability = {"Failure Rate": [failure_rate],
                                                "MTTF": [mttf]}
            
            metrics = ram_df[(ram_df["system id [-]"] == "-") &
                             (ram_df["subsystem id [-]"] == "Export Cable")]
            
            failure_rate = metrics["failure rate [1/10^6 hours]"].iloc[0]
            mttf = metrics["MTTF [hours]"].iloc[0] / year_hours
            
            self.data.export_cable_reliability = {
                                                "Failure Rate": [failure_rate],
                                                "MTTF": [mttf]}
            
            metrics = ram_df[(ram_df["system id [-]"].str.contains("subhub")) &
                             (ram_df["subsystem id [-]"] == "Substation")]
            
            if not metrics.empty:

                metrics_df = metrics.loc[:, ("system id [-]",
                                             "failure rate [1/10^6 hours]",
                                             "MTTF [hours]")]
                metrics_df[:, "MTTF [hours]"] /= year_hours
                
                metrics_df = metrics_df.rename(columns=metrics_map)
                metrics_df = metrics_df.reset_index(drop=True)
                
                self.data.hub_reliability = metrics_df
            
            metrics = ram_df[ram_df["subsystem id [-]"
                                ].str.lower().str.contains("elec sub-system")]
            
            if not metrics.empty:

                metrics_df = metrics.loc[:, ("system id [-]",
                                             "failure rate [1/10^6 hours]",
                                             "MTTF [hours]")]
                metrics_df.loc[:, "MTTF [hours]"] /= year_hours
                
                metrics_df = metrics_df.rename(columns=metrics_map)
                metrics_df = metrics_df.reset_index(drop=True)
                
                self.data.inter_cable_reliability = metrics_df
                
        if self.data.moor_found_network is not None:
            
            metrics = ram_df[ram_df["subsystem id [-]"
                                        ].str.contains("mooring foundation")]
            
            if not metrics.empty:

                metrics_df = metrics.loc[:, ("system id [-]",
                                             "failure rate [1/10^6 hours]",
                                             "MTTF [hours]")]
                metrics_df.loc[:, "MTTF [hours]"] /= year_hours
                
                metrics_df = metrics_df.rename(columns=metrics_map)
                metrics_df = metrics_df.reset_index(drop=True)
                
                self.data.moorings_reliability = metrics_df
                
            metrics = ram_df[ram_df["subsystem id [-]"
                                        ].str.contains("dynamic cable")]
            
            if not metrics.empty:

                metrics_df = metrics.loc[:, ("system id [-]",
                                             "failure rate [1/10^6 hours]",
                                             "MTTF [hours]")]
                metrics_df.loc[:, "MTTF [hours]"] /= year_hours
                
                metrics_df = metrics_df.rename(columns=metrics_map)
                metrics_df = metrics_df.reset_index(drop=True)
                
                self.data.umbilical_cable_reliability = metrics_df
                
        # Patch double counting of umbilical cable
        if (self.data.inter_cable_reliability is not None and
            self.data.umbilical_cable_reliability is not None):
            
            self.data.inter_cable_reliability["Failure Rate"] -= \
                    self.data.umbilical_cable_reliability["Failure Rate"]
            
            hours_to_years = 1e6 / 24 / 365.25
            mttf = [hours_to_years / rate for rate in
                            self.data.inter_cable_reliability["Failure Rate"]]
            self.data.inter_cable_reliability["MTTF"] = mttf

        return

        
    @classmethod
    def get_input_dict(cls, data,
                            core_network_configuration):
        
        if (data.moor_found_network is None and 
            data.electrical_network is None): return
            
        if data.moor_found_network is None:
            moor_found_network_hier = None
            moor_found_network_bom = None
        else:
            moor_found_network_hier = data.moor_found_network["topology"]
            moor_found_network_bom = data.moor_found_network["nodes"]
        
#        print data.electrical_network

        if data.electrical_network is None:
            electrical_network_hier = None
            electrical_network_bom = None
            network_configuration = None
        else:
            electrical_network_hier = data.electrical_network["topology"]
            electrical_network_bom = data.electrical_network["nodes"]
            if core_network_configuration == "Radial":
                network_configuration = "radial"
            elif core_network_configuration == "Star":
                network_configuration = "multiplehubs"
             
        # Component Check
        if data.electrical_network is not None:
                    
            if (data.collection_points_NCFR is None or 
                data.collection_points_CFR is None or
                data.dry_mate_connectors_NCFR is None or 
                data.dry_mate_connectors_CFR is None or
                data.dynamic_cable_NCFR is None or 
                data.dynamic_cable_CFR is None or
                data.static_cable_NCFR is None or
                data.static_cable_CFR is None or
                data.transformers_NCFR is None or
                data.transformers_CFR is None or
                data.wet_mate_connectors_NCFR is None or 
                data.wet_mate_connectors_CFR is None):
                 
                msg = ("Insufficient component reliability data entered to "
                       "undertake analysis for electrical network")
                module_logger.info(msg)
                 
                return
                 
        if data.moor_found_network is None:
            
            if (data.moorings_chain_NCFR is None or
                data.moorings_chain_CFR is None or
                data.foundations_anchor_NCFR is None or
                data.foundations_anchor_CFR is None or
                data.moorings_forerunner_NCFR is None or 
                data.moorings_forerunner_CFR is None or
                data.foundations_pile_NCFR is None or 
                data.foundations_pile_CFR is None or
                data.moorings_rope_NCFR is None or
                data.moorings_rope_CFR is None or
                data.moorings_shackle_NCFR is None or
                data.moorings_shackle_CFR is None or
                data.moorings_swivel_NCFR is None or
                data.moorings_swivel_CFR is None):
                
                msg = ("Insufficient component reliability data entered to "
                       "undertake analysis for moorings and foundations "
                       "network")
                module_logger.info(msg)
                
                return
    
        ## COMPONENTS
        compdict = {}

        if (data.collection_points_NCFR is None or 
            data.collection_points_CFR is None):
            
            pass
        
        else:
            
            collection_points_dict = get_component_dict(
                                            "collection point",
                                            data.collection_points_CFR,
                                            data.collection_points_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(collection_points_dict)
        
        if (data.dry_mate_connectors_NCFR is None or 
            data.dry_mate_connectors_CFR is None):
                
            pass
        
        else:
            
            dry_mate_connectors_dict = get_component_dict(
                                            "dry mate",
                                            data.dry_mate_connectors_CFR,
                                            data.dry_mate_connectors_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(dry_mate_connectors_dict)

        if (data.dynamic_cable_NCFR is None or 
            data.dynamic_cable_CFR is None):
                
            pass
        
        else:
            
            dynamic_cable_dict = get_component_dict(
                                            "dynamic cable",
                                            data.dynamic_cable_CFR,
                                            data.dynamic_cable_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(dynamic_cable_dict)
        
        if (data.static_cable_NCFR is None or
            data.static_cable_CFR is None):
            
            pass
        
        else:
            
            static_cable_dict = get_component_dict(
                                            "static cable",
                                            data.static_cable_CFR,
                                            data.static_cable_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(static_cable_dict)

        if (data.transformers_NCFR is None or
            data.transformers_CFR is None):
            
            pass
        
        else:
            transformers_dict = get_component_dict(
                                            "transformer",
                                            data.transformers_CFR,
                                            data.transformers_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(transformers_dict)     

        if (data.wet_mate_connectors_NCFR is None or 
            data.wet_mate_connectors_CFR is None):
            
            pass
        
        else:
            wet_mate_connectors_dict = get_component_dict(
                                            "wet mate",
                                            data.wet_mate_connectors_CFR,
                                            data.wet_mate_connectors_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(wet_mate_connectors_dict)  

        if (data.moorings_chain_NCFR is None or
            data.moorings_chain_CFR is None):
            
            pass
        
        else:
            
            moorings_chain_dict = get_component_dict(
                                            "chain",
                                            data.moorings_chain_CFR,
                                            data.moorings_chain_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(moorings_chain_dict)

        if (data.foundations_anchor_NCFR is None or
            data.foundations_anchor_CFR is None):
            
            pass
        
        else:
            
            foundations_anchor_dict = get_component_dict(
                                            "anchor",
                                            data.foundations_anchor_CFR,
                                            data.foundations_anchor_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(foundations_anchor_dict)
           
        if (data.moorings_forerunner_NCFR is None or 
            data.moorings_forerunner_CFR is None):
            
            pass
        
        else:
            
            moorings_forerunner_dict = get_component_dict(
                                            "forerunner",
                                            data.moorings_forerunner_CFR,
                                            data.moorings_forerunner_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(moorings_forerunner_dict)

        if (data.foundations_pile_NCFR is None or 
            data.foundations_pile_CFR is None):
            
            pass
        
        else:
            
            foundations_pile_dict = get_component_dict(
                                            "pile", 
                                            data.foundations_pile_CFR,
                                            data.foundations_pile_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(foundations_pile_dict)

        if (data.moorings_rope_NCFR is None or
            data.moorings_rope_CFR is None):
            
            pass
        
        else:
            
            moorings_rope_dict = get_component_dict(
                                            "rope",
                                            data.moorings_rope_CFR,
                                            data.moorings_rope_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(moorings_rope_dict)
           
        if (data.moorings_shackle_NCFR is None or
            data.moorings_shackle_CFR is None):
            
            pass
        
        else:
            
            moorings_shackle_dict = get_component_dict(
                                            "shackle",
                                            data.moorings_shackle_CFR,
                                            data.moorings_shackle_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(moorings_shackle_dict)   
           
        if (data.moorings_swivel_NCFR is None or
            data.moorings_swivel_CFR is None):
            
            pass
        
        else:
        
            moorings_swivel_dict = get_component_dict(
                                            "swivel",
                                            data.moorings_swivel_CFR,
                                            data.moorings_swivel_NCFR,
                                            check_keys=compdict.keys())
            compdict.update(moorings_swivel_dict)
            
        if (data.array_layout is None or
            data.subsystem_failure_rates is None):
            
            user_hier = None
            user_bom = None
            
        else:
            
            # Manufacture the user network for the device subsytems:
            subsytem_comps = ['hydro001',
                              'pto001',
                              'support001']
            
            subsystem_rates = data.subsystem_failure_rates
            
            if data.control_subsystem_failure_rates is not None:
                subsytem_comps.insert(2,'control001')
                subsystem_rates.update(data.control_subsystem_failure_rates)
                
            user_hier, user_bom = get_user_network(subsytem_comps,
                                                   data.array_layout)
            
            user_compdict = get_user_compdict(subsytem_comps,
                                              subsystem_rates)
            compdict.update(user_compdict)
                                    
        result = {"compdict": compdict,
                  "network_configuration": network_configuration,
                  "electrical_network_hier": electrical_network_hier,
                  "electrical_network_bom": electrical_network_bom,
                  "moor_found_network_hier": moor_found_network_hier,
                  "moor_found_network_bom": moor_found_network_bom,
                  'user_hier': user_hier,
                  'user_bom': user_bom}
                  
        return result
