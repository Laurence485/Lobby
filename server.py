#use socket and threading to handle connections
import socket
from _thread import *
import sys
import pickle

server = "192.168.1.147"
port = 5555

s  = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPV4 adress, TCP

#bind server and port to socket
try:
	s.bind((server, port))
except socket.error as e:
	str(e)

s.listen(2) #listen for connections - 2 connections to server only for now
print("Server started, waiting for connection...")

attributes = {
'x':0,
'y':0,
'L':False,
'R':False,
'U':False,
'D':True,
'standing':True,
'walk count':0,
}
players = [attributes, attributes]

def client(conn, player):
	conn.send(pickle.dumps(players[player]))
	reply = ""
	while True: #continously run whilst client still connected
		try:
			data = pickle.loads(conn.recv(1024)) #bits to receive
			players[player] = data

			if not data:
				print('Disconnected from server.')
				break
			else:
				if player == 1:
					reply = players[0]
				else:
					reply = players[1]

				print("Received: ", data)
				print("Sending: ", reply)

			conn.sendall(pickle.dumps(reply)) 
		except:
			break

	print('connection dropped.')
	conn.close()

player = 0 #increment when we make a new conn
while True: #continuously look for connections, if found, start new thread
	conn, addr = s.accept()
	print("Connected to:", addr)

	start_new_thread(client, (conn, player))
	player += 1