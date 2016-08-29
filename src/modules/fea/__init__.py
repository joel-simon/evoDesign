from evaluate import evaluate
import time
import math
from src.modules import Module, BaseModuleSimulation
from hexBody import HexBody
# from src.views.drawSpringWorld import draw_text
from src.modules.fea.drawFea import drawFeaWorld
from src.modules.fea.world import World

SQRT3 = math.sqrt(3)

class FeaSimulation(BaseModuleSimulation):
    """docstring for FeaSimulation"""
    def __init__(self, simulation, module, static_map, gravity=-10.0):
        super(FeaSimulation, self).__init__(simulation, module)
        self.static_map = static_map
        self.gravity = gravity
        self.hex_radius = 14/1

    def _create_body(self, world, cell):
        """ Create a physical representation of cell.
        """
        coords = cell.userData['coords']
        row, col = coords
        cell.userData['stress'] = 0.0

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
            world=world,
            position=(left, top),
            radius=self.hex_radius,
            neighbors=neighbor_bodies,
            static=self.static_map[coords]
        )

    def cell_init(self, cell):
        cell.userData['stress'] = 0.0

    def step(self):
        start = time.time()
        world = World(self.gravity)

        for cell in self.simulation.cells:
            if 'body' in cell.userData:
                del cell.userData['body']

        for cell in self.simulation.cells:
            self._create_body(world, cell)

        F, U = world.evaluate()
        self.F = F
        self.U = U
        self.world = world
        force_map = dict(zip(world.members, F))

        for cell in self.simulation.cells:
            body = cell.userData['body']
            cell.userData['fos'] = min(344*pow(10, 6)/force_map[m] for m in body.members)
            # force = max(force_map[m] for m in body.members)
            # cell.userData['stress'] = force
            # if force == 0:
            #     cell.userData['fos'] = 9#fos - 1
            # else:
            #     cell.userData['fos'] = 1/force#fos - 1
        print('Fea ran in: %f\n'%(time.time() - start))
    
    def handle_output(self, cell, outputs):
        """ The phsyics module has no outputs.
        """
        pass

    def create_input(self, cell):
        """
        """
        return [cell.userData['fos']-1]

    def render(self, surface):
        # world = World(self.gravity)

        # for cell in self.simulation.cells:
        #     if 'body' in cell.userData:
        #         del cell.userData['body']

        # for cell in self.simulation.cells:
        #     self._create_body(world, cell)

        drawFeaWorld(self.world, self.U, self.F, surface)
        #     mstress = max(c.userData['fos'] for c in self.simulation.cells)
        # else:
        #     mstress = 0
        # draw_text(surface, (0, 70), 'max_cell_stress:%f'%mstress)

class FeaModule(Module):
    """docstring for PhysicsModule"""
    def __init__(self, static_map):
        super(FeaModule, self).__init__(gene=None,
                                            simulation=FeaSimulation)

        self.simulation_config = {'static_map': static_map}

        self.inputs = ['stress']
        self.outputs = []

