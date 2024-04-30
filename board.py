import string
from constants import BOARD_SIZE, START_ROWS, Dir, Piece
from mouv import Movement

class Board(Movement):
	"""Représente le plateau de jeu, avec les positions de chaque pion.
	"""
	def __init__(self):
		super().__init__()
		self.reset()
#test
	def reset(self):
		self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(int(BOARD_SIZE * 1.5))] # Number, then letter -> /!\ reverse

		# White
		for i, row in enumerate(START_ROWS):
			for j, p in enumerate(row):
				self.board[i][j] = Piece.from_name(p)('W', (i, j), self)

		# Black and red, reversed
		for start, team in [(7, 'B'), (11, 'R')]:
			for i, row in enumerate(START_ROWS):
				for j, p in enumerate(row):
					self.board[start - i][j] = Piece.from_name(p)(team, (i, j), self)
		

	def get(self, i, j):
		return self.board[i][j]

	@classmethod
	def coords_to_index(cls, coords):
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

	def validate_coordinates(self, coords):
		# Check if coordinates are actually on the board
		# Returns bool

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

	def __getitem__(self, coords):
		""" val = dico['e5'] """
		
		x, y = self.coords_to_index(coords)
		return self.board[y][x]

	def __setitem__(self, coords, value):
		""" dico['e5'] = 'K' """
		x, y = self.coords_to_index(coords)
		self.board[y][x] = value

if __name__ == '__main__':
	b = Board()
	x, y = b.coords_to_index('f1')
	print(b.board[y][x].list_moves())
	assert b.coords_to_index('e8') == b.coords_to_index('i8')
	assert b.coords_to_index('i9') == b.coords_to_index('d9')
	assert b.coords_to_index('a9') == b.coords_to_index('l9')

	assert dict(b.get_adjacent('i5')) == {Dir.UP: 'j5', Dir.DOWN: 'd5', Dir.RIGHT: 'i9', Dir.LEFT: 'i6'}
	assert dict(b.get_adjacent('i9')) == {Dir.UP: 'e9', Dir.DOWN: 'j9', Dir.RIGHT: 'i5', Dir.LEFT: 'i10'}
	assert dict(b.get_adjacent('e4')) == {Dir.UP: 'f4', Dir.DOWN: 'd4', Dir.RIGHT: 'e3', Dir.LEFT: 'e9'}
	pass

	assert dict(b.get_adjacent('i5')) == {Dir.UP: 'j5', Dir.DOWN: 'd5', Dir.RIGHT: 'i9', Dir.LEFT: 'i6'}
	assert dict(b.get_adjacent('i9')) == {Dir.UP: 'e9', Dir.DOWN: 'j9', Dir.RIGHT: 'i5', Dir.LEFT: 'i10'}
	assert dict(b.get_adjacent('e4')) == {Dir.UP: 'f4', Dir.DOWN: 'd4', Dir.RIGHT: 'e3', Dir.LEFT: 'e9'}
	assert dict(b.get_adjacent('h9')) == {Dir.DOWN: 'g9', Dir.RIGHT: 'h4', Dir.LEFT: 'h10'}
	assert b.get_straight_line('k9', Dir.UP) == ['k9', 'j9', 'i9', 'e9', 'f9', 'g9', 'h9']
	assert b.get_straight_line('k5', Dir.DOWN) == ['k5', 'j5', 'i5', 'd5', 'c5', 'b5', 'a5']
	assert b.get_straight_line('h4', Dir.DOWN) == ['h4', 'g4', 'f4', 'e4', 'd4', 'c4', 'b4', 'a4']
	assert dict(b.get_adjacent_diagonale('b3')) == {Dir.DOWN: ['a4'], Dir.UP: ['c2'], Dir.LEFT: ['c4'], Dir.RIGHT: ['a2']}
	assert dict(b.get_adjacent_diagonale('d4')) in ({Dir.DOWN: ['c5'], Dir.UP: ['e3'], Dir.LEFT: ['e9', 'i5'], Dir.RIGHT: ['c3']}, {Dir.DOWN: ['c5'], Dir.UP: ['e3'], Dir.LEFT: ['i5', 'e9'], Dir.RIGHT: ['c3']})
	assert b.get_diagonal_line('d4', Dir.LEFT) in (['d4', 'e9', 'f10', 'i5', 'j6'], ['d4', 'i5', 'j6', 'e9', 'f10'])
	assert b.get_diagonal_line('i9', Dir.UP) in (['i9', 'd5', 'c6', 'e4', 'f3'], ['i9', 'e4', 'f3', 'd5', 'c6'])
	pass

