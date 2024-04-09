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
		print(self.coords_to_index(coord))
		mouvement_dispo = []
		mouvement_dispo_potentiel = self.mouvement_possible['P']
		if coord[1] == '2' or coord[1] == '7' or coord[1] == '11':
			mouvement_dispo_potentiel.append((2,0))
		coord_test = mouvement_dispo_potentiel[0]
		x,y = self.coords_to_index(coord)
		x -= coord_test[0]
		y += coord_test[1]
		if self.board[y][x] == None and (x>-1 and x<13) and (y>-1 and y<13):
			mouvement_dispo.append(coord_test)
		for i in range(1,len(mouvement_dispo_potentiel)):
			coord_test = mouvement_dispo_potentiel[i]
			x,y = self.coords_to_index(coord)
			x -= coord_test[0]
			y += coord_test[1]
			print(x,y)
			if self.board[y][x] == None and (x>-1 and x<13) and (y>-1 and y<13):
				mouvement_dispo.append(coord_test)
		return mouvement_dispo
				
			
	
