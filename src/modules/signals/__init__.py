from copy import copy
from src.modules import BaseModuleGene, BaseModuleSimulation
from src.views.drawUtils import draw_text, rgb_int
from colorsys import hsv_to_rgb
from src.views.drawHexMap import draw_hex_map

class BaseSignalGene(BaseModuleGene):
    def key(self):
        """ Each gene is given a unique key for lookup in cell userData.
        """
        return 'signal%i' % self.ID

    def mutate(self):
        pass

class BaseSignalSimulation(BaseModuleSimulation):
    """docstring for BaseSignalSimulation"""
    def __init__(self, simulation, module):
        super(BaseSignalSimulation, self).__init__(simulation, module,
                                                   has_render=True)

    def cell_init(self, cell):
        for gene in self.module.genes.values():
            cell.userData[gene.key()] = [0]*len(gene.outputs)

    def handle_output(self, cell, outputs):
        for gene in self.module.genes.values():
            cell.userData[gene.key()] = outputs

    def _draw_hex(self, coord, hexview):
        if self.simulation.hmap[coord] and len(self.module.genes) > 0:
            v = 0
            for gene in self.module.genes.values():
                values = self.simulation.hmap[coord].userData[gene.key()]
                v = max(v, max(values))
            v = min(v, 1.0)
            color = hsv_to_rgb(60.0/360, v, 1)
            hexview.fill(rgb_int(color))
            hexview.border()

        hexview.border((0,0,0), 1)

    def render(self, surface):
        draw_text(surface, (2, 10), "Num genes:%i"%len(self.module.genes))

        max_value = 0
        for cell in self.simulation.cells:
            for gene in self.module.genes.values():
                max_value = max(max_value, max(cell.userData[gene.key()]))

        draw_text(surface, (2, 30), "Max :%f"%max_value)
        draw_hex_map(surface, self.simulation.hmap, self._draw_hex)

