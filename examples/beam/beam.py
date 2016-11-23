import math
from src.simulation import Simulation
from src.map_utils import empty, shape, connected_mask

class Beam(Simulation):
    """docstring for Simulation"""
    inputs = ['gradient_x', 'gradient_y', 'gradient_z']
    outputs = [('apoptosis', 'sigmoid')]

    def __init__(self, genome, bounds, start=[(0,0,0)]):
        max_steps = 25
        self.static_map = empty(bounds)

        super(Beam, self).__init__(genome, bounds, max_steps, start)

    def cell_init(self, cell):
        cell.userData['connected'] = True

    def create_input(self, cell):
        gradient_x = cell.position[0] / float(self.bounds[0])
        gradient_y = cell.position[1] / float(self.bounds[1])
        gradient_z = cell.position[2] / float(self.bounds[2])
        return [ gradient_x, gradient_y, gradient_z ]

    def handle_output(self, cell, outputs):
        # pass
        if outputs[0] > .5: # Apoptosis.
            self.destroy_cell(cell)

    def render(self, viewer):
        """ Overwrite parent render so we dont draw boxes.
        """
        pass

    def fitness(self):
        if len(self.cells) == 0:
            return 0

        X, Y, Z = shape(self.hmap)

        static_cells = [c.position for c in self.cells if c.position[0] ==0]
        connected_array = connected_mask(self.hmap, start=static_cells)
        connected_cells = [ ]


        for c in self.cells:
            x, y, z = c.position
            if connected_array[x][y][z]:
                c.userData['connected'] = True
                connected_cells.append(c)
            else:
                c.userData['connected'] = False

        if len(connected_cells) == 0:
            return 0

        load_cell = None

        for cell in connected_cells:
            x, y, z = cell.position
            if (load_cell == None) or (x > load_cell.position[0]) or (x >= load_cell.position[0] and y > load_cell.position[1]):
                load_cell = cell

        for joint in self.module_simulations['truss'].truss.joints:
            joint.loads[0] = 0
            joint.loads[1] = 0
            joint.loads[2] = 0

        load_cell.userData['body'].joints[6].loads = [0, -15000, -15000]
        load_cell.userData['body'].joints[5].loads = [0, -15000, -15000]

        max_x = max(c.position[0] for c in connected_cells)
        max_x_fitness = (max_x+1) / float(self.bounds[0])

        self.module_simulations['truss'].calculate()
        truss = self.module_simulations['truss'].truss

        fos_fitness = (math.atan((truss.fos_total - 1) * 20) / math.pi) + 0.5

        max_mass = 250 * self.bounds[0] * self.bounds[1] * self.bounds[2]
        mass_fitness = 1 - min(1, truss.mass/max_mass)

        if self.verbose:
            print 'FITNESSES:'
            print 'fos', truss.fos_total
            print 'fos_fitness', fos_fitness
            print 'mass', truss.mass
            print 'max_mas', max_mass
            print 'mass_fitness', mass_fitness
            print 'max_x', max_x
            print 'max_x_fitness', max_x_fitness
            print

        return max_x_fitness**2 * fos_fitness * mass_fitness
