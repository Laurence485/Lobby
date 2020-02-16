import pygame
import config
class Menu:
	@classmethod
	def __init__(self, win, stats):
		menu_width, menu_height = 300, 150
		menu_x = config.window_width//2-menu_width//2 #centered
		menu_y = config.window_height//2-menu_height//2
		menu = (menu_x, menu_y, menu_width,menu_height)

		header_font = pygame.font.SysFont('verdana',12,True)
		header = header_font.render(f"{'Name:':<15}{'Kills:':<15}{'Deaths:':<15}{'K/D:':>}",1,(0,0,0))
		
		text_font = pygame.font.SysFont('verdana',10)

		max_len_name = 10
		name = 'A'
		name = name[:max_len_name] #truncate if >10
		name_pos = 12+12-len(name) #text positions relative to a name of max len 10
		text = text_font.render(f"{name:<{name_pos}}{stats['kills']:<15}{stats['deaths']:<12}{stats['K/D']:>12}",1,(0,0,0))

		menu_img = pygame.Surface((menu_width,menu_height)).convert_alpha()
		menu_img.fill((200,200,200,150))
		win.blit(menu_img, (menu_x,menu_y))
		win.blit(header, (menu_x, menu_y))
		win.blit(text, (menu_x, menu_y+20))