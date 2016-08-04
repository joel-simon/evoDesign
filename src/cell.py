from .cellGenome import CellGenome
from neat import nn
from neat_custom import ctrnn

class Cell(object):
    """docstring for Cell"""
    def __init__(self, cell_id, genome, body, userData):
        super(Cell, self).__init__()
        assert(isinstance(genome, CellGenome))
        self.id = cell_id
        self.genome = genome
        self.body = body
        self.userData = userData
        # self.network = nn.create_feed_forward_phenotype(genome)
        # self.network = nn.create_recurrent_phenotype(genome)
        self.network = ctrnn.create_phenotype(genome)

    def outputs(self, inputs):
        # return self.network.activate(inputs) # recurrent
        # return self.network.serial_activate(inputs) #feedforward
        return self.network.parallel_activate(inputs) # ctrnn
