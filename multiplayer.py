from characters import Player
class Multiplayer:
	@staticmethod
	def get_player_data(ash, net, players):
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