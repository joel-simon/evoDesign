import numpy as np

directions = np.array([[1,0,0], [-1,0,0], [0,1,0],
                       [0,-1,0], [0,0,1], [0,0,-1]])
import operator

# def add_direction(position, direction):
#     return tuple(map(operator.add, position, direction))

def shape(cmap):
    return (len(cmap), len(cmap[0]), len(cmap[0][0]))

def empty(shape):
    if len(shape) == 2:
        x, y = shape
        return [([0]*y) for j in range(x)]
    else:
        x, y, z = shape
        return [[([0]*z) for j in range(y)] for k in range(x)]

# def clear(cmap):
    #

def connected_mask(cmap, start):
    """ Take a 3d python list of objects and return a numpy mask of same shape
        of all points that are connected by a path to start

    """
    X, Y, Z = shape(cmap)
    filter_mask = empty((X, Y, Z))
    # start = []
    counts = [0] * len(start)

    # for x in range(X):
    #     for z in range(Z):
    #         if cmap[x][0][z]:
    #             start.append((x, 0, z))
    #             counts.append(0)

    for i, start_node in enumerate(start):
        if filter_mask[start_node[0]][start_node[1]][start_node[2]]:
            continue

        queue = [start_node]
        while queue:
            x, y, z = queue.pop()
            if not filter_mask[x][y][z]:
                filter_mask[x][y][z] = i+1
                counts[i] += 1

                if x > 0 and cmap[x-1][y][z]:
                    queue.append((x-1, y, z))

                if x < X-1 and cmap[x+1][y][z]:
                    queue.append((x+1, y, z))

                if y > 0 and cmap[x][y-1][z]:
                    queue.append((x, y-1, z))

                if y < Y-1 and cmap[x][y+1][z]:
                    queue.append((x, y+1, z))

                if z > 0 and cmap[x][y][z-1]:
                    queue.append((x, y, z-1))

                if z < Z-1 and cmap[x][y][z+1]:
                    queue.append((x, y, z+1))

    if len(counts) == 0:
        return filter_mask

    largest = counts.index(max(counts))+1
    for x in range(X):
        for y in range(Y):
            for z in range(Z):
                if filter_mask[x][y][z] != largest:
                    filter_mask[x][y][z] = 0
                else:
                    filter_mask[x][y][z] = cmap[x][y][z]
    # derp = filter_mask != counts.index(max(counts))+1
    # filter_mask[derp] = 0
    return filter_mask

# def in_bounds(cmap, position):
#     if position[0] < 0 or position[1] < 0 or position[2] < 0:
#         return False
#     try:
#         _ = cmap[position]
#         return True
#     except IndexError:
#         return False

# def has_neighbor(cmap, position, direction):
#     """ Return if there is a cell in that direction.
#     """
#     x = position[0] + direction[0]
#     y = position[1] + direction[1]
#     z = position[2] + direction[2]
#     if x < 0 or y < 0 or z < 0:
#         return False
#     elif x >= cmap.shape[0] or y >= cmap.shape[1] or z >= cmap.shape[2]:
#         return False
#     else:
#         return bool(cmap[x, y, z])

# def neighbor_positions(cmap, position):
#     """ Return all adjacent positions that have a cell
#     """

#     for direction in directions:
#         x = position[0] + direction[0]
#         y = position[1] + direction[1]
#         z = position[2] + direction[2]
#         if x >=0 and y >=0 and z>=0 and \
#           x < cmap.shape[0] and y < cmap.shape[1] and z < cmap.shape[2]:
#             yield x, y ,z

# def neighbors(cmap, position):
#     """ Return all cells that are adjacent.
#     """
#     for position in neighbor_positions(position):
#         yield cmap[position]
