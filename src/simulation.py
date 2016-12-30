from __future__ import print_function
import numpy as np
from os.path import join

from .cell import Cell
from .map_utils import empty
from .export import to_obj

class Simulation(object):
    def __init__(self, genome, bounds, max_steps, starting_positions,
                 verbose=False):
        assert(len(bounds) == 3)

        self.genome = genome
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
        self.hmap = empty(self.bounds)
        self.cells = []
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

    def _get_cell_id(self):
        self.next_cell_id += 1
        return self.next_cell_id

    def super_cell_init(self, cell):
        for module in self.module_simulations.values():
            module.cell_init(cell)
        self.cell_init(cell)

    def create_cell(self, x, y, z):
        assert not self.hmap[x][y][z]
        cell = Cell(self._get_cell_id(), self.genome, (x, y, z))
        self.hmap[x][y][z] = cell
        self.cells.append(cell)
        self.super_cell_init(cell)
        self.created_cells += 1
        # self.last_change = self.step_count

        return cell

    def destroy_cell(self, cell):
        # self.last_change = self.step_count
        for module in self.module_simulations.values():
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
        for cell in self.cells:
            inputs = self.create_input(cell)
            # assert len(inputs) == self.genome.non_module_inputs

            for mod_sim in self.module_simulations.values():
                mod_input = mod_sim.create_input(cell)
                # assert(len(mod_input) == len(mod_sim.module.total_inputs()))
                inputs.extend(mod_input)

            # assert(len(inputs) == self.genome.num_inputs)

            all_outputs.append(cell.outputs(inputs))

            # assert(len(all_outputs[-1]) == self.genome.num_outputs)

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
            for module, sim in zip(self.genome.modules, self.module_simulations.values()):
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
            print('Final cells: %i' % len(self.cells))
            print('Max fitness: %f' % self.max_fitness)

        self.step_count += 1

    def finished(self):
        # We are repeating the run. So we finish when we hit max score.
        # if self.verbose:
        #     print(self.genome.fitness, self.max_fitness)

        # if self.genome.fitness and self.max_fitness >= self.genome.fitness:
        #     return True

        # Check for inactivity.
        if self._steps_since_change >= 5:
            if self.verbose:
                print('Simulation end due to inactivity.')
            return True


        return False

    def run(self, viewer=None):
        for _ in range(self.max_steps):
            self.super_step()

            if viewer:
                self.render_all(viewer)
                viewer.main_loop()

            if self.finished():
                break

    def save(self, directory):
        to_obj(self.hmap, join(directory, 'cells.obj'))

    def save_all(self, directory):
        self.save(directory)
        for m_sim in self.module_simulations.values():
            m_sim.save(directory)

    def render(self, viewer):
        # Simulation defuaults to drawing block representation.
        viewer.set_map(self.hmap)

    def render_all(self, viewer):
        viewer.clear()
        self.render(viewer)
        for m_sim in self.module_simulations.values():
            m_sim.render(viewer)

