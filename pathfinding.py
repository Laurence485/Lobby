from queue import Queue
from queue import PriorityQueue
import config
import time
from snap_to_grid import SnaptoGrid

class Pathfinding:
	'''set up grid, pathfinding algorithms'''
	def __init__(self, nodes, weights):
		self.nodes = nodes #all available movement positions (objs are removed from here in map generation)
		self.square = config.grid_spacing
		self.weights = weights

	def compute_all_paths(self,start_x,start_y,end_x,end_y):
		'''use mouse to select path endpoint and compute routes for BFS, DA, A*'''
		target_x = SnaptoGrid.snap(end_x)
		target_y = SnaptoGrid.snap(end_y)
		print(f'starting route to ({target_x},{target_y})')
		bfs_time = time.time()
		bfs_route = self.breadth_first_search((start_x,start_y), (target_x,target_y))
		print(f'BFS took {round(time.time() - bfs_time, 4)} seconds')
		da_time = time.time()
		da_route = self.dijkstra_search((start_x,start_y), (target_x,target_y))
		print(f'DA took {round(time.time() - da_time, 4)} seconds')
		a_star_time = time.time()
		a_star_route = self.dijkstra_search((start_x,start_y), (target_x,target_y), True)
		print(f'A* took {round(time.time() - a_star_time, 4)} seconds')

		return bfs_route, da_route, a_star_route

	#relative cost for moving on diff sqaures. Normal = 1, grass = 2, water = 5
	def movement_cost(self, node):
		return self.weights.get(node, 0)

	#heuristic is just the straight line distance between the end (x,y) and (x,y) of a possible next node
	#A* algorithim seeks to minimise this by adding it as a cost to Dikjstra's Algorithm
	def heuristic(self, end, next_node):
		(x1, y1) = end
		(x2, y2) = next_node
		return abs(x1 - x2) + abs(y1 - y2)

	def neighbours(self, node):
		#East, South, West, North
		dirs = [[self.square, 0], [0, self.square], [-self.square, 0], [0, -self.square]]
		result = []
		for dir in dirs:
			neighbour = (node[0] + dir[0], node[1] + dir[1])
			if neighbour in self.nodes: 
				result.append(neighbour)		
		return result

	def breadth_first_search(self, start, end):
		print('computing BFS route...')
		positions = Queue()
		positions.put(start) #enqueue start
		previous_positions = {}
		previous_positions[start] = None

		while not positions.empty():
			current_pos = positions.get()
			
			if current_pos == end: #found end, stop searching
				break

			for next_pos in self.neighbours(current_pos):
				if next_pos not in previous_positions:
					positions.put(next_pos)
					previous_positions[next_pos] = current_pos

		return self.get_path_back(start, end, previous_positions)

	def dijkstra_search(self, start, end, a_star=False):
		print(f'computing {"Dijkstra" if not a_star else "A*"} route...')
		positions = PriorityQueue()
		positions.put(start, 0)
		previous_positions = {}
		previous_positions[start] = None
		cost_so_far = {}
		cost_so_far[start] = 0

		while not positions.empty():
			current_pos = positions.get()

			if current_pos == end:
				break

			for next_pos in self.neighbours(current_pos):
				new_cost = cost_so_far[current_pos] + self.movement_cost(next_pos)
				#havnt calculated cost for next pos or found a better route
				if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
					cost_so_far[next_pos] = new_cost
					priority = new_cost + self.heuristic(end, next_pos) if a_star else new_cost
					positions.put(next_pos, priority)
					previous_positions[next_pos] = current_pos

		return self.get_path_back(start, end, previous_positions)


	#reverse the path from end to start so we can map it
	def get_path_back(self, start, end, previous_positions):
		path = []
		path_back = end
		while path_back != start:
			path.append(path_back)
			path_back = previous_positions[path_back]
		path.reverse()

		return path