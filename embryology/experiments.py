from collections import defaultdict
from simulate import simulate

from hexmap import Map

from neat import ctrnn

from truss_analysis import truss_from_map

class Experiment(object):
	
	def fitnesses(self, genomes):
		for genome in genomes:
			genome.fitness = self.fitness(genome)		
	
	def draw(self, genome):

		if self.screen != None:
			from visualize import draw_hex_map
			import pygame
		
			self.screen.fill((255,255,255))
			hexmap = simulate(genome, self.shape, self.cell_inputs)[0]
			draw_hex_map(self.screen, hexmap)
			pygame.display.flip()

class SurfaceArea(Experiment):
	def __init__(self, shape, screen=None):
		self.shape  = shape
		self.screen = screen
		self.start = None

	def surfaceArea(self, hexmap):
		surfaceArea = 0
		for i, row in enumerate(hexmap.values):
			for j, cell in enumerate(row):
				if isinstance(cell, ctrnn.Network):
					neighbors = len(hexmap.neighbors((i, j)))
					surfaceArea += neighbors - hexmap.num_occupied_neighbors((i, j))

		return surfaceArea

	def grow(self, genome):
		hexmap = simulate(genome, self.shape)[0]
		return filter_unconnected( hexmap, set([(0,0)]) )

	def fitness(self, genome):
		hexmap = self.grow(genome)
		surfaceArea = self.surfaceArea(hexmap)
		n = hexmap.shape[0] * hexmap.shape[1]
		return surfaceArea / float(n * 2)

class Tree(Experiment):
	def __init__(self, shape, screen=None):
		self.shape  = shape
		self.screen = screen
		self.start = None
		self.num_input = 7

	def cell_inputs(self, hex_map, pheromone_maps):
		light_per_cell = defaultdict(float, self.lightInput(hex_map)[1])
		
		for i in range(hex_map.rows):
			for j in range(hex_map.cols):
				cell = hex_map.values[i][j]
				if isinstance(cell, ctrnn.Network):
					cell_inputs = []
					for n_i, occupied in enumerate(hex_map.occupied_neighbors((i, j))):
						if occupied != False:
							cell_inputs.append(1)
						else:
							cell_inputs.append(0)

					cell_inputs.append(light_per_cell[(i,j)])

					for p_map in pheromone_maps:
						cell_inputs.append(p_map.values[i][j])
					
					assert(len(cell_inputs) == self.num_input)
					yield ((i,j), cell_inputs)

	def lightInput(self, hexmap):
		light = 0
		open_columns = set(range(hexmap.cols))
		light_per_cell = dict()

		for i in range(hexmap.rows-1, -1, -1):
			to_remove = set()	
			light_value = i / float(hexmap.rows-1)
			for j in open_columns:
				cell = hexmap.values[i][j]
				if isinstance(cell, ctrnn.Network):
					light += light_value
					light_per_cell[(i,j)] = light_value
					to_remove.add(j)

			open_columns.difference_update(to_remove)
		
		return (light, light_per_cell)

	def num_cells(self, hexmap):
		n = 0
		for col in hexmap.values:
			for cell in col:
				if isinstance(cell, ctrnn.Network):
					n += 1
		return n

	def fitness(self, genome):
		hexmap = simulate(genome, self.shape, self.cell_inputs)[0]

		if hexmap.values[0][int(self.shape[1]/2.0)] == 0:
			return 0

		max_light = hexmap.cols
		light_fitness = self.lightInput(hexmap)[0] / max_light

		size = hexmap.rows*hexmap.cols
		weight_fitness = 1 - ( self.num_cells(hexmap) / float(size) )
		
		truss = truss_from_map(hexmap)

		y_force = -1000
		for joint in truss.joints:
			joint.loads[1] = y_force

		truss.calc_fos()

		if truss.fos_total < 1:
			return 0

		return (light_fitness + weight_fitness) / 2

class Truss(Experiment):
	def __init__(self, arg):
		self.arg = arg
	def draw(self, genome):
		pass
		# def plot_genome(genome):
# 	hex_map = simulate(genome, shape)[0]
# 	truss   = truss_from_map(hex_map, hex_radius)
# 	fitness = eval_fitness(genome)
# 	fos = None
# 	try:
# 		fos = eval_fos(truss)
# 	except:
# 		pass

# 	draw_truss(screen, truss, fitness, fos)

if __name__ == '__main__':
	hexmap = Map((4,4))
	for x in range(4):
		for y in range(4):
			hexmap.values[y][x] = ctrnn.Network(None,None,None)
	# hexmap.values[0][0] = ctrnn.Network(None,None,None)
	# hexmap.values[2][0] = ctrnn.Network(None,None,None)


	size = hexmap.rows*hexmap.cols
	tree = Tree((4,4), None)
	# weight_fitness = 1 - ( tree.num_cells(hexmap) / (size) )
	
	max_light = hexmap.rows
	print(tree.lightInput(hexmap)[1])

