import config


class centerItem:
	'''center item on screen - center along the horiziontal axis by default'''
	@staticmethod
	def center(item_dimension, axis='x'):
		window_width = config.window_width
		window_height = config.window_height

		return window_width//2 - item_dimension//2 if axis == 'x' else window_height//2 - item_dimension//2


