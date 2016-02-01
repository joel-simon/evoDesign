import numpy as np
from simulate import simulate
from visualize import draw_hex_map
from hexmap import Map
from sklearn import metrics
import pygame

""" Calculate percent of positions where values are the same """
def matrix_similarity(A, B):	
	""" Correct is where both 0 or both 1, which is xnor gate """
	return np.logical_not(np.logical_xor(A, B)).mean()

class Experiment(object):
	def fitnesses(self, genomes):
		for genome in genomes:
			genome.fitness = self.fitness(genome)		
	
	def fitness(self, genome):
		hex_map = simulate(genome, self.shape)[0]
		y_true = np.ravel(self.target.values)
		y_pred = np.ravel(hex_map.values)
		# return np.logical_and(hex_map.values, self.target.values).mean()
		# return matrix_similarity(hex_map.values, self.target.values)
		# return metrics.roc_auc_score(np.ravel(self.target.values), np.ravel(hex_map.values))
		return metrics.f1_score(y_true, y_pred)

	def draw(self, genome):
		hexmap = simulate(genome, self.shape)[0]
		self.screen.fill((255,255,255))
		draw_hex_map(self.screen, hexmap, start = (0,0))
		draw_hex_map(self.screen, self.target, start = (400,0))
		pygame.display.flip()

class RandomTarget(Experiment):
	def __init__(self, shape, screen):
		self.shape  = shape
		self.screen = screen
		self.target = Map(self.shape)
		self.target.values = np.random.randint(2, size = shape)
	
class ColumnTarget(Experiment):
	def __init__(self, shape, screen):
		self.shape  = shape
		self.screen = screen
		self.target = Map(self.shape)
		self.target.values[:, 4] = 1

class ColumnsTarget(Experiment):
	def __init__(self, shape, screen):
		self.shape  = shape
		self.screen = screen
		self.target = Map(self.shape)
		self.target.values[:, 3:5] = 1

class CircleTarget(Experiment):
	def __init__(self, shape, screen):
		self.shape  = shape
		self.screen = screen
		self.target = Map(self.shape)
		for row, col in self.target.neighbors((4,4)):
			self.target.values[row, col] = 1	

class RowTarget(Experiment):
	def __init__(self, shape, screen):
		self.shape  = shape
		self.screen = screen
		self.target = Map(self.shape)
		self.target.values[4] = 1