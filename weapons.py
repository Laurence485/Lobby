import pygame
from map_generation import Map
from random import choice
import config

class Weapon:
	'''place weapons / pick-ups in random locations in grass / water, set weapons timer when
	a pick-up occurs'''
	def __init__(self, img, name):
		self.weapon = img
		self.name = name

	def new_location(self, loc):
		#distance from right edge,bottom edge - and - left edge,top edge
		edge_dist = self.measure_area(loc,1) + self.measure_area(loc,-1)
		width = edge_dist[0] + abs(edge_dist[2])
		height = edge_dist[1] + abs(edge_dist[3])

		middle = (width//2 - self.weapon.get_width()//2, height//2 - self.weapon.get_height()//2)
		left_pos = loc[0] + edge_dist[2]
		top_pos = loc[1] + edge_dist[3]

		self.hidden_loc = loc
		self.location = (left_pos+middle[0],top_pos+middle[1])
		print(f'new {self.name} location {self.hidden_loc}')

	def measure_area(self,_coords,direction):
		'''go R/D or L/U until we hit edge of grass/water and return the distances'''
		coords = [_coords[0],_coords[1]]
		edges = [0,0]
		distance = config.grid_spacing*direction
		while tuple(coords) in Map.movement_cost_area:
			coords[0] += distance
			edges[0] += distance
		coords = [_coords[0],_coords[1]]
		while tuple(coords) in Map.movement_cost_area:
			coords[1] += distance
			edges[1] += distance
		return edges

	def draw(self,win):
		win.blit(self.weapon, (self.location))

class Mushroom(Weapon):
	def __init__(self):
		super().__init__(pygame.image.load('sprites/objects/Mushroom.png').convert_alpha(), 'mushroom')

class Bike(Weapon):
	def __init__(self):
		super().__init__(pygame.image.load('sprites/objects/bike.png').convert_alpha(), 'bike')

class Pokeball:
	'''default weapon - press spacebar to fire a pokeball up to 150px'''
	def __init__(self,x,y,player_width,player_height,direction,vel):
		self.bullet = pygame.image.load('sprites/objects/pokeball.png').convert_alpha()
		self.masterball = pygame.image.load('sprites/objects/masterball.png').convert_alpha()
		self.width = self.bullet.get_width()
		self.height = self.bullet.get_height()
		if direction == 'L':
			x = x - self.width
		elif direction == 'R':
			x = x + player_width
		elif direction == 'U':
			y = y - self.height
		elif direction == 'D':
			y = y + player_height
		self.x = x
		self.y = y
		self._direction = direction
		self._start_x = x
		self._start_y = y
		self.vel = vel*2

	def draw(self, win):
		win.blit(self.bullet, (self.x,self.y))

	def distance(self):
		return abs(self.x - self._start_x) + abs(self.y - self._start_y)