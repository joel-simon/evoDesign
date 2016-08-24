import math
from src.modules import Module, BaseModuleSimulation

def angular_distance(theta_1, theta_2, mod=2*math.pi):
    difference = abs(theta_1 % mod - theta_2 % mod)
    return min(difference, mod - difference)

class DivideThetaSimulation(BaseModuleSimulation):
    """docstring for DivideThetaSimulation"""
    def __init__(self, simulation, module):
        super(DivideThetaSimulation, self).__init__(simulation, module, has_render=False)
        self.hex_angles = map(math.radians, [30, 90, 150, 210, 270, 330])


    def handle_output(self, cell, outputs):
        """ outputs[0]: binary encoding division decision
            outputs[1,2]: cos and sin of theta.
            Decode theta by arctan2(sin/con), then fit to hex direction.
        """
        sim = self.simulation
        # print outputs
        if outputs[0] > .5:
            a = math.atan2(outputs[2], outputs[1])
            grow_direction = min(self.hex_angles,
                                 key=lambda b: angular_distance(b, a))
            sim.divide_cell(cell, self.hex_angles.index(grow_direction))

class DivideThetaModule(Module):
    """docstring for DivideThetaModule"""
    def __init__(self):
        super(DivideThetaModule, self).__init__(gene=None,
                                               simulation=DivideThetaSimulation)

        self.outputs = [
            ('divide', 'sigmoid'),
            ('axis_cos', 'identity'),
            ('axis_sin', 'identity')
        ]
