""" Cells input one value for each of their neighbors
    (1 out, 6 in)
"""
from src.modules import Module, BaseModuleGene
from src.modules.signals import BaseSignalGene, BaseSignalSimulation

class Signal2Gene(BaseSignalGene):

    def __init__(self, ID):
        inputs = [ 'signal%i_in%i' % (ID, i) for i in range(6) ]
        outputs = [ ('signal%i_out' % ID, 'sigmoid') ]
        super(Signal2Gene, self).__init__(ID, inputs=inputs, outputs=outputs)

class Signal2Simulation(BaseSignalSimulation):

    def create_input(self, cell):
        inputs = []
        neighbors = list(self.simulation.hmap.neighbors(cell.position))

        for gene in self.module.genes.values():
            key = gene.key()

            for i, neighbor in enumerate(neighbors):
                if neighbor and key in neighbor.userData:
                    inputs.append(neighbor.userData[key][0])
                else:
                    inputs.append(0)

        assert(len(inputs) == len(self.module.total_inputs()))
        return inputs

class Signal2Module(Module):

    def __init__(self, **kwargs):
        super(Signal2Module, self).__init__(gene=Signal2Gene,
                                            simulation=Signal2Simulation,
                                            **kwargs)

