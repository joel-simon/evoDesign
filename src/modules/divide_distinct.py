from src.modules import Module, BaseModuleSimulation

class DivideDistinctSimulation(BaseModuleSimulation):
    """docstring for DivideDistinctSimulation"""
    def __init__(self, simulation, module):
        super(DivideDistinctSimulation, self).__init__(simulation, module,
                                                       has_render=False)

    def handle_output(self, cell, outputs):
        sim = self.simulation
        idx = outputs.index(max(outputs))

        if outputs[idx] > .5:
            sim.divide_cell(cell, idx)

class DivideDistinctModule(Module):
    """docstring for DivideDistinctModule"""
    def __init__(self):
        super(DivideDistinctModule, self).__init__(gene=None,
                                            simulation=DivideDistinctSimulation)

        self.outputs = [('divide_%i'%i, 'sigmoid') for i in range(6)]
