# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Francesco Ferri
#    Copyright (C) 2017-2019 Mathew Topper
#    Copyright (C) 2019 Mathew Topper (Sandia National Labs)
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
.. moduleauthor:: Francesco Ferri <ff@civil.aau.dk>
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import abc

import numpy as np
from polylabel import polylabel
from scipy.spatial import Delaunay
from shapely.geometry import (LineString,
                              MultiLineString,
                              MultiPoint,
                              Point,
                              Polygon,
                              box)
from shapely.ops import cascaded_union, nearest_points, polygonize

try:
    from dtocean_hydro.utils.bathymetry_utility import get_unfeasible_regions
except ImportError:
    err_msg = ("The DTOcean hydrodynamics module must be installed in order "
               "to use this module")
    raise ImportError(err_msg)


class DevicePositioner(object):
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, lease_polygon,
                       layer_depths=None,
                       min_depth=None,
                       max_depth=None,
                       min_separation=None,
                       nogo_polygons=None,
                       lease_padding=None,
                       turbine_separation=None):
        
        self._lease_polygon = _buffer_lease_polygon(lease_polygon,
                                                    lease_padding,
                                                    turbine_separation)
        self._bounding_box = box(*lease_polygon.bounds)
        self._layer_depths = layer_depths
        self._min_depth = min_depth
        self._max_depth = max_depth
        self._min_separation = min_separation
        self._nogo_polygons = nogo_polygons
        
        return
    
    def is_grid_valid(self, delta_row, delta_col, beta, psi):
        
        """Check validity of inputs and check if the grid violates the 
        minimum distance constraint, using an ellipse rotated to the 
        array orientation.
        """
        
        self._check_grid_dims(delta_row, delta_col, beta, psi)
        
        p1 = [delta_row * np.cos(beta), delta_row * np.sin(beta)]
        p2 = [delta_col * np.cos(psi), delta_col * np.sin(psi)]
        p3 = (p2[0] - p1[0], p2[1] - p1[1])
        p4 = (p1[0] + p2[0], p1[1] + p2[1])
        
        minx = self._min_separation[0]
        miny = self._min_separation[1]
        
        tests = ((p1[0] / minx) ** 2 + (p1[1] / miny) ** 2 >= 1,
                 (p2[0] / minx) ** 2 + (p2[1] / miny) ** 2 >= 1,
                 (p3[0] / minx) ** 2 + (p3[1] / miny) ** 2 >= 1,
                 (p4[0] / minx) ** 2 + (p4[1] / miny) ** 2 >= 1)
        
        return all(tests)
    
    def _get_valid_nodes(self, nodes):
        
        nodes = _remove_exterior_nodes(nodes, self._lease_polygon)
        
        if self._nogo_polygons is not None:
            
            for polygon in self._nogo_polygons:
                nodes = _remove_interior_nodes(nodes, polygon)
        
        if self._layer_depths is not None:
            
            kwargs = {}
            
            if self._min_depth is not None:
                kwargs["min_depth"] = self._min_depth
            
            if self._max_depth is not None:
                kwargs["max_depth"] = self._max_depth
            
            nodes = _select_nodes_by_depth(nodes,
                                           self._layer_depths,
                                           **kwargs)
        
        return nodes
    
    def _make_grid_nodes(self, array_orientation,
                               delta_row,
                               delta_col,
                               beta,
                               psi,
                               add_rows=0,
                               add_cols=0):
        
        if not self.is_grid_valid(delta_row, delta_col, beta, psi):
            
            err_str = "Grid spacing violates minimum distance constraint"
            raise RuntimeError(err_str)
        
        # Estimate number of rows and cols using bounding box
        minx, miny, maxx, maxy = self._bounding_box.bounds
        
        xdiff = maxx - minx
        ydiff = maxy - miny
        ddiff = np.sqrt(xdiff ** 2 + ydiff ** 2)
        
        cos_beta = np.cos(beta)
        sin_beta = np.sin(beta)
        tan_inv_beta = abs(np.tan(np.pi / 2 - beta))
        cos_psi = np.cos(psi)
        sin_psi = np.sin(psi)
        tan_psi = abs(np.tan(psi))
        
        # Expand the grids to account for skew
        n_rows_beta = int(np.ceil((ddiff + ddiff * tan_inv_beta) / 
                                                              delta_row )) + 1
        n_cols_beta = int(np.ceil(ddiff / delta_col / sin_beta)) + 1
        
        n_rows_psi = int(np.ceil((ddiff + ddiff * tan_psi) / delta_row )) + 1
        n_cols_psi = int(np.ceil(ddiff / delta_col / cos_psi)) + 1
        
        # Ensure there is an odd number of rows and cols
        if n_rows_beta % 2 == 0: n_rows_beta += 1
        if n_cols_beta % 2 == 0: n_cols_beta += 1
        if n_rows_psi % 2 == 0: n_rows_psi += 1
        if n_cols_psi % 2 == 0: n_cols_psi += 1
        
        n_rows = max(n_rows_beta, n_rows_psi) + add_rows
        n_cols = max(n_cols_beta, n_cols_psi) + add_cols
        
        # Initiate the grid vertices
        i, j = np.meshgrid(np.arange(n_cols), np.arange(n_rows))
        
        # Centre indicies
        i = i - n_rows / 2
        j = j - n_cols / 2
        
        # Apply skew and scaling
        x = delta_col * cos_beta * i + delta_row * cos_psi * j
        y = delta_col * sin_beta * i + delta_row * sin_psi * j
        
        # 2D rotation matrix to apply array orientation rotation
        rot_angle = array_orientation - np.pi / 2.
        
        cos_array = np.cos(rot_angle)
        sin_array = np.sin(rot_angle)
        
        Rz = np.array([[cos_array, -1 * sin_array],
                       [sin_array, cos_array]])
        
        coord_raw = np.zeros((2, n_rows * n_cols))
        coord_raw[0,:] = x.ravel()
        coord_raw[1,:] = y.ravel()
        coords = np.dot(Rz, coord_raw).T
        
        # Translation to bounding box's centroid
        coords = coords + self._bounding_box.centroid
        
        return coords
    
    @classmethod
    def _check_grid_dims(cls, delta_row, delta_col, beta, psi):
        
        if delta_row <= 0:
            err_str = "Argument 'delta_row' must be greater than zero"
            raise ValueError(err_str)
            
        if delta_col <= 0:
            err_str = "Argument 'delta_col' must be greater than zero"
            raise ValueError(err_str)
        
        if not (0 < beta < np.pi):
            err_str = "Argument 'beta' must lie in the range (0, pi)"
            raise ValueError(err_str)
            
        if not (np.pi / -2 < psi < np.pi / 2):
            err_str = "Argument 'psi' must lie in the range (-pi / 2, pi / 2)"
            raise ValueError(err_str)
            
        return
    
    @abc.abstractmethod
    def _select_nodes(self, nodes, *args, **kwargs):
        """Hook method for selecting the final nodes"""
        return
    
    def __call__(self, *args, **kwargs):
        
        (array_orientation,
         delta_row,
         delta_col,
         beta,
         psi) = args[:5]
        
        combos = np.array([[0, 0],
                           [0, 1],
                           [1, 0],
                           [1, 1]])
        n_nodes = np.zeros(4)
        
        for i, combo in enumerate(combos):
            
            nodes = self._make_grid_nodes(array_orientation,
                                      delta_row,
                                      delta_col,
                                      beta,
                                      psi,
                                      combo[0],
                                      combo[1])
            nodes = self._get_valid_nodes(nodes)
            n_nodes[i] = len(nodes)
        
        most_devs_idx = np.argmax(n_nodes)
        bost_combo = combos[most_devs_idx]
        
        nodes = self._make_grid_nodes(array_orientation,
                                      delta_row,
                                      delta_col,
                                      beta,
                                      psi,
                                      bost_combo[0],
                                      bost_combo[1])
        nodes = self._get_valid_nodes(nodes)
        nodes = self._select_nodes(nodes, *args, **kwargs)
        
        return nodes


class DummyPositioner(DevicePositioner):
    
    def _select_nodes(self, nodes, *args, **kwargs):
        
        return nodes


class CompassPositioner(DevicePositioner):
    
    def _select_nodes(self, nodes, *args, **kwargs):
        
        delta_row = args[1]
        delta_col =  args[2]
        n_nodes = args[5]
        point_code = args[6] 
    
        if "alpha" not in kwargs or kwargs["alpha"] == "auto":
            alpha = 1. / max(delta_row, delta_col)
        else:
            alpha = kwargs["alpha"]
        
        concave_hull, edge_points = _alpha_shape(nodes, alpha)
        concave_hull = concave_hull.union(MultiPoint(nodes))
        
        if not isinstance(concave_hull, Polygon):
            concave_hull = concave_hull.minimum_rotated_rectangle
        
        if point_code.lower() == "centre" or point_code == "C":
            start_point = polylabel([concave_hull.exterior.coords])
        else:
            start_point_maker = PolyCompass(concave_hull)
            start_point = start_point_maker(point_code)
        
        start_coords = nearest_points(Point(start_point),
                                      concave_hull)[1].coords[:][0]
        nearest_nodes = _nearest_n_nodes(nodes, start_coords, n_nodes)
        
        actual_n_nodes = len(nearest_nodes)
        
        if actual_n_nodes < n_nodes:
            _raise_insufficient_nodes_error(actual_n_nodes, n_nodes)
        
        return nearest_nodes


class ParaPositioner(DevicePositioner):
    
    def _select_nodes(self, nodes, *args, **kwargs):
        
        delta_row = args[1]
        delta_col =  args[2]
        n_nodes = args[5]
        t1 = args[6]
        t2 = args[7]
        
        if len(nodes) < n_nodes:
            _raise_insufficient_nodes_error(len(nodes), n_nodes)
        
        if "alpha" not in kwargs or kwargs["alpha"] == "auto":
            alpha = 1. / max(delta_row, delta_col)
        else:
            alpha = kwargs["alpha"]
        
        if len(nodes) < 4:
            
            nearest_nodes = nodes[:n_nodes]
        
        else:
            
            concave_hull, edge_points = _alpha_shape(nodes, alpha)
            concave_hull = concave_hull.union(MultiPoint(nodes))
            start_coords = _parametric_point_in_polygon(concave_hull, t1, t2)
            nearest_nodes = _nearest_n_nodes(nodes, start_coords, n_nodes)
        
        actual_n_nodes = len(nearest_nodes)
        
        if actual_n_nodes < n_nodes:
            _raise_insufficient_nodes_error(actual_n_nodes, n_nodes)
        
        return nearest_nodes


class PolyCompass(object):
    
    def __init__(self, polygon, centre=None):
        
        self._polygon = polygon
        self._cx = None
        self._cy = None
        self._ns_intersections = None
        self._we_intersections = None
        self._swne_intersections = None
        self._nwse_intersections = None
        
        if centre is None:
            self._cx, self._cy = self._get_bbox_centroid()
        else:
            self._cx, self._cy = centre
        
        return
    
    def _get_bbox_centroid(self):
        
        return box(*self._polygon.bounds).centroid.coords[:][0]
    
    def _add_ns_intersections(self):
        
        ns_line_ends = [(self._cx, -9e8), (self._cx, 9e8)]
        ns_line = LineString(ns_line_ends)
        self._ns_intersections = [point.y for point in
                                  self._polygon.exterior.intersection(ns_line)]
        
        return
    
    def _add_we_intersections(self):
    
        we_line_ends = [(-9e8, self._cy), (9e8, self._cy)]
        we_line = LineString(we_line_ends)
        self._we_intersections = [point.x  for point in 
                                  self._polygon.exterior.intersection(we_line)]
        
        return
    
    def _add_swne_intersections(self):
        
        f = lambda x: x + self._cy - self._cx
        
        swne_line_ends = [(-9e8, f(-9e8)), (9e8, f(9e8))]
        swne_line = LineString(swne_line_ends)
        self._swne_intersections = \
                            self._polygon.exterior.intersection(swne_line)
        
        return
    
    def _add_nwse_intersections(self):
        
        f = lambda x: -x + self._cy + self._cx
        
        nwse_line_ends = [(-9e8, f(-9e8)), (9e8, f(9e8))]
        nwse_line = LineString(nwse_line_ends)
        self._nwse_intersections = \
                            self._polygon.exterior.intersection(nwse_line)
        
        return
    
    def _get_north(self):
        
        if self._ns_intersections is None: self._add_ns_intersections()
        
        return (self._cx, max(self._ns_intersections))
    
    def _get_east(self):
        
        if self._we_intersections is None: self._add_we_intersections()
        
        return (max(self._we_intersections), self._cy)
    
    def _get_south(self):
        
        if self._ns_intersections is None: self._add_ns_intersections()
        
        return (self._cx, min(self._ns_intersections))
    
    def _get_west(self):
        
        if self._we_intersections is None: self._add_we_intersections()
        
        return (min(self._we_intersections), self._cy)
    
    def _get_northeast(self):
        
        if self._swne_intersections is None: self._add_swne_intersections()
        
        get_y = lambda p: p.y
        sorted_intersections = sorted(self._swne_intersections, key=get_y)
        
        return sorted_intersections[-1].coords[0]
    
    def _get_southeast(self):
        
        if self._nwse_intersections is None: self._add_nwse_intersections()
        
        get_y = lambda p: p.y
        sorted_intersections = sorted(self._nwse_intersections, key=get_y)
        
        return sorted_intersections[0].coords[0]
    
    def _get_southwest(self):
        
        if self._swne_intersections is None: self._add_swne_intersections()
        
        get_y = lambda p: p.y
        sorted_intersections = sorted(self._swne_intersections, key=get_y)
        
        return sorted_intersections[0].coords[0]
    
    def _get_northwest(self):
        
        if self._nwse_intersections is None: self._add_nwse_intersections()
        
        get_y = lambda p: p.y
        sorted_intersections = sorted(self._nwse_intersections, key=get_y)
        
        return sorted_intersections[-1].coords[0]
    
    def __call__(self, point_code):
        
        code_map = {"north": "N",
                    "east": "E",
                    "south": "S",
                    "west": "W",
                    "northeast": "NE",
                    "southeast": "SE",
                    "southwest": "SW",
                    "northwest": "NW"}
        
        call_map = {"N": self._get_north,
                    "E": self._get_east,
                    "S": self._get_south,
                    "W": self._get_west,
                    "NE": self._get_northeast,
                    "SE": self._get_southeast,
                    "SW": self._get_southwest,
                    "NW": self._get_northwest}
        
        point_code_local = point_code
        
        if point_code.lower() in code_map:
            point_code_local = code_map[point_code.lower()]
        
        if point_code_local not in code_map.values():
            
            err_str = "Invalid point code entered"
            raise ValueError(err_str)
        
        func = call_map[point_code_local]
        
        return func()


def _buffer_lease_polygon(lease_polygon,
                          lease_padding=None,
                          turbine_separation=None):
    
    if (lease_padding is None and
        turbine_separation is None): return lease_polygon
    
    if lease_padding is None: lease_padding = 0.
    if turbine_separation is None: turbine_separation = 0.
        
    total_buffer = max(lease_padding, turbine_separation)
    lease_polygon_buffered = lease_polygon.buffer(-total_buffer)
    
    return lease_polygon_buffered


def _remove_exterior_nodes(nodes_array, polygon):
    
    new_nodes = [(x, y) for x, y in nodes_array
                                         if Point(x, y).intersects(polygon)]
    nodes_array = np.array(new_nodes)
    
    return nodes_array


def _remove_interior_nodes(nodes_array, polygon):
    
    new_nodes = [(x, y) for x, y in nodes_array
                                 if not Point(x, y).intersects(polygon)]
    nodes_array = np.array(new_nodes)
    
    return nodes_array


def _select_nodes_by_depth(nodes_array,
                           layer_depths,
                           min_depth=-np.inf,
                           max_depth=0):
    
    bathy = _extract_bathymetry(layer_depths)
    zv = bathy.depth.values.T
    xv, yv = np.meshgrid(layer_depths["x"].values,
                         layer_depths["y"].values)
    xyz = np.dstack([xv.flatten(), yv.flatten(), zv.flatten()])[0]
    safe_xyz = xyz[~np.isnan(xyz).any(axis=1)]
    
    exclude, _ = get_unfeasible_regions(safe_xyz, [min_depth, max_depth])
    
    if exclude is None: return nodes_array
    
    new_nodes = [node for node in nodes_array
                                 if not exclude.intersects(Point(node))]
    new_nodes_array = np.array(new_nodes)
    
    return new_nodes_array


def _extract_bathymetry(layer_depths):
    
    return layer_depths.sel(layer="layer 1")


def _alpha_shape(nodes, alpha):
    """
    Compute the alpha shape (concave hull) of a set
    of points.
    @param nodes: Iterable container of points.
    @param alpha: alpha value to influence the
        gooeyness of the border. Smaller numbers
        don't fall inward as much as larger numbers.
        Too large, and you lose everything!
        
    https://gist.github.com/dwyerk/10561690
    """
    
    if len(nodes) < 4:
        # When you have a triangle, there is no sense
        # in computing an alpha shape.
        return MultiPoint(nodes).convex_hull, None
    
    centre_xy = nodes.mean(axis=0)
    centre_nodes = nodes - centre_xy
    
    tri = Delaunay(centre_nodes)
    triangles = centre_nodes[tri.vertices]
    
    # Calculate triangle areas
    a = ((triangles[:,0,0] - triangles[:,1,0]) ** 2 +
                         (triangles[:,0,1] - triangles[:,1,1]) ** 2) ** 0.5
    b = ((triangles[:,1,0] - triangles[:,2,0]) ** 2 +
                         (triangles[:,1,1] - triangles[:,2,1]) ** 2) ** 0.5
    c = ((triangles[:,2,0] - triangles[:,0,0]) ** 2 +
                         (triangles[:,2,1] - triangles[:,0,1]) ** 2) ** 0.5
    
    s = ( a + b + c ) / 2.0
    
    with np.errstate(invalid='ignore'):
        areas = (s*(s-a)*(s-b)*(s-c)) ** 0.5
    
    # Filter out zero area (or close) triangles
    predicate = ~np.logical_or(np.isnan(areas), np.isclose(areas, 0.))
    a = a[predicate]
    b = b[predicate]
    c = c[predicate]
    areas = areas[predicate]
    triangles = triangles[predicate]
    
    circums = a * b * c / (4.0 * areas)
    filtered = triangles[circums < (1.0 / alpha)]
    
    edge1 = filtered[:, (0, 1)]
    edge2 = filtered[:, (1, 2)]
    edge3 = filtered[:, (2, 0)]
    edges = np.concatenate((edge1,edge2,edge3))
    edge_points = [(edge + centre_xy).tolist() for edge in edges]
    
    m = MultiLineString(edge_points)
    triangles = list(polygonize(m))
    concave_hull = cascaded_union(triangles)
    
    return concave_hull, edge_points


def _nearest_n_nodes(nodes, start_coords, number_of_nodes):
    
    start_point = Point(start_coords)
    
    def get_distance(xy):
        end_point = Point(xy)
        return start_point.distance(end_point)
    
    distances = np.apply_along_axis(get_distance, 1, nodes)
    order = np.argsort(distances)
    nodes_sorted = nodes[order, :]
    
    return nodes_sorted[:number_of_nodes, :]


def _parametric_point_in_polygon(poly, t1, t2):
    
    tparam = lambda x0, x1, x2: x0 + t1 * (x1 - x0) + t2 * (x2 - x0)
    
    coords = poly.minimum_rotated_rectangle.exterior.coords
    p0_idx = _get_p0_index(coords)
    p0, p1, p2 = _get_para_points(coords, p0_idx)
    
    return (tparam(p0[0], p1[0], p2[0]),
            tparam(p0[1], p1[1], p2[1]))


def _get_p0_index(coords):
    
    is_min_y = np.isclose(coords.xy[1][:-1],  min(coords.xy[1]), rtol=1e-10)
    min_y_indexs = np.where(is_min_y)[0]
        
    if len(min_y_indexs) > 1:
        min_y_xs = np.array(coords.xy[0])[min_y_indexs]
        is_min_x = np.isclose(min_y_xs, min(min_y_xs), rtol=1e-10)
        min_x_index = np.where(is_min_x)[0]
        min_y_index = min_y_indexs[min_x_index[0]]
    else:
        min_y_index = min_y_indexs[0]
        
    return min_y_index


def _get_para_points(coords, p0_idx):
    
    def next_idx():
        if p0_idx == len(coords) - 2:
            return 0
        else:
            return p0_idx + 1
        
    def prev_idx():
        if p0_idx == 0:
            return -2
        else:
            return p0_idx - 1
    
    if _clockwise(coords.xy[0][:-1], coords.xy[1][:-1]):
        
        p1_idx = prev_idx()
        p2_idx = next_idx()
        
    else:
        
        p1_idx = next_idx()
        p2_idx = prev_idx()
        
    p0 = coords.xy[0][p0_idx],  coords.xy[1][p0_idx]
    p1 = coords.xy[0][p1_idx],  coords.xy[1][p1_idx]
    p2 = coords.xy[0][p2_idx],  coords.xy[1][p2_idx]
    
    return p0, p1, p2


def _clockwise(x, y):
    """ Use the shoelace formula to determine whether the polygon points are
    defined in a clockwise direction"""
    # https://stackoverflow.com/a/1165943/3215152
    # https://stackoverflow.com/a/19875560/3215152
    if sum(x[i] * (y[i + 1] - y[i - 1]) for i in xrange(-1, len(x) - 1)) < 0:
        return True
    return False


def _raise_insufficient_nodes_error(actual, expected, Error=RuntimeError):
    
    err_str = ("Expected number of nodes not found. Expected {} but found "
               "{}").format(expected, actual)
    raise Error(err_str)
