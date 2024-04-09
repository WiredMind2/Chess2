import string
from constants import BOARD_SIZE, START_ROWS

class Movement:

	def __init__(self):
		
		self.mouvement_possible = {
	    "K": [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)],
	    "Q": [(i, j) for i in range(-7, 8) for j in range(-7, 8) if (i != 0 or j != 0) and (i == 0 or j == 0 or abs(i) == abs(j))],
	    "R": [(i, 0) for i in range(-7, 8)] + [(0, j) for j in range(-7, 8)],
	    "B": [(i, j) for i in range(-7, 8) for j in range(-7, 8) if abs(i) == abs(j) and i != 0],
	    "N": [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)],
	    "P": [(1,0), (1,1), (1,-1)]
		}
		
	
	def get_type(self,coord):
		"""
		Parameters
		----------
		board : La liste représentant le plateau du jeu

		Returns
		-------
		Le type de pièce qu'on a séléctionné

		"""
		x,y = self.coords_to_index(coord)
		if self.board[y][x] != None:
			return self.board[y][x][0]
		else:
			return None
	

	def mouvement_pion_possible(self,coord):
		mouvement_dispo = []
		mouvement_dispo_potentiel = self.mouvement_possible['P']
		if coord[1] == '2' or coord[1] == '7' or coord[1] == '11':
			mouvement_dispo_potentiel.append((2,0))
		coord_test = mouvement_dispo_potentiel[0]
		x,y = self.coords_to_index(coord)
		x -= coord_test[0]
		y += coord_test[1]
		if self.board[y][x] == None and (x>-1 and x<12) and (y>-1 and y<12):
			mouvement_dispo.append(coord_test)
		for i in range(1,len(mouvement_dispo_potentiel)):
			coord_test = mouvement_dispo_potentiel[i]
			x,y = self.coords_to_index(coord)
			x -= coord_test[0]
			y += coord_test[1]
			if self.board[y][x] == None and (x>-1 and x<12) and (y>-1 and y<12):
				mouvement_dispo.append(coord_test)
		return mouvement_dispo

	def get_adjacent_diagonale(self, coords):
		x, y = self.coords_to_index(coords)
		#cas particuliés
		if coords == 'e4':
			return ['d3', 'f3', 'd5', 'i9', 'f9']
		if coords == 'd4':
			return ['c3', 'e3', 'c5', 'i5', 'e9']
		if coords == 'd5':
			return ['c6', 'i6', 'i9', 'e4', 'c4']
		if coords == 'i9':
			return ['j10', 'e10', 'e4', 'j5', 'd5']
		if coords == 'e9':
			return ['i10', 'f10', 'f4', 'd4', 'i5']
		if coords == 'i5':
			return ['j6', 'd6', 'd4', 'e9', 'j9']
		for dx, dy in [(-1, -1), (1, 1), (1, -1), (-1, 1)]:
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
			
	
