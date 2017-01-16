from __future__ import print_function
import math
from datetime import datetime

# from src.experiment import Experiment
from src.simulation import Simulation
from src.modules import neighbors_distinct, divide_distinct
from src.map_utils import shape, connected_mask
from src.balance import balance_score

class Table(Simulation):
    inputs = ['gradient_y']#[]#['gradient_x', 'gradient_y', 'gradient_z'] ##
    outputs = [('apoptosis', 'sigmoid')]

    def __init__(self, genome, bounds, start=[(0,0,0)]):
        super(Table, self).__init__(genome, bounds, 50, start)

    def cell_init(self, cell):
        cell.userData['connected'] = True
        if 'body' in cell.userData:
            if cell.position[1] == self.bounds[1] - 1:
                cell.userData['body'].joints[4].loads[1] = -1000
                cell.userData['body'].joints[5].loads[1] = -1000
                cell.userData['body'].joints[6].loads[1] = -1000
                cell.userData['body'].joints[7].loads[1] = -1000


    def create_input(self, cell):
        # return []
        x, y, z = cell.position
        x_gradient = -1.0 + 2.0 * x / float(self.bounds[0]-1)
        y_gradient = -1.0 + 2.0 * y / float(self.bounds[1]-1)
        z_gradient = -1.0 + 2.0 * z / float(self.bounds[2]-1)
        return [y_gradient]
        # return [x_gradient, y_gradient, z_gradient]

    def handle_output(self, cell, outputs):
        if outputs[0] > .5: # Apoptos`is.
            self.destroy_cell(cell)

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

        y_max = 0
        top_covereage = 0
        for cell in connected_cells:
            y_max = max(y_max, cell.position[1])
            top_covereage += (cell.position[1] == Y-1)

        if 'truss' in self.module_simulations:
            self.module_simulations['truss'].calculate()
            truss = self.module_simulations['truss'].truss

            fos_fitness = (math.atan((truss.fos_total - 1) * 20) / math.pi) + 0.5
            weight_fitness = 1 - (truss.mass / float(X*Y*Z))

        else:
            fos_fitness = 1
            min_number_cells = (4*(Y-1)) + (X*Z)
            # print(min_number_cells, len(connected_cells))
            weight_fitness = 1 - ((len(connected_cells)- min_number_cells) / (float(X*Y*Z)- min_number_cells))

        height_fitness = y_max / float(Y-1)

        cover_fitness = top_covereage / float(X * Z)

        balance_fitness = balance_score(connected_cells, connected_array)


        total_fitness = ((.1*height_fitness+.9*cover_fitness) * weight_fitness * balance_fitness) ** (1/3.0)

        if self.verbose:
            print('#'*80)
            print('cover_fitness', cover_fitness)
            print('height_fitness', height_fitness)
            print('weight_fitness', weight_fitness)
            print('balance_fitness', balance_fitness)
            print('\ntotal_fitness', total_fitness)
            print('#'*80)
        # total_fitness = .1*height_fitness + .9*cover_fitness
        # total_fitness *= .4*weight_fitness + .6
        # total_fitness *= balance_fitness
        # total_fitness *= fos_fitness

        # if self.verbose:
        #     print('cover_fitness', cover_fitness)
        #     print('weight_fitness', weight_fitness)
        #     print('balance_fitness', balance_fitness)
        #     # print('fos', truss.fos_total)
        #     print('fos_fitness', fos_fitness)
        #     print('total_fitness', total_fitness)

        return total_fitness


    # def render(self, viewer):
    #     pass
