from copy import copy
from src.modules import BaseModuleGene, BaseModuleSimulation

# class BaseSignalSimulation(BaseModuleSimulation):
#     """docstring for BaseSignalSimulation"""
#     def __init__(self, simulation, module):
#         super(BaseSignalSimulation, self).__init__(simulation, module, has_render=False)

    # def cell_init(self, cell):

    # def handle_output(self, cell, outputs):
    #     for i in range(len(self.genes)):
    #         k = len(self.genes[i].outputs)
    #         self.genes[i].handle_output(cell, outputs[(i*k) : (i*k+k)])

    # def create_input(self, cell, sim):
    #     inputs = sum([s.create_input(cell, sim) for s in self.genes.values()], [])
    #     assert len(inputs) == len(self.inputs)
    #     return inputs


class BaseSignalGene(BaseModuleGene):
    def key(self):
        return 'signal%i' % self.ID

    # def handle_output(self, cell, outputs):
    #     assert(len(outputs) == len(self.outputs))
    #     cell.userData[self.key()] = outputs

    def copy(self):
        S = self.__class__(self.ID)
        S.node_genes = copy(self.node_genes)
        return S

    def create_child(self, other):
        S = self.__class__(self.ID)
        return S

    def mutate(self):
        pass

    # def __str__(self):
    #     return '%s(inputs:%s, outputs:%s)'%(self.__class__.__name__, str(self.inputs), str(self.outputs))

class Signal0Gene(BaseSignalGene):
    """ Cells input the average of their neighbors outputs.
        (1 in, 1 out)
    """
    def __init__(self, ID):
        inputs = [ 'signal%i_in' % ID ]
        outputs = [ ('signal%i_out' % ID, 'sigmoid') ]
        super(Signal0Gene, self).__init__(ID, inputs=inputs, outputs=outputs)

class Signal0Simulation(BaseModuleSimulation):
    def __init__(self, simulation, module):
        super(Signal0Simulation, self).__init__(simulation, module, has_render=False)
        
    def cell_init(self, cell):
        for gene in self.module.genes.values():
            cell.userData[gene.key()] = [0]*len(self.module.outputs)

    def create_input(self, cell):
        inputs = []
        neighbors = self.simulation.hmap.neighbors(cell.userData['coords'])

        for gene in self.module.genes.values():
            signal = 0
            key = gene.key()
            for neighbor in filter(bool, neighbors):
                signal += neighbor.userData[key][0] / 6.0

            inputs.append(signal)

        assert(len(inputs) == len(self.module.inputs))
        return inputs


class Signal1(BaseSignalGene):
    """ Cells input each of their neighbors outputs.
        (6 in, 1 out)
    """
    def __init__(self, ID):
        self.inputs = [ 'signal%i_in%i' % (ID, i) for i in range(6) ]
        self.outputs = [ ('signal%i_out' % ID, 'sigmoid') ]
        super(Signal1, self).__init__(ID)

    def create_input(self, cell, sim):
        inputs = []
        key = self.key()
        neighbors = sim.hmap.neighbors(cell.userData['coords'])

        for i, neighbor in enumerate(neighbors):
            if neighbor and key in neighbor.userData:
                inputs.append(neighbor.userData[key][0])
            else:
                inputs.append(0)

        assert(len(inputs) == len(self.inputs))
        return inputs

class Signal2(BaseSignalGene):
    """ Cells output each direction. Cells input neighbor average.
        (1 in, 6 out)
    """
    def __init__(self, ID):
        self.inputs = [ 'signal%i_in' % (ID)]
        self.outputs = [ ('signal%i_out%i'%(ID,i), 'sigmoid') for i in range(6)]
        # print(self.outputs)
        super(Signal2, self).__init__(ID)

    def create_input(self, cell, sim):
        signal_sum = 0.0
        key = self.key()
        neighbors = sim.hmap.neighbors(cell.userData['coords'])
        for i, neighbor in enumerate(neighbors):
            if neighbor and key in neighbor.userData:
                signal_sum += neighbor.userData[key][i]
            else:
                signal_sum += 0

        inputs = [ signal_sum / 6.0 ]
        assert(len(inputs) == len(self.inputs))
        return inputs

class Signal3(BaseSignalGene):
    """ Cells output each direction and input each neighbor
        (6 in, 6 out)
    """
    def __init__(self, ID):
        self.inputs = [ 'signal%i_in%i'%(ID,i) for i in range(6) ]
        self.outputs = [ ('signal%i_out%i'%(ID,i), 'sigmoid') for i in range(6)]
        super(Signal3, self).__init__(ID)

    def create_input(self, cell, sim):
        inputs = []
        key = self.key()
        neighbors = sim.hmap.neighbors(cell.userData['coords'])
        for i, neighbor in enumerate(neighbors):
            if neighbor and key in neighbor.userData:
                inputs.append(neighbor.userData[key][i])
            else:
                inputs.append(0)

        assert(len(inputs) == len(self.inputs))
        return inputs

class Signal4(BaseSignalGene):
    """ Cells output one value. Cells input neighbor average and three deltas
        (4 in, 1 out)
    """
    def __init__(self, ID):
        self.inputs = [ 'signal%i_avg' % (ID),
                        'signal%i_d0' % (ID),
                        'signal%i_d1' % (ID),
                        'signal%i_d2' % (ID) ]
        self.outputs = [ ('signal%i_out'%(ID), 'sigmoid') ]
        super(Signal4, self).__init__(ID)

    def create_input(self, cell, sim):
        signals = []
        key = self.key()
        neighbors = sim.hmap.neighbors(cell.userData['coords'])
        for neighbor in neighbors:
            if neighbor and key in neighbor.userData:
                signals.append(neighbor.userData[key][0])
            else:
                signals.append(0)

        inputs = [ sum(signals)/6,
                   signals[0]-signals[3],
                   signals[1]-signals[4],
                   signals[2]-signals[5]]

        assert(len(inputs) == len(self.inputs))
        return inputs
