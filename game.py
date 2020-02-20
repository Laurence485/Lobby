import config
import pygame
from characters import Player, Npc
from map_generation import Map
from random import choice
from network import Network
from menu import Menu
from weapons import Bike, Mushroom
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

	new_map = Map()
	#use all objects, set specific number of grass tree and water objects
	new_map.generate_map(grass=20,trees=20, water=2) 

	clock = pygame.time.Clock()

	ash = Player(choice(tuple(new_map.nodes)))
	p2 = Player((100,100))

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

	net = Network()

	ash.ID = net.playerID

	def redraw_gamewindow():
		win.blit(bg,(0,0)) #put picutre on screen (background)

		# draw grid
		for x in range(0,window_width,grid_spacing): #col
			for y in range(0,window_height,grid_spacing): #row
				pygame.draw.rect(win, (125,125,125), (x,y,grid_spacing,grid_spacing),1)

		Map.draw(win)

		ash.draw(win)
		npc.draw(win)
		bot.draw(win)
		p2.draw(win)

		bike.draw(win)
		mushroom.draw(win)

		for bullet in ash.inventory:
			ash.draw_bullet(win,bullet)
			ash.check_kill(bullet, p2)

		for xy in p2.inventory:
			bullet = pygame.image.load('sprites/objects/pokeball.png').convert_alpha()
			win.blit(bullet, xy)

		ash.check_trample(p2)

		time = font.render(f'Time: {round(pygame.time.get_ticks()/1000,2)}',1,(0,0,0))
		win.blit(time, (390, 10))

		if menu:
			Menu(win, ash.stats, p2.stats)

		pygame.display.update()

	def weapon_timer(item, start_ticks):
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

	#main event loop
	while running:
		clock.tick(9) #9 FPS

		p2_attrs = net.send(ash.attributes()) #return attributes of other players
		p2.x, p2.y = p2_attrs['x'], p2_attrs['y']
		p2.left, p2.right, p2.up, p2.down = p2_attrs['L'], p2_attrs['R'], p2_attrs['U'], p2_attrs['D']
		p2.standing, p2.walk_count = p2_attrs['standing'], p2_attrs['walk count']
		p2.bike, p2.mushroom = p2_attrs['bike'], p2_attrs['mushroom']
		p2.inventory = p2_attrs['inventory']
		p2.stats = p2_attrs['stats']
		p2.killed = p2_attrs['killed']
		p2.dead = p2_attrs['dead']
		p2.ID = p2_attrs['ID']

		#another played killed us
		if p2.killed == ash.ID and not ash.dead:
			ash.die()
			ash.dead = True

		#we've killed another player and they are dead so reset killed
		elif ash.killed == p2.ID and p2.dead:
			print('yes')
			ash.killed = None

		#we are dead and they havn't killed us so reset dead
		elif ash.dead and p2.killed != ash.ID:
			ash.dead = False

		# if p2.x + p2.width >= ash.x and p2.x <= (ash.x + ash.width) and p2.y + p2.height >= ash.y and p2.y <= (ash.y + ash.height):
		# 	print(f'touching! p2:{(p2.x,p2.y)} p1:{(ash.x,ash.y)}')

		for event in pygame.event.get(): #get mouse positions, keyboard clicks etc
			if event.type == pygame.QUIT: #we pressed the exit button
				running = False
			if event.type == pygame.KEYUP: 
				if event.key== pygame.K_SPACE:
					ash.space_up = True
				if event.key == pygame.K_z: #z for menu
					menu = True if not menu else False

		#bike timer 15s
		if ash.bike:
			weapon_timer(ash.bike, ash.start_bike_ticks)
		if ash.mushroom:
			weapon_timer(ash.mushroom, ash.start_mushroom_ticks)

		#move amongst available nodes 
		#(no movement out of bounds and in object coordinates)
		#movement cost in grass / water
		ash.move(new_map.objs_area, new_map.movement_cost_area, bike, mushroom)
		redraw_gamewindow()

	pygame.quit()

if __name__ == '__main__':
	main()