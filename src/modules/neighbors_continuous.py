from src.modules import Module, BaseModuleSimulation

class NeighborSimulation(BaseModuleSimulation):
    """docstring for NeighborSimulation"""
    def __init__(self, simulation, module):
        super(NeighborSimulation, self).__init__(simulation, module, has_render=False)

    def create_input(self, cell):
        """ encode number of neighbors as a float in [0,1]
        """
        coords = cell.position
        value = sum(map(bool, self.simulation.hmap.neighbors(coords))) / 6.0
        return [value]

class NeighborModule(Module):
    """docstring for NeighborModule"""
    def __init__(self):
        super(NeighborModule, self).__init__(gene=None,
                                             simulation=NeighborSimulation)
        self.inputs = ['neighbors']
