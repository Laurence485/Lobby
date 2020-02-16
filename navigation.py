class Navigation:
	'''traverse a list of coordinates identified by an algorithim'''
	def bfs(self, path, bot):
		print(f'\n must traverse {len(path)} squares to reach target')
		coordinates = iter(path)
		
		bot.right = False