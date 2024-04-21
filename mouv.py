from itertools import product
import string
from constants import BOARD_SIZE, REVERSE, START_ROWS, Dir


class Movement:

	def __init__(self):

		self.mouvement_possible = {
			"K": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],
			"Q": [
				(i, j)
				for i in range(-7, 8)
				for j in range(-7, 8)
				if (i != 0 or j != 0) and (i == 0 or j == 0 or abs(i) == abs(j))
			],
			"R": [(i, 0) for i in range(-7, 8)] + [(0, j) for j in range(-7, 8)],
			"B": [
				(i, j)
				for i in range(-7, 8)
				for j in range(-7, 8)
				if abs(i) == abs(j) and i != 0
			],
			"N": [
				(-2, 1),
				(-1, 2),
				(1, 2),
				(2, 1),
				(2, -1),
				(1, -2),
				(-1, -2),
				(-2, -1),
			],
			"P": [(1, 0), (1, 1), (1, -1)],
		}

	def get_type(self, coord):
		"""
		Parameters
		----------
		board : La liste représentant le plateau du jeu

		Returns
		-------
		Le type de pièce qu'on a séléctionné

		"""
		x, y = self.coords_to_index(coord)
		if self.board[y][x] != None:
			return self.board[y][x].type
		else:
			return None

	def mouvement_pion_possible(self, coord):
		mouvement_dispo = []
		case_adjcante = dict(self.get_adjacent(coord))
		x, y = self.coords_to_index(coord)

		if self.board[y][x] != None and self.board[y][x].team == "W":
			x, y = self.coords_to_index(case_adjcante[Dir.RIGHT])

			if self.board[y][x] == None and (x > -1 and x < 12) and (y > -1 and y < 12):
				mouvement_dispo.append(case_adjcante[Dir.RIGHT])

				case_adjcante3 = dict(self.get_adjacent(case_adjcante[Dir.RIGHT]))
				x, y = self.coords_to_index(case_adjcante3[Dir.RIGHT])

				if (
					self.board[y][x] == None
					and (x > -1 and x < 12)
					and (y > -1 and y < 12)
				):
					mouvement_dispo.append(case_adjcante3[Dir.RIGHT])

			case_adjcante2 = dict(self.get_adjacent(case_adjcante[Dir.RIGHT]))

			for direction in [Dir.UP, Dir.DOWN]:
				x, y = self.coords_to_index(case_adjcante2[direction])
				if (
					self.board[y][x] != None
					and (x > -1 and x < 12)
					and (y > -1 and y < 12)
				):
					mouvement_dispo.append(case_adjcante2[direction])

			return mouvement_dispo

		elif self.board[y][x] != None and self.board[y][x].team == "R":
			x, y = self.coords_to_index(case_adjcante[Dir.LEFT])
			if self.board[y][x] == None and (x > -1 and x < 12) and (y > -1 and y < 12):
				mouvement_dispo.append(case_adjcante[Dir.LEFT])
				case_adjcante3 = dict(self.get_adjacent(case_adjcante[Dir.LEFT]))
				x, y = self.coords_to_index(case_adjcante3[Dir.LEFT])
				if (
					self.board[y][x] == None
					and (x > -1 and x < 12)
					and (y > -1 and y < 12)
				):
					mouvement_dispo.append(case_adjcante3[Dir.LEFT])

			case_adjcante2 = dict(self.get_adjacent(case_adjcante[Dir.LEFT]))
			x, y = self.coords_to_index(case_adjcante2[Dir.UP])
			if self.board[y][x] != None and (x > -1 and x < 12) and (y > -1 and y < 12):
				mouvement_dispo.append(case_adjcante2[Dir.UP])
			x, y = self.coords_to_index(case_adjcante2[Dir.DOWN])
			if self.board[y][x] != None and (x > -1 and x < 12) and (y > -1 and y < 12):
				mouvement_dispo.append(case_adjcante2[Dir.DOWN])
			return mouvement_dispo

		else:
			x, y = self.coords_to_index(case_adjcante[Dir.LEFT])
			if self.board[y][x] == None and (x > -1 and x < 12) and (y > -1 and y < 12):
				mouvement_dispo.append(case_adjcante[Dir.LEFT])
				print(mouvement_dispo)
				case_adjcante3 = dict(self.get_adjacent(case_adjcante[Dir.LEFT]))
				print(case_adjcante3)
				x, y = self.coords_to_index(case_adjcante3[Dir.LEFT])
				if (
					self.board[y][x] == None
					and (x > -1 and x < 12)
					and (y > -1 and y < 12)
				):
					mouvement_dispo.append(case_adjcante3[Dir.LEFT])

			case_adjcante2 = dict(self.get_adjacent(case_adjcante[Dir.LEFT]))
			x, y = self.coords_to_index(case_adjcante2[Dir.UP])
			if self.board[y][x] != None and (x > -1 and x < 12) and (y > -1 and y < 12):
				mouvement_dispo.append(case_adjcante2[Dir.UP])
			x, y = self.coords_to_index(case_adjcante2[Dir.DOWN])
			if self.board[y][x] != None and (x > -1 and x < 12) and (y > -1 and y < 12):
				mouvement_dispo.append(case_adjcante2[Dir.DOWN])
			return mouvement_dispo

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
		x, y = self.coords_to_index(coords)
		for dir, (dx, dy) in [
			(Dir.DOWN, (-1, 0)),
			(Dir.UP, (1, 0)),
			(Dir.LEFT, (0, 1)),
			(Dir.RIGHT, (0, -1)),
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
			yield (dir, out)

	def get_diagonal_line(self, coords, direction, origin=None):
		# Renvoie une liste de coordonnées dans une direction donnée, en diagonale
		# S'arrête lorsque l'on atteint un mur ou une autre pièce, en ignorant la première case
		
		# Check limits
		if not self.validate_coordinates(coords):
			# Could be invalid coordinate, but it can still be mapped to a correct one
			return []

		# Check cell
		x, y = self.coords_to_index(coords)
		if origin is not None and self.board[y][x] is not None:
			return []

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
