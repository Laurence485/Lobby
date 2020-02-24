from random import choice

class RandomNode:
	'''choose a random node from our grid'''
	@classmethod
	def __init__(self, nodes):
		self.nodes = nodes
		self.node = choice(tuple(self.nodes))