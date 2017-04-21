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

from functools import partial

import pyproj
import numpy as np
import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
from descartes import PolygonPatch
from shapely.ops import transform
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta
import matplotlib.font_manager as font_manager
import matplotlib.dates
from matplotlib.dates import MONTHLY, DateFormatter, rrulewrapper, RRuleLocator
from pylab import arange, subplot2grid, yticks

from aneris.boundary.interface import MaskVariable

from . import PlotInterface

BLUE = '#6699cc'
GREEN = '#32CD32'
RED = '#B20000'


def cmap_env(position=None, bit=True):
    '''Colormap for the environmental package
    '''
    colors = [(128,0,128), (255,0,255), (255,0,0), (255,64,0), (255,128,0),
              (255,178,102), (255,255,51), (153,255,153), (255,255,255),
              (204,229,255), (102,178,255), (0,128,255),  (0,0,255)]

    bit_rgb = np.linspace(0,1,256)
    if position == None:
        position = np.linspace(0,1,len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red':[], 'green':[], 'blue':[]}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))
    
    cmap = matplotlib.colors.LinearSegmentedColormap('environment', cdict, 256)
    return cmap


class TidalPowerPerformancePlot(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Tidal Power Performance"
        
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

        input_list  =  ["device.turbine_performance",
                        "device.cut_in_velocity",
                        "device.cut_out_velocity"
                        ]
                                                
        return input_list
        
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
                  
        id_map = {"perf_curves": "device.turbine_performance",
                  "cut_in": "device.cut_in_velocity",
                  "cut_out": "device.cut_out_velocity"
                  }

        return id_map

    def connect(self):
        
        self.data.perf_curves.plot()

        cut_in = self.data.cut_in
        cut_in_title = self.meta.cut_in.title
        
        plt.axvline(x=cut_in,
                    color='r',
                    linestyle='--')
        plt.text(cut_in + 0.1,
                 0.1,
                 cut_in_title,
                 verticalalignment='bottom',
                 rotation=90)
        
        cut_out = self.data.cut_out
        cut_out_title = self.meta.cut_out.title
        
        plt.axvline(x=cut_out,
                    color='r',
                    linestyle='--')
        plt.text(cut_out + 0.1,
                 0.1,
                 cut_out_title,
                 verticalalignment='bottom',
                 rotation=90)
    
        plt.title(self.get_name())
        plt.xlabel("Velocity m/s")
        
        self.fig_handle = plt.gcf()
        
        return

class SiteBoundaryPlot(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Site Boundary"
        
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

        input_list  =  ["site.selected_name",
                        "hidden.site_boundaries"
                        ]
                                                
        return input_list
        
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
                  
        id_map = {"name": "site.selected_name",
                  "boundaries": "hidden.site_boundaries"
                  }

        return id_map

    def connect(self):
        
        site_poly = self.data.boundaries[self.data.name]
        
        centroid = np.array(site_poly.centroid)
        llcrnrlon = centroid[0] - 5.
        llcrnrlat = centroid[1] - 5.
        urcrnrlon = centroid[0] + 5.
        urcrnrlat = centroid[1] + 5.
        
        m = Basemap(llcrnrlon=llcrnrlon,
                    llcrnrlat=llcrnrlat,
                    urcrnrlon=urcrnrlon,
                    urcrnrlat=urcrnrlat,
                    projection='lcc',
                    lat_1=centroid[1],
                    lon_0=centroid[0],
                    resolution="l",
                    area_thresh=1000.)

        m.drawcountries(linewidth=0.25)
        m.fillcontinents(color='#8B7500')
        m.drawmapboundary(fill_color='lightblue')
        m.drawmeridians(np.arange(0,360,5), labels=[0,0,0,1],fontsize=10)
        m.drawparallels(np.arange(-90,90,5), labels=[1,0,0,0], fontsize=10)

        x, y = m(*centroid)
        m.plot(x, y, 's',
               mew=3, ms=20, fillstyle='none', markeredgecolor='yellow')
        
        ax = plt.gca()
        ax.annotate(self.data.name, 
                    xy=(x, y + 50000),
                    horizontalalignment='center',
                    color='black',
                    backgroundcolor="white",
                    size="large",
                    weight="roman")
        
        self.fig_handle = plt.gcf()
        
        return
        
class AllBoundaryPlot(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "All Boundaries Plot"
        
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

        input_list  =  ["hidden.site_boundary",
                        "site.lease_boundary",
                        "site.corridor_boundary",
                        "corridor.landing_point",
                        "site.projection"
                        ]
                                                
        return input_list
        
    @classmethod
    def declare_optional(cls):
        
        option_list  =  ["site.lease_boundary",
                         "site.corridor_boundary",
                         "corridor.landing_point"
                         ]

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
                  
        id_map = {"site_poly": "hidden.site_boundary",
                  "lease_poly": "site.lease_boundary",
                  "corridor_poly": "site.corridor_boundary",
                  "landing_point": "corridor.landing_point",
                  "projection": "site.projection"
                  }

        return id_map

    def connect(self):
        
        self.fig_handle = boundaries_plot(self.data.site_poly,
                                          self.data.projection,
                                          self.data.lease_poly,
                                          self.data.corridor_poly,
                                          self.data.landing_point)
        
        return
        

class DesignBoundaryPlot(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Design Boundaries Plot"
        
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

        input_list  =  ["site.lease_boundary",
                        "site.corridor_boundary",
                        "corridor.landing_point",
                        ]
                                                
        return input_list
        
    @classmethod
    def declare_optional(cls):
        
        option_list  =  ["site.lease_boundary",
                         "site.corridor_boundary",
                         "corridor.landing_point"
                         ]

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
                  "corridor_poly": "site.corridor_boundary",
                  "landing_point": "corridor.landing_point",
                  }

        return id_map

    def connect(self):
        
        self.fig_handle = boundaries_plot(
                                      lease_poly=self.data.lease_poly,
                                      corridor_poly=self.data.corridor_poly,
                                      landing_point=self.data.landing_point)
        
        return


def boundaries_plot(site_poly=None,
                    projection=None,
                    lease_poly=None,
                    corridor_poly=None,
                    landing_point=None):
    
    if (site_poly is None and
        lease_poly is None and
        corridor_poly is None): return None
        
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1,aspect='equal')
    
    # Convert the site polygon to local coordinate system
    if site_poly is not None:
        
        project = partial(
            pyproj.transform,
            pyproj.Proj(init='epsg:4326'), # source coordinate system
            pyproj.Proj(projection)) # destination coordinate system
    
        local_site_poly = transform(project, site_poly)  # apply projection
    
        patch = PolygonPatch(local_site_poly,
                             fc=RED,
                             ec=RED,
                             fill=False,
                             linewidth=1)
        ax1.add_patch(patch)
    
    if lease_poly is not None:
            
        patch = PolygonPatch(lease_poly,
                             fc=BLUE,
                             ec=BLUE,
                             fill=False,
                             linewidth=2)
        ax1.add_patch(patch)
        
        maxy = lease_poly.bounds[3] + 50.
        centroid = np.array(lease_poly.centroid)
        
        ax1.annotate("Lease Area",
                     xy=(centroid[0], maxy),
                     horizontalalignment='center',
                     verticalalignment='bottom',
                     weight="bold",
                     size='large')
            
    if corridor_poly is not None:
        
        patch = PolygonPatch(corridor_poly,
                             fc=GREEN,
                             ec=GREEN,
                             fill=False,
                             linewidth=2)
        ax1.add_patch(patch)
        
        miny = corridor_poly.bounds[1] - 50.
        centroid = np.array(corridor_poly.centroid)
        
        ax1.annotate("Cable Corridor",
                     xy=(centroid[0], miny),
                     horizontalalignment='center',
                     verticalalignment='top',
                     weight="bold",
                     size='large')
        
    if landing_point is not None:
        
        xy = list(landing_point.coords)[0]
        ax1.plot(xy[0], xy[1], 'or')
        
        label_xy = (xy[0] + 50, xy[1])
        
        ax1.annotate("Export Cable Landing",
                     xy=label_xy,
                     horizontalalignment='left',
                     verticalalignment='center',
                     weight="bold",
                     size='large')

    ax1.margins(0.1,0.1)
    ax1.autoscale_view()

    xlabel = 'UTM x (m)'
    ylabel = 'UTM y (m)'

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
            
    return fig


class EISPlot_hydro(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Environmental Impact Score"
        
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

        input_list  =  ["project.hydro_eis",
                        "project.hydro_confidence"
                        ]
                                                
        return input_list
        
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
                  
        id_map = {"eis": "project.hydro_eis",
                  "confidence": "project.hydro_confidence"
                  }

        return id_map

    def connect(self):

        eis = self.data.eis
        confidence_dict = self.data.confidence
        plot_title = "Hydrodynamics"
        
        self.fig_handle = eis_plot(eis,confidence_dict,plot_title)
        
        return


class EISPlot_elec(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Environmental Impact Score"
        
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

        input_list  =  ["project.elec_eis",
                        "project.elec_confidence"
                        ]
                                                
        return input_list
        
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
                  
        id_map = {"eis": "project.elec_eis",
                  "confidence": "project.elec_confidence"
                  }

        return id_map

    def connect(self):

        eis = self.data.eis
        confidence_dict = self.data.confidence
        plot_title = "Electrical Sub-Systems"
        
        self.fig_handle = eis_plot(eis,confidence_dict,plot_title)
        
        return

class EISPlot_moor(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Environmental Impact Score"
        
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

        input_list  =  ["project.moor_eis",
                        "project.moor_confidence"
                        ]
                                                
        return input_list
        
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
                  
        id_map = {"eis": "project.moor_eis",
                  "confidence": "project.moor_confidence"
                  }

        return id_map

    def connect(self):

        eis = self.data.eis
        confidence_dict = self.data.confidence
        plot_title = "Moorings and Foundations"
        
        self.fig_handle = eis_plot(eis,confidence_dict,plot_title)
        
        return


def eis_plot(eis,confidence_dict,plot_title):
        
    # Environmental impacts
    
    env_impacts = ["Energy Modification",
                   "Footprint",
                   "Collision Risk",
                   "Collision Risk Vessel",
                   "Chemical Pollution",
                   "Turbidity",
                   "Underwater Noise",
                   "Electric Fields",
                   "Magnetic Fields",
                   "Temperature Modification",
                   "Reef Effect",
                   "Reserve Effect",
                   "Resting Place"]
    
    value=[]
    impact=[]
    confidence=[]
    
    for key in env_impacts:
        if key in eis and eis[key] is not None:
            value.append(eis[key])
            impact.append(key)
            confidence.append(confidence_dict[key])
        else:
            value.append(0)
            impact.append(key)
            confidence.append(0)

    # if we want to sort the values
    #value, impact, confidence = zip(*sorted(zip(value, impact, confidence)))

    env_cmap = cmap_env()
    norm = matplotlib.colors.Normalize(-100, 50)
    env_color = env_cmap(norm(value))
    
    fig = plt.figure()

    ax1 = fig.add_subplot(1,1,1)
    x = np.arange(len(value))
    ax1.barh(x, value, align='center', color = env_color)
    ax1.set_xticklabels([])
    ax1.set_yticks(x)
    ax1.set_yticklabels(impact)
    ax1.axvline(0, color='grey')

    for i,v in zip(x, value):
        if v < 0:
            ax1.text(v - 4., i + 0.15 , str(int(round(v))), color = 'black', weight = 'bold')
        elif v > 0:
            ax1.text(v + 1., i + 0.15 , str(int(round(v))), color = 'black', weight = 'bold')
    
    plt.gca().invert_yaxis()

    ax2 = ax1.twinx()
    ax2.barh(x, np.zeros(len(x)), align='center')
    ax2.yaxis.tick_right()
    ax2.set_yticks(x)
    ax2.set_yticklabels(confidence)
    ax2.set_ylabel('Level of confidence')
    
    plt.xlim([-100,50])
    plt.title(plot_title)

    pos1 = ax1.get_position()
    
    cbar_ax = fig.add_axes([pos1.x0, pos1.y0 - 0.06, pos1.width, 0.025])
    
    cmmapable = cm.ScalarMappable(norm, env_cmap)
    cmmapable.set_array(range(-100, 50))
    plt.colorbar(cmmapable, orientation='horizontal',cax=cbar_ax)

    plt.title('(negative impact) --- SCORING SYSTEM SCALE --- (positive impact)')
        
    fig_handle = plt.gcf()

    return fig_handle
    
    
class GEISPlot_hydro(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Global Environmental Impact Score"
        
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

        input_list  =  ["project.hydro_global_eis"
                        ]
                                                
        return input_list
        
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
                  
        id_map = {"geis": "project.hydro_global_eis"
                  }

        return id_map

    def connect(self):

        geis = self.data.geis
        
        self.fig_handle = geis_plot(geis)
        
        return


class GEISPlot_elec(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Global Environmental Impact Score"
        
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

        input_list  =  ["project.elec_global_eis"
                        ]
                                                
        return input_list
        
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
                  
        id_map = {"geis": "project.elec_global_eis"
                  }

        return id_map

    def connect(self):

        geis = self.data.geis
        
        self.fig_handle = geis_plot(geis)
        
        return


class GEISPlot_moor(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Global Environmental Impact Score"
        
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

        input_list  =  ["project.moor_global_eis"
                        ]
                                                
        return input_list
        
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
                  
        id_map = {"geis": "project.moor_global_eis"
                  }

        return id_map

    def connect(self):

        geis = self.data.geis
        
        self.fig_handle = geis_plot(geis)
        
        return



def geis_plot(geis):
        
    value=[]

    if geis['Positive Impact'] is not None:
        value.append(geis['Positive Impact'])
    else:
        value.append(np.nan)

    if geis['Negative Impact'] is not None:
        value.append(geis['Negative Impact'])
    else:
        value.append(np.nan)

    if np.isnan(value[0]):
        pos_impact = 0.
        value[0] = 0.
    else:
        pos_impact = np.int(np.around(value[0]))
            
    if np.isnan(value[1]):
        neg_impact = 0.
        value[1] = 0.
    else:
        neg_impact = np.int(np.around(value[1]))

    env_cmap = cmap_env()
    norm = matplotlib.colors.Normalize(-100, 50)
    env_color = env_cmap(norm(value))
    
    fig = plt.figure()

    ax1 = fig.add_subplot(1,1,1)

    scalex=1.
    scaley=1.
        
    rectangles = {'Positive' : patches.Rectangle((0.2*scalex,0.2*scaley),
                                                  0.1*scalex, 0.2*scaley,
                                                  facecolor=env_color[0],
                                                  edgecolor='k', picker=5,
                            path_effects =
                            [path_effects.withSimplePatchShadow(offset=(10,-10))]),
                  'Negative' : patches.Rectangle((0.2*scalex,0.6*scaley),
                                                  0.1*scalex, 0.2*scaley,
                                                  facecolor=env_color[1],
                                                  edgecolor='k', picker=5,
                            path_effects =
                            [path_effects.withSimplePatchShadow(offset=(10,-10))])}

                                                                                                                                                               
    score = {'Positive' : pos_impact,
             'Negative' : neg_impact}

    if np.isnan(geis['Min Negative Impact']):
        min_neg = 0.
    else:
        min_neg = np.int(np.around(geis['Min Negative Impact']))
     
    if np.isnan(geis['Max Negative Impact']):
        max_neg = 0.
    else:
        max_neg = np.int(np.around(geis['Max Negative Impact']))
            
    if np.isnan(geis['Min Positive Impact']):
        min_pos = 0.
    else:
        min_pos = np.int(np.around(geis['Min Positive Impact']))
            
    if np.isnan(geis['Max Positive Impact']):
        max_pos = 0.
    else:
        max_pos = np.int(np.around(geis['Max Positive Impact']))

    for r in rectangles:
        ax1.add_artist(rectangles[r])
        rx, ry = rectangles[r].get_xy()
        cx = rx + rectangles[r].get_width()/2.0
        cy = ry + rectangles[r].get_height()/2.0

        ax1.annotate(r, (cx - 0.1*scalex, cy ), color='k', weight='bold', 
                     fontsize=16, ha='center', va='center', rotation=90)

        ax1.annotate(score[r], (cx + 0.15 * scalex, cy), color='b', 
                     fontsize=64, ha='center', va='center')

        if r == 'Positive':
            ax1.annotate([min_pos, max_pos], (cx + 0.5*scalex, cy ),
                         color='k', weight='bold', 
                         fontsize=16, ha='center', va='center')

        if r == 'Negative':
            ax1.annotate([min_neg, max_neg], (cx + 0.5*scalex, cy ),
                         color='k', weight='bold', 
                         fontsize=16, ha='center', va='center')
     
    ax1.set_xticks([])
    ax1.set_yticks([])

    plt.title('ENVIRONMENTAL IMPACT ASSESSMENT')

    pos1 = ax1.get_position()
    
    cbar_ax = fig.add_axes([pos1.x0, pos1.y0 - 0.1, pos1.width, 0.025])
    
    cmmapable = cm.ScalarMappable(norm, env_cmap)
    cmmapable.set_array(range(-100, 50))
    plt.colorbar(cmmapable, orientation='horizontal',cax=cbar_ax)

    plt.title('(negative impact) --- SCORING SYSTEM SCALE --- (positive impact)')
 
    fig_handle = plt.gcf()

    return fig_handle
    
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
    pos = arange(0.5,(num_phases)/2 + 1.0,0.5)

    ylabels = []
    customDates = []
    # for operation in Installation['OPERATION']:
    for operation in plan:

        l_phase = operation
        log_phase_descript = l_phase

        ylabels.append(log_phase_descript)
        start_dt = (installation[l_phase]['Start date'] -
                    timedelta(hours = installation[l_phase]['Prep time']))
        prep_dt = installation[l_phase]['Start date'] 
        depart_dt = installation[l_phase]['Depart date']
        end_dt = installation[l_phase]['End date']

        customDates.append([matplotlib.dates.date2num(start_dt),
                            matplotlib.dates.date2num(prep_dt),
                            matplotlib.dates.date2num(depart_dt),
                            matplotlib.dates.date2num(end_dt)])

    task_dates = {}

    for i,task in enumerate(ylabels):

        task_dates[task] = customDates[i]

    fig = plt.figure()
    ax = subplot2grid((1,2), (0,1), colspan=1)

    # Plot the data:
    start_date, end_prep_begin_wait_date, end_wait_begin_sea_date, end_date = \
        task_dates[ylabels[0]]

    ax.barh(0.5, (end_date - start_date), left=start_date, height=0.4,
            align='center', color='blue', alpha = 0.75)
    ax.barh(0.4, (end_prep_begin_wait_date - start_date), left=start_date,
            height=0.1, align='center', color='red', alpha=0.75,
            label="Prep Time")
    ax.barh(0.5, (end_wait_begin_sea_date - end_prep_begin_wait_date),
            left=end_prep_begin_wait_date, height=0.1, align='center',
            color='yellow', alpha = 0.75, label = "Waiting Time")
    ax.barh(0.6, (end_date - end_wait_begin_sea_date),
            left=end_wait_begin_sea_date, height=0.1, align='center', 
            color='green', alpha = 0.75, label = "Sea Time")

    for i in range(0,len(ylabels)-1):

        start_date,end_prep_begin_wait_date,end_wait_begin_sea_date,end_date =\
            task_dates[ylabels[i+1]]

        ax.barh((i*0.5)+1.0, (end_date - start_date), left=start_date,
                height=0.4, align='center', color='blue', alpha = 0.75)
        ax.barh((i*0.5)+1.0-0.1, (end_prep_begin_wait_date - start_date),
                left=start_date, height=0.1, align='center', color='red',
                alpha=0.75)
        ax.barh((i*0.5)+1.0,
                (end_wait_begin_sea_date - end_prep_begin_wait_date),
                left=end_prep_begin_wait_date, height=0.1, align='center',
                color='yellow', alpha = 0.75)
        ax.barh((i*0.5)+1.0+0.1, (end_date - end_wait_begin_sea_date),
                left=end_wait_begin_sea_date, height=0.1, align='center',
                color='green', alpha = 0.75)

    # Format the y-axis
    locsy, labelsy = yticks(pos,ylabels)
    plt.setp(labelsy, fontsize = 12)

    # Format the x-axis

    ax.axis('tight')
    ax.set_ylim(ymin = -0.1, ymax = (num_phases)/2 + 1.0)
    ax.grid(color = 'g', linestyle = ':')

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
    ax.legend(loc=1,prop=font)

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
    