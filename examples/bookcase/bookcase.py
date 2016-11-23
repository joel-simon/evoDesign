from src.map_utils import shape, connected_mask, empty
from src.balance import balance_score
from src.simulation import Simulation
from .place import place_items

# import pyximport
# import numpy
# pyximport.install(setup_args={"include_dirs":numpy.get_include()},
#                   reload_support=True)

class Bookcase(Simulation):
    inputs = ['gradient_x', 'gradient_y', 'gradient_z']
    outputs = [('apoptosis', 'sigmoid')]

    def __init__(self, genome, bounds, items, start=[(0,0,0)]):
        # All shelves have a starting position at (0,0,0) and max steps of 100
        super(Bookcase, self).__init__(genome, bounds, max_steps=100,
                                       starting_positions=start)
        self.items = items

    def cell_init(self, cell):
        cell.userData['connected'] = True

    def create_input(self, cell):
        gradient_x = cell.position[0] / float(self.bounds[0])
        gradient_y = cell.position[1] / float(self.bounds[1])
        gradient_z = cell.position[2] / float(self.bounds[2])
        return [ gradient_x, gradient_y, gradient_z ]

    def handle_output(self, cell, outputs):
        if outputs[0] > .5: # Apoptosis.
            self.destroy_cell(cell)

    def storage_score(self, cmap, cells):
        if len(self.items) == 0:
            return 1

        self.placement = place_items(cmap, cells, self.items)

        item_volume = 0.
        stored_volume = 0.
        
        for item, cell in zip(self.items, self.placement):
            v = item[0] * item[1]
            item_volume += v
            if cell:
                stored_volume += v

        return stored_volume / item_volume

    def fitness(self):
        if len(self.cells) == 0:
            return 0

        X, Y, Z = shape(self.hmap)

        static_cells = [c.position for c in self.cells if c.position[1] == 0]
        connected_array = connected_mask(self.hmap, start=static_cells)
        connected_cells = [ ]

        for c in self.cells:
            x, y, z = c.position
            if connected_array[x][y][z]:
                c.userData['connected'] = True
                connected_cells.append(c)
            else:
                c.userData['connected'] = False


        weight_fitness = 1 - (len(connected_cells) / float(X*Y*Z))
        balance_fitness = balance_score(connected_cells, connected_array)
        storage_fitness = self.storage_score(connected_array, connected_cells)
        
        fitness = (.8+.2*weight_fitness) * balance_fitness * storage_fitness
        
        if self.verbose:
            print "weight_fitness", weight_fitness
            print "balance_fitness", balance_fitness
            print "storage_fitness", storage_fitness
            print "fitness", fitness

        return fitness

    def render(self, viewer):
        super(Bookcase, self).render(viewer) # Draw shelf
        # Draw objects on shelf
        for item, cell in zip(self.items, self.placement):
            if cell:
                x, y, z = cell.position
                color = (.5, 1, .5, 1)
                dy = (item[0]-1) / 2.
                dz = (item[1]-1) / 2.
                scale = (1, item[0], item[1])
                viewer.foo(x, y+dy+1, z-dz, color=color, scale=scale, border=True)
