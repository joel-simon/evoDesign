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

        self.values = [[value for _ in range(shape[1])] for _ in range(shape[0])]

    def __str__( self ):
        return "Map (%d, %d)" % ( self.rows, self.cols )

    def __getitem__(self, index):
        if type(index) == type(tuple()):
            return self.values[index[0]][index[1]]
        else:
            return self.values[index]

    def __setitem__(self, index, value):
        if type(index) == type(tuple()):
            self.values[index[0]][index[1]] = value
        else:
            # return self.values[index]
            assert(False)

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
        assert(type(row) == type(1))
        assert(type(col) == type(1))
        if col < 0 or col >= self.cols: return False
        if row < 0 or row >= self.rows: return False
        return True

    def is_occupied(self, coords):
      return (self.valid_coords(coords) and bool(self[coords]))

    # def occupied_neighbors(self, center):
    #     return filter( self.is_occupied, neighbors)

    def neighbors(self, center, labels=False):
        if labels:
            return self.named_neighbors(center)
        else:
            neighbors = []
            for a, b in self.directions(center):
                derp = (center[0]+a, center[1]+b)
                if self.valid_coords(derp):
                    neighbors.append(derp)
            return neighbors


    def neighbor(self, coords, direction):
        assert(type(direction) == type(1))
        d = self.directions(coords)[direction]
        return (coords[0] + d[0], coords[1]+d[1])

    # def beepbop(self, center, direction):
    #     names = ['bottom','bottom_right', 'top_right',
    #             'top', 'top_left', 'bottom_left']
    #     coords = [ (center[0] +a, center[1] + b) for a, b in self.directions(center)]
    #     return dict(zip(names, coords))[direction]

    def named_neighbors(self, center):
        names = ['bottom','bottom_right', 'top_right',
                'top', 'top_left', 'bottom_left']
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

