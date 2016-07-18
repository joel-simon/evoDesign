from .cellGenome import CellGenome
from neat import nn
import math
import random

# def cell_factory(parent=object):

class Cell(object):
    """docstring for Cell"""
    def __init__(self, cell_id, genome, body):
        super(Cell, self).__init__()
        assert(isinstance(genome, CellGenome))
        self.id = cell_id
        self.genome = genome
        # self.cell_type = cell_type
        self.body = body
        self.age = 0

        self.userData = dict()
        # cell_type = genome.cell_types[cell_type]

        self.morphogens = [morph.values() for morph in self.genome.morphogen_genes.values()]
        self.num_morphogens = genome.num_morphogens

        self.morphogen_concentrations = [[0, 0] for _ in range(self.num_morphogens)]
        self.morphogen_productions    = [[0, 0] for _ in range(self.num_morphogens)]

        # print(genome)
        self.network = nn.create_feed_forward_phenotype(genome)

    # Used by create inputs.
    def get_threshold(self, c):
        max_value = 20
        p = c/max_value
        p = min(p, .9999)
        th = self.genome.morphogen_thresholds
        return int(p*th)

    # def create_inputs(self):

        # if 'stress' in self.genome.inputs:
        #     inputs[self.genome.inputs.index('stress')] = self.body.get_stress()

        # if 'size' in self.genome.inputs:
        #     inputs[self.genome.inputs.index('size')] = self.body.get_size() / 20.

        # for m in range(self.num_morphogens):
        #     a = self.morphogen_concentrations[m][0]
        #     t = self.get_threshold(a)
        #     ind = self.genome.inputs.index('a%it%i'%(m,t))
        #     inputs[ind] = 1

        # return inputs
#
    def step(self, simulation):
        inputs = [ inp.func(self, simulation) for inp in self.genome.inputs ]
        raw_values = self.network.serial_activate(inputs)

        for value, output in zip(raw_values, self.genome.outputs):
            if output.binary:
                if output.type == 'sigmoid':
                    if  value > .5:
                        output.func(self, simulation)
                elif output.type == 'tanh':
                    if value > 0:
                        output.func(self, simulation)
                else:
                    print(output.type)
                    raise ValueError('Unexpected activation type.')
            else:
                output.func(value)
