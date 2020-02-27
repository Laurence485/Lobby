import socket
import pickle
import config

class Network:
	def __init__(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.HOST = config.HOST
		self.PORT = config.PORT
		self.addr = (self.HOST, self.PORT)
		self.data = self.connect()

	def connect(self):
		try: #connect and get player ID
			self.client.connect(self.addr)
			self.maps, self.playerID = pickle.loads(self.client.recv(config.buffer_size))
		except:
			print("couldn't connect to host.")

	def send(self, data):
		try:
			self.client.send(pickle.dumps(data))
			return pickle.loads(self.client.recv(config.buffer_size))
		except socket.error as e:
			print(e)

