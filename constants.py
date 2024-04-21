import enum


BOARD_SIZE = 8

# PGN notation: K (king), Q (queen), R (rook), B (bishop), N (knight), P (pawn)
START_ROWS = ('RNBKQBNR', 'PPPPPPPP')

# For how long can the engine compute the best move
MAX_SEARCH_TIME = 5 # seconds

class Dir(enum.Enum):
	UP = 0
	DOWN = 1
	LEFT = 2
	RIGHT = 3
 
REVERSE = {Dir.UP: Dir.DOWN, Dir.LEFT: Dir.RIGHT, Dir.DOWN: Dir.UP, Dir.RIGHT: Dir.LEFT}
 
class Piece:
	def __init__(self, team, pos, board):
		self.team = team
		self.pos = pos
		self.board = board
		self.type = self.__class__.__name__

	def __repr__(self):
		return f'{self.team} {self.type}{self.pos}'

	def list_moves(self):
		# Return a list of all the possible moves for the given piece
		# Should return a list of strings
		raise NotImplementedError # Should be overwritten
  
	def validate_move(self, cell):
		# Check if that piece is allowed to go to the given cell
		# Returns a bool

		return cell in self.list_moves() # /!\ Just for testing, should be optimized for each piece

	@classmethod
	def from_name(self, name):
		names = {
			'K': King,
			'Q': Queen,
			'B': Bishop,
			'N': Knight,
			'R': Rook,
			'P': Pawn
		}
  
		return names.get(name, None)

class Pawn(Piece):
	def list_moves(self):
		# TODO
		return []

class Rook(Piece):
	def list_moves(self):
		# TODO
		return []

class King(Piece):
	def list_moves(self):
		# TODO
		return []

class Queen(Piece):
	def list_moves(self):
		# TODO
		return []

class Bishop(Piece):
	def list_moves(self):
		# TODO
		return []

class Knight(Piece):
	def list_moves(self):
		# TODO
		return []