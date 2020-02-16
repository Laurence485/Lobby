import socket
import select
import errno
import sys

header_len = 10
server = "192.168.1.147"
port = 5555

my_username = input("Username: ")
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((server, port))
client_sock.setblocking(False)

username = my_username.encode("utf-8")
username_header = f"{len(username):<{header_len}}".encode('utf-8')

client_sock.send(username_header + username)

while True:
	msg = input(f"{my_username} > ")
	if msg:
		msg = msg.encode("utf-8")
		msg_header = f"{len(msg):<{header_len}}".encode('utf-8')
		client_sock.send(msg_header + msg)

	try: #receive msgs until error
		while True:
			username_header = client_sock.recv(header_len)
			if not len(username_header):
				print("connection closed by server")
				sys.exit()

			username_len = int(username_header.decode("utf-8").strip())
			username = client_sock.recv(username_len).decode('utf-8')

			msg_header = client_sock.recv(header_len)
			msg_len = int(msg_header.decode('utf-8').strip())
			msg = client_sock.recv(msg_len).decode('utf-8')

			print(f"{username} > {msg}")

	except IOError as e:
		if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
			print('reading error', str(e))
			sys.exit()
		continue

	except Exception as e:
		print('general error!', str(e))
		sys.exit()
