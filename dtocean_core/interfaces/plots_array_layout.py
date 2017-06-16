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

import numpy as np
import matplotlib.pyplot as plt
from descartes import PolygonPatch
from shapely.geometry import Polygon

from . import PlotInterface

BLUE = '#6699cc'
GREEN = '#32CD32'
RED = '#B20000'
GREY = '#999999'


class ArrayLeasePlot(PlotInterface):
    
    @classmethod
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Lease Area Array Layout"
        
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

        input_list = ["site.lease_boundary",
                      "project.layout",
                      "options.boundary_padding"
                      ]
                                                
        return input_list
    
    @classmethod
    def declare_optional(cls):
        
        option_list = ["options.boundary_padding"]

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
                  
        id_map = {"lease_poly": "site.lease_boundary",
                  "layout": "project.layout",
                  "padding": "options.boundary_padding"
                  }

        return id_map

    def connect(self):
        
        x = []
        y = []

        for coords in self.data.layout.itervalues():
            x.append(coords.x)
            y.append(coords.y)

        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1, aspect='equal')
        ax1.plot(x, y, 'k+', mew=2, markersize=10)
        
        for key, point in self.data.layout.iteritems():
            
            coords = list(point.coords)[0]
            ax1.annotate(str(key),
                         xy=coords[:2],
                         xytext=(0, 10),
                         xycoords='data',
                         textcoords='offset pixels',
                         horizontalalignment='center',
                         weight="bold",
                         size='large')
            
        lease_boundary = self.data.lease_poly
            
        if self.data.padding is not None:
            
            outer_coords = list(lease_boundary.exterior.coords)
            inner_boundary = lease_boundary.buffer(-self.data.padding)
            inner_coords = list(inner_boundary.exterior.coords)
            lease_boundary = Polygon(outer_coords, [inner_coords[::-1]])

            patch = PolygonPatch(lease_boundary,
                                 fc=RED,
                                 fill=True,
                                 alpha=0.3,
                                 ls=None)
                
            ax1.add_patch(patch)
            
        patch = PolygonPatch(lease_boundary,
                             ec=BLUE,
                             fill=False,
                             linewidth=2)
        
        ax1.add_patch(patch)
        
        maxy = self.data.lease_poly.bounds[3] + 50.
        centroid = np.array(self.data.lease_poly.centroid)
        
        ax1.annotate("Lease Area",
                     xy=(centroid[0], maxy),
                     horizontalalignment='center',
                     verticalalignment='bottom',
                     weight="bold",
                     size='large')
        
        ax1.margins(0.1, 0.1)
        ax1.autoscale_view()

        xlabel = 'UTM x [$m$]'
        ylabel = 'UTM y [$m$]'

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)
        
        plt.title("Array Layout in Lease Area")
        
        self.fig_handle = plt.gcf()
        
        return
