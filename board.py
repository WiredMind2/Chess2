import string
from constants import START_ROWS, Dir
from mouv import Movement
from pieces import Piece

class Board(Movement):
	"""Represents the game board with the positions of each piece.

	Attributes:
		board (list): A 2D list representing the game board.
	"""

	def __init__(self, board=None):
		super().__init__()
  
		if board is None:
			self.reset()
		else:
			self.board = board

			for piece in self.iterate():
				piece.board = self

	def reset(self):
		"""Resets the game board to its initial state."""
		self.board = [[None for _ in range(8)] for _ in range(12)] # Number, then letter -> /!\ reverse

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
		"""Iterates over all pieces on the game board.

		Yields:
			Piece: The next piece on the game board.
		"""
		for row in self.board:
			for piece in row:
				if piece is not None:
					yield piece

	def copy(self):
		# Returns a copy of the board (for simulations etc)
		# This does NOT contains any image, don't use it for render!
		out = []
		for i, row in enumerate(self.board):
			out.append([])
			for piece in row:
				if piece is None:
					out[i].append(None)
				else:
					out[i].append(piece.copy())

		return Board(out)

	def move(self, src, dst):
		# Moves a piece from src to dst
		# Doesn't check if the move is valid, only use this function for simulations

		piece = self[src]

		self[src] = None
		x, y = self.coords_to_index(dst)

		self[dst] = piece
		piece.pos = x, y

	def remove_team(self, team):
		# Removes all pieces of a team
		for piece in self.iterate():
			if piece.team == team:
				self[piece.pos] = None
				piece.sprite.kill()

	def get(self, i, j):
		"""Gets the piece at the specified coordinates on the game board.

		Args:
			i (int): The column index.
			j (int): The row index.

		Returns:
			Piece|None: The piece at the specified coordinates, or None if the coordinates are out of bounds.
		"""
		if not (0 <= i < len(self.board[0]) and 0 <= j < len(self.board)):
			return None
		return self.board[j][i]

	def get_type(self, coord):
		"""Gets the type of piece at the specified coordinates on the game board.

		Args:
			coord (tuple): The coordinates of the piece.

		Returns:
			str|None: The type of piece at the specified coordinates, or None if there is no piece at the coordinates.
		"""
		x, y = self.coords_to_index(coord)
		if self.board[y][x] != None:
			return self.board[y][x].type
		else:
			return None

	def to_tuple(self):
		# Returns a tuple representation of the board
		# This is used for hashing the board state
		out = []
		for row in self.board:
			for piece in row:
				if piece is None:
					out.append(None)
				else:
					out.append((piece.type, piece.team))
		return tuple(out)

	def __getitem__(self, coords) : 
		"""Gets the piece at the specified coordinates on the game board using the square bracket notation.

		Args:
			coords (str): The coordinates of the piece in algebraic notation.

		Returns:
			Piece|None: The piece at the specified coordinates, or None if the coordinates are out of bounds.
		"""
		if coords is None:
			return None
		x, y = self.coords_to_index(coords)
		try:
			return self.board[y][x]
		except IndexError:
			return None

	def __setitem__(self, coords, value):
		"""Sets the piece at the specified coordinates on the game board using the square bracket notation.

		Args:
			coords (str): The coordinates of the piece in algebraic notation.
			value (Piece): The piece to be placed at the specified coordinates.
		"""
		x, y = self.coords_to_index(coords)
		self.board[y][x] = value

if __name__ == '__main__':
	b = Board()
	#b['b3'] = Piece.from_name('P')('R', b.coords_to_index('d3'), b)
	#b['i7'] = None
	#b['f1'] = None
	#b['g1'] = None
	#print(b['e1'].list_moves())
	#print(b['e1'].roque())
	#a = 'j9'
	#b[a] = Piece.from_name('P')('B', b.coords_to_index(a), b)
	#print(b[a].list_moves())
	print(b.board[0][0].type)
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
	pass
