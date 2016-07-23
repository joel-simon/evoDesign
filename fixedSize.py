# import pyximport; pyximport.install()
import argparse

# from src.experiment import Experiment#, Input, Output, OutputCluster
from src.hexSimulation import HexSimulation
from src.hexmap import Map

from src.classification import f1_score
# from src.hexRenderer import HexRenderer as Renderer

class FixedSize(HexSimulation):
    """docstring for FixedSize"""
    genome_config = {
        'num_morphogens': 1,
        'morphogen_thresholds': 4
    }
    genome_config['inputs'] = [
        'neighbor_t', 'neighbor_tr',
        'neighbor_br', 'neighbor_b',
        'neighbor_bl', 'neighbor_tl',
        'a0t0','a0t1','a0t2','a0t3'
    ]
    genome_config['outputs'] = [
        'apoptosis', 'divide_t', 'divide_tr', 'divide_br',
        'divide_b', 'divide_bl', 'divide_tl', 'a0', 'i0'
    ]
    def __init__(self, genome):
        super(FixedSize, self).__init__(genome,
            max_steps = 60, bounds=(9, 9))
        self.target = 60

        # Where we want to have a cell
        self.true = Map(self.bounds, 0)

        self.center = (4, 4)
        for r in range(self.bounds[0]):
            for c in range(self.bounds[1]):
                if self.true.distance(self.center, (r,c)) < 3:
                    self.true[r][c] = 1
        self.true[4][4] = 0

    def _morphogen_inputs(self, cell):
        """Get the morphogens threshholds
        """
        inputs = [0.0] * 4
        coords = cell.userData['coords']
        value = self.A[coords[0]][coords[1]]
        max_value = 30

        # value = max(cell.userData['max_a'], value)
        if 'max_a' not in cell.userData:
            cell.userData['max_a'] = 0.0
        cell.userData['max_a'] = max(cell.userData['max_a'], value)

        p = cell.userData['max_a']/max_value
        p = min(p, .9999)
        inputs[int(p*4)] = 1

        return inputs

    def create_inputs(self, cell):
        # inputs = []
        coords = cell.userData['coords']
        inputs = list(map(bool, self.hmap.neighbors(coords)))
        inputs.extend(self._morphogen_inputs(cell))
        return inputs

    def handle_outputs(self, cell, outputs):
        if outputs[0] > .5:
            self.destroy_cell(cell)
            return

        grow_outputs = outputs[1:-2]
        assert(len(grow_outputs) == 6)

        m = max(grow_outputs)
        # if m > 0.5:
        #     self.divide_cell(cell, grow_outputs.index(m))

        for i in range(6):
            if grow_outputs[i] > 0.5:
                self.divide_cell(cell, i)

        # Update the morphogen production amounts
        coords = cell.userData['coords']
        self.PA[coords[0]][coords[1]] = outputs[-2]
        self.PI[coords[0]][coords[1]] = outputs[-1]

    def set_up(self):
        cell = self.create_cell(coords=self.center)

    def fitness(self, sim):
        # n = len(sim.cells)
        # fitness = 1 - abs(n-self.target)/float(self.target)
        # fitness = min(.95, fitness)
        # return fitness
        # score = 0
        score = f1_score(true=sum(self.true,[]), pred=sum(sim.hmap, []))
        if self.hmap[self.center]:
            score /= 2
        return score
