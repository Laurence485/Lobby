import socket
import pickle
#MAGIC NUMBERS

class Network:
	def __init__(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.HOST = "192.168.1.147"
		self.PORT = 5555
		self.addr = (self.HOST, self.PORT)
		self.data = self.connect()

	def get_data(self):
		return self.data

	def connect(self):
		try: #connect and send info back to validate
			self.client.connect(self.addr)
			self.playerID = pickle.loads(self.client.recv(1024))
			# return pickle.loads(self.client.recv(1024))
		except:
			pass

	def send(self, data):
		try:
			self.client.send(pickle.dumps(data))
			return pickle.loads(self.client.recv(2048))
		except socket.error as e:
			print(e)

