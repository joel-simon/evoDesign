import time
import math
from src.modules import Module, BaseModuleSimulation
from hexBody import HexBody

from src.modules.truss.truss import Truss
from src.modules.truss.drawTruss import drawTruss

SQRT3 = math.sqrt(3)

class TrussSimulation(BaseModuleSimulation):
    """docstring for TrussSimulation"""
    def __init__(self, simulation, module, static_map):
        super(TrussSimulation, self).__init__(simulation, module)
        self.static_map = static_map
        self.hex_radius = 14

    def _create_body(self, truss, cell):
        """ Create a physical representation of cell.
        """
        coords = cell.userData['coords']
        row, col = coords

        neighbor_bodies = []
        for n in self.simulation.hmap.neighbors(coords):
            if n and 'body' in n.userData:
                neighbor_bodies.append(n.userData['body'])
            else:
                neighbor_bodies.append(None)

        # Calculate position.
        offset = self.hex_radius * SQRT3 / 2 if col % 2 else 0
        left = 1.5 * col * self.hex_radius
        top = offset + SQRT3 * row * self.hex_radius

        cell.userData['body'] = HexBody(
            ID=cell.id,
            truss=truss,
            position=(left, top),
            radius=self.hex_radius,
            neighbors=neighbor_bodies,
            static=self.static_map[coords]
        )

    def cell_init(self, cell):
        cell.userData['stress'] = 0.0

    def step(self):
        start = time.time()
        truss = Truss()
        self.truss = truss

        if len(self.simulation.cells) == 0:
            return

        for cell in self.simulation.cells:
            if 'body' in cell.userData:
                del cell.userData['body']

        for cell in self.simulation.cells:
            self._create_body(truss, cell)

        truss.calc_mass()
        truss.calc_fos()

        for cell in self.simulation.cells:
            body = cell.userData['body']
            cell.userData['fos'] = min(m.fos for m in body.members)
        
        
        # print('Truss ran in: %f\n'%(time.time() - start))
    
    def handle_output(self, cell, outputs):
        """ The phsyics module has no outputs.
        """
        pass

    def create_input(self, cell):
        """
        """
        return [cell.userData['fos']-1]

    def render(self, surface):
        drawTruss(self.truss, surface)

class TrussModule(Module):
    """docstring for PhysicsModule"""
    def __init__(self, static_map):
        super(TrussModule, self).__init__(gene=None,
                                            simulation=TrussSimulation)

        self.simulation_config = {'static_map': static_map}

        self.inputs = ['fos']
        self.outputs = []

