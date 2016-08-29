import math
from colorsys import hsv_to_rgb
from src.modules import Module, BaseModuleSimulation
from src.hexmap import Map

from src.views.drawHexMap import draw_hex_map
from src.views.drawUtils import draw_text, rgb_int

class LightSimulation(BaseModuleSimulation):
    """docstring for LightSimulation"""
    def __init__(self, simulation, module, light_coverage):
        # self.simulation = simulation
        super(LightSimulation, self).__init__(simulation, module)
        self.light_coverage = light_coverage
        self.light_map = Map(simulation.bounds)

    def _calculate_light(self):
        bounds = self.light_map.shape
        light = [1] * bounds[1]
        DECAY = 1.0 / bounds[0]

        # Iterate rows from top to bottom.
        for row in range(bounds[0]-1, -1, -1):
            for col in range(bounds[1]):
                cell = self.simulation.hmap[row][col]
                self.light_map[row][col] = light[col]

                if cell:
                    cell.userData['light'] = light[col] * self.light_coverage

                light[col] -= DECAY
                light[col] *= 1 - (bool(cell) * self.light_coverage)
                light[col] = max(light[col], 0)

    def cell_init(self, cell):
        cell.userData['light'] = 0.0

    def step(self):
        """
        """
        self._calculate_light()

    def handle_output(self, cell, outputs):
        """ The light module has no outputs.
        """
        pass

    def create_input(self, cell):
        """ The cell recieves its physical stress as one value.
        """
        return [cell.userData['light']]

    def _draw_hex(self, coord, hexview):
        if self.simulation.hmap[coord]:
            color = hsv_to_rgb(45.0/255, 1, self.light_map[coord])
            hexview.fill(rgb_int(color))
        else:
            color = hsv_to_rgb(45.0/255, 1, self.light_map[coord])
            hexview.border(rgb_int(color))
            # hexview.fill((255, 255, 255))

    def render(self, surface):
        max_light = self.simulation.bounds[1]
        total_light = 0

        for cell in self.simulation.cells:
            total_light += cell.userData['light']

        draw_hex_map(surface, self.simulation.hmap, self._draw_hex)
        draw_text(surface, (10, 10), "light:%f"%total_light)
        draw_text(surface, (10, 30), "light_percentage:%f"%(total_light/max_light))

class LightModule(Module):
    """docstring for LightModule"""
    def __init__(self, light_coverage):
        super(LightModule, self).__init__(gene=None, simulation=LightSimulation)

        self.simulation_config = {'light_coverage': light_coverage}

        self.inputs = ['light']
        self.outputs = []

