from itertools import product
from src.map_utils import shape, connected_mask, empty

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

def fits(depth_map, dx, dy, dz):
    if len(depth_map) < dy:
        return 0
    elif depth_map[dy - 1] < dz:
        return 0
    else:
        return 1  

def makey(cmap, cells):
    front_edge_cells = []
    depth_maps = []

    X, Y, Z = shape(cmap)

    # positions = np.zeros((len(cells), 3))
    front_map = empty((X, Y)) # Store the formost z position at each (xy).
    for cell in cells:
        x, y, z = cell.position
        if z > front_map[x][y]:
            front_map[x][y] = z

    for x in range(X):
        for y in range(Y-1):
            z = front_map[x][y]
            cell = cmap[x][y][z]
            if cell and not cmap[x][y+1][z]:
                front_edge_cells.append(cell)
                depth_maps.append(depthmap(cmap, front_map, cell))
    
    return front_edge_cells, depth_maps, front_map
    
def place_items(cmap, cells, items):
    """ Items is list of dimensions
        return list where spot i is cell for object i
    """
    num_items = len(items)
    # front_map = empty((X, Y))
    # create depth maps for each front edge cells
    front_edge_cells, depth_maps, front_map = makey(cmap, cells)
    # print depth_maps
    # print front_map

    # item id -> cell
    results = [None] * num_items
    for i in xrange(num_items):
        dy, dz = items[i]
        for j, (depth_map, cell) in enumerate(zip(depth_maps, front_edge_cells)):
            x, y, z = cell.position
            
            if len(depth_map) >= dy and depth_map[dy - 1] >= dz:
                foo = False
                for _y in range(dy):
                    if front_map[x][y+_y+1] >= z:
                        foo = True
                        break
                if foo:
                    continue    

                results[i] = cell
                # cell.userData[]
                # front_edge_cells.remove(cell)
                del depth_maps[j]
                del front_edge_cells[j]
                for _y in range(dy):
                    front_map[x][y+_y+1] = z

                break

    # print 'results', results
    return results


