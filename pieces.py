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
		x,y = self.pos[0], self.pos[1]
		coord = self.index_to_coords(x,y)
		posibilities = self.get_adjacent(coord)

		out = []
		for posibilitie in posibilities:
			
			if self.board[posibilitie[1]] == None:
				out.append(posibilitie[1])
			elif self.board[posibilitie[1]].team != self.board[coord].team: 
				out.append(posibilitie[1])

		
		posibilities2 = self.get_adjacent_diagonale(coord)
		for posibilitie in posibilities2:
			for each in posibilitie[1]:
				if self.board[each] == None:
					out.append(each)
				elif self.board[each].team != self.board[coord].team and self.board[each].type != self.board[coord].type: 
					out.append(each)

		return out 

class Queen(Piece):
	def list_moves(self):
		x,y = self.pos[0], self.pos[1]
		cord = self.index_to_coords(x,y)
		out = []
		self.board[cord] = self.from_name("R")(f'{self.team}', (x, y), self.board)
		out += (self.board[cord].list_moves())

		self.board[cord] = self.from_name("B")(f'{self.team}', (x, y), self.board)
		out += (self.board[cord].list_moves())

		self.board[cord] = self.from_name("Q")(f'{self.team}', (x, y), self.board)

		return out 
	
class Bishop(Piece):
	def list_moves(self):
		out = []
		for dir in list(Dir):
			out += self.get_diagonal_line(self.pos, dir)

		k = self.index_to_coords(self.pos[0], self.pos[1])
		a = self.index_to_coords(self.pos[0], self.pos[1])

		out2 = []
		for i in out:
			if i != k and self.board[i] == None:
				out2.append(i)
			elif i != k and self.board[a].team != self.board[i].team: 
				out2.append(i)
		return out2
	
class Knight(Piece):
	def list_moves(self):

		x,y = self.pos[0], self.pos[1]
		coord = self.index_to_coords(x,y)

		cant = []
		for one in self.get_adjacent(coord):
			cant.append(one[1])

		step = []
		a = list(self.get_adjacent_diagonale(coord))
		for one in a:
			for two in one[1]:
				step.append(two)
		can = []
		for each in step:
			for one in self.get_adjacent(each):
				if one[1] not in cant:
					can.append(one[1])
		out = []
		for each in can:
			if self.board[each] == None:
				out.append(each)
			elif self.board[each].team != self.board[coord].team: 
				out.append(each)
				
		return out