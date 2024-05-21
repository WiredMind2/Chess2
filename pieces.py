from constants import Dir
from mouv import Movement



class Piece(Movement):
	def __init__(self, team, pos, board):
		self.team = team
		self.pos = pos
		self.board = board
		self.type = self.__class__.__name__
		self.type_short = self.type[0] if self.type != 'Knight' else 'N'
		self.sprite = None

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

	def promotion(self):
		x, y = self.pos
		print(y)
		if {'W': [7,11], 'B': [0,11], 'R': [0,7]}[self.team][0] == y or {'W': [7,11], 'B': [0,11], 'R': [0,7]}[self.team][1] == y:
			new_type = str(input("Q,R,Q,B:  "))
			self.board[self.pos] = Piece.from_name(new_type)(self.team, self.coords_to_index(self.pos), self.board)


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

		out += self.roque()

		return out 

	def roque(self): # TODO - Check if mate
		x,y = self.pos
		coord = self.index_to_coords(x,y)
		out = []
		
		if self.board[coord].team == 'W' and coord == 'e1':
			if self.board['f1'] == None and self.board['g1'] == None and self.board['h1'].team == "W":
				out.append('g1')
			if self.board['d1'] == None and self.board['c1'] == None and self.board['b1'] == None and self.board['a1'].team == "W":
				out.append('c1')
		elif self.board[coord].team == 'R' and coord == 'i12':
			if self.board['f12'] == None and self.board['g12'] == None and self.board['h12'].team == "R":
				out.append('g12')
			if self.board['i12'] == None and self.board['j12'] == None and self.board['k12'] == None and self.board['l12'].team == "R":
				out.append('j12')
		elif self.board[coord].team == 'B' and coord == 'd8':
			if self.board['c8'] == None and self.board['b8'] == None and self.board['a8'].team == "B":
				out.append('b8')
			if self.board['i8'] == None and self.board['j8'] == None and self.board['k8'] == None and self.board['l8'].team == "B":
				out.append('j8')

		return out

class Queen(Piece):
	def list_moves(self):
		x,y = self.pos[0], self.pos[1]

		out = self.from_name("R")(f'{self.team}', (x, y), self.board).list_moves()
		out += self.from_name("B")(f'{self.team}', (x, y), self.board).list_moves()

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

		x,y = self.pos
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

		out2 = []
		center = ['i5','i9','e9','e4','d4','d5']
		if coord in center:
			for i in out:
				if i not in center:
					out2.append(i)
			return out2
		return out