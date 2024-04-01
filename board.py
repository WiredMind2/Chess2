import string
from constants import BOARD_SIZE, START_ROWS


class Board:
	"""Représente le plateau de jeu, avec les positions de chaque pion.
	"""
	def __init__(self):
		self.reset()

	def reset(self):
		self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(int(BOARD_SIZE * 1.5))] # Number, then letter -> /!\ reversed

		# White
		for i, row in enumerate(START_ROWS):
			for j, p in enumerate(row):
				self.board[i][j] = (p, 'W')

		# Black and red, reversed
		for start, team in [(7, 'B'), (11, 'R')]:
			for i, row in enumerate(START_ROWS):
				for j, p in enumerate(row):
					self.board[start - i][j] = (p, team)

	@classmethod
	def coords_to_index(cls, coords):
		x, y = coords[0], coords[1:]
		x, y = string.ascii_lowercase.index(x), int(y)-1

		if x >= 8 and y >= 8: # >= i / Red
			x = 11 - x # = 4 - (x - 9) <=> lkji => abcd

		elif x >= 8 and 4 <= y <= 8: # Black
			x = x - 4 # ijkl => efgh

		return x, y

	@classmethod
	def index_to_coords(cls, x, y):
		if y <= 3:
			# White zone
			pass # Don't change anything
		elif y <= 7:
			# Black zone
			if x <= 3:
				# White side
				pass # Don't change anything
			else:
				# Red side
				x = x + 4 # efgh => ijkl
		else:
			# Red zone
			if x <= 3:
				# Black side
				x = 11 - x # abcd => lkji
			else:
				# White side
				pass # Don't change anything
		
		return ''.join((string.ascii_lowercase[x], str(y+1)))

	def __getitem__(self, coords):
		""" val = dico['e5'] """
		
		x, y = self.coords_to_index(coords)
		return self.board[y][x]

	def __setitem__(self, coords, value):
		""" dico['e5'] = 'K' """
		x, y = self.coords_to_index(coords)
		self.board[y][x] = value

	def get_adjacent(self, coords):
		x, y = self.coords_to_index(coords)
		for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
			nx, ny = x+dx, y+dy

			# region: bounds
   
			if not (0 <= x < 8):
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
			yield out


if __name__ == '__main__':
	b = Board()
	assert b.coords_to_index('e8') == b.coords_to_index('i8')
	assert b.coords_to_index('i9') == b.coords_to_index('d9')
	assert b.coords_to_index('a9') == b.coords_to_index('l9')
	assert set(b.get_adjacent('i5')) == {'d5', 'j5', 'i9', 'i6'}
	assert set(b.get_adjacent('i9')) == {'i10', 'j9', 'e9', 'i5'}
	assert set(b.get_adjacent('e4')) == {'d4', 'f4', 'e3', 'e9'}
	pass