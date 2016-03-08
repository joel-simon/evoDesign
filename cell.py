from cellGenome import CellGenome
from neat import nn
directions = [(0,1), (1,0), (0,-1), (-1,0)]
import math

class Cell(object):
	"""docstring for Cell"""
	def __init__(self, cell_id, genome, node, cell_type=0):
		assert(isinstance(genome, CellGenome))
		self.id = cell_id
		self.genome    = genome
		self.network   = nn.create_feed_forward_phenotype(genome)
		self.cell_type = cell_type
		self.node = node
		self.morphogens = [0] * genome.morphogens

	def create_inputs(self):
		inputs = [0] * self.genome.num_inputs
		inputs[self.cell_type] = 1
		for i in range(0, len(self.morphogens)):
			inputs[i+1] = self.morphogens[i]
		return inputs

	def get_growth_direction(self, growth_directions):
		return directions[growth_directions.index(max(growth_directions))]
	# 	r = 5
	# 	dx, dy = directions[growth_directions.index(max(growth_directions))]
	# 	dx = r * math.cos(self.direction) * dx
	# 	dy = r * math.sin(self.direction) * dx
	# 	return (dx, dy)

	def parse_actions(self, actions):
		assert(len(actions)==self.genome.num_outputs)
		parsed_actions = dict()
		parsed_actions['apoptosis'] = actions[0]

		divisions = actions[1:1+self.genome.cell_types]
		if max(divisions) > 0:
			# If there is the signal for cell division or diffentiation.
			# One for each cell type, if multiple, pick the max.
			growth_directions = actions[1+self.genome.cell_types:1+self.genome.cell_types+4]
			parsed_actions['growth'] = divisions.index(max(divisions))
			parsed_actions['growth_direction'] = self.get_growth_direction(growth_directions)
		else:
			parsed_actions['growth'] = None
			parsed_actions['growth_direction'] = None

		parsed_actions['morphogens'] = actions[-self.genome.morphogens:]
		# print(parsed_actions['morphogens'])

		return parsed_actions

	def activate(self):
		inputs = self.create_inputs()
		action = self.network.serial_activate(inputs)
		return self.parse_actions(action)


