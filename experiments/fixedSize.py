# import pyximport; pyximport.install()
import argparse

# from src.experiment import Experiment#, Input, Output, OutputCluster
from src.hexSimulation import HexSimulation
from src.hexmap import Map

from src.classification import f1_score, joel_score, precision_recall
# from src.hexRenderer import HexRenderer as Renderer

class Simulationn(HexSimulation):
    """docstring for Simulation"""
    genome_config = {
        'num_morphogens': 1,
        'morphogen_thresholds': 3
    }
    genome_config['inputs'] = [
        'neighbor_t', 'neighbor_tr',
        'neighbor_br', 'neighbor_b',
        'neighbor_bl', 'neighbor_tl',
        'a0t0','a0t1','a0t2',#'a0t3',
        # 'a1t0','a1t1','a1t2','a1t3'
    ]
    genome_config['outputs'] = [
        'apoptosis', 'divide_t', 'divide_tr', 'divide_br',
        'divide_b', 'divide_bl', 'divide_tl', 'a0', 'i0',# 'a1', 'i1'
    ]
    def __init__(self, genome):
        super(Simulation, self).__init__(genome,
            max_steps = 40, bounds=(12, 12))
        # self.target = 60

        # Where we want to have a cell
        self.true = Map(self.bounds, 1)

        self.center = (self.bounds[0]/2, self.bounds[1]/2)

        for r in range(self.bounds[0]):
            for c in range(self.bounds[1]):
                d = self.true.distance(self.center, (r,c))
                if d < 2:
                    self.true[r][c] = 0

        # self.true[4][4] = 0

        # CREATE STARTING CELLS.
        cell = self.create_cell(coords=self.center)


    def _morphogen_inputs(self, cell, i):
        """Get the morphogens threshholds
        """
        inputs = [0.0] * 3
        coords = cell.userData['coords']
        value = self.A[i][coords[0]][coords[1]]
        max_value = 30

        # if 'max_a' not in cell.userData:
        #     cell.userData['max_a'] = 0.0
        # cell.userData['max_a'] = max(cell.userData['max_a'], value)
        # value = cell.userData['max_a']

        p = value/max_value
        p = min(p, .9999)
        inputs[int(p* 3)] = 1

        return inputs

    def create_inputs(self, cell):
        # inputs = []
        coords = cell.userData['coords']
        inputs = list(map(bool, self.hmap.neighbors(coords)))
        for i in range(self.genome.num_morphogens):
            inputs.extend(self._morphogen_inputs(cell, i))
        return inputs

    def handle_outputs(self, cell, outputs):
        if outputs[0] > .5:
            self.destroy_cell(cell)
            return

        grow_outputs = outputs[1:7]
        assert(len(grow_outputs) == 6)

        # m = max(grow_outputs)
        # if m > 0.5:
        #     self.divide_cell(cell, grow_outputs.index(m))

        for i in range(6):
            if grow_outputs[i] > 0.5:
                self.divide_cell(cell, i)

        # Update the morphogen production amounts
        coords = cell.userData['coords']
        self.PA[0][coords[0]][coords[1]] = outputs[7]
        self.PI[0][coords[0]][coords[1]] = outputs[8]

        # self.PA[1][coords[0]][coords[1]] = outputs[9]
        # self.PI[1][coords[0]][coords[1]] = outputs[10]

    def fitness(self):
        n = len(self.cells)
        # fitness = 1 - abs(n-self.target)/float(self.target)
        # fitness = min(.95, fitness)
        # return fitness
        # score = 0
        # total = self.bounds[0] * self.bounds[1] - 7
        # if n < total:
        #     score = (n / float(total)) / 3
        # else:
        #     score = joel_score(true=sum(self.true,[]), pred=sum(self.hmap, []))
        true = sum(self.true,[])
        pred = sum(self.hmap, [])
        # print(precision_recall(true=true, pred=pred))
        precision, recall = precision_recall(true=true, pred=pred)
        if recall < .9:
            return recall / 3
        else:
            return joel_score(true=sum(self.true,[]), pred=sum(self.hmap, []))
            # return (recall + precision)/2
        # return score
