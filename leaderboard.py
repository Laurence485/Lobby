import sqlite3

class Leaderboard:
	def __init__(self):
		self.conn = sqlite3.connect('leaderboard.db') #leaderboard.db'

		self.c = self.conn.cursor()

	def create_leaderboard(self):
		with self.conn:
			self.c.execute("""CREATE TABLE leaderboard (
						name TEXT PRIMARY KEY,
						kills INT,
						deaths INT,
						kd DECIMAL (5, 2)
				)""")

	def insert_new_player(self, name):
		with self.conn:
			self.c.execute("SELECT 1 FROM leaderboard WHERE name = ?", (name,))

			entry = self.c.fetchone()

			if entry is None:
				self.c.execute("INSERT INTO leaderboard VALUES(?, ?, ?, ?)", (name,0,0,0.0,))

	def update_player(self, name,k,d,kd):
		with self.conn:
			self.c.execute("UPDATE leaderboard SET kills = ?, deaths = ?, kd = ? WHERE name= ?;",(k,d,kd,name,))

	def get_leaderboard(self):
		with self.conn:
			self.c.execute("SELECT * FROM leaderboard ORDER BY kills DESC LIMIT 10;")
			return self.c.fetchall()