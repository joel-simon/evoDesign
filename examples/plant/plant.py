from itertools import product
from os import path

from src.export import to_obj
from src.map_utils import shape, connected_mask, empty
from src.balance import balance_score
from src.simulation import Simulation


class Plant(Simulation):
    inputs = ['water', 'light']
    outputs = [('apoptosis', 'sigmoid')]

    def __init__(self, genome, bounds, dirt_height, steps, start=None):
        self.dirt_height = dirt_height
        self.light_fitness = 0
        # self.

        if start == None:
            start = [(bounds[0]/2, dirt_height-1, bounds[2]/2)]

        super(Plant, self).__init__(genome, bounds, steps, start)

    def cell_init(self, cell):
        cell.userData['connected'] = True
        cell.userData['water'] = 0
        cell.userData['light'] = 0

    def create_input(self, cell):
        root = cell.position[1] < self.dirt_height
        return [root, cell.userData['light']]

    def handle_output(self, cell, outputs):
        if outputs[0] > .5: # Apoptosis.
            self.destroy_cell(cell)

    def calculate_light(self, ccells, ccmap):
        X, Y, Z = shape(ccmap)
        top_map = empty((X, Z))
        total_light = 0

        for cell in ccells:
            x, y, z = cell.position
            cell.userData['light'] = 0
            if y > top_map[x][z]:
                top_map[x][z] = y

        for x in range(X):
            for z in range(Z):
                y = top_map[x][z]
                if y > 0:
                    ccmap[x][y][z].userData['light'] = y
                    total_light += y

        total_light /= float(X * (Y-1) * Z)

        return total_light

    def calculate_water(self, ccells, ccmap):
        water_collection = 0
        X, Y, Z = self.bounds
        for y in range(self.dirt_height):
            for x in range(X):
                for z in range(Z):
                    cell = ccmap[x][y][z]
                    if cell:
                        cell_collection = 0
                        if x > 0 and not ccmap[x-1][y][z]:
                            cell_collection += .5
                        if x < X-1 and not ccmap[x+1][y][z]:
                            cell_collection += .5
                        if y > 0 and not ccmap[x-1][y-1][z]:
                            cell_collection += .5
                        if y < Y-1 and not ccmap[x][y+1][z]:
                            cell_collection += .5
                        if z > 0 and not ccmap[x][y][z-1]:
                            cell_collection += .5
                        if z < Z-1 and not ccmap[x][y][z+1]:
                            cell_collection += .5
                        cell.userData['water'] = cell_collection
                        water_collection += cell_collection

        return water_collection

    def watered_cells(self, ccells, ccmap):
        X, Y, Z = self.bounds

        queue = []
        seen = set()

        watered_cells = []
        watered_map = empty(self.bounds)
        
        water = self.calculate_water(ccells, ccmap)
        
        if self.verbose:
            print 'water_collection:', water

        for x, z in product(range(self.bounds[0]), range(self.bounds[2])):
            if ccmap[x][self.dirt_height][z]:
                queue.append((x, self.dirt_height, z))

        while queue and water >= 1:
            xyz = queue.pop(0)
            if xyz in seen:
                continue
            
            seen.add(xyz)
            
            if xyz[1] < self.dirt_height:
                continue
            
            x, y, z = xyz
            watered_cells.append(ccmap[x][y][z])
            watered_map[x][y][z] = ccmap[x][y][z]
            water -= 1
            
            if x > 0 and ccmap[x-1][y][z]:
                queue.append((x-1, y, z))
            if x < X-1 and ccmap[x+1][y][z]:
                queue.append((x+1, y, z))
            if y > 0 and ccmap[x][y-1][z]:
                queue.append((x, y-1, z))
            if y < Y-1 and ccmap[x][y+1][z]:
                queue.append((x, y+1, z))
            if z > 0 and ccmap[x][y][z-1]:
                queue.append((x, y, z-1))
            if z < Z-1 and ccmap[x][y][z+1]:
                queue.append((x, y, z+1))

        return watered_cells, watered_map
    
    def _get_connected(self):
        static_cells = [c.position for c in self.cells if c.position[1] < self.dirt_height]
        ccmap = connected_mask(self.hmap, start=static_cells)
        ccells = []

        for c in self.cells:
            x, y, z = c.position
            if ccmap[x][y][z]:
                c.userData['connected'] = True
                ccells.append(c)
            else:
                c.userData['connected'] = False
        return ccells, ccmap

    def step(self):
        ccells, ccmap = self._get_connected()
        wcells, wcmap = self.watered_cells(ccells, ccmap)
        
        # Only watered cells collect light.
        self.light_fitness = self.calculate_light(wcells, wcmap)

        self.ccmap = ccmap
        self.wcmap = wcmap

    def fitness(self):
        N = float(self.bounds[0] * self.bounds[1] * self.bounds[2])
        self.weight_fitness = 1 - (len(self.cells) / N)
        # balance_fitness = balance_score(ccells, ccmap)

        if self.verbose:
            print "light_fitness", self.light_fitness
            print 'weight_fitness', self.weight_fitness

        return self.light_fitness * (.6 + .4*self.weight_fitness)

    def render(self, viewer):
        viewer.start_draw()

        for cell in self.cells:
            x, y, z = cell.position

            if self.ccmap[x][y][z]:
                if y < self.dirt_height:
                    viewer.draw_cube(x, y, z, (169/255., 104/255., 54/255.))
                else:
                    if self.wcmap[x][y][z]:
                        r = self.wcmap[x][y][z].userData['light'] / 2
                        viewer.draw_cube(x, y, z, (r, 1, 0))
                    else:
                        viewer.draw_cube(x, y, z, (0, .4, 0))

            else:
                viewer.draw_cube(x, y, z, (.1, .1, .1, .5), border=False)

        viewer.end_draw()
        # super(Plant, self).render(viewer) # Draw shelf

    def save(self, directory):
        ccells, ccmap = self._get_connected()
        to_obj(ccmap, path.join(directory, 'cells.obj'))