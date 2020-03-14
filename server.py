#use socket and threading to handle connections
import socket
from _thread import *
import pickle
import config
from random import shuffle
from leaderboard import Leaderboard

HOST = config.HOST
PORT = config.PORT
buffer_size = config.buffer_size
maps = config.maps
shuffle(maps)

attributes = {
'x':0,
'y':0,
'L':False,
'R':False,
'U':False,
'D':True,
'standing':True,
'walk count':0,
'hit slow': False,
'inventory': [],
'bike': False,
'mushroom': False,
'stats': {
	'kills':0,
	'deaths':0,
	'K/D': 0
	},
'killed': None,
'dead': False,
'ID':None,
'username':'Noob',
'map': 0
}
players = [attributes]*config.num_players


def client(conn, player):
	with conn:
		#init game with map, player ID and start time form server
		conn.send(pickle.dumps((maps, player)))

		db = Leaderboard()

		#add player to leaderboard db if not already there
		username = pickle.loads(conn.recv(config.buffer_size))
		db.insert_new_player(username)

		print(db.get_leaderboard())

		# db.insert_new_player(players[])
		while True: #continously run whilst client still connected
			try:
				data = pickle.loads(conn.recv(config.buffer_size)) #received player attrs

				stats = list(players[player]['stats'].values())

				#a players stats have been updated, update the leaderboard db
				if any(list(data['stats'].values())[i] != stats[i] for i in range(len(stats))):
					kills = data['stats']['kills']
					deaths = data['stats']['deaths']
					kd = data['stats']['K/D']

					db.update_player(data['username'],kills,deaths,kd)

					print('leaderboard updated.')

				players[player] = data

				if not data:
					print('Disconnected from server.')
					break
				else:
					#slice out this player and return other players only, or we could do a deepcopy
					reply = (players[:player]+players[player+1:])

				conn.sendall(pickle.dumps(reply)) 
			except:
				break
		current_player = players[player]['username']
		print(f'connection dropped ({current_player}, ID:{player}).')
		
		#player DCed so reset to defaults and add to DC list so we can re-add if they re-connect
		players[player] = attributes
		DC.append(player)

DC = [] #disconnected player IDs
player = 0 #player ID
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #IPV4 adress, TCP

	s.bind((HOST, PORT))
	s.listen(10) #listen for up to 10 connections
	print("Server started, waiting for connection...")

	while True: #continuously look for connections, if found, start new thread
		conn, addr = s.accept()
		print("Connected by:", addr)
		if len(DC):
			DC_player = DC.pop()
			start_new_thread(client, (conn, DC_player))
		else:
			start_new_thread(client, (conn, player))
			player += 1