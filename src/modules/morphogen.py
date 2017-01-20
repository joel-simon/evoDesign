"""
"""
import math
import numpy as np
from random import gauss, choice

from src.modules import Module, BaseModuleGene, BaseModuleSimulation

import copy

def guassian_3d(r, s):
    s += .1
    kernel = np.zeros((2*r+1, 2*r+1, 2*r+1))
    for x in range(0, r+1):
        for y in range(0, r+1):
            for z in range(0, r+1):
                foo = - (x*x + y*y + z*z) / s**2
                v = (1/(s**3 * (2*math.pi)**1.5 )) * math.exp(foo)
                kernel[x+r, y+r, z+r] = v
                kernel[x+r, y+r, -z+r] = v
                kernel[x+r, -y+r, z+r] = v
                kernel[x+r, -y+r, -z+r] = v
                kernel[-x+r, y+r, z+r] = v
                kernel[-x+r, y+r, -z+r] = v
                kernel[-x+r, -y+r, z+r] = v
                kernel[-x+r, -y+r, -z+r] = v

    return kernel
# print(guassian_3d(4, 1))
# print(np.around(guassian_3d(3, 1), 4))

class MorphogenGene(BaseModuleGene):
    def __init__(self, ID, decay=.5, diffusion=.25):
        inputs = [ 'morphogen%i_in' % (ID) ]
        outputs = [ ('morphogen%i_out' % (ID), 'identity') ]
        self.mutation_power = 0.25

        self.kernel_r = 3

        self.decay = decay # [0,1]
        self.diffusion = diffusion # [0,1]

        super(MorphogenGene, self).__init__(ID, inputs=inputs, outputs=outputs)

    def _get_kernel(self):
        """ A normal distributon on a hexagon grid.
        """
        kernel = np.zeros((2*self.kernel_r+1, 2*self.kernel_r+1))
        min_sig = .1 # cannot have a variance less than .1
        sig = (self.diffusion * (self.kernel_r-min_sig)) + min_sig #variance

        for index, v in np.ndenumerate(kernel):
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
        # mg.node_gene_ids = copy.copy(self.node_gene_ids)
        mg = super(MorphogenGene, self).copy()
        mg.decay = self.decay
        mg.diffusion = self.diffusion
        return mg

    def get_child(self, other):
        mg = MorphogenGene(self.ID,
                             # choice(self.strength, other.strength),
                             choice((self.decay, other.decay)),
                             choice((self.diffusion, other.diffusion)))
        # mg.node_gene_ids = copy.copy(self.node_gene_ids)
        return mg

class MorphogenSimulation(BaseModuleSimulation):
    def __init__(self, simulation, module):
        super(MorphogenSimulation, self).__init__(simulation, module,
                                               num_inputs=1*len(module.genes),
                                               num_outputs=1*len(module.genes))
        x, y, z = simulation.bounds
        padding = 3
        self.padding = padding
        # self.morphogens = np.zeros((len(module.genes), x+2*padding, y+2*padding, z+2*padding))
        self.morphogens = [np.zeros((x+2*padding, y+2*padding, z+2*padding)) for mgene in module.genes.values()]
        self.kernels = [guassian_3d(mgene.kernel_r, mgene.diffusion) for mgene in module.genes.values()]

    def handle_output(self, x, y, z, outputs, current, next):
        px = x + self.padding
        py = y + self.padding
        pz = z + self.padding
        for morph, kern, o in zip(self.morphogens, self.kernels, outputs):
            if o > .5:
                r = 3
                morph[px-r:px+r+1, py-r:py+r+1, pz-r:pz+r+1] += kern*o

    def create_input(self, x, y, z, input, current):
        """ Cell gets the concentration of each signal at its position.
        """
        px = x + self.padding
        py = y + self.padding
        pz = z + self.padding
        for i, morph in enumerate(self.morphogens):
            input[i] = morph[px, py, pz]

    def step(self):
        """ Simulation logic.
            Each morphogen field decays exponentialy by its decay value.
        """
        for mgene, morph in zip(self.module.genes.values(), self.morphogens):
            morph *= mgene.decay

class MorphogenModule(Module):
    name = 'morphogen'
    def __init__(self, **kwargs):
        super(MorphogenModule, self).__init__(gene=MorphogenGene,
                                              simulation=MorphogenSimulation,
                                              **kwargs)

        # for i, (strength, gid) in enumerate(zip(outputs, gene_ids)):
        #     if strength <= .5:
        #         continue
        #     mgene = self.module.genes[gid]
        #     kernel = self.kernels[i]
        #     for r in range(0, kernel.shape[0]):
        #         for c in range(0, kernel.shape[1]):
        #             a = cell_r - mgene.kernel_r + r
        #             b = cell_c - mgene.kernel_r + c
        #             if a >=0 and a < bounds[0] and b >=0 and b < bounds[1]:
        #                 self.values[i, a, b ] += kernel[r, c] * strength
        #                 self.values[i, a, b ] = max(0, self.values[i, a, b ])
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


