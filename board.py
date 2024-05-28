import string
from constants import BOARD_SIZE, START_ROWS, Dir
from mouv import Movement
from pieces import Piece

class Board(Movement):
	"""Représente le plateau de jeu, avec les positions de chaque pion.
	"""
	def __init__(self):
		super().__init__()
		self.reset()

	def reset(self):
		self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(int(BOARD_SIZE * 1.5))] # Number, then letter -> /!\ reverse

		# White
		for i, row in enumerate(START_ROWS):
			for j, p in enumerate(reversed(row)):
				self.board[i][j] = Piece.from_name(p)('W', (j, i), self)

		# Black and red, reversed
		for start, team in [(7, 'B'), (11, 'R')]:
			for i, row in enumerate(START_ROWS):
				for j, p in enumerate(row):
					self.board[start - i][j] = Piece.from_name(p)(team, (j, start-i), self)

	def iterate(self):
		"""Iterate over all pieces"""
		for row in self.board:
			for piece in row:
				if piece is not None:
					yield piece

	def get(self, i, j):
		if not (0 <= i < len(self.board[0]) and 0 <= j < len(self.board)):
			return None
		return self.board[j][i]

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
	b['c3'] = Piece.from_name('K')('W', b.coords_to_index('c3'), b)
	print(b['c3'].list_moves())

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


	b['c6'] = Piece.from_name('P')('W', b.coords_to_index('c6'), b)
	print(b['d7'].list_moves())