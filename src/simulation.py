from abc import ABCMeta, abstractmethod

class Simulation(object):
	"""docstring for Simulation"""
	__metaclass__ = ABCMeta
	
	def __init__(self, arg):
		self.arg = arg
	
	@abstractmethod
	def run(self, a, b):
		pass



class Derp(Simulation):
	"""docstring for Derp"""
	def __init__(self, arg):
		self.arg = arg
		
	def run(self, a):
		pass


d = Derp(1)
