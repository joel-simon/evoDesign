""" Cells output one value. Cells input neighbor average and three deltas
    (4 in, 1 out)
"""
from src.modules import Module, BaseModuleGene
from src.modules.signals import BaseSignalGene, BaseSignalSimulation

class Signal4Gene(BaseSignalGene):

    def __init__(self, ID):
        inputs = [ 'signal%i_avg' % (ID),
                    'signal%i_d0' % (ID),
                    'signal%i_d1' % (ID),
                    'signal%i_d2' % (ID) ]
        outputs = [ ('signal%i_out'%(ID), 'sigmoid') ]
        super(Signal4Gene, self).__init__(ID, inputs=inputs, outputs=outputs)

class Signal4Simulation(BaseSignalSimulation):

    def create_input(self, cell):
        inputs = []
        neighbors = list(self.simulation.hmap.neighbors(cell.userData['coords']))

        for gene in self.module.genes.values():
            key = gene.key()
            signals = []

            for neighbor in neighbors:
                if neighbor and key in neighbor.userData:
                    signals.append(neighbor.userData[key][0])
                else:
                    signals.append(0)

            inputs.extend([sum(signals)/6,
                           signals[0]-signals[3],
                           signals[1]-signals[4],
                           signals[2]-signals[5]])


        assert(len(inputs) == len(self.module.total_inputs()))
        return inputs

class Signal4Module(Module):

    def __init__(self, **kwargs):
        super(Signal4Module, self).__init__(gene=Signal4Gene,
                                            simulation=Signal4Simulation,
                                            **kwargs)

