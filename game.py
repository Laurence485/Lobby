import config
import pygame
from characters import Player, Npc
from map_generation import Map
from random_node import RandomNode
from random import choice
from network import Network
from menu import Menu
from weapons import Bike, Mushroom, WeaponStatus
from multiplayer import Multiplayer
import time

#change frame update to dirty_rects: https://www.pygame.org/docs/tut/newbieguide.html
def main():
	username = input("Welcome to Pokéwars \n Movement: arrow keys \n Shoot: Spacebar \n Strafe: S \n Menu: Z \n Show Grid: X \n Change Map (Host only): C \n\n Enter Username: ")

	pygame.init()
	pygame.running = True
	running = True
	menu = False
	grid = False

	# window for drawing on
	window_width = config.window_width
	window_height = config.window_height
	grid_spacing = config.grid_spacing
	win = pygame.display.set_mode((window_width,window_height)) #width and height of window

	pygame.display.set_caption("Pokéwars")

	bg = pygame.image.load('sprites/background.jpg').convert()

	net = Network()	

	#generate and save map
	# new_map = Map()
	#new_map.generate_map('city', True)

	#load first shuffled map from server
	current_map = 0
	Map.load(net.maps[current_map])

	clock = pygame.time.Clock()

	#create client player object and assign colour based on ID, username from input, map from server
	ash = Player(RandomNode(Map.nodes).node, net.playerID, username, current_map)

	#other player objects
	p2, p3, p4, p5 = None, None, None, None
	players = [p2,p3,p4,p5]

	npc = Npc(150,170,400)
	bot = Player((290,90))

	bikes = [Bike() for i in range(config.bikes)]
	mushrooms = [Mushroom() for i in range(config.mushrooms)]

	WeaponStatus.set_locations(bikes, mushrooms)
	
	music = pygame.mixer.music.load(config.theme)
	pygame.mixer.music.set_volume(0.5)
	pygame.mixer.music.play(-1)

	font = pygame.font.SysFont('verdana',10,False,True)

	ash.ID = net.playerID

	def redraw_gamewindow(grid):
		'''draw objects onto the screen: background, grid, players, weapons'''
		win.blit(bg,(0,0)) #put picutre on screen (background)

		# draw grid
		if grid:
			for x in range(0,window_width,grid_spacing): #col
				for y in range(0,window_height,grid_spacing): #row
					pygame.draw.rect(win, (125,125,125), (x,y,grid_spacing,grid_spacing),1)

		Map.draw(win)
		for bike in bikes:
			bike.draw(win)
		for mushroom in mushrooms:
			mushroom.draw(win)
		npc.draw(win)
		ash.draw(win)

		#draw all players
		for p in players:
			if p and p.ID != None:
				p.draw(win)

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
					win.blit(bullet_sprite, (x,y))

				ash.check_trample(p)

		#pressed z
		if menu:
			Menu(win, [ash.stats,ash.username], [[p.stats,p.username] for p in players if p])

		for bullet in ash.inventory:
			ash.draw_bullet(win,bullet)
			for p in players:
				if p and p.ID != None:
					ash.check_kill(bullet, p)

		pygame.display.update()


	def change_map():
		'''host (ID=0) may change map i.e. go to next shuffled map from server or back to 0'''
		if ash.map < len(net.maps)-1:
			ash.map += 1
		else: ash.map = 0
		Map.load(net.maps[ash.map])
		WeaponStatus.set_locations(bikes, mushrooms)
		
	#main event loop
	while running:
		clock.tick(9) #9 FPS

		Multiplayer.get_player_data(ash, net, players, bikes, mushrooms)
		Multiplayer.check_death_status(ash, players)
		WeaponStatus(ash)

		for event in pygame.event.get(): #get mouse positions, keyboard clicks etc
			if event.type == pygame.QUIT: #we pressed the exit button
				running = False
			if event.type == pygame.KEYUP: 
				if event.key== pygame.K_SPACE:
					ash.space_up = True
				if event.key == pygame.K_z: #z for menu
					menu = True if not menu else False
				if event.key == pygame.K_x: #a for grid
					grid = True if not grid else False
				if event.key == pygame.K_c and ash.ID == 0: #host can press c to change map
					change_map()

		#move amongst available nodes 
		#(no movement out of bounds and in object coordinates)
		#movement cost in grass / water
		ash.move(Map.objs_area, Map.movement_cost_area, bikes, mushrooms)
		redraw_gamewindow(grid)

	pygame.quit()

if __name__ == '__main__':
	main()