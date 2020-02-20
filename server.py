#use socket and threading to handle connections
import socket
from _thread import *
import pickle

HOST = "192.168.1.147"
PORT = 5555

attributes = {
'x':0,
'y':0,
'L':False,
'R':False,
'U':False,
'D':True,
'standing':True,
'walk count':0,
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
'ID':None
}
players = [attributes, attributes]

def client(conn, player):
	with conn:
		conn.send(pickle.dumps(player)) #send player ID
		# reply = ""
		while True: #continously run whilst client still connected
			try:
				data = pickle.loads(conn.recv(2048)) #bits to receive
				players[player] = data

				if not data:
					print('Disconnected from server.')
					break
				else:
					if player == 1:
						reply = players[0]
					else:
						reply = players[1]

					# print("Received: ", data)
					# print("Sending: ", reply)
				conn.sendall(pickle.dumps(reply)) 
			except:
				break

		print('connection dropped.')


player = 0 #player ID
num_players = 0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #IPV4 adress, TCP

	s.bind((HOST, PORT))
	s.listen(10) #listen for up to 10 connections
	print("Server started, waiting for connection...")

	while True: #continuously look for connections, if found, start new thread
		conn, addr = s.accept()
		print("Connected by:", addr)

		start_new_thread(client, (conn, player))
		player += 1