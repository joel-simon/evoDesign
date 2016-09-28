from __future__ import print_function
import numpy as np

from .cell import Cell
from .map_utils import empty

class Simulation(object):
    def __init__(self, genome, bounds=(8, 8, 8), verbose=False, max_steps=64):
        assert(len(bounds) == 3)

        self.genome = genome
        self.bounds = bounds
        self.verbose = verbose
        self.max_steps = max_steps

        # State data
        self.hmap = empty(bounds)
        self.cells = []
        self.next_cell_id = 0
        self.last_change = 0

        # Step statistics
        self.step_count = 0
        self.created_cells = 0
        self.destroyed_cells = 0

        self.module_simulations = []
        self._init_module_simulations()

    def _init_module_simulations(self):
        """ Each module may have its own simulation class. Initialize them here.
            Only called from self.init
        """
        for module in self.genome.modules:
            if module.simulation:
                sim = module.simulation(self, module, **module.simulation_config)
                self.module_simulations.append(sim)

    def _get_cell_id(self):
        self.next_cell_id += 1
        return self.next_cell_id

    def super_cell_init(self, cell):
        self.cell_init(cell)
        for module in self.module_simulations:
            module.cell_init(cell)

    def create_cell(self, x, y, z):
        assert not self.hmap[x][y][z]
        cell = Cell(self._get_cell_id(), self.genome, (x, y, z))
        self.hmap[x][y][z] = cell
        self.cells.append(cell)
        self.super_cell_init(cell)
        self.created_cells += 1
        self.last_change = self .step_count

        return cell

    def destroy_cell(self, cell):
        self.last_change = self.step_count
        for module in self.module_simulations:
            module.cell_destroy(cell)
        self.cells.remove(cell)
        x, y, z = cell.position
        self.hmap[x][y][z] = 0
        self.destroyed_cells += 1
        cell.alive = False

    def create_input(self, cell):
        raise NotImplementedError()

    def handle_output(self, cell, outputs):
        raise NotImplementedError()

    def step(self):
        pass

    def create_all_outputs(self):
        """ Collect all inputs first so simulation
            state does not change during input collection
        """
        all_outputs = []
        # print(len(self.cells))
        for cell in self.cells:
            inputs = self.create_input(cell)
            assert len(inputs) == self.genome.non_module_inputs

            for mod_sim in self.module_simulations:
                mod_input = mod_sim.create_input(cell)
                assert(len(mod_input) == len(mod_sim.module.total_inputs()))
                inputs.extend(mod_input)

            assert(len(inputs) == self.genome.num_inputs)

            all_outputs.append(cell.outputs(inputs))

            assert(len(all_outputs[-1]) == self.genome.num_outputs)

        return all_outputs

    def handle_all_outputs(self, all_outputs):
        # Handle all outputs.
        # Make a list copy because self.cells will change during iteration.
        for cell, outputs in list(zip(self.cells, all_outputs)):

            nmi = self.genome.non_module_outputs
            self.handle_output(cell, outputs[:nmi])
            if not cell.alive:
                continue

            # Handle Module outputs
            i = nmi
            for module, sim in zip(self.genome.modules, self.module_simulations):
                k = len(module.total_outputs())
                module_output = outputs[i:i+k]
                assert(len(module_output) == k)
                sim.handle_output(cell, module_output)
                i += k
                if not cell.alive:
                    break

    def super_step(self):
        self.created_cells = 0
        self.destroyed_cells = 0

        if self.verbose:
            print('#'*40,'step', self.step_count,'#'*40)

        all_outputs = self.create_all_outputs()
        self.handle_all_outputs(all_outputs)

        # Handle experiment logic.
        self.step()

        ### Handle Module Logic
        for mod_sim in self.module_simulations:
            mod_sim.step()

        if self.verbose:
            print('destroyed %i cells' % self.destroyed_cells)
            print('created %i cells:' % self.created_cells)
            print('final cells: %i' % len(self.cells))

        self._fitness = self.fitness()
        self.step_count += 1

    def run(self, viewer=None):
        max_fitness = 0

        for _ in range(self.max_steps):
            self.super_step()

            max_fitness = max(max_fitness, self._fitness)

            # print(viewer)
            if viewer:
                self.render_all(viewer)
                viewer.main_loop()

            # We are repeating the run to visualize. So we dont want to render
            # past reaching the max score.
            if self.genome.fitness and max_fitness == self.genome.fitness:
                return max_fitness

            # Check for inactivity.
            if self.step_count - self.last_change > 5:
                if self.verbose:
                    print('Simulation end due to inactivity.')
                return max_fitness

        return max_fitness


    def render(self, view):
        # Simulation defuaults to drawing block representation.
        viewer.set_mesh(self.hmap)

    def render_all(self, viewer):
        self.render(viewer)
        for m_sim in self.module_simulations:
            m_sim.render(viewer)

