import math
import random
import copy
SQRT3 = math.sqrt( 3 )



cpdef class Map( object ):
    def __init__(self, int rows, int cols, value=0):
        #Map size
        self.rows = rows
        self.cols = cols

        cdef double values[rows][cols]
        # self.values = int [5][10]
        # self.values = [[value for _ in range(shape[1])] for _ in range(shape[0])]

    def __str__( self ):
        return "Map (%d, %d)" % ( self.rows, self.cols )

    # def __getitem__(self, index):
    #     if type(index) == type(tuple()):
    #         return self.values[index[0]][index[1]]
    #     else:
    #         return self.values[index]

    # def __setitem__(self, index, value):
    #     if type(index) == type(tuple()):
    #         self.values[index[0]][index[1]] = value
    #     else:
    #         # return self.values[index]
    #         assert(False)

    cpdef int distance( self, start, destination ):
        """Takes two hex coordinates and determine the distance between them."""
        diffX = destination[0] - start[0]
        diffY = destination[1] - start[1]

        distance = min( abs( diffX ), abs( diffY ) ) + abs( diffX - diffY )
        return distance

    cpdef def directions(self, row, col):
        # for a hex in an odd column
        directions_odd = [(-1, 0), (0,1), (1,1), (1,0), (1, -1), (0,-1)]
        # for a hex in an even column
        directions_even = [(-1, 0), (-1, 1), (0,1), (1,0), (0, -1), (-1,-1)]
        return directions_even if (col % 2 == 0) else directions_odd

    cdef bint valid_coords( self, int row, int col ):
        if col < 0 or col >= self.cols: return 0
        if row < 0 or row >= self.rows: return 0
        return 1

    cpdef is_occupied(self, int row, int col):
      # return (self.valid_coords(coords) and bool(self[coords]))

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


if __name__ == '__main__':
    hex_map = Map((8,8), value=0)
