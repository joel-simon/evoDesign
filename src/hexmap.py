import math
import random
import copy
SQRT3 = math.sqrt( 3 )

directions = [
    [ (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 0), (-1, 1)],
    [ (1, 1), (1, 0), (1, -1), (0, -1), (-1, 0), (0, 1)]
]

def cube_distance(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) / 2.0

def offset_to_cube(row, col):
    x = col
    z = row - (col - (col&1)) / 2.0
    y = -x-z
    return (x, y, z)


class Map( object ):
    def __init__( self, shape, value=0):
        #Map size
        self.shape = shape
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

    def hash(self):
        string_list = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.values[r][c]:
                    string_list.append('1')
                else:
                    string_list.append('0')
        return hash(''.join(string_list))

    def distance( self, start, destination ):
        """Takes two hex coordinates and determine the distance between them."""
        ac = offset_to_cube(*start)
        bc = offset_to_cube(*destination)
        return cube_distance(ac, bc)


    def directions(self, position):
        # for a hex in an odd column
        return directions[position[1] % 2]

    def valid_coords( self, coords ):
        if coords == None:
            return False
        row, col = coords
        if col < 0 or col >= self.cols: return False
        if row < 0 or row >= self.rows: return False
        return True

    def is_occupied(self, coords):
        return (self.valid_coords(coords) and bool(self[coords]))

    def neighbors(self, center):
        for a, b in self.directions(center):
            row = center[0]+a
            col = center[1]+b
            if col < 0 or col >= self.cols:
                yield None
            elif row < 0 or row >= self.rows:
                yield None
            else:
                yield self.values[row][col]

    def neighbor_coords(self, center, filter_valid=False):
        for a, b in self.directions(center):
            coords = (center[0]+a, center[1]+b)
            if filter_valid:
                if self.valid_coords(coords):
                    yield coords
            else:
                yield coords


    def neighbor(self, coords, direction):
        assert(type(direction) == type(1))
        d = self.directions(coords)[direction]
        return (coords[0] + d[0], coords[1]+d[1])


    def zero(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.values[row][col] = 0



if __name__ == '__main__':
    hex_map = Map((8,8), value=0)
