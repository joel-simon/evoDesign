from src.modules import Module, BaseModuleSimulation

class NeighborSimulation(BaseModuleSimulation):
    """docstring for NeighborSimulation"""
    def __init__(self, simulation, module):
        super(NeighborSimulation, self).__init__(simulation, module, has_render=False)

    def create_input(self, cell):
        """ Binary encoding of six neighbors.
        """
        coords = cell.userData['coords']
        inputs = [0] * 6
        for i, n, in enumerate(self.simulation.hmap.neighbors(coords)):
            inputs[i] = int(bool(n))
        return inputs

class NeighborModule(Module):
    """docstring for NeighborModule"""
    def __init__(self):
        super(NeighborModule, self).__init__(gene=None,
                                            simulation=NeighborSimulation)

        self.inputs = ['neighbor_t', 'neighbor_tr',  'neighbor_br',
                       'neighbor_b', 'neighbor_bl', 'neighbor_tl']
