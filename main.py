import config
import pygame
from center_item import centerItem

def main():
	pygame.init()
	running = True
	global walk_count
	walk_count = 0

	# window for drawing on
	window_width = config.window_width
	window_height = config.window_height

	win = pygame.display.set_mode((window_width,window_height)) #width and height of window

	pygame.display.set_caption("Pokéwars")

	bg = pygame.image.load('sprites/homescreen.jpg').convert()
	play_button = pygame.image.load('sprites/play.png').convert_alpha()
	play_button_width = play_button.get_width()
	leaderboard_button = pygame.image.load('sprites/leaderboard.png').convert_alpha()
	leaderboard_button_width = leaderboard_button.get_width()
	pointer = pygame.image.load('sprites/pointer.png').convert_alpha()

	clock = pygame.time.Clock()

	ash_walk_anim =[ pygame.image.load('sprites/player 0/down2.png').convert_alpha(),  pygame.image.load('sprites/player 0/down3.png').convert_alpha()]
	scaled_player_width = ash_walk_anim[0].get_width()*2*2
	scaled_player_height = ash_walk_anim[0].get_height()*2*2

	def show_homescreen():
		global walk_count
		if walk_count + 1 > 8:
			walk_count = 0

		scaled_player = pygame.transform.scale2x(pygame.transform.scale2x(ash_walk_anim[walk_count//4]))

		win.blit(bg,(0,0))
		win.blit(scaled_player, (centerItem.center(scaled_player_width),110))
		win.blit(play_button, (centerItem.center(play_button_width),230))
		win.blit(leaderboard_button, (centerItem.center(leaderboard_button_width),310))

		walk_count += 1

		pygame.display.update()

	while running:
		clock.tick(9)

		for event in pygame.event.get(): #get mouse positions, keyboard clicks etc
			if event.type == pygame.QUIT: #we pressed the exit button
				running = False

		show_homescreen()

	pygame.quit()

if __name__ == '__main__':
	main()