from cellGenome import CellGenome
from neat import nn
directions = [(0,1), (1,0), (0,-1), (-1,0)]
import math
from Vector import Vector
import random

# TODO move this
class Node(object):
    """docstring for Node"""
    def __init__(self, p):
        self.p = p
        self.m = 1
        self.v = Vector(0,0)
        self.a = Vector(0,0)
        self.static = False
        self.stress = 0.0
        self.r = 16.0

    def applyForce(self, f):
        self.stress += abs(f.norm())
        if not self.static:
          self.a += f / self.m

class Cell(Node):
    """docstring for Cell"""
    def __init__(self, cell_id, genome, p, cell_type=0):
        assert(isinstance(genome, CellGenome))
        self.id = cell_id
        self.genome = genome
        self.cell_type = cell_type

        self.morphogens = [morph.values() for morph in self.genome.morphogen_genes.values()]

        self.num_morphogens = genome.num_morphogens


        M = self.num_morphogens
        self.morphogen_concentrations = [[0, 0] for _ in range(M)]
        self.morphogen_productions    = [[0, 0] for _ in range(M)]

        self.network = nn.create_feed_forward_phenotype(genome)

        super(Cell, self).__init__(p)

    # Used by create inputs.
    def get_threshold(self, c):
        max_value = 5
        p = c/max_value
        p = min(p, .9999)
        th = self.genome.morphogen_thresholds
        return int(p*th)

    def create_inputs(self):
        inputs = [0] * self.genome.num_inputs
        inputs[self.genome.inputs.index('stress')] = self.stress

        for m in range(self.num_morphogens):
            a = self.morphogen_concentrations[m][0]
            t = self.get_threshold(a)
            ind = self.genome.inputs.index('a%it%i'%(m,t))
            inputs[ind] = 1

        return inputs

    # def get_growth_direction(self, growth_directions):
    #     return directions[growth_directions.index(max(growth_directions))]
    #   r = 5
    #   dx, dy = directions[growth_directions.index(max(growth_directions))]
    #   dx = r * math.cos(self.direction) * dx
    #   dy = r * math.sin(self.direction) * dx
    #   return (dx, dy)


        # # divisions = actions[1:1+self.genome.cell_types]
        # if max(divisions) > 0:
        #     # If there is the signal for cell division or diffentiation.
        #     # One for each cell type, if multiple, pick the max.
        #     # growth_directions = actions[1+self.genome.cell_types:1+self.genome.cell_types+4]
        #     parsed_actions['growth'] = divisions.index(max(divisions))
        #     parsed_actions['growth_direction'] = self.get_growth_direction(growth_directions)
        # else:
        #     parsed_actions['growth'] = None
        #     parsed_actions['growth_direction'] = None

        # parsed_actions['morphogens'] = actions[-self.genome.morphogens:]

    def get_outputs(self):
        inputs  = self.create_inputs()
        outputs = self.network.serial_activate(inputs)

        parsed_outputs = dict()
        parsed_outputs['apoptosis']  = (outputs[0] > .75)
        parsed_outputs['division']   = (outputs[1] > .75)
        parsed_outputs['a1'] = outputs[2]*.1
        parsed_outputs['h1'] = outputs[3]*.1

        assert(len(parsed_outputs) == self.genome.num_outputs)
        return parsed_outputs
