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
Created on Wed Apr 06 15:59:04 2016

@author: 108630
"""

from datetime import timedelta

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from matplotlib.dates import (MONTHLY, 
                              DateFormatter,
                              RRuleLocator, 
                              date2num,
                              rrulewrapper)

from . import PlotInterface

    
class InstallationGanttChartPlot(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Installation Gantt Chart Plot"

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

        input_list  =  [
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
            "project.installation_plan"]
                                                
        return input_list
        
    @classmethod
    def declare_optional(cls):
        
        option_list  =  [
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
            "project.installation_plan"]

        return option_list
        
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
                  
        id_map = {"install_support_structure_dates":
                      "project.install_support_structure_dates",
                  "install_devices_dates":
                      "project.install_devices_dates",
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
                  "plan": "project.installation_plan"
                  }

        return id_map

    def connect(self):
        
        self.fig_handle = installation_gantt_chart(
        
            install_support_structure_dates = \
                self.data.install_support_structure_dates,
            install_devices_dates = self.data.install_devices_dates,
            install_dynamic_cable_dates = \
                self.data.install_dynamic_cable_dates,
            install_export_cable_dates = self.data.install_export_cable_dates,                    
            install_array_cable_dates = self.data.install_array_cable_dates,
            install_surface_piercing_substation_dates = \
                self.data.install_surface_piercing_substation_dates,
            install_subsea_collection_point_dates = \
                self.data.install_subsea_collection_point_dates,
            install_cable_protection_dates = \
                self.data.install_cable_protection_dates,
            install_support_structure_prep_time = \
                self.data.install_support_structure_prep_time,                      
            install_devices_prep_time = self.data.install_devices_prep_time,
            install_dynamic_cable_prep_time = \
                self.data.install_dynamic_cable_prep_time,                      
            install_export_cable_prep_time = \
                self.data.install_export_cable_prep_time,                      
            install_array_cable_prep_time = \
                self.data.install_array_cable_prep_time,
            install_surface_piercing_substation_prep_time = \
                self.data.install_surface_piercing_substation_prep_time,
            install_subsea_collection_point_prep_time = \
                self.data.install_subsea_collection_point_prep_time,
            install_cable_protection_prep_time = \
                self.data.install_cable_protection_prep_time,                   
            install_driven_piles_dates = self.data.install_driven_piles_dates,
            install_direct_embedment_dates = \
                self.data.install_direct_embedment_dates,
            install_gravity_based_dates = \
                self.data.install_gravity_based_dates,
            install_pile_anchor_dates = self.data.install_pile_anchor_dates,
            install_drag_embedment_dates = \
                self.data.install_drag_embedment_dates,
            install_suction_embedment_dates = \
                self.data.install_suction_embedment_dates,
            install_driven_piles_prep_time = \
                self.data.install_driven_piles_prep_time,
            install_direct_embedment_prep_time = \
                self.data.install_direct_embedment_prep_time,
            install_gravity_based_prep_time = \
                self.data.install_gravity_based_prep_time,
            install_pile_anchor_prep_time = \
                self.data.install_pile_anchor_prep_time,
            install_drag_embedment_prep_time = \
                self.data.install_drag_embedment_prep_time,
            install_suction_embedment_prep_time = \
                self.data.install_suction_embedment_prep_time,
            plan=self.data.plan          
            )
        
        return


def installation_gantt_chart(
        install_support_structure_dates=None,
        install_devices_dates=None,
        install_dynamic_cable_dates=None,
        install_export_cable_dates=None,
        install_array_cable_dates=None,
        install_surface_piercing_substation_dates=None,
        install_subsea_collection_point_dates=None,
        install_cable_protection_dates=None,
        install_support_structure_prep_time=None,
        install_devices_prep_time=None,
        install_dynamic_cable_prep_time=None,                      
        install_export_cable_prep_time=None,                      
        install_array_cable_prep_time=None,
        install_surface_piercing_substation_prep_time=None,
        install_subsea_collection_point_prep_time=None,
        install_cable_protection_prep_time=None,
        install_driven_piles_dates=None,
        install_direct_embedment_dates=None,
        install_gravity_based_dates=None,
        install_pile_anchor_dates=None,
        install_drag_embedment_dates=None,
        install_suction_embedment_dates=None,
        install_driven_piles_prep_time=None,
        install_direct_embedment_prep_time=None,
        install_gravity_based_prep_time=None,
        install_pile_anchor_prep_time=None,
        install_drag_embedment_prep_time=None,
        install_suction_embedment_prep_time=None,
        plan=None):
    
    if plan is None:
        
        return None
        
    else:
        
        installation = {}
        # sort data
        if any('support structure' in phase for phase in plan):
            
            values = installation_gantt_dates(
                install_support_structure_dates,
                install_support_structure_prep_time)

            installation['Installation of support structure'] = values

        if any('devices' in phase for phase in plan):
            
            values = installation_gantt_dates(install_devices_dates,
                                              install_devices_prep_time)

            installation['Installation of devices'] = values
        
        if any('dynamic' in phase for phase in plan):

            values = installation_gantt_dates(install_dynamic_cable_dates,
                                              install_dynamic_cable_prep_time)

            installation['Installation of dynamic cables'] = values

        if any('export' in phase for phase in plan):
            
            values = installation_gantt_dates(install_export_cable_dates,
                                              install_export_cable_prep_time)

            installation['Installation of static export cables'] = values
        
        if any('array' in phase for phase in plan):
            
            values = installation_gantt_dates(install_array_cable_dates,
                                              install_array_cable_prep_time)

            installation['Installation of static array cables'] = values

        if any('surface piercing' in phase for phase in plan):
            
            values = installation_gantt_dates(
                install_surface_piercing_substation_dates,
                install_surface_piercing_substation_prep_time)
                
            installation[
                'Installation of collection point (surface piercing)'] = values

        if any('seabed' in phase for phase in plan):
            
            values = installation_gantt_dates(
                install_subsea_collection_point_dates,
                install_subsea_collection_point_prep_time)
            
            installation['Installation of collection point (seabed)'] = values

        if any('cable protection' in phase for phase in plan):
            
            values = installation_gantt_dates(
                install_cable_protection_dates,
                install_cable_protection_prep_time)

            installation['Installation of external cable protection'] = values
            
        if any('driven piles' in phase for phase in plan):

            values = installation_gantt_dates(install_driven_piles_dates,
                                              install_driven_piles_prep_time)

            installation['Installation of driven piles anchors/foundations'] =\
                values

        if any('direct-embedment' in phase for phase in plan):

            values = installation_gantt_dates(
                install_direct_embedment_dates,
                install_direct_embedment_prep_time)

            installation[
                'Installation of mooring systems with direct-embedment '
                'anchors'] = values

        if any('gravity based' in phase for phase in plan):

            values = installation_gantt_dates(install_gravity_based_dates,
                                              install_gravity_based_prep_time)

            installation['Installation of gravity based foundations'] = values

        if any('pile anchor' in phase for phase in plan):

            values = installation_gantt_dates(install_pile_anchor_dates,
                                              install_pile_anchor_prep_time)

            installation[
                'Installation of mooring systems with pile anchors'] = values

        if any('drag-embedment' in phase for phase in plan):

            values = installation_gantt_dates(install_drag_embedment_dates,
                                              install_drag_embedment_prep_time)

            installation[
                'Installation of mooring systems with drag-embedment '
                'anchors'] = values 

        if any('suction-embedment' in phase for phase in plan):
            
            values = installation_gantt_dates(
                install_suction_embedment_dates,
                install_suction_embedment_prep_time)

            installation[
                'Installation of mooring systems with suction-embedment '
                'anchors'] = values

    # Data
    num_phases = len(plan)
    pos = np.arange(0.5, num_phases / 2. + 1.0, 0.5)

    ylabels = []
    customDates = []
    # for operation in Installation['OPERATION']:
    for operation in plan:

        l_phase = operation
        log_phase_descript = l_phase

        ylabels.append(log_phase_descript)
        start_dt = (installation[l_phase]['Start date'] -
                    timedelta(hours=installation[l_phase]['Prep time']))
        prep_dt = installation[l_phase]['Start date'] 
        depart_dt = installation[l_phase]['Depart date']
        end_dt = installation[l_phase]['End date']

        customDates.append([date2num(start_dt),
                            date2num(prep_dt),
                            date2num(depart_dt),
                            date2num(end_dt)])

    task_dates = {}

    for i,task in enumerate(ylabels):

        task_dates[task] = customDates[i]

    fig = plt.figure()
    ax = plt.subplot2grid((1, 2), (0, 1), colspan=1)

    # Plot the data:
    (start_date,
     end_prep_begin_wait_date,
     end_wait_begin_sea_date,
     end_date) = task_dates[ylabels[0]]

    ax.barh(0.5, (end_date - start_date),
            left=start_date,
            height=0.4,
            align='center',
            color='blue',
            alpha = 0.75)
    
    ax.barh(0.4, (end_prep_begin_wait_date - start_date),
            left=start_date,
            height=0.1,
            align='center',
            color='red',
            alpha=0.75,
            label="Prep Time")
    
    ax.barh(0.5, (end_wait_begin_sea_date - end_prep_begin_wait_date),
            left=end_prep_begin_wait_date,
            height=0.1,
            align='center',
            color='yellow',
            alpha=0.75,
            label="Waiting Time")
    
    ax.barh(0.6, (end_date - end_wait_begin_sea_date),
            left=end_wait_begin_sea_date,
            height=0.1,
            align='center', 
            color='green',
            alpha=0.75,
            label="Sea Time")

    for i in range(0,len(ylabels)-1):

        (start_date,
         end_prep_begin_wait_date,
         end_wait_begin_sea_date,
         end_date) = task_dates[ylabels[i+1]]

        ax.barh((i * 0.5) + 1.0, (end_date - start_date),
                left=start_date,
                height=0.4,
                align='center',
                color='blue',
                alpha=0.75)
        
        ax.barh((i * 0.5) + 0.9, (end_prep_begin_wait_date - start_date),
                left=start_date,
                height=0.1,
                align='center',
                color='red',
                alpha=0.75)
        
        ax.barh((i * 0.5) + 1.0,
                (end_wait_begin_sea_date - end_prep_begin_wait_date),
                left=end_prep_begin_wait_date,
                height=0.1,
                align='center',
                color='yellow',
                alpha=0.75)
        
        ax.barh((i * 0.5) + 1.1, (end_date - end_wait_begin_sea_date),
                left=end_wait_begin_sea_date,
                height=0.1,
                align='center',
                color='green',
                alpha=0.75)

    # Format the y-axis
    locsy, labelsy = plt.yticks(pos, ylabels)
    plt.setp(labelsy, fontsize=12)

    # Format the x-axis

    ax.axis('tight')
    ax.set_ylim(ymin=-0.1, ymax=(num_phases) / 2 + 1.0)
    ax.grid(color='g', linestyle=':')

    ax.xaxis_date() #Tell matplotlib that these are dates...

    rule = rrulewrapper(MONTHLY, interval=1)
    loc = RRuleLocator(rule)
    formatter = DateFormatter("%b '%y")

    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    labelsx = ax.get_xticklabels()
    plt.setp(labelsx, rotation=30, fontsize=11)

    # Format the legend
    font = font_manager.FontProperties(size='small')
    ax.legend(loc=1, prop=font)

    # Finish up
    ax.invert_yaxis()
    fig.autofmt_xdate()

    return fig


def installation_gantt_dates(dates, prep_time):
    
    gantt_dict = {'Start date': dates.index[0].to_datetime(),
                  'Depart date': dates.index[1].to_datetime(),
                  'End date': dates.index[2].to_datetime(),
                  'Prep time': prep_time}
    
    return gantt_dict
    