import config
import pygame
from center_item import centerItem
from network import Network
from start_game import StartGame

def main(username):
	'''init pygame and set up homescreen objects'''
	pygame.init()
	running = True

	global walk_count
	walk_count = 0

	game_started = False

	# window for drawing on
	window_width = config.window_width
	window_height = config.window_height

	win = pygame.display.set_mode((window_width,window_height)) #width and height of window

	pygame.display.set_caption("Pokéwars")

	bg = pygame.image.load('sprites/homescreen.jpg').convert()

	ash_walk_anim =[ pygame.image.load('sprites/player 0/down2.png').convert_alpha(),  pygame.image.load('sprites/player 0/down3.png').convert_alpha()]
	scaled_player_width = ash_walk_anim[0].get_width()*2*2
	scaled_player_height = ash_walk_anim[0].get_height()*2*2
	scaled_player_ypos = 120

	play_button = pygame.image.load('sprites/play.png').convert_alpha()
	play_button_ypos = scaled_player_ypos + 120
	play_button_pos =  (centerItem.center(play_button.get_width()),play_button_ypos)

	leaderboard_button = pygame.image.load('sprites/leaderboard.png').convert_alpha()
	leaderboard_button_ypos = play_button_ypos + 80
	leaderboard_button_pos = (centerItem.center(leaderboard_button.get_width()),leaderboard_button_ypos)

	pointer = pygame.image.load('sprites/pointer.png').convert_alpha()
	server_offline_text = pygame.image.load('sprites/server_offline.png').convert_alpha()

	clock = pygame.time.Clock()


	net = Network(username.lower())


	def show_homescreen():
		'''blit homescreen objects onto screen'''
		global walk_count
		if walk_count + 1 > 8:
			walk_count = 0

		scaled_player = pygame.transform.scale2x(pygame.transform.scale2x(ash_walk_anim[walk_count//4]))

		#blit menu items on screen
		win.blit(bg,(0,0))
		win.blit(scaled_player, (centerItem.center(scaled_player_width),120))
		win.blit(play_button, play_button_pos)
		win.blit(leaderboard_button, leaderboard_button_pos)
		if net.data is None:
			win.blit(server_offline_text, (5,window_height-server_offline_text.get_height()-5))

		check_hover_over_menu_item()


		walk_count += 1

		pygame.display.update()

	def check_hover_over_menu_item(click=False):
		'''blit pointer arrow on screen when hovering over menu buttons'''
		for index, menu_item in enumerate([[play_button_pos,play_button.get_rect()],[leaderboard_button_pos,leaderboard_button.get_rect()]]):
			
			pos = menu_item[0]
			dimensions = menu_item[1]

			if pygame.Rect(pos[0],pos[1],dimensions[2],dimensions[3]).collidepoint(pygame.mouse.get_pos()):
				if click:
					return 'play' if index == 0 else 'leaderboard'
				win.blit(pointer, (pos[0]-pointer.get_width()*2,pos[1]))

	def show_leaderboard(all_player_stats):
		'''format and print leaderboard stats from db'''
		print("---LEADERBOARD---")
		for stats in all_player_stats:
			name = stats[0]
			kills = stats[1]
			deaths = stats[2]
			kd = stats[3]
			print(f" ------- \n (player) {name}:  \n kills: {kills} \n deaths: {deaths} \n K/D: {kd}\n------- \n")

	while running:
		for event in pygame.event.get(): #get mouse positions, keyboard clicks etc
			if event.type == pygame.QUIT: #we pressed the exit button
				running = False

			if not game_started:
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						menu_item = check_hover_over_menu_item(click=True)
						#clicking on an item
						if menu_item is not None:
							if menu_item == 'play':
								#if server was offline on init then try and connect again when we click play
								if net.data is None:
									net = Network(username.lower())
									if net.data is not None:
										print('successfully connected to server.')
										game_started = True
										game = StartGame(win, net, username)
								else:
									#---JOIN A GAME----
									game_started = True
									game = StartGame(win, net, username)
							elif menu_item == 'leaderboard':
								if net.data is None:
									net = Network(username.lower())
									if net.data is not None:
										print('successfully connected to server.')
										show_leaderboard(net.leaderboard)
								else:
									show_leaderboard(net.leaderboard)
			else:
				game.check_keyboard_input(event)

		if not game_started:
			clock.tick(9)
			show_homescreen()
		else:
			#rather than 2x the bike speed, we 2x the FPS so we can still move 1sq at a time
			clock.tick(9) if not game.ash.bike else clock.tick(18)
			game.fetch_data()
			game.check_collisions_and_pickups()
			game.redraw_gamewindow()

	pygame.quit()

if __name__ == '__main__':
	username = input("Welcome to Pokéwars \n Movement: arrow keys \n Shoot: Spacebar \n Strafe: S \n Menu: Z \n Show Grid: X \n Change Map (Host only): C \n\n Enter Username: ")
	main(username)