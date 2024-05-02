import string
from constants import REVERSE, Dir

class Movement:

	@classmethod
	def coords_to_index(cls, coords):
		if not isinstance(coords, str):
			coords = cls.index_to_coords(*coords)

		x, y = coords[0], coords[1:]
		x, y = string.ascii_lowercase.index(x), int(y)-1

		if x >= 8 and y >= 8: # >= i / Red
			x = 11 - x # = 4 - (x - 9) <=> lkji => abcd

		elif x >= 8 and 4 <= y <= 8: # Black
			x = x - 4 # ijkl => efgh 

		return x, y # x= lettre, y = chiffre

	@classmethod
	def index_to_coords(cls, x, y):
		if y <= 3:
			# White zone
			pass  # Don't change anything
		elif y <= 7:
			# Black zone
			if x <= 3:
				# White side
				pass  # Don't change anything
			else:
				# Red side
				x = x + 4  # efgh => ijkl
		else:
			# Red zone
			if x <= 3:
				# Black side
				x = 11 - x  # abcd => lkji
			else:
				# White side
				pass  # Don't change anything
	
		return ''.join((string.ascii_lowercase[x], str(y+1)))

	def get_straight_line(self, coords, direction, skipped_first=False):
		# Renvoie une liste de coordonnées dans une direction donnée
		# S'arrête lorsque l'on atteint un mur ou une autre pièce, en ignorant la première case

		# Check limits
		if not self.validate_coordinates(coords):
			# Could be invalid coordinate, but it can still be mapped to a correct one
			return []

		# Check cell
		x, y = self.coords_to_index(coords)
		if not skipped_first and self.board[y][x] is not None:
			return []

		next_cell = next(
			filter(
				lambda e: e[0] == direction, 
				self.get_adjacent(coords)), 
			[None, None]
		)[1]  # equivalent à dict(self.get_adjacent(x, y))[direction] mais un peu plus rapide

		if next_cell is None:
			return [coords]

		out = [coords] + self.get_straight_line(
			next_cell, direction, skipped_first=True
		)
		return out

	def get_adjacent(self, coords):
		if isinstance(coords, str):
			x, y = self.coords_to_index(coords)
		else:
			x, y = coords

		for dir, (dx, dy) in [(Dir.DOWN, (-1, 0)), (Dir.UP, (1, 0)), (Dir.RIGHT, (0, -1)), (Dir.LEFT, (0, 1))]:
			nx, ny = x+dx, y+dy

			# region: bounds

			if not (0 <= nx < 8):
				# Out of bounds
				continue
			
			if y == 0 and dy == -1:
				# Out of bounds, behind white
				continue

			if y == 7 and dy == 1:
				# Out of bounds, behind black
				continue

			if y == 11 and dy == 1:
				# Out of bounds, behind red
				continue

			# endregion

			# region: Red borders

			if y == 8 and dy == -1:
				# Red zone outer border
				if 4 <= x:
					# White side
					ny = 3
				else:
					# Black side
					nx, ny = 7-nx, 4

			if y >= 8:
				# Red zone inner border
				if x == 4 and dx == -1: # == e
					# White side
					nx = 8
				elif x == 8 and dx == 1:
					# Black side
					nx = 4

			# endregion

			# region: White border
			if y == 3 and x >= 4 and dy == 1:
				# Red side
				ny += 4

			# endregion

			# region: Black border
			if y == 4 and x >= 4 and dy == -1:
				# Red side
				ny = 8
				nx = 7-nx

			# endregion

			out = self.index_to_coords(nx, ny)
			yield (dir, out)

	def get_diagonal_line(self, coords, direction, origin=None):
		# Renvoie une liste de coordonnées dans une direction donnée, en diagonale
		# S'arrête lorsque l'on atteint un mur ou une autre pièce, en ignorant la première case
		
		if not isinstance(coords, str):
			coords = self.index_to_coords(*coords)

		# Check limits
		if not self.validate_coordinates(coords):
			# Could be invalid coordinate, but it can still be mapped to a correct one
			return []

		# Check cell
		if isinstance(self.board, list):
			b = self
		else:
			b = self.board

		if origin is not None and b[coords] is not None:
			return [coords]

		adj = dict(self.get_adjacent_diagonale(coords))
		if origin is not None:
			for dir, cells in adj.items():
				if origin in cells:
					break
			else:
				# wtf?
				raise Exception

			next_cells = adj.get(REVERSE[dir], [])
		else:
			next_cells = adj.get(direction, [])

		out = [coords]
		for next_cell in next_cells:
			out += self.get_diagonal_line(
				next_cell, None, coords
			)
		return out

	def get_adjacent_diagonale(self, coords):
		x, y = self.coords_to_index(coords)

		for dir, (dx, dy) in [
			(Dir.DOWN, (-1, 1)),
			(Dir.UP, (1, -1)),
			(Dir.LEFT, (1, 1)),
			(Dir.RIGHT, (-1, -1)),
		]:
			nx, ny = x + dx, y + dy

			# region: bounds

			if not (0 <= nx < 8):
				# Out of bounds
				continue

			if y == 0 and dy == -1:
				# Out of bounds, behind white
				continue

			if y == 7 and dy == 1:
				# Out of bounds, behind black
				continue

			if y == 11 and dy == 1:
				# Out of bounds, behind red
				continue

			# endregion

			# region: Center

			center = {3, 4, 7, 8}
			if {x, y, nx, ny} <= center:
				# Crossing the center

				if (x - y) % 4 == 0:
					# Gray cross
					cross = {"d4", "e9", "i5"} # Gray cross
				else:
					cross = {"e4", "d5", "i9"} # White cross

				yield (dir, list(cross - {coords}))

				continue

			# endregion

			# region: Red borders

			if y == 8 and dy == -1:
				# Red zone outer border
				if 4 <= x:
					# White side
					ny = 3
				else:
					# Black side
					nx, ny = 7 - nx, 4

			if y >= 8:
				# Red zone inner border
				if x == 4 and dx == -1:  # == e
					# White side
					nx = 8
				elif x == 8 and dx == 1:
					# Black side
					nx = 4

			# endregion

			# region: White border
			if y == 3 and x >= 4 and dy == 1:
				# Red side
				ny += 4

			# endregion

			# region: Black border
			if y == 4 and x >= 4 and dy == -1:
				# Red side
				ny = 8
				nx = 7 - nx

			# endregion

			out = self.index_to_coords(nx, ny)
			yield (dir, [out])

	def validate_coordinates(self, coords):
		# Check if coordinates are actually on the board
		# Returns bool

		if not isinstance(coords, str):
			coords = self.index_to_coords(*coords)

		x, y = coords[0], coords[1:]
		x, y = string.ascii_lowercase.index(x), int(y)-1

		if 0 <= x < 4:
			if 0 <= y < 8:
				return True

		elif x < 8:
			if 0 <= y < 4 or 8 <= y < 12:
				return True

		elif x < 12:
			if 4 <= y < 12:
				return True

		return False

	def is_check(self, src, dest):
		# TODO - Check all kind of possible movements (queen + knight?) around each king in case there is a check
		return False
