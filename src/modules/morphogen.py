"""
"""
import math
import numpy
from random import gauss, choice

from src.modules import Module, BaseModuleGene, BaseModuleSimulation
from src.hexmap import Map, distance

from src.views.drawUtils import draw_text, rgb_int
from src.views.drawHexMap import draw_hex_map
from colorsys import hsv_to_rgb
import copy

class MorphogenGene(BaseModuleGene):
    def __init__(self, ID, decay=.5, diffusion=.25):
        inputs = [ 'morphogen%i_in' % (ID) ]
        outputs = [ ('morphogen%i_out' % (ID), 'identity') ]
        self.mutation_power = 0.25

        self.ID = ID
        self.kernel_r = 5

        self.decay = decay # [0,1]
        self.diffusion = diffusion # [0,1]

        super(MorphogenGene, self).__init__(ID, inputs=inputs, outputs=outputs)

    def _get_kernel(self):
        """ A normal distributon on a hexagon grid.
        """
        kernel = numpy.zeros((2*self.kernel_r+1, 2*self.kernel_r+1))
        min_sig = .1 # cannot have a variance less than .1
        sig = (self.diffusion * (self.kernel_r-min_sig)) + min_sig #variance

        for index, v in numpy.ndenumerate(kernel):
            d = distance(index, (self.kernel_r,self.kernel_r))
            v = (1 / (math.sqrt(2*sig*math.pi))) * math.exp((-d**2) / (2*sig))
            kernel[index] = v

        kernel *= 10 / kernel.sum()

        return kernel

    def _mutate_value(self, v):
        new_v = v + gauss(0, 1) * self.mutation_power
        return max(0, min(new_v, 1))

    def mutate(self):
        self.decay = self._mutate_value(self.decay)
        self.diffusion = self._mutate_value(self.diffusion)

    def copy(self):
        # mg = MorphogenGene(self.ID, self.decay, self.diffusion)
        # mg.node_gene_ids = copy(self.node_gene_ids)
        return super(MorphogenGene, self).copy(self)

    def get_child(self, other):
        mg = MorphogenGene(self.ID,
                             # choice(self.strength, other.strength),
                             choice((self.decay, other.decay)),
                             choice((self.diffusion, other.diffusion)))
        mg.node_gene_ids = copy.copy(self.node_gene_ids)
        return mg

class MorphogenSimulation(BaseModuleSimulation):
    def __init__(self, simulation, module):
        super(MorphogenSimulation, self).__init__(simulation, module,
                                                   has_render=True)
        self.allow_negative = False
        shape = (len(module.genes), simulation.bounds[0], simulation.bounds[1])
        self.values = numpy.zeros(shape)

        self.kernels = [mgene._get_kernel() for mgene in module.genes.values()]

    def cell_init(self, cell):
        pass

    def cell_destroy(self, cell):
        pass

    def handle_output(self, cell, outputs):
        gene_ids = sorted(self.module.genes.keys())
        cell_r, cell_c = cell.position
        bounds = self.simulation.bounds

        for i, (strength, gid) in enumerate(zip(outputs, gene_ids)):
            if strength <= .5:
                continue
            mgene = self.module.genes[gid]
            kernel = self.kernels[i]
            for r in range(0, kernel.shape[0]):
                for c in range(0, kernel.shape[1]):
                    a = cell_r - mgene.kernel_r + r
                    b = cell_c - mgene.kernel_r + c
                    if a >=0 and a < bounds[0] and b >=0 and b < bounds[1]:
                        self.values[i, a, b ] += kernel[r, c] * strength
                        self.values[i, a, b ] = max(0, self.values[i, a, b ])
                # a = mgene.kernel_r
                # # Deal with negative indexes.
                # crop_r = -1 * (r-a) if r-a < 0 else 0
                # crop_c = -1 * (c-a) if c-a < 0 else 0
                # print r, c
                # print 'crops', crop_r, crop_c
                # print 'value', self.values[i, max(0, r-a):r+a+1, max(0, c-a):c+a+1].shape
                # print 'kernel', self.kernels[i][crop_r:, crop_c:].shape
                # print
                # row_end = self.values[i].shape[0] - (r+a+1)
                # col_end = self.values[i].shape[1] - (c+a+1)

                # kern = self.kernels[i][crop_r:row_end, crop_c:col_end] * strength
                # self.values[i, max(0, r-a):r+a+1, max(0, c-a):c+a+1] += kern
#
    def create_input(self, cell):
        """ Cell gets the concentration of each signal at its position.
        """
        coords = cell.position
        # print [v[coords] for v in self.values]
        return [v[coords] for v in self.values]

    def step(self):
        """ Simulation logic.
            Each morphogen field decays exponentialy by its decay value.
        """
        for mgene, values in zip(self.module.genes.values(), self.values):
            values *= mgene.decay

    def _draw_hex(self, coord, hexview):
        v = self.values[:, coord[0], coord[1]].sum()
        if v > 0:
            v /= self.values.max()
        color = hsv_to_rgb(60.0/360, v, 1)
        hexview.fill(rgb_int(color))
        hexview.border((0,0,0), 1)

    def render(self, surface):
        max_value = self.values.max()
        draw_text(surface, (2, 10), "Morphogens (%i genes)"%len(self.module.genes))
        draw_text(surface, (2, 30), "Max :%f"%max_value)

        hmap = Map(self.simulation.bounds)
        # hmap.values = self.values
        draw_hex_map(surface, hmap, self._draw_hex)

class MorphogenModule(Module):

    def __init__(self, **kwargs):
        super(MorphogenModule, self).__init__(gene=MorphogenGene,
                                              simulation=MorphogenSimulation,
                                              **kwargs)

def add_kernel(hmap, center, kernel):
    assert(kernel.shape[0] % 2 == 1)
    assert(kernel.shape[1] % 2 == 1)

    hmap[center[0]-int(kernel/2): ]


