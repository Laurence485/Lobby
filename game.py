import config
import pygame
from characters import Player, Npc
from map_generation import Map
from random import choice
from network import Network
from menu import Menu
from weapons import Bike, Mushroom, WeaponStatus
from multiplayer import Multiplayer
#change frame update to dirty_rects: https://www.pygame.org/docs/tut/newbieguide.html
#chat saying who killed who
#kill streak to chat
def main():
	pygame.init()
	pygame.running = True
	running = True
	menu = False

	# window for drawing on
	window_width = config.window_width
	window_height = config.window_height
	grid_spacing = config.grid_spacing
	win = pygame.display.set_mode((window_width,window_height)) #width and height of window

	pygame.display.set_caption("Pokémon Crisis")

	bg = pygame.image.load('sprites/background.jpg').convert()

	net = Network()

	new_map = Map()
	#use all objects, set specific number of grass tree and water objects
	new_map.generate_map(grass=20,trees=20, water=2) 

	clock = pygame.time.Clock()

	ash = Player(choice(tuple(new_map.nodes)),net.playerID)

	p2, p3, p4, p5 = None, None, None, None
	players = [p2,p3,p4,p5] #players

	npc = Npc(150,170,400)
	bot = Player((290,90))

	bike = Bike()
	mushroom = Mushroom()
	bike.new_location(choice(tuple(Map.movement_cost_area)))
	mushroom.new_location(choice(tuple(Map.movement_cost_area)))
	
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
			Menu(win, ash.stats, [p.stats for p in players if p])

		for bullet in ash.inventory:
			ash.draw_bullet(win,bullet)
			for p in players:
				if p and p.ID != None:
					ash.check_kill(bullet, p)


		time = font.render(f'Time: {round(pygame.time.get_ticks()/1000,2)}',1,(0,0,0))
		win.blit(time, (390, 10))

		pygame.display.update()

	def get_player_data():
		'''get player data from server and map data to local player objects'''
		attrs = net.send(ash.attributes()) #return attributes of other players

		for i in range(len(players)):
			a = attrs[i]

			#create new player instance if:
			#1) we haven't already created an instance
			#2) they have an ID (they are connected to server)
			if not players[i] and a['ID'] != None:
				print('creating new player')
				players[i] = Player()

			#returned attributes of ith player from server
			elif players[i]:
				players[i].x, players[i].y = a['x'], a['y']
				players[i].left, players[i].right, players[i].up, players[i].down = a['L'], a['R'], a['U'], a['D']
				players[i].standing, players[i].walk_count = a['standing'], a['walk count']
				players[i].hit_slow, players[i].bike, players[i].mushroom = a['hit slow'], a['bike'], a['mushroom']
				players[i].inventory = a['inventory']
				players[i].stats = a['stats']
				players[i].killed = a['killed']
				players[i].dead = a['dead']
				players[i].ID = a['ID']


	def check_death_status():
		'''check if we have died or if another player has been killed by us through ash.check_kill().
		call ash.die() and set our death and kill status accordingly.'''

		#another player killed us and we are not already dead
		if any(p.killed == ash.ID for p in players if p) and not ash.dead:
			ash.die()
			ash.dead = True

		#we've killed another player and they are dead so reset killed
		elif any(ash.killed == p.ID and p.dead for p in players if p):
			ash.killed = None

		#we are dead and no one else has killed us so reset dead
		elif ash.dead and all(p.killed != ash.ID for p in players if p):
			ash.dead = False

	#main event loop
	while running:
		clock.tick(9) #9 FPS

		Multiplayer.get_player_data(ash, net, players)
		# get_player_data()
		check_death_status()
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