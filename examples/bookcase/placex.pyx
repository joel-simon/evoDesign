from itertools import product
from src.map_utils import shape, connected_mask, empty

import numpy as np
# cimport numpy as np

# import cython
# cimport cython

# from libc.math cimport sqrt, M_PI, pow, abs

# DTYPE = np.float64
# ctypedef np.float64_t DTYPE_t

# ITYPE = np.int64
# ctypedef np.int64_t ITYPE_t

def depth(cmap, x, y, z):
    d = 0
    while (z-d) >= 0 and not cmap[x][y][z-d]:
        d += 1
    return d

def depthmap(cmap, front_map, cell):
    x, y, z = cell.position
    X, Y, Z = shape(cmap)
    h = 1

    # The depths of filled surface behind cell.
    d = 0
    while (z-d) >= 0 and cmap[x][y][z-d]:
        d += 1

    depths = []
    while (y+h) <= Y-1 and front_map[x][y+h] <=z:
        _d = min(d, depth(cmap, x, y+h, z))
        if depths:
            _d = min(depths[-1], _d)
        if _d == 0:
            break
        depths.append(_d)
        h += 1

    return depths

# def fits(cmap, dmap, item, cell):
#     dy, dz = item
#     X, Y , Z = shape(cmap)
#     dx = 1
#     x, y, z = cell.position
#     cells = []

#     if x + dx > X or (z - dz + 1) < 0 or y+dy+1 > Y: # Bounds check.
#         # print 'not in bounds', cell.position, item, Z, z-dz
#         return []

#     for i in reversed(xrange(dx)):
#         # for _y in range(dy):
#         #     if dmap[x+i][y+_y+1] >= z:
#         #         return []

#         c = cmap[x+i][y][z]
#         if not c:
#             return []

#         if 'depth_map' not in c.userData or len(c.userData['depth_map']) < dy:
#             return []

#         if c.userData['depth_map'][dy-1] < dz:
#             return []

#         cells.append(c)

#     return cells

# cdef int fits
def fits(depth_map, dx, dy, dz):
    if depth_map.shape[0] < dy:
        return 0
    elif depth_map[dy - 1] < dz:
        return 0
    else:
        return 1  

def place_items(cmap, cells, items):
    # import pickle
    # pickle.dump((cmap, cells, items), open('place_data.p', 'wb'))
    """ Items is list of dimensions
        return list where spot i is cell for object i
    """
    i = 0
    num_items = len(items)
    X, Y, Z = shape(cmap)

    positions = np.zeros((len(cells), 3))
    front_map = np.zeros((X, Y), dtype='int16') # Store the formost z position at each (xy).

    for i in range(len(cells)):
        cell = cells[i]
        x, y, z = cell.position
        positions[i, 0] = x
        positions[i, 1] = y
        positions[i, 2] = z

        if z > front_map[x, y]:
            front_map[x, y] = z

    # create depth maps for each front edge cells
    front_edge_cells = []
    depth_maps = []

    for x in range(X):
        for y in range(Y-1):
            z = front_map[x][y]
            cell = cmap[x][y][z]
            if cell and not cmap[x][y+1][z]:
                front_edge_cells.append(cell)
                depth_maps.append(depthmap(cmap, front_map, cell))
    depth_maps = np.array(depth_maps)
    
    # print depth_maps
    # print front_map

    # item id -> cell
    results = [None] * num_items
    for i in xrange(num_items):
        dy, dz = items[i]
        placed = False
        for depth_map, cell in zip(depth_maps, front_edge_cells):
            if fits(depth_map, 1, dy, dz):
                results[i] = cell
                front_edge_cells.remove(cell)
                placed = True
                break
        if not placed:
            break

    # print 'results', results
    return results


