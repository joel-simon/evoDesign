from neat.genome import Genome

class CellGenome(Genome):
	"""Extend the default genome with more behavior."""
	def __init__(self, *args, **kwargs):
		self.morphogens = 1
		self.morphogen_thresholds = 4
		self.cell_types = 1

		config = args[1]
		config.input_nodes = self.get_num_inputs()
		config.output_nodes = self.get_num_outputs()
		super(CellGenome, self).__init__(*args, **kwargs)

	def get_num_inputs(self):
		n = self.cell_types # One binary value for each cell type.
		n += self.morphogens*self.morphogen_thresholds
		return n

	def get_num_outputs(self):
		num_outputs = 1 # Apoptosis.
		num_outputs += self.cell_types # Cell division differentiation.
		num_outputs += 4 # Cell division direction.
		num_outputs += self.morphogens
		return num_outputs
