import socket
import select

header_len = 10
server = "192.168.1.147"
port = 5555

server_sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reconnect using diff ports

server_sock.bind((server, port))
server_sock.listen()

sockets_list = [server_sock]

clients = {}

def receive_msg(client_socket):
	try:
		msg_header = client_socket.recv(header_len)

		if not len(msg_header): #client closed conn
			return False

		msg_len = int(msg_header.decode('utf-8'))
		return {'header': msg_header, "data":client_socket.recv(msg_len)}

	except: #aggressive closing by client
		return False

while True:
	#read list, write list and sockets to iterate on
	read_socks, _, exception_socks = select.select(sockets_list, [], sockets_list)

	for notified_socket in read_socks:
		if notified_socket == server_sock:
			client_sock, client_addr = server_sock.accept()

			user = receive_msg(client_sock)
			if user is False:
				continue

			sockets_list.append(client_sock)

			clients[client_sock] = user

			print(f"accepted new connection from {client_addr[0]}:{client_addr[1]} username: {user['data'].decode('utf-8')}")
		else:
			msg = receive_msg(notified_socket)
			if msg is False:
				print(f"Connection closed from {clients[notified_socket]['data'].decode('utf-8')}")
				sockets_list.remove(notified_socket)
				del clients[notified_socket]
				continue

			user = clients[notified_socket]
			print(f"received msg from {user['data'].decode('utf-8')}: {msg['data'].decode('utf-8')}")

			for client_sock in clients:
				if client_sock != notified_socket: #dont send back to sender
					client_sock.send(user['header'] + user['data'] + msg['header'] + msg['data'])

			for notified_socket in exception_socks:
				sockets_list.remove(notified_socket)
				del clients[notified_socket]