import config
import pygame
from pathfinding import Pathfinding
from navigation import Navigation
from characters import Player, Npc
from map_generation import Map
from random import choice
from weapons import Bike, Mushroom

def main():
	pygame.init()
	pygame.running = True
	running = True
	start_route = False

	# window for drawing on
	window_width = config.window_width
	window_height = config.window_height
	grid_spacing = config.grid_spacing
	win = pygame.display.set_mode((window_width,window_height)) #width and height of window

	pygame.display.set_caption("Pokémon Crisis")

	bg = pygame.image.load('sprites/background.jpg').convert()
	oak = pygame.image.load('sprites/oak.png')

	new_map = Map()
	#use all objects, set specific number of grass tree and water objects
	new_map.generate_map(grass=20,trees=20, water=2) 

	clock = pygame.time.Clock()

	ash = Player(choice(tuple(new_map.nodes)))
	npc = Npc(150,170,400)


	font = pygame.font.SysFont('verdana',10,False,True)

	path = Pathfinding(new_map.nodes, new_map.movement_cost_area)

	# traverse = Navigation()
	# traverse.bfs(bfs_route, bot)
	bike = Bike()
	mushroom = Mushroom()
	bike.new_location(choice(tuple(Map.movement_cost_area)))
	mushroom.new_location(choice(tuple(Map.movement_cost_area)))

	def redraw_gamewindow():
		win.blit(bg,(0,0)) #put picutre on screen (background)
		pygame.draw.rect(win, (200,200,200), (0,0,window_width,window_height))

		# # draw grid
		# for x in range(0,window_width,grid_spacing): #col
		# 	for y in range(0,window_height,grid_spacing): #row
		# 		pygame.draw.rect(win, (125,125,125), (x,y,grid_spacing,grid_spacing),1)

		Map.draw(win)

		if start_route:
			# draw bfs route
			for x,y in routes['BFS']:
				pygame.draw.rect(win, (0,0,255), (x,y,grid_spacing,grid_spacing))
			# draw dijkstra route
			for x,y in routes['GBFS']:
				pygame.draw.rect(win, (255,0,0), (x,y,grid_spacing,grid_spacing))
			#draw DA route
			for x,y in routes['DA']:
				pygame.draw.rect(win, (0,255,0), (x,y,grid_spacing,grid_spacing))
			# draw A* route
			for x,y in routes['A*']:
				pygame.draw.rect(win, (100,100,100), (x,y,grid_spacing,grid_spacing))

			# re-position oak if oob
			oak_x = target_x
			oak_y = target_y
			if oak_x > window_width-oak.get_width(): oak_x -= grid_spacing
			elif oak_y > window_height-oak.get_height(): oak_y -= grid_spacing
			win.blit(oak,(oak_x,oak_y))

		ash.draw(win)
		npc.draw(win)

		time = font.render(f'Time: {round(pygame.time.get_ticks()/1000,2)}',1,(0,0,0))
		win.blit(time, (390, 10))

		pygame.display.update()

	#main event loop
	while running:
		clock.tick(9) #9 FPS

		for event in pygame.event.get(): #get mouse positions, keyboard clicks etc
			if event.type == pygame.QUIT: #we pressed the exit button
				running = False
			if event.type == pygame.MOUSEBUTTONDOWN and not start_route:
				target_x, target_y = event.pos[0], event.pos[1]
				routes = path.compute_all_paths(ash.x,ash.y,target_x,target_y)
				start_route = True

		#move amongst available nodes 
		#(no movement out of bounds and in object coordinates)
		#movement cost in grass / water
		ash.move(new_map.objs_area, new_map.movement_cost_area, bike, mushroom)
		redraw_gamewindow()

	pygame.quit()

if __name__ == '__main__':
	main()