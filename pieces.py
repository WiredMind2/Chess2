from constants import Dir
from mouv import Movement



class Piece(Movement):
	"""
	Base class for all chess pieces, handling initialization, representation, and move validation.
	"""

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
		'''
		Return a list of all the possible moves for the given piece.
		Should return a list of strings.
		'''
		raise NotImplementedError # Should be overwritten

	def validate_move(self, cell):
		'''
		Check if that piece is allowed to go to the given cell.
		Returns a bool.
		'''
		return cell in self.list_moves() # /!\ Just for testing, should be optimized for each piece

	def check_promotion(self):
		# Just cause it's easier like this
		return False

	def copy(self):
		return self.__class__(self.team, self.pos, self.board)

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
	"""
	Class representing a Pawn piece.
	"""

	def list_moves(self):
		"""
		Returns a list of boxes on which the pawn can move.
		"""
		out = []

		x, y = self.pos
		coord = self.index_to_coords(x, y)

		if coord[0] in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'] and coord[1:] in ['1', '2', '3', '4']:
			# check which region the pawn is in

		# for dx in (-1, 1):
		# 	c = self.board.get(x+dx, ny)
		# 	if c is not None and c.team != self.team:
		# 		out.append(self.index_to_coords(x+dx, ny))

		# return out

		
			if self.team == 'W': # finds the direction of movement according to the colour of the pawn
				direc = Dir.LEFT
			if self.team == 'B':
				direc = Dir.RIGHT
			if self.team == 'R':
				direc = Dir.RIGHT
			adj = dict(self.get_adjacent(coord))
			# finds the boxes adjacent to his
			if direc not in adj:
				adj2 = {}
			else:
				adj2 = dict(self.get_adjacent(adj[direc]))
				# find the boxes adjacent to the one in front of him

				if self.board[adj[direc]] == None:
					# add the one in front of him if it is empty
					out.append(adj[direc])
					if coord[1] == '2' and direc in adj2 and self.board[adj2[direc]] == None:
						# adds the second in front of him if it is empty and it is first movement
						out.append(adj2[direc])

			for i in (Dir.UP, Dir.DOWN):
				# adds diagonal squares in front of him if he can eat pieces
				if i in adj2.keys() and self.board[adj2[i]] != None and self.board[adj2[i]].team != self.team and self.board[adj2[i]].type != 'King':
					out.append(adj2[i])

		if coord[0] in ['a', 'b', 'c', 'd', 'i', 'j', 'k', 'l'] and coord[1:] in ['5', '6', '7', '8']:
			# check which region the pawn is in

			if self.team == 'W':
				# finds the direction of movement according to the colour of the pawn
				direc = Dir.LEFT
			if self.team == 'B':
				direc = Dir.RIGHT
			if self.team == 'R':
				direc = Dir.LEFT
			adj = dict(self.get_adjacent(coord))
			# finds the boxes adjacent to his
			if direc not in adj:
				adj2 = {}
			else:
				adj2 = dict(self.get_adjacent(adj[direc]))
				# find the boxes adjacent to the one in front of him

				if self.board[adj[direc]] == None:
					# add the one in front of him if it is empty
					out.append(adj[direc])
					if coord[1:] == '7' and direc in adj2 and self.board[adj2[direc]] == None:
						# adds the second in front of him if it is empty and it is first movement
						out.append(adj2[direc])

			for i in (Dir.UP, Dir.DOWN):
				# adds diagonal squares in front of him if he can eat pieces
				if i in adj2.keys() and self.board[adj2[i]] != None and self.board[adj2[i]].team != self.team and self.board[adj2[i]].type != 'King':
					out.append(adj2[i])

		if coord[0] in ['i', 'j', 'k', 'l', 'e', 'f', 'g', 'h'] and coord[1:] in ['9', '10', '11', '12']:
			# check which region the pawn is in

			if self.team == 'W':
				# finds the direction of movement according to the colour of the pawn
				direc = Dir.LEFT
			if self.team == 'B':
				direc = Dir.LEFT
			if self.team == 'R':
				direc = Dir.RIGHT
			adj = dict(self.get_adjacent(coord))
			# finds the boxes adjacent to his
			if direc not in adj:
				adj2 = {}
			else:
				adj2 = dict(self.get_adjacent(adj[direc]))
				# find the boxes adjacent to the one in front of him

				if self.board[adj[direc]] == None:
					# add the one in front of him if it is empty
					out.append(adj[direc])
					if coord[1:] == '11' and direc in adj2 and self.board[adj2[direc]] == None:
						# adds the second in front of him if it is empty and it is first movement
						out.append(adj2[direc])

			for i in (Dir.UP, Dir.DOWN):
				# adds diagonal squares in front of him if he can eat pieces
				if i in adj2.keys() and self.board[adj2[i]] != None and self.board[adj2[i]].team != self.team:
					out.append(adj2[i])
		
		return out # returns the list containing the coordinates of the boxes on which it can move

	def check_promotion(self):
		x, y = self.pos
		dico = {'W': [7,11], 'B': [0,11], 'R': [0,7]}

		return y in dico[self.team]

	def promote(self, choice):
		"""
		Promote the Pawn if it reaches the end of the board.
		"""
		if choice not in 'QNRB':
			raise ValueError('Invalid promotion choice') # If you see this, then someone tried to be smart and failed

		new_piece = Piece.from_name(choice)(self.team, self.coords_to_index(self.pos), self.board)
		self.board[self.pos] = new_piece
		new_piece.sprite = self.sprite
		new_piece.sprite.piece = new_piece
		new_piece.sprite.update_image()


class Rook(Piece):
	"""
	Class representing a Rook piece.

	Inherits from the Piece class.
	"""

	def list_moves(self):
		"""
		returns a list of boxes on which the rook can move
		"""

		out = []
		for dir in list(Dir): # Get all possible diagonal moves
			out += self.get_straight_line(self.pos, dir)

		k = self.index_to_coords(self.pos) # Current position in coordinates

		out2 = []
		for i in out:
			if i != k and (self.board[i] == None or self.team != self.board[i].team):
				out2.append(i) # Add empty squares or squares occupied by opponent's pieces
		return out2

class King(Piece):
	"""
	Class representing a King piece.
	"""

	def list_moves(self):
		"""
		Returns a list of boxes on which the king can move.
		"""
		x, y = self.pos[0], self.pos[1]
		coord = self.index_to_coords(x, y)
		posibilities = self.get_adjacent(coord)

		out = []
		for posibilitie in posibilities:  # check if it can go on the boxes in front of it, behind it and on the sides
			if self.board[posibilitie[1]] == None:
				out.append(posibilitie[1])
			elif self.board[posibilitie[1]].team != self.board[coord].team:
				out.append(posibilitie[1])

		posibilities2 = self.get_adjacent_diagonale(coord)

		for posibilitie in posibilities2:  # check if it can go on the boxes on the diagonals
			for each in posibilitie[1]:
				if self.board[each] == None:
					out.append(each)
				elif (
					self.board[each].team != self.board[coord].team
					and self.board[each].type != self.board[coord].type
				):
					out.append(each)

		out += self.roque()  # add the boxes where it can rook if it can

		return out

	def roque(self):
		"""
		Determine the valid castling moves for the piece.
		"""
		x, y = self.pos
		coord = self.index_to_coords(x, y)
		out = []

		# check the both cases for each teams

		if self.board[coord].team == "W" and coord == "e1":
			if (
				self.board["f1"] == None
				and self.board["g1"] == None
				and self.board["h1"] is not None and self.board["h1"].team == "W"
			):
				out.append("g1")
			if (
				self.board["d1"] == None
				and self.board["c1"] == None
				and self.board["b1"] == None
				and self.board["a1"] is not None and self.board["a1"].team == "W"
			):
				out.append("c1")
		elif self.board[coord].team == "R" and coord == "i12":
			if (
				self.board["f12"] == None
				and self.board["g12"] == None
				and self.board["h12"] is not None and self.board["h12"].team == "R"
			):
				out.append("g12")
			if (
				self.board["i12"] == None
				and self.board["j12"] == None
				and self.board["k12"] == None
				and self.board["l12"] is not None and self.board["l12"].team == "R"
			):
				out.append("j12")
		elif self.board[coord].team == "B" and coord == "d8":
			if (
				self.board["c8"] == None
				and self.board["b8"] == None
				and self.board["a8"] is not None and self.board["a8"].team == "B"
			):
				out.append("b8")
			if (
				self.board["i8"] == None
				and self.board["j8"] == None
				and self.board["k8"] == None
				and self.board["l8"] is not None and self.board["l8"].team == "B"
			):
				out.append("j8")

		return out

class Queen(Piece):
	"""
	Class representing a Queen piece.
	"""
	def list_moves(self):
		"""
		returns a list of boxes on which the queen can move
		"""
		x,y = self.pos

		out = self.from_name("R")(f'{self.team}', (x, y), self.board).list_moves() # uses the rook’s list_move function 
		out += self.from_name("B")(f'{self.team}', (x, y), self.board).list_moves() # uses the bishop’s list_move function
		return out 
	
class Bishop(Piece):
	"""
	Class representing a Bishop piece.
	"""
	def list_moves(self):
		"""
		returns a list of boxes on which the bishop can move
		 """
		out = []
		for dir in list(Dir): # Get all possible diagonal moves
			out += self.get_diagonal_line(self.pos, dir)

		k = self.index_to_coords(self.pos[0], self.pos[1]) # Current position in coordinates

		out2 = []
		for i in out:
			if i != k and self.board[i] == None:
				out2.append(i) # Add empty squares
			elif i != k and self.board[k].team != self.board[i].team: 
				out2.append(i) # Add squares occupied by opponent's pieces
		return out2
	
class Knight(Piece):
	"""
	Class representing a knight piece.
	"""

	def list_moves(self):
		"""
		Returns a list of boxes on which the knight can move.
		"""
		x, y = self.pos
		coord = self.index_to_coords(x, y)

		cant = []  # Squares adjacent to the knight's current position
		for one in self.get_adjacent(coord):
			cant.append(one[1])

		step = []  # Potential knight moves
		a = list(self.get_adjacent_diagonale(coord))
		for one in a:
			for two in one[1]:
				step.append(two)

		can = []  # Valid knight moves
		for each in step:
			for one in self.get_adjacent(each):
				if one[1] not in cant:
					can.append(one[1])

		out = []  # Valid and possible movement
		for each in can:
			if self.board[each] == None:
				out.append(each)
			elif self.board[each].team != self.board[coord].team:
				out.append(each)

		out2 = []  # Special rules for the center squares
		center = ['i5', 'i9', 'e9', 'e4', 'd4', 'd5']
		if coord in center:
			for i in out:
				if i not in center:
					out2.append(i)
			return out2
		return out