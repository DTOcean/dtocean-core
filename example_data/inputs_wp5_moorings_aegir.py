# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 11:49:00 2016

@author: acollin
"""

import os
import pandas as pd
import numpy as np
from shapely.geometry import Point
import pickle

this_dir = os.path.dirname(os.path.realpath(__file__))
installation_dir = os.path.join(this_dir, "installation")

### Equipment
file_path = os.path.join(installation_dir, 'logisticsDB_equipment_python.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
sheet_names = xls_file.sheet_names

equipment_rov= xls_file.parse(sheet_names[0])
equipment_divers = xls_file.parse(sheet_names[1])
equipment_cable_burial = xls_file.parse(sheet_names[2])
equipment_excavating = xls_file.parse(sheet_names[3])
equipment_mattress = xls_file.parse(sheet_names[4])
equipment_rock_filter_bags = xls_file.parse(sheet_names[5])
equipment_split_pipe = xls_file.parse(sheet_names[6])
equipment_hammer = xls_file.parse(sheet_names[7])
equipment_drilling_rigs = xls_file.parse(sheet_names[8])
equipment_vibro_driver = xls_file.parse(sheet_names[9])

### Ports
file_path = os.path.join(installation_dir, 'logisticsDB_ports_python.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
ports = xls_file.parse(header=0, index_col=0)

### Vessels
file_path = os.path.join(installation_dir, 'logisticsDB_vessel_python.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
vessels = xls_file.parse(header=0, index_col=0)

### Site
bathy_table = pd.read_csv(os.path.join(installation_dir, 'aegirbath2.txt'),
                          delimiter="\t",
                          header=None)
                        
soil_grid = pd.read_csv(os.path.join(installation_dir, 'aegirsoil3.txt'),
                        delimiter="\t",
                        header=None)

Z1=bathy_table[2]
dZ=soil_grid[3]

Z=np.array([Z1.values,(Z1-dZ).values]).T
sediment = np.array([soil_grid[2].values,soil_grid[4].values]).T
x_max = bathy_table.max()[0]
y_max = bathy_table.max()[1]
x_min = bathy_table.min()[0]
y_min = bathy_table.min()[1]

nx=144
ny=176

dx = (x_max-x_min)/(nx-1)
dy = (y_max-y_min)/(ny-1)

x= np.linspace(x_min , x_max , nx)
y = np.linspace(y_min , y_max , ny)
[X,Y] = np.meshgrid(x,y)

bathy_table[0]=np.ravel(X)
bathy_table[1]=np.ravel(Y)

layers = (1,)

depth_layers = []
sediment_layers = []

for z in layers:
    depths = []
    sediments = []
    
    for y_count in y:
        
        d = []
        s = []
        
        for x_count in x:
            
            point_df = bathy_table[(bathy_table[0] == x_count) &
                                   (bathy_table[1] == y_count)].index[0]
            
            d.append(Z[point_df,z])
            s.append(sediment[point_df,z])
                
        depths.append(d)
        sediments.append(s)
        
    depth_layers.append(depths)
    sediment_layers.append(sediments)
    
depth_array = np.swapaxes(np.array(depth_layers, dtype=float), 0, 2)
sediment_array = np.swapaxes(np.array(sediment_layers), 0, 2)

layer_names = ["layer {}".format(x_layers) for x_layers in layers]

strata = strata={"values": {"depth": depth_array,
                            'sediment': sediment_array},
                 "coords": [x, y, layer_names]}

lease_utm_zone = \
    "+proj=utm +zone=30 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

### Metocean
file_path = os.path.join(installation_dir, 'inputs_user.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
metocean = xls_file.parse('metocean', index_col = 0)

fmtStr = "%Y-%m-%d %H:%M:%S.%f"
datetime_index_dict = {'year': metocean['year'],
                       'month': metocean['month'],
                       'day' : metocean['day'],
                       'hour' : metocean['hour']}

wave_series = metocean.loc[:, ['Hs', 'Tp']]
wave_series['DateTime'] = pd.to_datetime(datetime_index_dict, format = fmtStr)
#wave_series = wave_series.set_index(["DateTime"])

tidal_series = metocean.loc[:, ['Cs']]
tidal_series['DateTime'] = pd.to_datetime(datetime_index_dict, format =fmtStr)
#tidal_series = tidal_series.set_index(["DateTime"])

wind_series = metocean.loc[:, ['Ws']]
wind_series['DateTime'] = pd.to_datetime(datetime_index_dict, format = fmtStr)
#wind_series = wind_series.set_index(["DateTime"])

### Device
device = xls_file.parse('device', index_col = 0)

system_type = device['type'].values.item()
system_length = device['length'].values.item()
system_width = device['width'].values.item()
system_height = device['height'].values.item()
system_mass = device['dry mass'].values.item()
assembly_duration = device['assembly duration'].values.item()
load_out_method = device['load out'].values.item()
transportation_method = device['transportation method'].values.item()
bollard_pull = device['bollard pull'].values.item()
connect_duration = device['connect duration'].values.item()
disconnect_duration = device['disconnect duration'].values.item()
project_start_date = pd.to_datetime(device['Project start date'].values.item())
project_start_date = project_start_date.to_datetime()
#sub_systems = device['sub system list'].values.item()
installation_limit_Hs = device['max Hs'].values.item()
installation_limit_Tp = device['max Tp'].values.item()
installation_limit_Ws = device['max wind speed'].values.item()
installation_limit_Cs = device['max current speed'].values.item()

### Subdevice
sub_device = xls_file.parse('sub_device')

### Landfall
landfall = xls_file.parse('landfall', index_col = 0)

### Rates
file_path = os.path.join(installation_dir, 'equipment_perf_rates.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')

equipment_penetration_rates = xls_file.parse('penet')
installation_soil_compatibility = xls_file.parse('laying')
temp_other = xls_file.parse('other')

surface_laying_rate = temp_other[temp_other.index ==
    'Surface laying [m/h]'].values[0][0]
split_pipe_laying_rate = temp_other[temp_other.index ==
    'Installation of iron cast split pipes [m/h]'].values[0][0]
loading_rate = temp_other[temp_other.index ==
    'Loading rate [m/h]'].values[0][0]
grout_rate = temp_other[temp_other.index ==
    'Grout rate [m3/h]'].values[0][0]
fuel_cost_rate = temp_other[temp_other.index ==
    'Fuel cost rate [EUR/l]'].values[0][0]
port_percentage_cost = temp_other[temp_other.index ==
    'Port percentual cost [%]'].values[0][0]
comissioning_time = temp_other[temp_other.index ==
    'Comissioning time [weeks]'].values[0][0]
cost_contingency = temp_other[temp_other.index ==
    'Cost Contingency [%]'].values[0][0]

### Safety factors
port_sf_dict = {"Parameter": ["Terminal area [m^2]",
                              "Terminal load bearing [t/m^2]"],
                "Safety Factor": [0.2, 0.2]
                }
port_sf = pd.DataFrame(port_sf_dict)

vessel_sf_dict = {"Parameter":  ['Deck space [m^2]',
                                 'Deck loading [t/m^2]',
                                 'Max. cargo [t]',
                                 'Crane capacity [t]',
                                 'Bollard pull [t]',
                                 'Turntable loading [t]',
                                 'Turntable inner diameter [m]',
                                 'Turntable outer diameter [m]',
                                 'Dredge depth [m]',
                                 'AH winch rated pull [t]',
                                 'AH drum capacity [m]',
                                 'JackUp max payload [t]',
                                 'JackUp max water depth [m]'],
                "Safety Factor": [0.2,
                                  0.2,
                                  0.2,
                                  0.2,
                                  0.2,
                                  0.2,
                                  0.2,
                                  0.2,
                                  0.2,
                                  0.0,
                                  0.0,
                                  0.2,
                                  0.2]
                }
vessel_sf = pd.DataFrame(vessel_sf_dict)

rov_sf_dict = {"Parameter": ["Manipulator grip force [N]", "Depth rating [m]"],
               "Safety Factor": [0.2, 0.]}
rov_sf = pd.DataFrame(rov_sf_dict)

divers_sf_dict = {"Parameter": ["Max operating depth [m]"],
                  "Safety Factor": [0.]}
divers_sf = pd.DataFrame(divers_sf_dict)

hammer_sf_dict = {"Parameter": ["Max pile diameter [mm]"],
                  "Safety Factor": [0.2]}
hammer_sf = pd.DataFrame(hammer_sf_dict)

vibro_driver_sf_dict = {"Parameter": ['Max pile diameter [mm]',
                                      'Max pile weight [t]',
                                      'Depth rating [m]'],
                        "Safety Factor": [0.2, 0.2, 0.]}
vibro_driver_sf = pd.DataFrame(vibro_driver_sf_dict)

cable_burial_sf_dict = {"Parameter": ['Jetting trench depth [m]',
                                      'Ploughing trench depth [m]',
                                      'Cutting trench depth [m]',
                                      'Max cable diameter [mm]',
                                      'Min cable bending radius [m]',
                                      'Max operating depth [m]'],
                        "Safety Factor": [0, 0, 0, 0, 0, 0]}
cable_burial_sf = pd.DataFrame(cable_burial_sf_dict)

split_pipe_sf_dict = {"Parameter": ['Max cable size [mm]',
                                    'Min bending radius [m]'],
                      "Safety Factor": [0., 0.]}
split_pipe_sf = pd.DataFrame(split_pipe_sf_dict)

### Configuration options
# installation order

# lease area entry point
file_path = os.path.join(installation_dir, 'inputs_user.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
entry_point = xls_file.parse('entry_point', index_col = 0)

x = entry_point.loc[:, 'x coord'].item()
y = entry_point.loc[:, 'y coord'].item()

entry_point_shapely = Point(x,y)

### Hydrodynamic
layout_dict = {'device001': [585500.0, 6650000.0, 0.0]}

#for _, device in layout.iterrows():
#
#    layout_dict[device['device']] = (device['x coord'], device['y coord'], 0)

### Electrical
electrical_network = {}
electrical_network['topology'] = {}
electrical_network['nodes'] = {}

electrical_components = {'Key Identifier': {},
                         'Installation Type' : {},
                         'Quantity' : {},	
                         'UTM X' : {},
                         'UTM Y' : {},
                         'Marker' : {}}

electrical_components_df = pd.DataFrame(electrical_components)

cable_routes = {'Key Identifier' : {},
                'Burial Depth' : {},
                'Split Pipe' : {},
                'UTM X' : {},
                'UTM Y' : {},
                'Marker' : {}}

cable_routes_df = pd.DataFrame(cable_routes)

substations = {'Substation Identifier' : {},
               'Type' : {},
               'Mass' : {},
               'Volume' : {},
               'Length' : {},
               'Width' : {},
               'Height' : {},
               'Profile' : {},
               'Wet Frontal Area' : {},
               'Wet Beam Area' : {},
               'Dry Frontal Area' : {},
               'Dry Beam Area' : {},
               'Surface Roughness' : {},
               'Orientation Angle' : {},
               'Marker' : {}}

substations_df = pd.DataFrame(substations)

umbilicals = {'Key Identifier' : {},
              'Length' : {},
              'Dry Mass' : {},
              'Required Floatation' : {},
              'Floatation Length' : {},
              'Marker' : {}}

umbilicals_df = pd.DataFrame(umbilicals)
### M & F
file_path = os.path.join(installation_dir,
                         'wp4_floating_twoD.pkl')

pkl_file = open(file_path, 'rb')
wp4_data = pickle.load(pkl_file)

mf_network = wp4_data['network']

foundations_data_df = wp4_data['foundations_data']

foundations_layers_df = wp4_data['foundation_layers']

moorings_data_df = wp4_data['moorings']

line_data_df = wp4_data['lines']

lines_id = ['line' + str(n).zfill(3) for n in range(len(line_data_df))]

line_data_df['Line Identifier'] = \
    pd.Series(lines_id, index = line_data_df.index)

line_markers = np.repeat(lines_id, 8)

moorings_data_df['Line Identifier'] = \
    pd.Series(line_markers, index = moorings_data_df.index)

umbilical_data_df = wp4_data['umbilical']

# Need to remove some foundation froms this example otherwise no solution is
# found
# only consider devices for now

foundations_data_df.drop(foundations_data_df.index[[8,9,10]], inplace = True)

## and remove large foundation

foundations_data_df.drop(foundations_data_df.index[[2,6]], inplace = True)

## reset index as must be sequential
foundations_data_df.reset_index(drop=True, inplace = True)

# collect together
test_data = {"component.rov" : equipment_rov,
             "component.divers" : equipment_divers,
             "component.cable_burial" : equipment_cable_burial,
             "component.excavating" : equipment_excavating,
             "component.mattress_installation" : equipment_mattress,
             "component.rock_bags_installation" : equipment_rock_filter_bags,
             "component.split_pipes_installation" : equipment_split_pipe,
             "component.hammer" : equipment_hammer,
             "component.drilling_rigs" : equipment_drilling_rigs,
             "component.vibro_driver" : equipment_vibro_driver,
             "component.vessels" : vessels,
             "component.ports" : ports,

             "project.electrical_network" : None,
             "project.electrical_component_data" : electrical_components_df,
             "project.cable_routes" : cable_routes_df,
             "project.substation_props" : substations_df,
             "project.umbilical_cable_data" : umbilicals_df,

             "project.moorings_foundations_network" : mf_network,
             "project.foundations_component_data" : foundations_data_df,
             "project.foundations_soil_data" : foundations_layers_df,
             "project.moorings_component_data" : moorings_data_df,
             "project.moorings_line_data" : line_data_df,

             "component.equipment_penetration_rates" :
                 equipment_penetration_rates,
             "component.installation_soil_compatibility" :
                 installation_soil_compatibility,
             "project.surface_laying_rate" : surface_laying_rate,
             "project.split_pipe_laying_rate" : split_pipe_laying_rate,
             "project.loading_rate" : loading_rate,
             "project.grout_rate" : grout_rate,
             "project.fuel_cost_rate" : fuel_cost_rate,

             "project.port_percentage_cost" : port_percentage_cost,
             "farm.comissioning_time" : comissioning_time,
             
             "farm.cost_contingency" : cost_contingency,
             
             "project.port_safety_factors" : port_sf,
             "project.vessel_safety_factors" : vessel_sf,
             "project.rov_safety_factors": rov_sf,
             "project.divers_safety_factors": divers_sf,
             "project.hammer_safety_factors": hammer_sf,
             "project.vibro_driver_safety_factors": vibro_driver_sf,
             "project.cable_burial_safety_factors": cable_burial_sf,
             "project.split_pipe_safety_factors": split_pipe_sf,
             
             "project.lease_area_entry_point" : entry_point_shapely,
             "project.layout" : layout_dict,

             "device.system_type" : system_type,
             "device.system_length" : system_length,
             "device.system_width" : system_width,
             "device.system_height" : system_height,
             "device.system_mass": system_mass,
             "device.assembly_duration" : assembly_duration,
             "device.load_out_method" : load_out_method,
             "device.transportation_method" : transportation_method,
             "device.bollard_pull" : bollard_pull,
             "device.connect_duration" : connect_duration,
             "device.disconnect_duration" : disconnect_duration,
             "project.start_date" : project_start_date,
             
             "device.subsystem_installation" : sub_device,

             "device.installation_limit_Hs" : installation_limit_Hs,
             "device.installation_limit_Tp" : installation_limit_Tp,
             "device.installation_limit_Ws" : installation_limit_Ws,
             "device.installation_limit_Cs" : installation_limit_Ws,
             
             "farm.wave_series_installation" : wave_series,
             "farm.tidal_series_installation" : tidal_series,
             "farm.wind_series_installation" : wind_series,
             
             "bathymetry.layers" : strata,
             
             "installation_delete.landfall" : landfall,
             
             "site.projection" : lease_utm_zone,

             }

if __name__ == "__main__":

    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)
    
    print "generate test data: {}".format(pkl_path)
