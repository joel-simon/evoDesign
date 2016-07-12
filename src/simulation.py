from src.cell import Cell
import random
import time
import math

class Simulation(object):
    def __init__(self, genome, physics, bounds=200,
                    max_size=999, verbose=False
                    max_steps=100):
        self.genome = genome
        self.physics = physics
        self.verbose = verbose
        self.max_steps = max_steps
        self.max_size = max_size
        self.reset()
        self.bounds = bounds
        self.steps = 0

        if self.bounds != None:
            t = 20
            w = self.bounds
            # Floor
            self.physics.create_static_box(position=(0,-t/2),dimensions=(w/2,t/2))
            # Ceiling
            self.physics.create_static_box(position=(0,w+t/2),dimensions=(w/2,t/2))
            # Walls
            self.physics.create_static_box(position=((-w-t)/2,w/2),dimensions=(t/2,w/2+t))
            self.physics.create_static_box(position=((w+t)/2,w/2),dimensions=(t/2,w/2+t))

    def reset(self):
        self.cells = []
        self.next_cell_id = 0
        self.steps_since_change = 0

    def get_id(self):
        self.next_cell_id += 1
        return self.next_cell_id

    def create_cell(self, position, size=[1, 1], cell_type=0, body=None):
        if body == None:
            body = self.physics.create_body(position, size)
        cell = Cell(self.get_id(), self.genome, body)
        self.cells.append(cell)
        body.userData['cell'] = cell
        return cell

    def kill_cell(self, cell):
        self.physics.destroy_body(cell.body)
        self.cells.remove(cell)

    def divide_cell(self, cell, angle):
        daughter_body = self.physics.divide_body(cell.body, angle)
        if daughter_body:
            daughter = Cell(self.get_id(), self.genome, daughter_body)
            daughter_body.userData['cell'] = daughter
            return daughter
        return None

    def grow_cell(self, cell, n):
        daughter_body = self.physics.grow_body(cell.body, n)
        if daughter_body:
            self.create_cell(None, None, None, daughter_body)
            # self.cells.append(daughter)

    def spread_morphogen(self, mid, morphogen, steps=1000, saturate=False):
        values = morphogen.values()
        Da = values['activator_diffusion']
        Ra = values['activator_decay']
        Pa = 0#values['activator_production']

        Db = values['inhibitor_diffusion']
        Rb = values['inhibitor_decay']
        Pb = 0#values['inhibitor_production']

        for s in range(steps):
            new_values = { cell: [0,0] for cell in self.cells }
            for cell in self.cells:
                av, bv = cell.morphogen_concentrations[0]

                # production.
                Prod_a = Pa + cell.morphogen_productions[0][0]

                a_2 = (av**2)
                if saturate:
                    a_2 /= (1+.01*a_2)

                if bv != 0: Prod_a += a_2 / bv
                else:       Prod_a += a_2

                Prod_b = (av*av) + Pb + cell.morphogen_productions[0][1]

                # removal.
                Rem_a = Ra*av
                Rem_b = Rb*bv

                # diffision.
                neighbors = [ b.userData['cell'] for b in self.physics.neighbors(cell.body) ]
                n = len(neighbors)

                neighbors_a = [c.morphogen_concentrations[0][0] for c in neighbors]
                Dif_a = Da*(sum(neighbors_a) - n*av)

                neighbors_b = [c.morphogen_concentrations[0][1] for c in neighbors]
                Dif_b = Db*(sum(neighbors_b) - n*bv)

                # update values
                new_values[cell][0] = av+Prod_a-Rem_a+(Da*Dif_a)
                new_values[cell][1] = bv+Prod_b-Rem_b+(Db*Dif_b)

            # print(new_values.values())
            for cell in self.cells:
                new_values[cell][0] = max(new_values[cell][0], 0)
                new_values[cell][1] = max(new_values[cell][1], 0)

                if not math.isnan(new_values[cell][0]):
                    cell.morphogen_concentrations[0][0] = new_values[cell][0]

                if not math.isnan(new_values[cell][1]):
                    cell.morphogen_concentrations[0][1] = new_values[cell][1]

        # C = [ n.morphogen_concentrations[0][0] for n in self.cells ]

    def step(self):
        changes_made = False
        derp = [(cell, cell.get_outputs()) for cell in self.cells]
        apoptosis = 0
        division = 0

        for cell, outputs in derp:

            if outputs['apoptosis']:
                print('apoptosis')
                self.kill_cell(cell)
                apoptosis += 1
                # cannot apoptosis and do other things.
                continue

            # Cell Growth
            if outputs['grow'] > .5:
                self.grow_cell(cell, 1)


            divides = [outputs['divide0'],outputs['divide1'],outputs['divide2'],outputs['divide3']]
            if max(divides) > .5:
                print('divide')
                # angles = np.linspace(0,2*math.pi,4,endpoint=False)
                angles = [ 0., 1.57079633,  3.14159265,  4.71238898]
                angle = angles[divides.index(max(divides))]
                self.divide_cell(cell, angle)
                division += 1


        if (apoptosis + division > 0):
            self.steps_since_change = 0
        else:
            self.steps_since_change += 1

        self.physics.run()

        for mid, morphogen in self.genome.morphogen_genes.items():
            self.spread_morphogen(mid, morphogen, steps=1000)

        # for node_a, neighbors in list(self.physics.adjacencies.items()):
        #   for node_b in neighbors:
        #     assert(node_a in self.physics.adjacencies[node_b])


        if self.verbose:
            print('\tapoptosis:%i' % apoptosis)
            print('\tdivision:%i' % division)
            print("\tcells left%i" % len(self.cells))

    def finished(self):
        if self.max_steps and self.steps >= self.max_steps:
            return True

        if len(self.cells) == 0:
            return True

        if len(self.cells) > self.max_size:
            return True

        # if self.steps_since_change >= 5:
        #   return True

        return False

    def run(self):
        self.steps = 0
        if len(self.cells) == 0:
            raise StandardError('Simulation run with no cells.')

        while not self.finished():
            if self.verbose:
                print('#'*20,"Simulation: step %i" % self.steps, '#'*20)
            self.step()
            self.steps += 1

        # print('done')
