import socket
import pickle
#MAGIC NUMBERS

class Network:
	def __init__(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server = "192.168.1.147"
		self.port = 5555
		self.addr = (self.server, self.port)
		# self.position = self.connect()

	# def get_position(self):
	# 	return self.position

	def connect(self):
		try: #connect and send info back to validate
			self.client.connect(self.addr)
			return pickle.loads(self.client.recv(1024))
		except:
			pass

	def send(self, data):
		try:
			self.client.send(pickle.dumps(data))
			return pickle.loads(self.client.recv(1024))
		except socket.error as e:
			print(e)

