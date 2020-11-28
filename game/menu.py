import pygame

import config


class Menu:
	@classmethod
	def __init__(cls, win, player, enemy):
		menu_width, menu_height = 300, 150
		menu_x = config.window_width//2-menu_width//2 #centered
		menu_y = config.window_height//2-menu_height//2
		menu = (menu_x, menu_y, menu_width,menu_height)

		header_font = pygame.font.SysFont('verdana',12,True)
		header = header_font.render(f"{'Name:':<15}{'Kills:':<15}{'Deaths:':<15}{'K/D:':>}",1,(0,0,0))
		
		text_font = pygame.font.SysFont('verdana',10)
		max_len_name = 10

		menu_img = pygame.Surface((menu_width,menu_height)).convert_alpha()
		menu_img.fill((200,200,200,150))
		win.blit(menu_img, (menu_x,menu_y))
		win.blit(header, (menu_x, menu_y))

		all_stats = [player]
		[all_stats.append(e) for e in enemy]

		for  i, stats in enumerate(all_stats):
			status, name = stats
			name = name[:max_len_name] #truncate if >10
			#give names a width of 70
			while text_font.size(name)[0] < 80:
				name += " "
			name_pos = 12
			row = f"{name:<{name_pos}}{status['kills']:<15}{status['deaths']:<12}{status['K/D']:>12}"
			text = text_font.render(row,1,(0,0,0))
			win.blit(text, (menu_x, menu_y+20+i*20))

		
