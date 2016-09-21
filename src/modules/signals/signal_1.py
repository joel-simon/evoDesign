""" Cells output each direction. Cells input neighbor average.
    (1 in, 6 out)
"""
from src.modules import Module, BaseModuleGene
from src.modules.signals import BaseSignalGene, BaseSignalSimulation

class Signal1Gene(BaseSignalGene):

    def __init__(self, ID):
        inputs = [ 'signal%i_in' % (ID)]
        outputs = [ ('signal%i_out%i'%(ID,i), 'sigmoid') for i in range(6)]
        super(Signal1Gene, self).__init__(ID, inputs=inputs, outputs=outputs)

class Signal1Simulation(BaseSignalSimulation):

    def create_input(self, cell):
        inputs = []
        coords = cell.userData['coords']
        neighbors = list(self.simulation.hmap.neighbors(coords))

        for gene in self.module.genes.values():
            key = gene.key()
            neighbor_sum = 0
            for i, neighbor in enumerate(neighbors):
                if neighbor and key in neighbor.userData:
                    neighbor_sum += neighbor.userData[key][0]
            inputs.append(neighbor_sum / 6)

        assert(len(inputs) == len(self.module.total_inputs()))
        return inputs

class Signal1Module(Module):

    def __init__(self, **kwargs):
        super(Signal1Module, self).__init__(gene=Signal1Gene,
                                            simulation=Signal1Simulation,
                                            **kwargs)



