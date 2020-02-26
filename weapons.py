import pygame
from map_generation import Map
from random_node import RandomNode
import config

class Weapon:
	'''place weapons / pick-ups in random locations in grass / water, set weapons timer when
	a pick-up occurs'''
	def __init__(self, img, name):
		self.weapon = img
		self.name = name
		self.hidden_loc = None
		self.location = None

	def new_location(self, loc, mca=True):
		#distance from right edge,bottom edge - and - left edge,top edge
		if mca: #maps with movement cost areas (grass/water)
			edge_dist = self.measure_area(loc,1) + self.measure_area(loc,-1)
			width = edge_dist[0] + abs(edge_dist[2])
			height = edge_dist[1] + abs(edge_dist[3])

			middle = (width//2 - self.weapon.get_width()//2, height//2 - self.weapon.get_height()//2)
			left_pos = loc[0] + edge_dist[2]
			top_pos = loc[1] + edge_dist[3]

			self.hidden_loc = loc
			self.location = (left_pos+middle[0],top_pos+middle[1])
		else:
			self.hidden_loc = loc
			self.location = loc
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

class WeaponStatus:
	'''check if we've picked up a weapon'''
	def __init__(self, ash):
		if ash.bike:
			self.weapon_timer(ash.bike, ash.start_bike_ticks, ash)
		if ash.mushroom:
			self.weapon_timer(ash.mushroom, ash.start_mushroom_ticks, ash)

	def weapon_timer(self, item, start_ticks, ash):
		'''start 15s timers for bike / mushroom'''
		seconds=(pygame.time.get_ticks()-start_ticks)/1000
		if seconds > 15:
			if item == ash.mushroom:
				ash.mushroom = False
				ash.width /=2
				ash.height /=2
				ash.start_mushroom_ticks = 0
			elif item == ash.bike:
				ash.bike = False
				ash.start_bike_ticks = 0
			#return to default music if nothing activated
			if not ash.mushroom and not ash.bike:
				music = pygame.mixer.music.load(config.theme)
				pygame.mixer.music.set_volume(0.5)
				pygame.mixer.music.play(-1)

	@classmethod
	def set_locations(cls, bikes, mushrooms):
		'''put bikes and mushrooms in grass/water if we're using a map with grass/water else random available node'''
		for bike in bikes:
			if len(Map.movement_cost_area):
				bike.new_location(RandomNode(Map.movement_cost_area).node)
			else:
				bike.new_location(RandomNode(Map.nodes).node, False)

		for mushroom in mushrooms:
			if len(Map.movement_cost_area):
				mushroom.new_location(RandomNode(Map.movement_cost_area).node)
			else:
				mushroom.new_location(RandomNode(Map.nodes).node, False)