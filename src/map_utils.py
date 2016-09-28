import numpy as np

directions = np.array([[1,0,0], [-1,0,0], [0,1,0],
                       [0,-1,0], [0,0,1], [0,0,-1]])
import operator

# def add_direction(position, direction):
#     return tuple(map(operator.add, position, direction))

def shape(hmap):
    return (len(hmap), len(hmap[0]), len(hmap[0][0]))

# def in_bounds(hmap, position):
#     if position[0] < 0 or position[1] < 0 or position[2] < 0:
#         return False
#     try:
#         _ = hmap[position]
#         return True
#     except IndexError:
#         return False

# def has_neighbor(hmap, position, direction):
#     """ Return if there is a cell in that direction.
#     """
#     x = position[0] + direction[0]
#     y = position[1] + direction[1]
#     z = position[2] + direction[2]
#     if x < 0 or y < 0 or z < 0:
#         return False
#     elif x >= hmap.shape[0] or y >= hmap.shape[1] or z >= hmap.shape[2]:
#         return False
#     else:
#         return bool(hmap[x, y, z])

# def neighbor_positions(hmap, position):
#     """ Return all adjacent positions that have a cell
#     """

#     for direction in directions:
#         x = position[0] + direction[0]
#         y = position[1] + direction[1]
#         z = position[2] + direction[2]
#         if x >=0 and y >=0 and z>=0 and \
#           x < hmap.shape[0] and y < hmap.shape[1] and z < hmap.shape[2]:
#             yield x, y ,z

# def neighbors(hmap, position):
#     """ Return all cells that are adjacent.
#     """
#     for position in neighbor_positions(position):
#         yield hmap[position]

def empty(shape):
    if len(shape) == 2:
        x, y = shape
        return [([0]*y) for j in xrange(y)]
    else:
        x, y, z = shape
        return [[([0]*z) for j in xrange(y)] for k in xrange(x)]

def connected_mask(hmap):
    """ Take a 3d python list of objects and return a numpy mask of same shape
        of all points that are connected by a path to start

    """
    X, Y, Z = shape(hmap)
    filter_mask = np.zeros((X, Y, Z), dtype=int)
    start = []
    counts = []


    for x in xrange(X):
        for z in xrange(Z):
            if hmap[x][0][z]:
                start.append((x, 0, z))
                counts.append(0)

    for i, start_node in enumerate(start):
        if filter_mask[start_node]:
            continue

        queue = [start_node]
        while queue:
            node = queue.pop()
            if not filter_mask[node]:
                filter_mask[node] = i+1
                counts[i] += 1
                x, y, z = node
                if x > 0 and hmap[x-1][y][z]:
                    queue.append((x-1, y, z))

                if x < X-1 and hmap[x+1][y][z]:
                    queue.append((x+1, y, z))

                if y > 0 and hmap[x][y-1][z]:
                    queue.append((x, y-1, z))

                if y < Y-1 and hmap[x][y+1][z]:
                    queue.append((x, y+1, z))

                if z > 0 and hmap[x][y][z-1]:
                    queue.append((x, y, z-1))

                if z < Z-1 and hmap[x][y][z+1]:
                    queue.append((x, y, z+1))
    
    if len(counts) == 0:
        return filter_mask

    derp = filter_mask != counts.index(max(counts))+1
    filter_mask[derp] = 0
    return filter_mask
