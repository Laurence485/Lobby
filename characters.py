import pygame
from snap_to_grid import SnaptoGrid
import config
from map_generation import Map
from random_node import RandomNode
from weapons import Pokeball
import config

class Character:
	'''setup common characteristics of movable characters 
	---> player, npc, pathfinder characters etc'''
	def __init__(self,x, y, vel, l1,l2,r1,r2,d1,d2,u1,u2, width=15, height=19):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self._vel = vel #non-changing reference
		self.vel = vel
		self.walk_count = 0
		self.hitbox = (self.x, self.y, self.width, self.height)
		self.walk_left = [pygame.image.load(f'sprites/{l1}').convert_alpha(), pygame.image.load(f'sprites/{l2}').convert_alpha()]
		self.walk_right = [pygame.image.load(f'sprites/{r1}').convert_alpha(), pygame.image.load(f'sprites/{r2}').convert_alpha()]
		self.walk_down = [pygame.image.load(f'sprites/{d1}').convert_alpha(), pygame.image.load(f'sprites/{d2}').convert_alpha()]
		self.walk_up = [pygame.image.load(f'sprites/{u1}').convert_alpha(), pygame.image.load(f'sprites/{u2}').convert_alpha()]
		self.hit_slow = False #slowed movement area: grass/water
		self.mushroom = False
		self.stats = {
		'kills':0,
		'deaths':0,
		'K/D': 0
		}
		self.ID = None
		self.killed = None
		self.dead = False

	def walk_animation(self, direction, win):
		if not self.hit_slow:
			if not self.mushroom:
				win.blit(direction[self.walk_count//2], (self.x,self.y))
			else: 
				self.enlarge(direction[self.walk_count//2], win)
		else: #we are in grass/water
			if not self.mushroom: #chop off bottom of player
				win.blit(direction[self.walk_count//2], (self.x,self.y), (0,0,SnaptoGrid.snap(self.width),self.height-self.height//4))
			else: 
				self.enlarge(direction[self.walk_count//2], win)

		self.walk_count += 1

	def stand_sprite(self, direction, win):
		if not self.hit_slow:
			if not self.mushroom:
				win.blit(direction, (self.x,self.y))
			else:
				self.enlarge(direction, win)
		else:
			if not self.mushroom:
				win.blit(direction, (self.x,self.y), (0,0,SnaptoGrid.snap(self.width),self.height-self.height//4))
			else:
				self.enlarge(direction, win)

	def enlarge(self, direction, win):
		'''scale up the player by 2x'''
		win.blit(pygame.transform.scale2x(direction), (self.x,self.y))

class Player(Character):
	def __init__(self,xy=(50,70), ID=0, username='Noob'):
		super().__init__(xy[0],xy[1], config.player_vel, f'player {ID}/left2.png',f'player {ID}/left3.png',f'player {ID}/right2.png',f'player {ID}/right3.png',f'player {ID}/down2.png', f'player {ID}/down3.png', f'player {ID}/up2.png', f'player {ID}/up3.png')
		self.stand_left = pygame.image.load(f'sprites/player {ID}/left1.png').convert_alpha()
		self.stand_right = pygame.image.load(f'sprites/player {ID}/right1.png').convert_alpha()
		self.stand_up = pygame.image.load(f'sprites/player {ID}/up1.png').convert_alpha()
		self.stand_down = pygame.image.load(f'sprites/player {ID}/down1.png').convert_alpha()
		self.bike_left = [pygame.image.load(f'sprites/player {ID}/bike_left2.png').convert_alpha(),pygame.image.load(f'sprites/player {ID}/bike_left3.png').convert_alpha()]
		self.bike_right = [pygame.image.load(f'sprites/player {ID}/bike_right2.png').convert_alpha(),pygame.image.load(f'sprites/player {ID}/bike_right3.png').convert_alpha()]
		self.bike_up = [pygame.image.load(f'sprites/player {ID}/bike_up2.png').convert_alpha(), pygame.image.load(f'sprites/player {ID}/bike_up3.png').convert_alpha()]
		self.bike_down = [pygame.image.load(f'sprites/player {ID}/bike_down2.png').convert_alpha(), pygame.image.load(f'sprites/player {ID}/bike_down3.png').convert_alpha()]
		self.stand_left_bike = pygame.image.load(f'sprites/player {ID}/bike_left1.png').convert_alpha()
		self.stand_right_bike = pygame.image.load(f'sprites/player {ID}/bike_right1.png').convert_alpha()
		self.stand_up_bike = pygame.image.load(f'sprites/player {ID}/bike_up1.png').convert_alpha()
		self.stand_down_bike = pygame.image.load(f'sprites/player {ID}/bike_down1.png').convert_alpha()
		self.left = False
		self.right = False
		self.up = False
		self.down = True
		self.standing = True
		self.inventory = []
		self.bullet_interval = 0
		self.space_up = False
		self.direction = 'D' #use to track bullet shooting direction
		self.bike = False
		self.bike_vel = config.bike_vel
		self.start_bike_ticks = 0 #bike timer
		self.start_mushroom_ticks = 0 #enlarged size timer
		self.username = username

	#we send these attributes from the server to the client for multiplayer
	def attributes(self):
		attrs = {
		'x':self.x,
		'y':self.y,
		'L':self.left,
		'R':self.right,
		'U':self.up,
		'D':self.down,
		'standing':self.standing,
		'walk count':self.walk_count,
		'hit slow':self.hit_slow, #we are in a reduced movement area...chop bottom off
		'inventory': [(bullet.x, bullet.y, bullet._direction, bullet._start_x, bullet._start_y) for bullet in self.inventory],
		'bike': self.bike,
		'mushroom': self.mushroom,
		'stats': self.stats,
		'killed': self.killed,
		'dead':self.dead,
		'ID':self.ID,
		'username':self.username
		}
		return attrs

	#draw ash onto the screen
	#animate directions
	def draw(self, win):
		if self.walk_count + 1 > 4:
			self.walk_count = 0
		if not self.standing:
			if self.right:
				if self.bike:
					self.walk_animation(self.bike_right, win)
				else: self.walk_animation(self.walk_right, win)
			elif self.left:
				if self.bike:
					self.walk_animation(self.bike_left, win)
				else: self.walk_animation(self.walk_left, win)
			elif self.up:
				if self.bike:
					self.walk_animation(self.bike_up, win)
				else: self.walk_animation(self.walk_up, win)
			elif self.down:
				if self.bike:
					self.walk_animation(self.bike_down, win)
				else: self.walk_animation(self.walk_down, win)
		else:
			if self.right:
				if self.bike:
					self.stand_sprite(self.stand_right_bike,win)
				else: self.stand_sprite(self.stand_right,win)
			elif self.left:
				if self.bike:
					self.stand_sprite(self.stand_left_bike,win)
				else: self.stand_sprite(self.stand_left,win)
			elif self.up:
				if self.bike:
					self.stand_sprite(self.stand_up_bike,win)
				else: self.stand_sprite(self.stand_up,win)
			elif self.down:	
				if self.bike:
					self.stand_sprite(self.stand_down_bike,win)
				else: self.stand_sprite(self.stand_down,win)

		#simple timer for shooting
		self.bullet_interval += 1
		if self.bullet_interval > 5: self.bullet_interval = 0

		#update the hitbox every frame
		# self.hitbox = (self.x, self.y, self.width, self.height)
		# pygame.draw.rect(win, (255,0,0), self.hitbox,2)

	def move(self, collision_zone, movement_cost_area, bike=None, mushroom=None):
		keys = pygame.key.get_pressed()

		#simple collision detection:
		#check if player (x,y) is in the set of object coordinates
		#given player dimensions (w=15,h=19) setting +/- grid spacing (1 square) works ok
		bounds = (SnaptoGrid.snap(self.x),SnaptoGrid.snap(self.y+config.grid_spacing))
		hit_wall = True if bounds in collision_zone else False
		self.hit_slow = True if bounds in movement_cost_area else False

		if self.hit_slow:
			#slow movement speed
			if not self.mushroom:
				speed = self._vel if not self.bike else self.bike_vel
				slow_speed = speed - movement_cost_area[bounds]
				self.vel = slow_speed
			else: 
				self.vel = self._vel if not self.bike else self.bike_vel

			#found a bike
			if bounds == bike.hidden_loc and not self.bike:
				self.bike = True
				self.start_bike_ticks = pygame.time.get_ticks() #start bike timer 15s
				bike.new_location(RandomNode(Map.movement_cost_area).node)
				print('found bike!')
				self.snap()

			#found a mushroom - 2x size
			if bounds == mushroom.hidden_loc and not self.mushroom:
				self.mushroom = True
				self.width *= 2
				self.height *= 2
				self.start_mushroom_ticks = pygame.time.get_ticks() #start bike timer 15s
				mushroom.new_location(RandomNode(Map.movement_cost_area).node)
				print('found mushroom!')
				self.snap()
		else:
			self.vel = self._vel if not self.bike else self.bike_vel
			#we must re-snap to grid as (x,y) no longer to nearest square
			self.snap()

		if not hit_wall:
			if self.space_up and self.bullet_interval == 0 :
				self.space_up = False
				self.inventory.append(Pokeball(self.x,self.y,self.width,self.height,self.direction, self.vel))
			if keys[pygame.K_LEFT]:
				self.x -= self.vel
				self.left = True
				self.right = False
				self.up = False
				self.down = False
				self.standing = False
				self.direction = 'L'
			elif keys[pygame.K_RIGHT]:
				self.x += self.vel
				self.left = False
				self.right = True
				self.up = False
				self.down = False
				self.standing = False
				self.direction = 'R'
			elif keys[pygame.K_UP]:
				self.y -= self.vel
				self.left = False
				self.right = False
				self.up = True
				self.down = False
				self.standing = False
				self.direction = 'U'
			elif keys[pygame.K_DOWN]:
				self.y += self.vel
				self.left = False
				self.right = False
				self.up = False
				self.down = True
				self.standing = False
				self.direction = 'D'
			else:
				self.standing = True
				self.walk_count = 0
		else: #collision
			if self.left: self.x += self.vel
			elif self.right: self.x -= self.vel
			elif self.up: self.y += self.vel
			elif self.down: self.y -= self.vel

		#prevent movement beyond the screen
		if self.x > config.window_height-config.grid_spacing: #we would normally use self.width but as 10px grid spacing we want to be able to navigate the rightmost square
			self.x -= self.vel
		elif self.x < 0:
			self.x += self.vel
		elif self.y < 0:
			self.y += self.vel
		elif self.y > config.window_height-self.height:
			self.y -= self.vel

	def draw_bullet(self, win, bullet):
		bullet.draw(win)
		# print((bullet.x,bullet.y), (self.x,self.y))
		if bullet._direction == 'L':
			bullet.x -= bullet.vel
		elif bullet._direction == 'R' :
			bullet.x += bullet.vel
		elif bullet._direction == 'U':
			bullet.y -= bullet.vel
		elif bullet._direction == 'D':
			bullet.y += bullet.vel
		#delete bullets after distance of 150px
		if bullet.distance() > 150: 
			self.inventory.pop(self.inventory.index(bullet))

	def check_kill(self, bullet, enemy):
		'''check kill (collision) by pokeball'''
		# sq = config.grid_spacing
		#adding 1 square padding to enemy bounds lets us attack when we are 1sq away
		if bullet.x + bullet.width >= enemy.x and bullet.x <= enemy.x + enemy.width:
			if bullet.y + bullet.height >= enemy.y and bullet.y <= enemy.y + enemy.height:
				try: #bullet might already be removed from distance check
					self.inventory.pop(self.inventory.index(bullet))
					if not enemy.mushroom:
						print(f'You killed {enemy.username}!')
						self.killed = enemy.ID
						self.kill()
				except: 
					print('Warning: already removed bullet from distance check.')


	def check_trample(self, enemy):
		'''check if we've trampled someone with double size'''
		if self.mushroom:
			if enemy.x + enemy.width >= self.x and enemy.x <= self.x + self.width:
				if enemy.y + enemy.height >= self.y and enemy.y <= self.y + self.height:
					#check None to avoid multiple kills of same player for 1 hit before server updates
					if not enemy.mushroom and self.killed == None:
						print(f'You trampled {enemy.username}!')
						self.killed = enemy.ID
						self.kill()
						

	def kill(self):
		'''update kill stats with +1'''
		self.stats['kills'] += 1
		self.stats['K/D'] = self.KD_ratio()

	def die(self, username):
		'''update death stats with +1 and reset player attributes'''
		self.stats['deaths'] += 1
		self.stats['K/D'] = self.KD_ratio()
		respawn = RandomNode(Map.nodes).node
		print(f"You were killed by {username}...respawning at {respawn}")
		self.x,self.y = respawn
		self.left = False
		self.right = False
		self.up = False
		self.down = True
		self.standing = True
		self.inventory = []
		self.bullet_interval = 0
		self.space_up = False
		self.direction = 'D'
		self.walk_count = 0
		self.vel = config.player_vel
		self.hit_slow = False

	def KD_ratio(self):
		return round(self.stats['kills'] / self.stats['deaths'], 2) if self.stats['deaths'] > 0 else 'infinity'

	def snap(self):
		'''snap player x,y to grid'''
		self.x, self.y = SnaptoGrid.snap(self.x), SnaptoGrid.snap(self.y)


class Npc(Character):
	'''Npc character moves back and forth between specific coordinates'''
	def __init__(self, x, y, end):
		super().__init__(x,y,config.player_vel,'player2/left2.png','player2/left3.png','player2/right2.png','player2/right3.png','player2/down2.png', 'player2/down3.png', 'player2/up2.png', 'player2/up3.png')
		self.end = end
		self.path = (self.x, self.end)
		
	def draw(self, win):
		self.move()
		if self.walk_count + 1 > 4:
			self.walk_count = 0
		if self.vel > 0:
			self.walk_animation(self.walk_right, win)
		else:
			self.walk_animation(self.walk_left, win)

	def move(self):
		if self.vel > 0: #moving right
			if self.x + self.vel < self.path[1]:
				self.x += self.vel
			else:
				self.vel = self.vel * -1 #switch direction
				self.walk_count = 0
		else: #moving left
			if self.x - self.vel > self.path[0]:
				self.x += self.vel
			else:
				self.vel = self.vel * -1
				self.walk_count = 0

# print(Player.__mro__) 
# print(Character.__doc__)