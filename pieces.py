from constants import Dir
from mouv import Movement



class Piece(Movement):
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
		if self.team == 'W':
			dy = 1
		else:
			dy = -1
		
		x, y = self.pos
		ny = y+dy

		out = [self.index_to_coords(x, ny)]

		if {'W': 1, 'B': 6, 'R': 10}[self.team] == y:
			# First move, we can move two cells forward
			out.append(self.index_to_coords(x, ny+dy))

		for dx in (-1, 1):
			c = self.board.get(x+dx, ny)
			if c is not None and c.team != self.team:
				out.append(self.index_to_coords(x+dx, ny))
		
		return out

class Rook(Piece):
	def list_moves(self):
		def recur(pos, dir):
			adjs = dict(self.get_adjacent(pos))
			adj = adjs.get(dir, None)
			if adj is not None:
				if self.board[adj] is None:
					return [adj] + recur(adj, dir)
				elif self.board[adj].team != self.team:
					return [adj]
			return []

		out = []
		for dir in list(Dir):
			out += recur(self.pos, dir)
		return out

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
		mouvement_possible = []
		a,b = self.coords_to_index(self.pos)
		for direction in self.dir:
				x = self.get_diagonal_line(self, self.pos, direction)


class Knight(Piece):
	def list_moves(self):
		# TODO
		return []