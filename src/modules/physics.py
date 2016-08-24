import math
from src.modules import Module, BaseModuleSimulation
from src.springs.Spring2D import World
# from src.hexmap import Map
from src.springs.hexBody import HexBody
from src.views.drawSpringWorld import drawSpringWorld, draw_text

SQRT3 = math.sqrt(3)

class PhysicsSimulation(BaseModuleSimulation):
    """docstring for PhysicsSimulation"""
    def __init__(self, simulation, module, static_map, gravity=-10.0):
        super(PhysicsSimulation, self).__init__(simulation, module)
        self.static_map = static_map
        self.gravity = gravity
        self.max_physics_steps = 100
        self.hex_radius = 14/1
        self.forces = dict()
        self.world = World(gravity, resolve_steps=150)

        self.max_force = .01

    def _reset(self):
        # Reset Bodies
        for body in self.world.bodies:
            body.position = body.userData['origin'].copy()
            body.previous = body.userData['origin'].copy()
            body.acceleration.zero()

    def _calculate_forces(self):
        prev_total_stress = 0.0
        self.forces = dict()

        for _ in range(self.max_physics_steps):
            self.world.step()

            forces = [ j.GetReactionForce() for j in self.world.joints ]
            next_total_stress = sum(forces)

            if next_total_stress > prev_total_stress:
                prev_total_stress = next_total_stress
            else:
                break
        # print('')
        self.forces = dict(zip(self.world.joints, forces))
        assert(len(self.forces) == len(self.world.joints))

    def cell_init(self, cell):
        """ Create a physical representation of cell.
        """
        # print
        coords = cell.userData['coords']
        row, col = coords
        cell.userData['stress'] = 0.0

        neighbor_bodies = []
        for n in self.simulation.hmap.neighbors(coords):
            if n:
                neighbor_bodies.append(n.userData['body'])
            else:
                neighbor_bodies.append(None)

        # Calculate position.
        offset = self.hex_radius * SQRT3 / 2 if col % 2 else 0
        left = 1.5 * col * self.hex_radius
        top = offset + SQRT3 * row * self.hex_radius

        cell.userData['body'] = HexBody(
            ID=cell.id,
            world=self.world,
            position=(left, top),
            radius=self.hex_radius,
            neighbors=neighbor_bodies,
            static=self.static_map[coords]
        )

    def cell_destroy(self, cell):
        cell.userData['body'].destroy()

    def step(self):
        """ Run the physics engine.
        """
        self._calculate_forces()
        self._reset()

    def handle_output(self, cell, outputs):
        """ The phsyics module has no outputs.
        """
        pass

    def create_input(self, cell):
        """ The cell recieves its physical stress as one value.
        """
        cellbody = cell.userData['body']

        stress = sum(self.forces[j] for j in cellbody.joints) / 6.0
        normed = stress / self.max_force

        cell.userData['stress'] = normed

        return [stress]

    def render(self, surface):
        if len(self.simulation.cells):
            self._calculate_forces()
            drawSpringWorld(self.world, surface)
            mstress = max(c.userData['stress'] for c in self.simulation.cells)
        else:
            mstress = 0
        draw_text(surface, (0, 70), 'max_cell_stress:%f'%mstress)
        self._reset()

class PhysicsModule(Module):
    """docstring for PhysicsModule"""
    def __init__(self, static_map):
        super(PhysicsModule, self).__init__(gene=None,
                                            simulation=PhysicsSimulation)

        self.simulation_config = {'static_map': static_map}

        self.inputs = ['stress']
        self.outputs = []

