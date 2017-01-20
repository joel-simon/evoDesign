from __future__ import division, print_function
import pyximport
import numpy as np
pyximport.install(setup_args={"include_dirs":np.get_include()},
                  reload_support=True)

from os.path import join

from src.export import to_obj

# from neat import nn
from src.neat_custom import nnx as nn
# from numba import jit

class Simulation(object):
    def __init__(self, genome, bounds, max_steps, starting_positions,
                 verbose=False):
        assert(len(bounds) == 3)

        self.genome = genome

        # self.network = NEAT.NeuralNetwork()
        # genome.BuildPhenotype(self.network)
        self.network = nn.create_feed_forward_phenotype(genome)

        self.bounds = bounds
        self.max_steps = max_steps
        self.starting_positions = starting_positions
        self.verbose = verbose
        self.reset()

    def reset(self):
        # State data
        self._fitness = 0
        self._last_fitness = 0
        self._steps_since_change = 0

        self.max_fitness = 0
        self.max_fitness_steps = 0

        self.cell_positions = set()

        self.cmap = np.zeros(self.bounds, dtype=bool)
        self.cmap_next = np.zeros(self.bounds, dtype=bool)

        # dx, dy, dz = self.bounds
        # self.inputs = np.zeros((dx, dy, dz, self.genome.num_inputs))
        # self.outputs = np.zeros((dx, dy, dz, self.genome.num_outputs))

        # self.cells = set()
        self.next_cell_id = 0

        # Step statistics
        self.step_count = 0
        self.created_cells = 0
        self.destroyed_cells = 0

        self.module_simulations = dict()
        self._init_module_simulations()

        for x, y, z in self.starting_positions:
            self.create_cell(x, y, z)

    def _init_module_simulations(self):
        """ Each module may have its own simulation class. Initialize them here.
            Only called from self.init
        """
        for module in self.genome.modules:
            if module.simulation:
                sim = module.simulation(self, module, **module.simulation_config)
                self.module_simulations[module.name] = sim

    # def _get_cell_id(self):
    #     self.next_cell_id += 1
    #     return self.next_cell_id

    # def super_cell_init(self, cell):
    #     for module in self.module_simulations.values():
    #         module.cell_init(cell)
    #     # self.cell_init(cell)

    def create_cell(self, x, y, z):
        assert not self.cmap[x, y, z]
        # cell = Cell(self._get_cell_id(), self.genome, (x, y, z))
        self.cmap[x, y, z] = 1
        self.cell_positions.add((x, y, z))
        # self.cells.add(cell)
        # self.super_cell_init(x, y, z)
        self.created_cells += 1
        for sim in self.module_simulations.values():
            sim.cell_init(x, y, z)
        # return cell

    # def destroy_cell(self, cell):
    #     self.cell_positions[]
    #     # self.last_change = self.step_count
    #     for module in self.module_simulations.values():
    #         module.cell_destroy(cell)
    #     self.cells.remove(cell)
    #     x, y, z = cell.position
    #     self.cmap[x][y][z] = 0
    #     self.destroyed_cells += 1
    #     cell.alive = False

    # def create_input(self, cell):
    #     raise NotImplementedError()

    # def handle_output(self, cell, outputs):
    #     raise NotImplementedError()

    def activate(self, inputs, outputs):
        # # print(inputs)
        # self.network.Flush()
        # self.network.Input(inputs)  # can input numpy arrays, too
        # return self.network.Activate()
        return self.network.serial_activate(inputs, outputs)

    # @profile
    def step(self):
        sim_list = list(self.module_simulations.values())
        cells = list(self.cell_positions) # make copy, will change during iteration
        inputs = np.zeros(self.genome.num_inputs)
        outputs = np.zeros(self.genome.num_outputs)

        for x, y, z in cells:
            inputs.fill(0)
            k = 0
            for sim in sim_list:
                if sim.num_inputs > 0:
                    # assert(len(inputs[k:k+sim.num_inputs]) == sim.num_inputs)
                    sim.create_input(x, y, z, inputs[k:k+sim.num_inputs], self.cmap)
                k += sim.num_inputs

            self.activate(inputs, outputs)

            if outputs[0] > .5: # Apoptosis.
                for sim in sim_list:
                    sim.cell_destroy(x, y, z)
            else: # Continue to next generation
                self.cmap_next[x, y, z] = 1

            k = 1
            for sim in sim_list:
                if sim.num_outputs > 0:
                    # assert(len(outputs[k:k+sim.num_outputs]) == sim.num_outputs)
                    sim.handle_output(x, y, z, outputs[k:k+sim.num_outputs], self.cmap, self.cmap_next)
                k += sim.num_outputs

        self.cmap, self.cmap_next = self.cmap_next, self.cmap
        self.cmap_next[:, :, :] = False

    def super_step(self):
        self.created_cells = 0
        self.destroyed_cells = 0

        if self.verbose:
            print('#'*40,'step', self.step_count,'#'*40)

        # Handle experiment logic.
        self.step()

        # Handle Module Logic
        for mod_sim in self.module_simulations.values():
            mod_sim.step()

        self._fitness = self.fitness()

        if self._fitness == self._last_fitness:
            self._steps_since_change += 1
        else:
            self._steps_since_change = 0

        if self._fitness > self.max_fitness:
            self.max_fitness = self._fitness
            self.max_fitness_steps = self.step_count

        self._last_fitness = self._fitness

        if self.verbose:
            print('Destroyed %i cells' % self.destroyed_cells)
            print('Created %i cells:' % self.created_cells)
            # print('Final cells: %i' % len(self.cells))
            print('Max fitness: %f' % self.max_fitness)

        self.step_count += 1

    def finished(self):
        # We are repeating the run. So we finish when we hit max score.
        # if self.verbose:
        #     print(self.genome.fitness, self.max_fitness)

        # Check for inactivity.
        if self._steps_since_change >= 4:
            if self.verbose:
                print('Simulation end due to inactivity.')
            return True


        return False

    def run(self, viewer=None):
        for i in range(self.max_steps):
            self.super_step()

            if viewer:
                self.render_all(viewer)
                viewer.main_loop()

            if self.finished():
                break
        # print(self.cmap.sum())

    def save(self, directory):
        to_obj(self.cmap, join(directory, 'cells.obj'))

    def save_all(self, directory):
        self.save(directory)
        for m_sim in self.module_simulations.values():
            m_sim.save(directory)

    def render(self, viewer):
        # Simulation defuaults to drawing block representation.
        viewer.set_map(self.cmap)

    def render_all(self, viewer):
        viewer.clear()
        self.render(viewer)
        # for m_sim in self.module_simulations.values():
        #     m_sim.render(viewer)

