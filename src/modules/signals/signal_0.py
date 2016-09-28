""" Cells input the average of their neighbors outputs.
    (1 in, 1 out)
"""
from src.modules import Module, BaseModuleGene#, BaseModuleSimulation
from src.modules.signals import BaseSignalGene, BaseSignalSimulation

class Signal0Gene(BaseSignalGene):

    def __init__(self, ID):
        inputs = [ 'signal%i_in' % ID ]
        outputs = [ ('signal%i_out' % ID, 'sigmoid') ]
        super(Signal0Gene, self).__init__(ID, inputs=inputs, outputs=outputs)

class Signal0Simulation(BaseSignalSimulation):

    def create_input(self, cell):
        inputs = []
        neighbors = self.simulation.hmap.neighbors(cell.position)

        for gene in self.module.genes.values():
            signal = 0
            key = gene.key()
            for neighbor in filter(bool, neighbors):
                signal += neighbor.userData[key][0] / 6.0

            inputs.append(signal)

        assert(len(inputs) == len(self.module.total_inputs()))
        return inputs

class Signal0Module(Module):
    """docstring for Signal0Module"""
    def __init__(self, **kwargs):
        super(Signal0Module, self).__init__(gene=Signal0Gene,
                                            simulation=Signal0Simulation,
                                            **kwargs)

