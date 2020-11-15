from characters import Player
from map_generation import Map
from random_node import RandomNode
from menu import Menu
from weapons import Bike, Mushroom, WeaponStatus
from network import Network
from multiplayer import Multiplayer
import config
import pygame

class StartGame:
	'''main game class'''
	def __init__(self, win, net, username):
		self.menu = False
		self.grid = False
		self.win = win
		self.net = net

		#generate and save map
		# new_map = Map()
		# new_map.generate_map('random', False)

		self.bg = pygame.image.load('sprites/background.jpg').convert()

		#load first shuffled map from server
		self.current_map = 0
		Map.load('myfirstmap')

		#create client player object and assign colour based on ID, username from input, map from server
		# self.ash = Player(RandomNode(Map.nodes).node, self.net.playerID, username, self.current_map)
		self.ash = Player(RandomNode(Map.nodes).node, 0, username, self.current_map)

		#other player objects
		p2, p3, p4, p5 = None, None, None, None
		self.players = [p2,p3,p4,p5]

		self.bikes = [Bike() for i in range(config.bikes)]
		self.mushrooms = [Mushroom() for i in range(config.mushrooms)]

		WeaponStatus.set_locations(self.bikes, self.mushrooms)

		# music = pygame.mixer.music.load(config.theme)
		# pygame.mixer.music.set_volume(0.5)
		# pygame.mixer.music.play(-1)

		self.ash.ID = 0

	def redraw_gamewindow(self):
		'''draw objects onto the screen: background, grid, players, weapons'''
		self.win.blit(self.bg,(0,0)) #put picutre on screen (background)

		# draw grid
		if self.grid:
			for x in range(0,config.window_width,config.grid_spacing): #col
				for y in range(0,config.window_height,config.grid_spacing): #row
					pygame.draw.rect(self.win, (125,125,125), (x,y,config.grid_spacing,config.grid_spacing),1)

		Map.draw(self.win)
		for bike in self.bikes:
			bike.draw(self.win)
		for mushroom in self.mushrooms:
			mushroom.draw(self.win)
		self.ash.draw(self.win)

		#draw all players
		for p in self.players:
			if p and p.ID != None:
				p.draw(self.win)

				#note that we are 20px behind (last position doesnt show... this is temp fix)
				for bullet in p.inventory:
					bullet_sprite = pygame.image.load('sprites/objects/pokeball.png').convert_alpha()
					x,y,_dir,start_x,start_y = bullet
					if _dir == 'L':
						x += 20
					elif _dir == 'R':
						x -= 20
					elif _dir == 'U':
						y += 20
					elif _dir == 'D':
						y -= 20
					self.win.blit(bullet_sprite, (x,y))

				self.ash.check_trample(p)

		#pressed z
		if self.menu:
			Menu(self.win, [self.ash.stats,self.ash.username], [[p.stats,p.username] for p in self.players if p])

		for bullet in self.ash.inventory:
			self.ash.draw_bullet(self.win,bullet)
			for p in self.players:
				if p and p.ID != None:
					self.ash.check_kill(bullet, p)

		pygame.display.update()

	def change_map(self):
		'''host (ID=0) may change map i.e. go to next shuffled map from server or back to 0'''
		if self.ash.map < len(self.net.maps)-1:
			self.ash.map += 1
		else: self.ash.map = 0
		Map.load(self.net.maps[self.ash.map])
		WeaponStatus.set_locations(self.bikes, self.mushrooms)


	def check_keyboard_input(self, event):
		'''check for Z,X,C'''
		if event.type == pygame.KEYUP:
			if event.key== pygame.K_SPACE:
				self.ash.space_up = True
			if event.key == pygame.K_z: #z for menu
				self.menu = True if not self.menu else False
			if event.key == pygame.K_x: #a for grid
				self.grid = True if not self.grid else False
			if event.key == pygame.K_c and self.ash.ID == 0: #host can press c to change map
				self.change_map()

	def fetch_data(self):
		'''get data from server, player positions, stats, kill status etc'''
		Multiplayer.get_player_data(self.ash, self.net, self.players, self.bikes, self.mushrooms)
		Multiplayer.check_death_status(self.ash, self.players)

	def check_collisions_and_pickups(self):
		WeaponStatus(self.ash)
		self.ash.move(Map.objs_area, Map.movement_cost_area, self.bikes, self.mushrooms)


if __name__ == '__main__':

	pygame.init()
	running = True

	# window for drawing on
	window_width = config.window_width
	window_height = config.window_height

	win = pygame.display.set_mode((window_width,window_height)) #width and height of window

	pygame.display.set_caption("Pokéwars")

	username = 'testUser'

	net = Network(username.lower())

	game = StartGame(win, net, username)

	if net.data is not None:
		print('successfully connected to server.')
	else:
		print('cannot connect to server.')

	clock = pygame.time.Clock()

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: #we pressed the exit button
					running = False
		clock.tick(9)
		# game.fetch_data()
		game.check_collisions_and_pickups()
		game.check_keyboard_input(event)
		game.redraw_gamewindow()
