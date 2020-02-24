import config
import pygame
from characters import Player, Npc
from map_generation import Map
from random_node import RandomNode
from network import Network
from menu import Menu
from weapons import Bike, Mushroom, WeaponStatus
from multiplayer import Multiplayer
#change frame update to dirty_rects: https://www.pygame.org/docs/tut/newbieguide.html
#2 fncs - generate map, load map
#we use generate map to generate new maps and pickel them, we use load map to pic
#a map via name or random (we pickle nodes, objs, obj coords, movement cost nodes)
#we then dont need seed, and solves global weapons problem + allows us to have diff maps
def main():
	username = input("Welcome to Pokéwars \n Enter Username: ")

	pygame.init()
	pygame.running = True
	running = True
	menu = False

	# window for drawing on
	window_width = config.window_width
	window_height = config.window_height
	grid_spacing = config.grid_spacing
	win = pygame.display.set_mode((window_width,window_height)) #width and height of window

	pygame.display.set_caption("Pokéwars")

	bg = pygame.image.load('sprites/background.jpg').convert()

	net = Network()

	new_map = Map()
	#use all objects, set specific number of grass tree and water objects
	new_map.generate_map(grass=20,trees=20, water=2) 

	clock = pygame.time.Clock()

	#create client player object and assign colour based on ID
	ash = Player(RandomNode(new_map.nodes).node,net.playerID, username)

	#other player objects
	p2, p3, p4, p5 = None, None, None, None
	players = [p2,p3,p4,p5]

	npc = Npc(150,170,400)
	bot = Player((290,90))

	bike = Bike()
	mushroom = Mushroom()
	bike.new_location(RandomNode(Map.movement_cost_area).node)
	mushroom.new_location(RandomNode(Map.movement_cost_area).node)
	
	# target_sound = pygame.mixer.Sound('sounds/objective.wav') #run with target_sound.play()
	# music = pygame.mixer.music.load('sounds/music.mp3')
	# pygame.mixer.music.play(-1)

	font = pygame.font.SysFont('verdana',10,False,True)

	ash.ID = net.playerID

	def redraw_gamewindow():
		win.blit(bg,(0,0)) #put picutre on screen (background)

		# draw grid
		for x in range(0,window_width,grid_spacing): #col
			for y in range(0,window_height,grid_spacing): #row
				pygame.draw.rect(win, (125,125,125), (x,y,grid_spacing,grid_spacing),1)

		Map.draw(win)
		bike.draw(win)
		mushroom.draw(win)
		npc.draw(win)
		ash.draw(win)

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

		if menu:
			Menu(win, [ash.stats,ash.username], [[p.stats,p.username] for p in players if p])

		for bullet in ash.inventory:
			ash.draw_bullet(win,bullet)
			for p in players:
				if p and p.ID != None:
					ash.check_kill(bullet, p)


		time = font.render(f'Time: {round(pygame.time.get_ticks()/1000,2)}',1,(0,0,0))
		win.blit(time, (390, 10))

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

		#move amongst available nodes 
		#(no movement out of bounds and in object coordinates)
		#movement cost in grass / water
		ash.move(new_map.objs_area, new_map.movement_cost_area, bike, mushroom)
		redraw_gamewindow()

	pygame.quit()

if __name__ == '__main__':
	main()