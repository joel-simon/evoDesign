from collections import defaultdict
from cell import Cell
# from Vector import Vector
from physics import VoronoiSpringPhysics
import random

import time
import math

# from visualize import plot

def clamp(n, minn=0, maxn=1):
  return max(min(maxn, n), minn)

class Simulation(object):
  def __init__(self, genome, physics, dimensions, verbose=False):
    self.genome = genome
    self.physics = physics
    self.verbose = verbose

    self.reset()

    for _ in range(10):
      x = 400+20*(random.random()-.5)
      y = 400+20*(random.random()-.5)
      self.create_cell(x, y)

  def reset(self):
    self.cells = dict()
    self.next_cell_id = 0
    self.steps_since_change = 0


  def create_cell(self, px, py, cell_type=0):
    cell = Cell(self.next_cell_id, self.genome, px, py, cell_type)
    self.physics.add_node(cell)
    self.cells[cell.id] = cell
    self.next_cell_id += 1
    return cell

  def calculate_light(self):
    pass
    # dx = 10
    # # dy = 10
    # foo = [[]] * dx
    # for cell_id, cell in self.cells.items()
    #   i = int(cell.node.p[0]/800)
    #   foo[i].append((cell_id, cell.))

  # def cell_neighbors(self, cell):
  #   return self.physics.neighbors(cell)
  # def spread_

  def spread_morphogen(self, mid, morphogen, steps=500, saturate=False):
    values = morphogen.values()
    Da = values['activator_diffusion']
    Ra = values['activator_decay']
    Pa = values['activator_production']

    Db = values['inhibitor_diffusion']
    Rb = values['inhibitor_decay']
    Pb = values['inhibitor_production']


    # Da = 0.02   #diffusion of the activator (unit: , if regions on x-axis have a width of 1 mu)
    # Ra = 0.02   #removal rate of the activator
    # Pa = 0.001   #activator-independent activator production rate

    # Db = 0.15   #Diffusion of the inhibitor
    # Rb = 0.02   #Removal rate of the inhibitor
    # Pb = 0.001  #activator-independent inhibitor production rate

    for s in range(steps):
      new_values = { cell: [0,0] for cell in self.cells.values() }
      for cell in self.cells.values():
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
        neighbors = self.physics.neighbors(cell)
        n = len(neighbors)

        neighbors_a = [c.morphogen_concentrations[0][0] for c in neighbors]
        Dif_a = Da*(sum(neighbors_a) - n*av)

        neighbors_b = [c.morphogen_concentrations[0][1] for c in neighbors]
        Dif_b = Db*(sum(neighbors_b) - n*bv)

        # update values
        new_values[cell][0] = av+Prod_a-Rem_a+(Da*Dif_a)
        new_values[cell][1] = bv+Prod_b-Rem_b+(Db*Dif_b)

      for cell in self.cells.values():
        new_values[cell][0] = max(new_values[cell][0], 0)
        new_values[cell][1] = max(new_values[cell][1], 0)

        if not math.isnan(new_values[cell][0]):
          cell.morphogen_concentrations[0][0] = new_values[cell][0]

        if not math.isnan(new_values[cell][1]):
          cell.morphogen_concentrations[0][1] = new_values[cell][1]

    C = [ n.morphogen_concentrations[0][0] for n in self.cells.values() ]

  def handle_cell_outputs(self, cell, outputs):
    change = False
    # Apoptopis
    if outputs['apoptosis']:
      self.physics.remove_node(cell)
      del self.cells[cell.id]
      change = True

    # Cell division
    if outputs['division']:
      px = cell.px + random.random()-.5
      py = cell.py + random.random()-.5
      daughter = self.create_cell(px, py)
      for i in range(1):
        daughter.morphogen_concentrations[i][0] = cell.morphogen_concentrations[i][0]/2
        daughter.morphogen_concentrations[i][1] = cell.morphogen_concentrations[i][1]/2

        cell.morphogen_concentrations[i][0] /= 2
        cell.morphogen_concentrations[i][1] /= 2


      change = True

    # Morphogen Spread.
    # for i in range(1):
    cell.morphogen_productions[0][0] += outputs['a1']
    cell.morphogen_productions[0][1] += outputs['h1']

    return change

  def step(self):
    # self.calculate_light()
    changes_made = False
    self.physics.run()

    for mid, morphogen in self.genome.morphogen_genes.items():
      self.spread_morphogen(mid, morphogen, steps=1000)

    derp = [(cell, cell.get_outputs()) for cell in self.cells.values()]

    for cell, outputs in derp:
      changes_made |= self.handle_cell_outputs(cell, outputs)

    # print(changes_made)
    if changes_made:
      self.steps_since_change = 0
    else:
      self.steps_since_change += 1

  def finished(self):
    if len(self.cells) == 0:
      return True

    if len(self.cells) > 200:
      return True

    if self.steps_since_change >= 5:
      return True

    return False

  def run(self, generations):
    # print('Running %i generations' % generations)
    step = 0
    while step < generations and not self.finished():
      if self.verbose:
        print("Running step %i" % step)

      self.step()
      step += 1

      if self.verbose:
        print("\t%i cells left" % len(self.cells))

    # print('done')
