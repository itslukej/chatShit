import socket, threading, random, string

clients = []

host = ""
port = 8094

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(4)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

motd = """Welcome to chatShit!
Your current nickname is {0}, you can change it by doing "nick <nickname>".
You can also quit by doing "quit".
Have fun!
"""

def send_message(data):
	for client in clients:
		client.socket.send(data.encode())

def send_daemon(message):
	formatted = "<chatShitD> {0}\r\n".format(message)
	send_message(formatted)


class Client(threading.Thread):
	buffer = []
	def __init__(self, connection_info):
		threading.Thread.__init__(self)
		self.daemon = True
		self.socket, self.address = connection_info
		self.nickname = "Guest"+random.choice(string.ascii_uppercase)
		self.socket.send(motd.format(self.nickname).encode())

	def recv(self):
		self.buffer= ""
		while not self.buffer.endswith("\r\n"):
			self.buffer += self.socket.recv(1024).decode("utf-8", errors="replace")
		self.buffer = self.buffer.strip().split("\r\n")
		return self.buffer

	def run(self):
		clients.append(self)
		send_daemon("{0} has joined.".format(self.nickname))
		while True:
			data = self.recv()
			for line in data:
				if len(line) == 0:
					continue

				formatted = "<{0}> {1}\r\n".format(self.nickname, line)
				send_message(formatted)

				if line.startswith("nick "):
					new_nickname = line.split(" ")[1]
					if new_nickname in [client.nickname for client in clients]:
						send_daemon("Nickname is already in use.")
					else:
						send_daemon("{0} is now known as {1}.".format(self.nickname, new_nickname))
						self.nickname = new_nickname

				if line == "quit":
					send_daemon("{0} has left.".format(self.nickname))
					self.socket.close()
					clients.remove(self)
					break



try:
	while True:
		Client(s.accept()).start()
except:
	s.close()
