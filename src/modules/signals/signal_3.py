""" Cells output each direction and input each neighbor
    (6 in, 6 out)
"""
from src.modules import Module, BaseModuleGene
from src.modules.signals import BaseSignalGene, BaseSignalSimulation

class Signal3Gene(BaseSignalGene):

    def __init__(self, ID):
        inputs = [ 'signal%i_in%i'%(ID,i) for i in range(6) ]
        outputs = [ ('signal%i_out%i'%(ID, i), 'sigmoid') for i in range(6)]
        super(Signal3Gene, self).__init__(ID, inputs=inputs, outputs=outputs)

class Signal3Simulation(BaseSignalSimulation):

    def create_input(self, cell):
        inputs = []
        neighbors = list(self.simulation.cmap.neighbors(cell.position))

        for gene in self.module.genes.values():
            key = gene.key()

            for i, neighbor in enumerate(neighbors):
                if neighbor and key in neighbor.userData:
                    inputs.append(neighbor.userData[key][i])
                else:
                    inputs.append(0)

        assert(len(inputs) == len(self.module.total_inputs()))
        return inputs

class Signal3Module(Module):

    def __init__(self, **kwargs):
        super(Signal3Module, self).__init__(gene=Signal3Gene,
                                            simulation=Signal3Simulation,
                                            **kwargs)
