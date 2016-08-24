import math
from heapq import heappush, heappop
from colorsys import hsv_to_rgb
from collections import defaultdict

from src.modules import Module, BaseModuleSimulation
from src.hexmap import Map

from src.views.drawHexMap import draw_hex_map
from src.views.drawUtils import draw_text, rgb_int


class WaterSimulation(BaseModuleSimulation):
    """docstring for WaterSimulation"""
    def __init__(self, simulation, module, efficiency, production_map, cell_input=True):
        super(WaterSimulation, self).__init__(simulation, module)
        self.simulation = simulation
        self.efficiency = efficiency
        self.production_map = production_map
        self.water_map = Map(simulation.bounds)
        self.water_collection = 0.0
        self.cell_input = cell_input

    def _calculate_water(self):
        self.water_collection = 0.0
        self.water_map.zero()
        hmap = self.simulation.hmap

        queue = []
        seen = set()
        # Calculate how much water is produced by roots.
        for coord in self.production_map.coords():
            # If cell is in a priduction zone (underground).
            if self.production_map[coord] and hmap[coord]:
                # Production is equal to surface area.
                neighbors = hmap.neighbors(coord)
                water = (6 - (sum(map(bool, neighbors)) / 1.0)) / 2.0
                self.water_map[coord] = water
                self.water_collection += water
                seen.add(coord)

        for i in range(self.simulation.bounds[1]):
            if hmap[3][i]:
                queue.append((3, i))

        foo = self.water_collection

        while queue and foo > 0:
            coord = queue.pop(0)
            if coord in seen:
                continue
            seen.add(coord)
            self.water_map[coord] = 1
            for n_coord in hmap.neighbor_coords(coord, filter_valid=True):
                if hmap[n_coord] and n_coord not in seen:
                    queue.append(n_coord)
            foo -= 1

    def step(self):
        self._calculate_water()

    def create_input(self, cell):
        """ The cell recieves its physical stress as one value.
        """
        if self.cell_input:
            return [self.water_map[cell.userData['coords']]]
        else:
            return []

    def _draw_hex(self, coord, hexview):
        max_water = max(self.water_map.iter_values())
        v = self.water_map[coord]

        if self.simulation.hmap[coord]:
            if self.production_map[coord]:
                color = hsv_to_rgb(280.0/360, v/6, 1)
                hexview.fill(rgb_int(color))
            elif v > 0:
                color = hsv_to_rgb(2.4/3.6, 1, 1)
                hexview.fill(rgb_int(color))
            hexview.border()

            hexview.text(str(int(v)))

        else:
            if self.production_map[coord]:
                color = hsv_to_rgb(280.0/360, 1, 1)
                hexview.border(rgb_int(color))

    def render(self, surface):
        draw_hex_map(surface, self.water_map, self._draw_hex)
        draw_text(surface, (10, 10), "water_collection:%f"%self.water_collection)
        # draw_text(surface, (10, 10), "water_demand:%f"%len(self.simulationc))

class WaterModule(Module):
    """docstring for WaterModule"""
    def __init__(self, production_map, cell_input=True):
        super(WaterModule, self).__init__(gene=None,
                                          simulation=WaterSimulation)

        self.cell_input = cell_input
        self.simulation_config = {'production_map': production_map,
                                   'cell_input': cell_input,
                                   'efficiency': .8
                                   }

        if cell_input:
            self.inputs = ['water']
        else:
            self.inputs = []

        self.outputs = []
