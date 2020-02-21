import math
import config
class SnaptoGrid:
	'''we are using 10x10 grid squares so 
	snap the object widths and heights to the nearest 10'''
	@staticmethod
	def snap(n):
		'''round to nearest 5 or 10'''
		if config.grid_spacing == 5:	
			return int(round(n/5)*5)

		elif config.grid_spacing == 10:
			floor = (n//10) * 10
			ceil = math.ceil(n/10)*10

			return int(floor) if n-floor < 5 else int(ceil)	


	# @staticmethod
	# def snap(n):
	# 	#round to nearest 10
	# 	floor = (n//10) * 10
	# 	ceil = math.ceil(n/10)*10

	# 	return int(floor) if n-floor < 5 else int(ceil)