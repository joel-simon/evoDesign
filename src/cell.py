from src.cellGenome import CellGenome
from src.neat_custom import ctrnn
from neat import nn


class Cell(object):
    """docstring for Cell"""
    def __init__(self, cell_id, genome, position):
        assert(isinstance(genome, CellGenome))
        self.id = cell_id
        self.genome = genome
        self.position = position
        self.userData = dict()
        self.alive = True

        # self.network = nn.create_feed_forward_phenotype(genome)
        self.network = nn.create_recurrent_phenotype(genome)
        # self.network = ctrnn.create_phenotype(genome)

    def outputs(self, inputs):
        # assert self.alive
        # return self.network.serial_activate(inputs) #feedforward
        return self.network.activate(inputs) # recurrent
        # return self.network.parallel_activate(inputs) # ctrnn
