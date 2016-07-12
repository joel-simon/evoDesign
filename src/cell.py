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

        # cell_type = genome.cell_types[cell_type]

        self.morphogens = [morph.values() for morph in self.genome.morphogen_genes.values()]
        self.num_morphogens = genome.num_morphogens
        M = self.num_morphogens
        self.morphogen_concentrations = [[0, 0] for _ in range(M)]
        self.morphogen_productions    = [[0, 0] for _ in range(M)]

        self.network = nn.create_feed_forward_phenotype(genome)

    # Used by create inputs.
    def get_threshold(self, c):
        max_value = 20
        p = c/max_value
        p = min(p, .9999)
        th = self.genome.morphogen_thresholds
        return int(p*th)

    def create_inputs(self):
        inputs = [0] * self.genome.num_inputs

        # for i, (name, func) in enumerate(self.genome.inputs):
        #     inputs[i] = func(self)

        if 'stress' in self.genome.inputs:
            inputs[self.genome.inputs.index('stress')] = self.body.get_stress()

        if 'size' in self.genome.inputs:
            inputs[self.genome.inputs.index('size')] = self.body.get_size() / 20.

        for m in range(self.num_morphogens):
            a = self.morphogen_concentrations[m][0]
            t = self.get_threshold(a)
            ind = self.genome.inputs.index('a%it%i'%(m,t))
            inputs[ind] = 1

        return inputs

    def get_outputs(self):
        inputs  = self.create_inputs()
        outputs = self.network.serial_activate(inputs)
        parsed_outputs = dict()

        for i in range(len(outputs)):
            name, act_type, binary = self.genome.outputs[i]
            value = outputs[i]

            if binary:
                if act_type == 'sigmoid':
                    parsed_outputs[name] = (value > .5)
                elif act_type == 'tanh':
                    parsed_outputs[name] = (value > 0)
                else:
                    print(act_type)
                    raise ValueError('Unexpected activaiton type')
            else:
                parsed_outputs[name] = value


        assert(len(parsed_outputs) == self.genome.num_outputs)
        return parsed_outputs
