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
#if server time reaches 3m, change map. Then done!
def main():
	username = input("Welcome to Pokéwars \n Enter Username: ")

	pygame.init()
	pygame.running = True
	running = True
	menu = False
	grid = False
	game_time_loop = config.game_time_loop

	# window for drawing on
	window_width = config.window_width
	window_height = config.window_height
	grid_spacing = config.grid_spacing
	win = pygame.display.set_mode((window_width,window_height)) #width and height of window

	pygame.display.set_caption("Pokéwars")

	bg = pygame.image.load('sprites/background.jpg').convert()

	net = Network()

	# new_map = Map()
	#generate and save map
	# # new_map.generate_map('city', True)
	# maps = ['myfirstmap','grass','water','trees','city']

	#load map from server
	current_map = 0
	Map.load(net.maps[current_map])

	clock = pygame.time.Clock()
	start_time = net.start_time #start game timer

	#create client player object and assign colour based on ID
	ash = Player(RandomNode(Map.nodes).node,net.playerID, username)

	#other player objects
	p2, p3, p4, p5 = None, None, None, None
	players = [p2,p3,p4,p5]

	npc = Npc(150,170,400)
	bot = Player((290,90))

	bike = Bike()
	mushroom = Mushroom()
	#put bikes and mushrooms in grass/water if we're using a map with grass/water else random available node
	if len(Map.movement_cost_area):
		bike.new_location(RandomNode(Map.movement_cost_area).node)
		mushroom.new_location(RandomNode(Map.movement_cost_area).node)
	else:
		bike.new_location(RandomNode(Map.nodes).node, False)
		mushroom.new_location(RandomNode(Map.nodes).node, False)
	
	# target_sound = pygame.mixer.Sound('sounds/objective.wav') #run with target_sound.play()
	# music = pygame.mixer.music.load('sounds/music.mp3')
	# pygame.mixer.music.play(-1)

	font = pygame.font.SysFont('verdana',10,False,True)

	ash.ID = net.playerID

	def end_game(current_map):
		print('game ended.')
		if current_map < len(net.maps)-1:
			current_map += 1
		else: current_map = 0
		Map.load(net.maps[current_map])


	def game_timer(game_time_loop, current_map):
		'''3m timers for each map, after 180s, server time will be 180, so we must
		*2 the game_time_loop i.e. check for 360s on the next map and so on'''
		seconds=(time.time()-start_time)
		print(game_time_loop, seconds)
		if seconds > game_time_loop:
			game_time_loop *= 2
			end_game(current_map)
			running = False
			print(game_time_loop, seconds)
			return 0

		return 180-seconds

	def redraw_gamewindow(grid):
		win.blit(bg,(0,0)) #put picutre on screen (background)

		# draw grid
		if grid:
			for x in range(0,window_width,grid_spacing): #col
				for y in range(0,window_height,grid_spacing): #row
					pygame.draw.rect(win, (125,125,125), (x,y,grid_spacing,grid_spacing),1)

		Map.draw(win)
		bike.draw(win)
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

		#pressed z or time ran out
		if menu or game_timer(game_time_loop, current_map)==0:
			Menu(win, [ash.stats,ash.username], [[p.stats,p.username] for p in players if p])

		for bullet in ash.inventory:
			ash.draw_bullet(win,bullet)
			for p in players:
				if p and p.ID != None:
					ash.check_kill(bullet, p)


		time = font.render(f'Time: {round(game_timer(game_time_loop, current_map),0)}',1,(0,0,0))
		win.blit(time, (0, 0))

		pygame.display.update()

	#main event loop
	while running:
		clock.tick(9) #9 FPS

		Multiplayer.get_player_data(ash, net, players)
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
				if event.key == pygame.K_a: #a for grid
					grid = True if not grid else False

		#move amongst available nodes 
		#(no movement out of bounds and in object coordinates)
		#movement cost in grass / water
		ash.move(Map.objs_area, Map.movement_cost_area, bike, mushroom)
		redraw_gamewindow(grid)

	pygame.quit()

if __name__ == '__main__':
	main()