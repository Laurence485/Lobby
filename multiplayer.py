from characters import Player
from map_generation import Map
from weapons import WeaponStatus

class Multiplayer:
	'''class containing functions checking data from the server'''
	@staticmethod
	def get_player_data(ash, net, players, bikes, mushrooms):
			'''get player data from server and map data to local player objects'''
			attrs = net.send(ash.attributes()) #return attributes of other players
			print((attrs))
			for i in range(len(players)):
				'''ith player should map to ith attribute on server as players are
				added in order which clients connect. If client DCs and reconnects, they are
				issued the same player id'''
				a = attrs[i] 

				#create new player instance if:
				#1) we haven't already created an instance
				#2) they have an ID (they are connected to server)
				if not players[i] and a['ID'] != None:
					print(f'{a["username"]} connected.')
					new_player = Player((a['x'],a['y']),a['ID'])
					players.append(new_player)
					print(len(players))

				#update player from server
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
					players[i].username = a['username']
					players[i].map = a['map']

					#change local map if the host has changed the map
					if players[i].ID == 0 and players[i].map!=ash.map:
						ash.map = players[i].map
						Map.load(net.maps[players[i].map])
						WeaponStatus.set_locations(bikes, mushrooms)

	@staticmethod
	def check_death_status(ash, players):
		'''check if we have died or if another player has been killed by us through ash.check_kill().
		call ash.die() and set our death and kill status accordingly.'''
		for p in players:
			if p:
				#another player killed us and we are not already dead
				if p.killed == ash.ID and not ash.dead:
					ash.die(p.username)
					ash.dead = True
				# #we've killed another player and they are dead so reset killed
				elif p.dead and ash.killed == p.ID:
					ash.killed = None
			
		#we are dead and no one else has killed us so reset dead
		if ash.dead and all(p.killed != ash.ID for p in players if p):
			ash.dead = False

