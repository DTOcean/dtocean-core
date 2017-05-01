# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 12:02:41 2016

@author: 108630
"""

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

# Set up logging
import logging
module_logger = logging.getLogger(__name__)

import re
import calendar
import datetime as dt
from collections import Counter

import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator

from .reliability import get_component_dict


def get_input_tables(system_type,
                     network_type,
                     array_layout,
                     bathymetry,
                     maintenance_start,
                     annual_maintenance_start,
                     annual_maintenance_end,
                     elec_network,
                     moor_network,
                     moor_bom,
                     electrical_components,
                     elec_database,
                     operations_onsite_maintenance,
                     operations_replacements,
                     operations_inspections,
                     subsystem_access,
                     subsystem_costs,
                     subsystem_failure_rates,
                     subsystem_inspections,
                     subsystem_maintenance,
                     subsystem_maintenance_parts,
                     subsystem_operation_weightings,
                     subsystem_replacement,
                     subsystem_replacement_parts,
                     control_subsystem_access,
                     control_subsystem_costs,
                     control_subsystem_failure_rates,
                     control_subsystem_inspections,
                     control_subsystem_maintenance,
                     control_subsystem_maintenance_parts,
                     control_subsystem_operation_weightings,
                     control_subsystem_replacement,
                     control_subsystem_replacement_parts,
                     umbilical_operations_weighting,
                     array_cables_operations_weighting,
                     substations_operations_weighting,
                     export_cable_operations_weighting,
                     foundations_operations_weighting,
                     moorings_operations_weighting,
                     electrical_failure_rates,
                     moorings_failure_rates,
                     calendar_maintenance_interval,
                     condition_maintenance_soh,
                     electrical_onsite_requirements,
                     moorings_onsite_requirements,
                     electrical_replacement_requirements,
                     moorings_replacement_requirements,
                     electrical_inspections_requirements,
                     moorings_inspections_requirements,
                     electrical_onsite_parts,
                     moorings_onsite_parts,
                     electrical_replacement_parts,
                     moorings_replacement_parts,
                     moorings_subsystem_costs,
                     subsystem_monitering_costs,
                     transit_cost_multiplier=0.,
                     loading_cost_multiplier=0.
                     ):
    
    """Dynamically generate the Component, Failure_Mode, Repair_Action & 
    Inspection tables for the operations and maintenance module"""
    
    if "floating" in system_type.lower():
                               
        moor_subsystem_share = {'Foundations': 0.5,
                                'Mooring Lines': 0.5}
                               
    else:
                               
        moor_subsystem_share = {'Foundations': 1.0}
    
    # Define required subsystems

    # Device
    device_subsystems = ['Prime Mover',
                         'PTO',
                         'Support Structure']
        
    if control_subsystem_replacement_parts is not None:
        device_subsystems.append('Control')
        subsystem_access = subsystem_access.append(control_subsystem_access)
        subsystem_costs = subsystem_costs.append(control_subsystem_costs)
        subsystem_failure_rates = subsystem_failure_rates.append(
                                        control_subsystem_failure_rates)
        subsystem_inspections = subsystem_inspections.apppend(
                                        control_subsystem_inspections)
        subsystem_maintenance = subsystem_maintenance.append(
                                        control_subsystem_maintenance)
        subsystem_maintenance_parts = subsystem_maintenance_parts.append(
                                        control_subsystem_maintenance_parts)
        subsystem_operation_weightings = subsystem_operation_weightings.append(
                                        control_subsystem_operation_weightings)
        subsystem_replacement = subsystem_replacement.append(
                                        control_subsystem_replacement)
        subsystem_replacement_parts = subsystem_replacement_parts.append(
                                        control_subsystem_replacement_parts)
                         
    all_subsystems = device_subsystems[:]
    
    # Electrical
    subhubs = None
    
    if elec_network is not None:
    
        elec_subsystems = ['Inter-Array Cables',
                           'Substations',
                           'Export Cable']
    
        if "floating" in system_type.lower():
            elec_subsystems.append('Umbilical Cable')
            
        all_subsystems.extend(elec_subsystems)
        
        # Check for subhubs
        n_subhubs = len(elec_network['nodes']) - len(array_layout) - 1

        if n_subhubs > 0:
            subhubs = ["subhub{:0>3}".format(x + 1) for x in xrange(n_subhubs)]

        electrical_subsystem_costs = get_electrical_system_cost(
                                                        electrical_components,
                                                        elec_subsystems,
                                                        elec_database)
        
    # Moorings and Foundations
    if moor_network is not None:
    
        moor_subsystems = ['Foundations']
                           
        if "floating" in system_type.lower():
            moor_subsystems.append('Mooring Lines')
            
        all_subsystems.extend(moor_subsystems)
    
    array_subsystems = ['Substations',
                        'Export Cable']
                       
    subsystems_map = {'Prime Mover': 'Hydrodynamic',
                      'PTO': 'Pto',
                      'Control': 'Control',
                      'Support Structure': 'Support structure',
                      'Umbilical Cable': 'Dynamic cable',
                      'Inter-Array Cables': 'Array elec sub-system',
                      'Substations': 'Substation',
                      'Export Cable': 'Export Cable',
                      'Foundations': 'Foundation',
                      'Mooring Lines': 'Mooring line'}
                      
    weightings_map = {
                'Prime Mover': 
                    subsystem_operation_weightings.loc['Prime Mover'],
                'PTO': subsystem_operation_weightings.loc['PTO'],
                'Support Structure':
                    subsystem_operation_weightings.loc['Support Structure'],
                'Umbilical Cable': umbilical_operations_weighting,
                'Inter-Array Cables': array_cables_operations_weighting,
                'Substations': substations_operations_weighting,
                'Export Cable': export_cable_operations_weighting,
                'Foundations': foundations_operations_weighting,
                'Mooring Lines': moorings_operations_weighting}
        
    if control_subsystem_replacement_parts is not None:
        weightings_map['Control'] = \
                      subsystem_operation_weightings.loc['Control']
                      
    repair_map = {
            'Maintenance Duration': 'duration_maintenance',
            'Access Duration': 'duration_accessibility',
            'Interruptable': 'interruptable',
            'Crew Preparation Delay': 'delay_crew',
            'Other Delay': 'delay_organisation',
            'Spare Parts Preparation Delay': 'delay_spare',
            'Technicians Required': 'number_technicians',
            'Specialists Required': 'number_specialists',
            'Max Wave Height for Access': 'wave_height_max_acc',
            'Max Wave Period for Access': 'wave_periode_max_acc',
            'Max Wind Speed for Access': 'wind_speed_max_acc',
            'Max Current Speed for Access': 'current_speed_max_acc',
            'Max Wave Height for Maintenance': 'wave_height_max_om',
            'Max Wave Period for Maintenance': 'wave_periode_max_om',
            'Max Wind Speed for Maintenance': 'wind_speed_max_om',
            'Max Current Speed for Maintenance': 'current_speed_max_om'}
            
    inspections_map = {
            'Inspection Duration': 'duration_inspection',
            'Access Duration': 'duration_accessibility',
            'Crew Preparation Delay': 'delay_crew',
            'Other Delay': 'delay_organisation',
            'Technicians Required': 'number_technicians',
            'Specialists Required': 'number_specialists',
            'Max Wave Height for Access': 'wave_height_max_acc',
            'Max Wave Period for Access': 'wave_periode_max_acc',
            'Max Wind Speed for Access': 'wind_speed_max_acc',
            'Max Current Speed for Access': 'current_speed_max_acc',
            'Max Wave Height for Inspections': 'wave_height_max_om',
            'Max Wave Period for Inspections': 'wave_periode_max_om',
            'Max Wind Speed for Inspections': 'wind_speed_max_om',
            'Max Current Speed for Inspections': 'current_speed_max_om'}
                      
    modes_map = {'Spare Parts Mass': 'spare_mass',
                 'Spare Parts Max Height': 'spare_height',
                 'Spare Parts Max Width': 'spare_width',
                 'Spare Parts Max Length': 'spare_length'}
                             
    # Start end dates
    months = list(calendar.month_name)
    
    start_month_int = None
    this_year = maintenance_start.year
    next_year = this_year + 1
    
    if annual_maintenance_start is not None:
        
        start_month_int = months.index(annual_maintenance_start)
        start_date = dt.datetime(this_year,
                                 start_month_int,
                                 1)
        
        if start_date < maintenance_start:
            start_date = start_date.replace(year=next_year)
            
    else:
        
        start_date = dt.datetime(next_year, 1, 1)
        
    if annual_maintenance_end is not None:
        
        end_month_int = months.index(annual_maintenance_end)
        
        if (start_month_int is not None and
            end_month_int < start_month_int):
                
            errStr = ("Annual maintenance end month may not be earlier than "
                      "start month")
            raise ValueError(errStr)
            
        last_day = calendar.monthrange(this_year,
                                       end_month_int)[1]

        end_date = dt.datetime(this_year,
                               end_month_int,
                               last_day,
                               23,
                               59,
                               59)
        
        if end_date < maintenance_start:

            last_day = calendar.monthrange(next_year,
                                           end_month_int)[1]

            end_date = dt.datetime(next_year,
                                   end_month_int,
                                   last_day,
                                   23,
                                   59,
                                   59)
            
    else:
        
        end_date = dt.datetime(next_year,
                               12,
                               31,
                               23,
                               59,
                               59)
        
    logMsg = "Annual operations start on date {}".format(start_date)
    module_logger.info(logMsg)
    
    logMsg = "Annual operations end on date {}".format(end_date)
    module_logger.info(logMsg)
    
    # Final tables
    all_comp = pd.DataFrame()
    all_modes = pd.DataFrame()
    all_repair = pd.DataFrame()
    all_inspection = pd.DataFrame()
    
    # Error string helper
    shortErr = "{0} {1} data has not been provided for sub-system {2}"
    
    longErr = ("{0} {1} operations {2} data has not been provided, yet "
               "{1} operations are selected for sub-system {3}")
        
    for subsystem in all_subsystems:
        
        # Initiate temporary table data
        temp_comp = pd.Series()
        temp_modes = pd.Series()
        
        subsystem_root = subsystems_map[subsystem]

        # Collect the operations weightings in advance so that the failure
        # modes table can be completed per operation type
        operations_weightings = {"onsite": None,
                                 "replacement": None,
                                 "inspections": None}
        
        if (operations_onsite_maintenance is not None and
            operations_onsite_maintenance[subsystem]):
            
            weighting = weightings_map[subsystem]["On-Site Maintenance"]
            operations_weightings["onsite"] = weighting
            
        if (operations_replacements is not None and
            subsystem in operations_replacements and
            operations_replacements[subsystem]):
            
            weighting = weightings_map[subsystem]["Replacement"]
            operations_weightings["replacement"] = weighting

        if (operations_inspections is not None and
            operations_inspections[subsystem]):
            
            weighting = weightings_map[subsystem]["Inspections"]
            operations_weightings["inspections"] = weighting

        weighting_set = set(operations_weightings.values())

        # No work to do for this subsystem
        if len(weighting_set) == 1 and None in weighting_set: continue
    
        # Build temporary component table series
        temp_comp["Component_subtype"] = subsystem_root
        temp_comp["start_date_calendar_based_maintenance"] = start_date
        temp_comp["end_date_calendar_based_maintenance"] = end_date
        temp_comp["start_date_condition_based_maintenance"] = start_date
        temp_comp["end_date_condition_based_maintenance"] = end_date

        # Number of operation types active
        active_ops = [k for k, v in operations_weightings.items()
                                                             if v is not None]
        total_weight = sum([v for k, v in operations_weightings.items()
                                                             if v is not None])
                                                             
        temp_comp["number_failure_modes"] = len(active_ops)

        # Failure rates
        if subsystem in device_subsystems:
            
            temp_comp["failure_rate"] = subsystem_failure_rates[subsystem]

        elif subsystem in elec_subsystems:
            
            temp_comp["failure_rate"] = electrical_failure_rates[subsystem]

        elif subsystem in moor_subsystems:
            
            if moor_bom is None:
                temp_comp["failure_rate"] = np.nan
            else:
                temp_comp["failure_rate"] = moorings_failure_rates[subsystem]
    
        # Calendar maintenance interval
        temp_comp["interval_calendar_based_maintenance"] = \
                                    calendar_maintenance_interval[subsystem]

        # State of health
        temp_comp["soh_threshold"] = condition_maintenance_soh[subsystem]

        # Add subsytem to the Component table
        all_comp = update_comp_table(subsystem,
                                     subsystem_root,
                                     array_layout,
                                     temp_comp,
                                     all_comp,
                                     subhubs)

        # Base Costs
        if subsystem in device_subsystems:
            
            base_cost = subsystem_costs[subsystem]

        elif subsystem in elec_subsystems:
            
            base_cost = electrical_subsystem_costs[subsystem]

        elif subsystem in moor_subsystems:
            
            if moor_bom is not None:
            
                base_cost = (moor_bom["Cost"] * 
                             moor_bom["Quantity"]).sum() * \
                                            moor_subsystem_share[subsystem]
                
            else:
            
                if moorings_subsystem_costs is None:
                    
                    errStr = shortErr.format("Moorings and Foundations",
                                             "costs",
                                             subsystem)
                    raise RuntimeError(errStr)
                                
                base_cost = moorings_subsystem_costs[subsystem]

        # Conditioning monitering costs
        if subsystem_monitering_costs is None:
            monitering_cost = 0.
        else:
            monitering_cost = subsystem_monitering_costs[subsystem]

        # Costs can be divided per device
        if subsystem not in array_subsystems:
            
            n_devices = len(array_layout)
            base_cost /= n_devices

        # Add on-site operations
        if "onsite" in active_ops:
            
            # Initiate temporary table data
            onsite_modes = temp_modes.copy()
            
            # Build Repair Actions and Failure Mode series
            if subsystem in device_subsystems:
                
                access_map = {
                  'Operation Duration': 'duration_accessibility',
                  'Max Hs': 'wave_height_max_acc',
                  'Max Tp': 'wave_periode_max_acc',
                  'Max Wind Velocity': 'wind_speed_max_acc',
                  'Max Current Velocity': 'current_speed_max_acc'}
                
                device_repair_map = {
                  'Operation Duration': 'duration_maintenance',
                  'Interruptable': 'interruptable',
                  'Crew Preparation Delay': 'delay_crew',
                  'Other Delay': 'delay_organisation',
                  'Spare Parts Preparation Delay': 'delay_spare',
                  'Technicians Required': 'number_technicians',
                  'Specialists Required': 'number_specialists',
                  'Max Hs': 'wave_height_max_om',
                  'Max Tp': 'wave_periode_max_om',
                  'Max Wind Velocity': 'wind_speed_max_om',
                  'Max Current Velocity': 'current_speed_max_om'}
                
                temp_access = subsystem_access.loc[subsystem]
                temp_access = temp_access.rename(access_map)
                                
                onsite_modes = onsite_modes.append(
                                    subsystem_maintenance_parts.loc[subsystem])
                
                temp_repair = subsystem_maintenance.loc[subsystem]
                temp_repair = temp_repair.rename(device_repair_map)
                temp_repair = temp_repair.append(temp_access)

            elif subsystem in elec_subsystems:
                
                if electrical_onsite_requirements is None:
                    
                    errStr = longErr.format("Electrical Sub-Systems",
                                            "on-site",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)
                    
                if electrical_onsite_parts is None:
                    
                    errStr = longErr.format("Electrical Sub-Systems",
                                            "on-site",
                                            "parts",
                                            subsystem)
                    raise RuntimeError(errStr)
                
                temp_repair = electrical_onsite_requirements.loc[subsystem]
                onsite_modes = onsite_modes.append(
                                       electrical_onsite_parts.loc[subsystem])
                
                temp_repair = temp_repair.rename(repair_map)

            elif subsystem in moor_subsystems:
                
                if moorings_onsite_requirements is None:
                    
                    errStr = longErr.format("Moorings and Foundations",
                                            "on-site",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)
                    
                if moorings_onsite_parts is None:
                    
                    errStr = longErr.format("Moorings and Foundations",
                                            "on-site",
                                            "parts",
                                            subsystem)
                    raise RuntimeError(errStr)
                
                temp_repair = moorings_onsite_requirements.loc[subsystem]
                onsite_modes = onsite_modes.append(
                                       moorings_onsite_parts.loc[subsystem])
                
                temp_repair = temp_repair.rename(repair_map)

            onsite_modes = onsite_modes.rename(modes_map)
            
            # Costs
            onsite_modes["cost_spare"] = base_cost
            onsite_modes["cost_spare_transit"] = \
                                        base_cost * transit_cost_multiplier
            onsite_modes["cost_spare_loading"] = \
                                        base_cost * loading_cost_multiplier
                                        
            onsite_modes["CAPEX_condition_based_maintenance"] = monitering_cost
                                        
            # Probability
            onsite_modes["mode_probability"] = \
                        operations_weightings["onsite"] / total_weight * 100.

            # Add operation to Failure Mode and Repair Actions Tables
            (all_modes,
             all_repair) = update_onsite_tables(subsystem,
                                                subsystem_root,
                                                system_type,
                                                array_layout,
                                                bathymetry,
                                                onsite_modes,
                                                temp_repair,
                                                all_modes,
                                                all_repair,
                                                subhubs)

        # Add replacement operations
        if "replacement" in active_ops:
            
            replacement_modes = temp_modes.copy()
            
            # Build Repair Actions and Failure Mode series
            if subsystem in device_subsystems:
                
                access_map = {
                  'Operation Duration': 'duration_accessibility',
                  'Max Hs': 'wave_height_max_acc',
                  'Max Tp': 'wave_periode_max_acc',
                  'Max Wind Velocity': 'wind_speed_max_acc',
                  'Max Current Velocity': 'current_speed_max_acc'}
                
                device_repair_map = {
                  'Operation Duration': 'duration_maintenance',
                  'Interruptable': 'interruptable',
                  'Crew Preparation Delay': 'delay_crew',
                  'Other Delay': 'delay_organisation',
                  'Spare Parts Preparation Delay': 'delay_spare',
                  'Technicians Required': 'number_technicians',
                  'Specialists Required': 'number_specialists',
                  'Max Hs': 'wave_height_max_om',
                  'Max Tp': 'wave_periode_max_om',
                  'Max Wind Velocity': 'wind_speed_max_om',
                  'Max Current Velocity': 'current_speed_max_om'}
                
                temp_access = subsystem_access.loc[subsystem]
                temp_access = temp_access.rename(access_map)
                
                temp_repair = subsystem_replacement.loc[subsystem]
                temp_repair = temp_repair.rename(device_repair_map)
                temp_repair = temp_repair.append(temp_access)
                                
                replacement_modes = replacement_modes.append(
                                subsystem_replacement_parts.loc[subsystem])

            elif subsystem in elec_subsystems:
                
                if electrical_replacement_requirements is None:
                    
                    errStr = longErr.format("Electrical Sub-Systems",
                                            "replacement",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)
                    
                if electrical_replacement_parts is None:
                    
                    errStr = longErr.format("Electrical Sub-Systems",
                                            "on-site",
                                            "parts",
                                            subsystem)
                    raise RuntimeError(errStr)
                
                temp_repair = \
                            electrical_replacement_requirements.loc[subsystem]
                replacement_modes = replacement_modes.append(
                                   electrical_replacement_parts.loc[subsystem])
                
                temp_repair = temp_repair.rename(repair_map)

            elif subsystem in moor_subsystems:
                
                if moorings_replacement_requirements is None:
                    
                    errStr = longErr.format("Moorings and Foundations",
                                            "replacement",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)
                    
                if moorings_replacement_parts is None:
                    
                    errStr = longErr.format("Moorings and Foundations",
                                            "on-site",
                                            "parts",
                                            subsystem)
                    raise RuntimeError(errStr)
                
                temp_repair = moorings_replacement_requirements.loc[subsystem]
                replacement_modes = replacement_modes.append(
                                   moorings_replacement_parts.loc[subsystem])
                
                temp_repair = temp_repair.rename(repair_map)

            replacement_modes = replacement_modes.rename(modes_map)
            
            # Costs
            replacement_modes["cost_spare"] = base_cost
            replacement_modes["cost_spare_transit"] = \
                                        base_cost * transit_cost_multiplier
            replacement_modes["cost_spare_loading"] = \
                                        base_cost * loading_cost_multiplier
                                        
            replacement_modes["CAPEX_condition_based_maintenance"] = \
                                                             monitering_cost
                                        
            # Probability
            replacement_modes["mode_probability"] = \
                    operations_weightings["replacement"] / total_weight * 100.

            # Add operation to Failure Mode and Repair Actions Tables
            (all_modes,
             all_repair) = update_replacement_tables(subsystem,
                                                     subsystem_root,
                                                     system_type,
                                                     array_layout,
                                                     replacement_modes,
                                                     temp_repair,
                                                     all_modes,
                                                     all_repair)

        if "inspections" in active_ops:
            
            # Initiate temporary table data
            inspections_modes = temp_modes.copy()
            
            # Add some fake parts data
            inspections_modes['spare_mass'] = 0.1
            inspections_modes['spare_height'] = 0.1
            inspections_modes['spare_width'] = 0.1
            inspections_modes['spare_length'] = 0.1
            
            if subsystem in device_subsystems:
                
                access_map = {
                  'Operation Duration': 'duration_accessibility',
                  'Max Hs': 'wave_height_max_acc',
                  'Max Tp': 'wave_periode_max_acc',
                  'Max Wind Velocity': 'wind_speed_max_acc',
                  'Max Current Velocity': 'current_speed_max_acc'}
                
                temp_access = subsystem_access.loc[subsystem]
                temp_access = temp_access.rename(access_map)

                device_inspections_map = {
                  'Operation Duration': 'duration_inspection',
                  'Crew Preparation Delay': 'delay_crew',
                  'Other Delay': 'delay_organisation',
                  'Technicians Required': 'number_technicians',
                  'Specialists Required': 'number_specialists',
                  'Max Hs': 'wave_height_max_om',
                  'Max Tp': 'wave_periode_max_om',
                  'Max Wind Velocity': 'wind_speed_max_om',
                  'Max Current Velocity': 'current_speed_max_om'}
                
                temp_inspection = \
                            subsystem_inspections.loc[subsystem]
                            
                temp_inspection = temp_inspection.rename(
                                                        device_inspections_map)
                
                temp_inspection = temp_inspection.append(temp_access)

            elif subsystem in elec_subsystems:
                
                if electrical_inspections_requirements is None:
                    
                    errStr = longErr.format("Electrical Sub-Systems",
                                            "inspections",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)
                
                temp_inspection = \
                            electrical_inspections_requirements.loc[subsystem]
                            
                temp_inspection = temp_inspection.rename(inspections_map)

            elif subsystem in moor_subsystems:
                
                if moorings_inspections_requirements is None:
                    
                    errStr = longErr.format("Moorings and Foundations",
                                            "inspections",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)

                temp_inspection = \
                            moorings_inspections_requirements.loc[subsystem]
                
                temp_inspection = temp_inspection.rename(inspections_map)

            # Costs
            inspections_modes["cost_spare"] = 0.
            inspections_modes["cost_spare_transit"] = 0.
            inspections_modes["cost_spare_loading"] = 0.
                                        
            inspections_modes["CAPEX_condition_based_maintenance"] = \
                                                            monitering_cost
                                        
            # Probability
            inspections_modes["mode_probability"] = \
                    operations_weightings["inspections"] / total_weight * 100.

            # Add operation to Failure Mode and Inspection Tables
            (all_modes,
             all_inspection) = update_inspections_tables(subsystem,
                                                         subsystem_root,
                                                         system_type,
                                                         array_layout,
                                                         bathymetry,
                                                         inspections_modes,
                                                         temp_inspection,
                                                         all_modes,
                                                         all_inspection,
                                                         subhubs)
            
    assert all_comp.shape[0] == 11
    assert all_modes.shape[0] == 11
    assert all_repair.shape[0] == 18
    assert all_inspection.shape[0] == 16

    assert all_modes.shape[1] == all_repair.shape[1] + \
                                                all_inspection.shape[1]
                
    return all_comp, all_modes, all_repair, all_inspection
    
def update_comp_table(subsystem,
                      subsystem_root,
                      array_layout,
                      temp_comp,
                      all_comp,
                      subhubs):
    
    array_subsystems = ['Substations',
                        'Export Cable']

    # Build final tables
    if subsystem in array_subsystems:
        
        subsystem_id = "{}001".format(subsystem_root)
        temp_comp["Component_ID"] = subsystem_id
        temp_comp["Component_type"] = subsystem_id

        num_cols = all_comp.shape[1]
        temp_comp = temp_comp.rename(num_cols)
        all_comp = pd.concat([all_comp, temp_comp], axis=1)
        
        if subsystem == 'Substations' and subhubs is not None:
            
            for subhub_id in subhubs:
                
                temp_comp["Component_ID"] = subhub_id
                temp_comp["Component_type"] = subhub_id
                temp_comp["Component_subtype"] = "subhub"
        
                num_cols = all_comp.shape[1]
                temp_comp = temp_comp.rename(num_cols)
                all_comp = pd.concat([all_comp, temp_comp], axis=1)
        
    else:
        
        # Iterate through the devices
        for device_id, position in array_layout.iteritems():
            
            numstrs = re.findall('\d+', device_id)
            num = int(numstrs[0])
            
            subsystem_id = "{}{:0>3}".format(subsystem_root, num)
            temp_comp["Component_ID"] = subsystem_id
            temp_comp["Component_type"] = device_id

            num_cols = all_comp.shape[1]
            temp_comp = temp_comp.rename(num_cols)
            all_comp = pd.concat([all_comp, temp_comp], axis=1)
                
    return all_comp
    
def update_onsite_tables(subsystem,
                         subsystem_root,
                         system_type,
                         array_layout,
                         bathymetry,
                         temp_modes,
                         temp_repair,
                         all_modes,
                         all_repair,
                         subhubs):
    
    operation = 'onsite'
    
    array_subsystems = ['Substations',
                        'Export Cable']
                        
    operations_map = {'onsite' : "MoS",
                      "replacement": "RtP",
                      'inspections': "Insp"}

    array_dict = {'Substations': [1, 1],
                  'Export Cable': [7, 3]}

    array_df = pd.DataFrame(array_dict, index=['onsite', 'inspections'])

    iterables = [['Fixed', 'Floating'], ['Shallow', 'Deep']]
    op_index = pd.MultiIndex.from_product(iterables, names=['Type', 'Depth'])
    
    onsite_dict = {'Prime Mover': [3, 4, 1, 1],
                   'PTO': [3, 4, 1, 1],
                   'Control': [3, 4, 1, 1],
                   'Support Structure': [3, 4, 3, 4],
                   'Umbilical Cable': [-1, -1, 3, 4],
                   'Inter-Array Cables': [7, 7, 7, 7],
                   'Foundations': [6, 6, 6, 6],
                   'Mooring Lines': [5, 5, 5, 5]}

    onsite_df = pd.DataFrame(onsite_dict, index=op_index)

    # Build final tables
    if subsystem in array_subsystems:
        
        subsystem_id = "{}001".format(subsystem_root)
        
        # Get the operation type
        op_number = array_df[subsystem][operation]
        op_code = operations_map[operation]
        op_id = "{}{}".format(op_code, op_number)
        
        temp_repair["Component_ID"] = subsystem_id
        temp_repair["FM_ID"] = op_id

        num_cols = all_repair.shape[1]
        temp_repair = temp_repair.rename(num_cols)
        all_repair = pd.concat([all_repair, temp_repair], axis=1)

        temp_modes["Component_ID"] = subsystem_id
        temp_modes["FM_ID"] = op_id

        num_cols = all_modes.shape[1]
        temp_modes = temp_modes.rename(num_cols)
        all_modes = pd.concat([all_modes, temp_modes], axis=1)
        
        if subsystem == 'Substations' and subhubs is not None:
            
            for subhub_id in subhubs:
                
                temp_repair["Component_ID"] = subhub_id
        
                num_cols = all_repair.shape[1]
                temp_repair = temp_repair.rename(num_cols)
                all_repair = pd.concat([all_repair, temp_repair], axis=1)
        
                temp_modes["Component_ID"] = subhub_id
        
                num_cols = all_modes.shape[1]
                temp_modes = temp_modes.rename(num_cols)
                all_modes = pd.concat([all_modes, temp_modes], axis=1)
            
    else:
        
        # Iterate through the devices
        for device_id, position in array_layout.iteritems():
            
            numstrs = re.findall('\d+', device_id)
            num = int(numstrs[0])
            
            subsystem_id = "{}{:0>3}".format(subsystem_root, num)
            
            # Get device depth and position type
            depth = get_point_depth(bathymetry, position)
            
            if depth < -30.:
                depth_type = "Deep"
            else:
                depth_type = "Shallow"
                
            pos_type = system_type.split()[1]

            # Get the operation type
            op_number = onsite_df[subsystem][pos_type][depth_type]
            op_id = "MoS{}".format(op_number)
            
            temp_repair["Component_ID"] = subsystem_id
            temp_repair["FM_ID"] = op_id

            num_cols = all_repair.shape[1]
            temp_repair = temp_repair.rename(num_cols)
            all_repair = pd.concat([all_repair, temp_repair],
                                   axis=1)

            temp_modes["Component_ID"] = subsystem_id
            temp_modes["FM_ID"] = op_id

            num_cols = all_modes.shape[1]
            temp_modes = temp_modes.rename(num_cols)
            all_modes = pd.concat([all_modes, temp_modes], axis=1)
                
    return all_modes, all_repair
    
def update_replacement_tables(subsystem,
                              subsystem_root,
                              system_type,
                              array_layout,
                              temp_modes,
                              temp_repair,
                              all_modes,
                              all_repair):
    
    array_subsystems = ['Substations',
                        'Export Cable']
    
    replacement_dict = {'Prime Mover': [2, 3],
                        'PTO': [2, 1],
                        'Control': [2, 1],
                        'Support Structure': [2, 2],
                        'Umbilical Cable': [6, 6],
                        'Mooring Lines': [5, 5]}

    replacement_df = pd.DataFrame(replacement_dict,
                                  index=['Fixed', 'Floating'])

    # Build final tables
    if subsystem not in array_subsystems:

        # Iterate through the devices
        for device_id, position in array_layout.iteritems():
            
            numstrs = re.findall('\d+', device_id)
            num = int(numstrs[0])
            
            subsystem_id = "{}{:0>3}".format(subsystem_root, num)
            pos_type = system_type.split()[1]
                
            # Get the operation type
            op_number = replacement_df[subsystem][pos_type]
            op_id = "RtP{}".format(op_number)
            
            temp_repair["Component_ID"] = subsystem_id
            temp_repair["FM_ID"] = op_id

            num_cols = all_repair.shape[1]
            temp_repair = temp_repair.rename(num_cols)
            all_repair = pd.concat([all_repair, temp_repair],
                                   axis=1)

            temp_modes["Component_ID"] = subsystem_id
            temp_modes["FM_ID"] = op_id

            num_cols = all_modes.shape[1]
            temp_modes = temp_modes.rename(num_cols)
            all_modes = pd.concat([all_modes, temp_modes], axis=1)
                
    return all_modes, all_repair
    
def update_inspections_tables(subsystem,
                              subsystem_root,
                              system_type,
                              array_layout,
                              bathymetry,
                              temp_modes,
                              temp_inspection,
                              all_modes,
                              all_inspection,
                              subhubs):
    
    operation = "inspections"
    
    array_subsystems = ['Substations',
                        'Export Cable']
                        
    operations_map = {'onsite' : "MoS",
                      "replacement": "RtP",
                      'inspections': "Insp"}

    array_dict = {'Substations': [1, 1],
                  'Export Cable': [7, 3]}

    array_df = pd.DataFrame(array_dict, index=['onsite', 'inspections'])

    iterables = [['Fixed', 'Floating'], ['Shallow', 'Deep']]
    op_index = pd.MultiIndex.from_product(iterables, names=['Type', 'Depth'])
    
    inspections_dict = {'Prime Mover': [3, 4, 1, 1],
                        'PTO': [3, 4, 1, 1],
                        'Control': [3, 4, 1, 1],
                        'Support Structure': [3, 4, 3, 4],
                        'Umbilical Cable': [-1, -1, 3, 4],
                        'Inter-Array Cables': [3, 4, 3, 4],
                        'Foundations': [3, 4, 3, 4],
                        'Mooring Lines': [3, 4, 3, 4]}

    inspections_df = pd.DataFrame(inspections_dict, index=op_index)

    # Build final tables
    if subsystem in array_subsystems:
        
        subsystem_id = "{}001".format(subsystem_root)
        
        # Get the operation type
        op_number = array_df[subsystem][operation]
        op_code = operations_map[operation]
        op_id = "{}{}".format(op_code, op_number)
                    
        temp_inspection["Component_ID"] = subsystem_id
        temp_inspection["FM_ID"] = op_id

        num_cols = all_inspection.shape[1]
        temp_inspection = temp_inspection.rename(num_cols)
        all_inspection = pd.concat([all_inspection,
                                    temp_inspection], axis=1)

        temp_modes["Component_ID"] = subsystem_id
        temp_modes["FM_ID"] = op_id

        num_cols = all_modes.shape[1]
        temp_modes = temp_modes.rename(num_cols)
        all_modes = pd.concat([all_modes, temp_modes], axis=1)
        
        if subsystem == 'Substations' and subhubs is not None:
            
            for subhub_id in subhubs:
                
                temp_inspection["Component_ID"] = subhub_id
        
                num_cols = all_inspection.shape[1]
                temp_inspection = temp_inspection.rename(num_cols)
                all_inspection = pd.concat([all_inspection,
                                            temp_inspection], axis=1)
        
                temp_modes["Component_ID"] = subhub_id
        
                num_cols = all_modes.shape[1]
                temp_modes = temp_modes.rename(num_cols)
                all_modes = pd.concat([all_modes, temp_modes], axis=1)
            
    else:
        
        # Iterate through the devices
        for device_id, position in array_layout.iteritems():
            
            numstrs = re.findall('\d+', device_id)
            num = int(numstrs[0])
            
            subsystem_id = "{}{:0>3}".format(subsystem_root, num)
            
            # Get device depth and position type
            depth = get_point_depth(bathymetry, position)
            
            if depth < -30.:
                depth_type = "Deep"
            else:
                depth_type = "Shallow"
                
            pos_type = system_type.split()[1]
                                
            # Get the operation type
            op_number = inspections_df[subsystem][pos_type][depth_type]
            op_id = "Insp{}".format(op_number)

            temp_inspection["Component_ID"] = subsystem_id
            temp_inspection["FM_ID"] = op_id

            num_cols = all_inspection.shape[1]
            temp_inspection = temp_inspection.rename(num_cols)
            all_inspection = pd.concat([all_inspection,
                                        temp_inspection], axis=1)

            temp_modes["Component_ID"] = subsystem_id
            temp_modes["FM_ID"] = op_id

            num_cols = all_modes.shape[1]
            temp_modes = temp_modes.rename(num_cols)
            all_modes = pd.concat([all_modes, temp_modes], axis=1)
                
    return all_modes, all_inspection
    
def get_user_network(subsytem_comps, array_layout):
    
    """Manufacture the user network for the device subsytems"""
    
    subsystem_names = ['Hydrodynamic',
                       'Pto',
                       'Support structure']
    
    if len(subsytem_comps) == 4:
        subsystem_names.insert(2, 'Control')
    
    user_hierarchy = {'array': {}}
    user_bom = {}

    device_subsytem_hierarchy = {k: [v] for k, v in zip(subsystem_names,
                                                        subsytem_comps)}
                                 
    device_subsytem_bom = {k: {'quantity': Counter({v: 1})}
                            for k, v in zip(subsystem_names, subsytem_comps)}

    for device_id in array_layout.keys():
        
        user_hierarchy[device_id] = device_subsytem_hierarchy
        user_bom[device_id] = device_subsytem_bom

    return user_hierarchy, user_bom
    
def get_user_compdict(subsytem_comps,
                      subsystem_failure_rates):
    
    subsystem_names = ['Prime Mover',
                       'PTO',
                       'Support Structure']
    
    if len(subsytem_comps) == 4:
        subsystem_names.insert(2, 'Control')
    
    all_rates = [subsystem_failure_rates[x] for x in subsystem_names]
    rates_dict = {'Key Identifier': subsytem_comps,
                  "Lower Bound": all_rates,
                  "Mean": all_rates,
                  "Upper Bound": all_rates}
    
    rates_df = pd.DataFrame(rates_dict)
    
    comp_db = get_component_dict('user-defined',
                                 rates_df,
                                 rates_df)
        
    return comp_db

def get_point_depth(bathyset, position):
    
    x = bathyset["x"].values
    y = bathyset["y"].values

    zv = bathyset["depth"].max(dim=["layer"]).values

    bathy_interp_function = RegularGridInterpolator((x, y), zv)
    
    depth = bathy_interp_function(position.coords[0][0:2])
    
    return depth
    
def get_events_table(raw_df):
    
    raw_df = raw_df.dropna()
    
    data_df = raw_df[[u'repairActionRequestDate [-]',
                      u'repairActionDate [-]',
                      u'downtimeDuration [Hour]',
                      u'ComponentSubType [-]',
                      u'FM_ID [-]',
                      u'costLogistic [Euro]',
                      u'costOM_Labor [Euro]',
                      u'costOM_Spare [Euro]']]

    data_df["repairActionRequestDate [-]"] = pd.to_datetime(
                            data_df["repairActionRequestDate [-]"])
    data_df = data_df.sort_values(by="repairActionRequestDate [-]")
    data_df = data_df.reset_index(drop=True)
    
    def mode_match(x):
        
        if "Insp" in x:
            return "Inspection"
        
        if "MoS" in x:
            return "On-Site Maintenance"
        
        if "Rtp" in x:
            return "Replacement"
    
    data_df["FM_ID [-]"] = data_df["FM_ID [-]"].apply(mode_match)
    
    name_map = {
            "repairActionRequestDate [-]": "Operation Request Date",
            "repairActionDate [-]": "Operation Completion Date",
            "downtimeDuration [Hour]": "Downtime",
            "ComponentSubType [-]": "Sub-System",
            "FM_ID [-]": "Operation Type",
            "costLogistic [Euro]": "Logistics Cost",
            "costOM_Labor [Euro]": "Labour Cost",
            "costOM_Spare [Euro]": "Parts Cost"}

    data_df = data_df.rename(columns=name_map)
    
    subsytem_map = { 'Array elec sub-system': 'Inter-Array Cables',
                     'Control': 'Control',
                     'Dynamic cable': 'Umbilical Cable',
                     'Export Cable': 'Export Cable',
                     'Foundation': 'Foundations',
                     'Hydrodynamic': 'Prime Mover',
                     'Mooring line': 'Mooring Lines',
                     'Pto': 'PTO',
                     'Substation': 'Substations',
                     'Support structure': 'Support Structure' }
    
    data_df["Sub-System"] = data_df["Sub-System"].replace(subsytem_map)
    
    return data_df

def get_electrical_system_cost(component_data, electrical_sys, db):
    
    '''Get cost of each electrical subsystem in electrical_sys.

    Args:
        component_data (pd.DataFrame) [-]: Table of components used in
            the electrical network.
        electrical_sys (list) [-]: List of electrical subsystems in the
            electrical network.
        db (Object) [-]: Electrical component database object. 

    Attributes:
        cost_dict (dict) [E]: Cost of each subsystem;
            key = subsystem, val = total cost.

    Returns:
        cost_dict

    '''
    
    subsytem_map = {'array': 'Inter-Array Cables',
                    'export': 'Export Cable',
                    'substation': 'Substations',
                    'umbilical': 'Umbilical Cable'}
    
    cost_dict = {key: 0 for key in electrical_sys}

    for _, component in component_data.iterrows():
                        
        install_type = component['Installation Type']

        if install_type not in subsytem_map.keys(): continue
    
        subsytem_type = subsytem_map[install_type]
        
        if subsytem_type not in electrical_sys: continue
    
        cost_dict[subsytem_type] += _get_db_cost(component['Key Identifier'],
                                                 component.Quantity,
                                                 db,
                                                 install_type)

    return cost_dict
    
def _convert_labels(label):
    
    '''Convert labels from subsystems to db compatible names.
    
    Args:
        label (str) [-]: Component type.
        
    Attribute:
        converted_label (str) [-]: DB compatible name.
        
    Returns:
        converted_label
 
    '''

    if any(label in s for s in ['export', 'array']):

        converted_label = 'static_cable'

    elif any(label in s for s in ['substation', 'subhub']):

        converted_label = 'collection_points'

    elif label == 'umbilical':

        converted_label = 'dynamic_cable'

    else:

        converted_label = label

    return converted_label

def _get_db_cost(component_key, quantity, db, type_):
        
    '''Use component key and quantity to calculate total cost.

    Args:
        component_key (int) [-]: Database key.
        quantity (float) [-]: Quantity of component used.
        db (Object) [-]: Electrical component database object.
    
    Attributes:
        val (float) [E]: Total cost of component.

    Returns:
        val

    '''

    converted_type = _convert_labels(type_)

    component_db = getattr(db, converted_type)
    
    cost = \
        component_db[
            component_db.id == component_key].cost.values[0]

    val = quantity * cost

    return val

def _electrical_system_quantity(component_data, electrical_sys):

    '''Count number of instances of electrical systems.
    
    Args:
        component_data (pd.DataFrame) [-]: Table of components used in
            the electrical network.
        electrical_sys (list) [-]: List of electrical subsystems in the
            electrical network.

    Attributes:
        counts (dict) [-]: Number of occurrences of each electrical
            subsystem.

    Returns:
        counts

    Note:
        Can be used to normalise the total cost.

    '''

    counts = {}

    for system in electrical_sys:

        counts[system] = \
            component_data.install_type.value_counts()[system]

    return counts

