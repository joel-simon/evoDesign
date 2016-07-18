import math
import random
import copy
SQRT3 = math.sqrt( 3 )

from functools import partial

directions_odd = [(-1, 0), (0,1), (1,1), (1,0), (1, -1), (0,-1)]
# for a hex in an even column
directions_even = [(-1, 0), (-1, 1), (0,1), (1,0), (0, -1), (-1,-1)]

class Map( object ):
    def __init__( self, shape, value=0):
        #Map size
        self.shape  = shape
        self.rows = shape[0]
        self.cols = shape[1]

        # self.value
        self.values = [[value for _ in range(shape[1])] for _ in range(shape[0])]

    def __str__( self ):
        return "Map (%d, %d)" % ( self.rows, self.cols )

    def __getitem__(self, index):
        if type(index) == type(tuple()):
            return self.values[index[0]][index[1]]
        else:
            return self.values[index]

    def __iter__(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self[row][col]:
                    yield self[row][col]

    def itemss(self):
        for row in range(self.rows):
            for col in range(self.cols):
                # if self[row][col]:
                yield (row, col), self[row][col]


    # def __setitem__(self,index,value):
    #     self.values[index] = value
    # @property
    # def size( self ):
    #   """Returns the size of the grid as a tuple (row, col)"""
    #   return ( self.rows, self.cols )

    def distance( self, start, destination ):
        """Takes two hex coordinates and determine the distance between them."""
        diffX = destination[0] - start[0]
        diffY = destination[1] - start[1]

        distance = min( abs( diffX ), abs( diffY ) ) + abs( diffX - diffY )
        return distance

    def directions(self, position):
        # for a hex in an odd column
        return directions_even if position[1] % 2 == 0 else directions_odd

    def valid_coords( self, coords ):
        row, col = coords
        if col < 0 or col >= self.cols: return False
        if row < 0 or row >= self.rows: return False
        return True

    # @memoize
    # def valid_neighbor_coords( self, center ):
    #     """
    #     Return the valid cells neighboring the provided cell.
    #     """
    #     neighbors = [ (center[0] +a, center[1] + b) for a, b in self.directions(center)]
    #     return list(filter( self.valid_coords, neighbors ))

    def neighbor_coords(self, center, direction):
        names = ['b','br', 'tr', 't', 'tl', 'bl']
        d = self.directions(center)[names.index(direction)]
        coords = (center[0]+d[0], center[1] + d[1])
        return coords

    def is_occupied(self, coords):
      return (self.valid_coords(coords) and self[coords])

    def occupied_neighbors(self, center):
        return filter( self.is_occupied, neighbors)

    def neighbors(self, center):
        neighbors = []
        for a, b in self.directions(center):
            derp = (center[0]+a, center[1]+b)
            if self.valid_coords(derp):
                neighbors.append(derp)
        # neighbors = []
        # for r, c in coords:
        #     if self.valid_coords((r,c)):
        #         neighbors.append(self.values[r][c])
        #     else:
        #         neighbors.append(None)
        # assert(len(neighbors) == 6)
        return neighbors

    def named_neighbors(self, center):
        print('$'*80)
        names = ['b','br', 'tr', 't', 'tl', 'bl']
        coords = [ (center[0] +a, center[1] + b) for a, b in self.directions(center)]
        neighbors = []
        for r, c in coords:
            if self.valid_coords((r,c)):
                neighbors.append(self.values[r][c])
            else:
                neighbors.append(False)
        assert(len(neighbors) == 6)
        return dict(zip(names, neighbors))

    # def num_occupied_neighbors(self, center):
    #     n = 0
    #     for a, b in self.directions(center):
    #         if self.is_occupied((center[0] + a, center[1] + b)):
    #             n += 1
    #     return n

if __name__ == '__main__':
    hex_map = Map((8,8), value=0)
    # print(hex_map.ascii())

