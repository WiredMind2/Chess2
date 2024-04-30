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
		mouvement_dispo = []
		case_adjcante = dict(self.get_adjacent(self.pos))
		x, y = self.coords_to_index(self.pos)

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

		if self.board[y][x] != None and self.board[y][x].team == "R":
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
		
		elif self.board[y][x] != None and self.board[y][x].team == 'B':
			x,y = self.coords_to_index(case_adjcante[Dir.LEFT])
			if self.board[y][x] == None and (x>-1 and x<12) and (y>-1 and y<12):
				mouvement_dispo.append(case_adjcante[Dir.LEFT])
				print(mouvement_dispo)
				case_adjcante3 = dict(self.get_adjacent(case_adjcante[Dir.LEFT]))
				print(case_adjcante3)
				x,y = self.coords_to_index(case_adjcante3[Dir.LEFT])
				if self.board[y][x] == None and (x>-1 and x<12) and (y>-1 and y<12):
					mouvement_dispo.append(case_adjcante3[Dir.LEFT])
			
			case_adjcante2 = dict(self.get_adjacent(case_adjcante[Dir.LEFT]))
			x,y = self.coords_to_index(case_adjcante2[Dir.UP])
			if self.board[y][x] != None and (x>-1 and x<12) and (y>-1 and y<12):
				mouvement_dispo.append(case_adjcante2[Dir.UP])
			x,y = self.coords_to_index(case_adjcante2[Dir.DOWN])
			if self.board[y][x] != None and (x>-1 and x<12) and (y>-1 and y<12):
				mouvement_dispo.append(case_adjcante2[Dir.DOWN])
			return mouvement_dispo


class Rook(Piece):
	def list_moves(self):
		mouvement_dispo = []
		a,b = self.coords_to_index(self.pos)
		case_adjcante = dict(self.get_adjacent(self.pos))
		i = 0
		for case in case_adjcante.values():
			continu = True
			while continu == True:
				x, y = self.coords_to_index(case)
				if (x>-1 and x<8) and (y>-1 and y<12) and self.board[y][x] == None :
					mouvement_dispo.append(case)
					case_adjcante = dict(self.get_adjacent(case))
					case = list(case_adjcante.values())[i]
				elif (x>-1 and x<8) and (y>-1 and y<12) and self.board[y][x].team != self.board[b][a].team  :
					mouvement_dispo.append(case)
					case_adjcante = dict(self.get_adjacent(case))
					case = list(case_adjcante.values())[i]
					continu = False
				else:
					continu = False
			
			i += 1
		return mouvement_dispo


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