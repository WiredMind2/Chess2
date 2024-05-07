from functools import cache
import math
import os
import pygame

from board import Board
from constants import COLORS, SCREEN_SIZE
from pieces import Piece

class GUI:
	def __init__(self) -> None:
		self.running = False
		self.scale = 1
		self.selected = None
		self.team_turn = 'W'
		self.update = True

		self.board = Board()

		self.load_pieces()

	def start(self):
		pygame.init()
		self.screen = pygame.display.set_mode(SCREEN_SIZE)
		self.clock = pygame.time.Clock()

		self.running = True
		self.mainloop()

		pygame.quit()

	def mainloop(self):
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False

				if event.type == pygame.MOUSEBUTTONDOWN:
					self.handle_click(event)

			self.render()

			pygame.display.flip()

			self.clock.tick(60)

	def handle_click(self, event):
		button = event.button
		pos = event.pos

		cell = self.pos_to_coords(pos)

		if button == 1: # Left click
			piece = self.board[cell]

			if piece is not None:
				if self.selected is None:
					if piece.team == self.team_turn:
						self.selected = cell
				else:
					if self.validate_move(self.selected, cell):
						self.move(self.selected, cell)
						self.selected = None

	def render(self):
		if not self.update:
			return
		self.update = False
		self.screen.fill("purple")
		dest = self.render_board()
		piece = self.board.get(0, 11)
		self.render_pieces()

		# self.screen.blit(self.board_surf, dest)

	def render_board(self):
		surf = pygame.image.load(os.path.join('assets', 'board.png'))
		s_rect = self.screen.get_rect()

		dest = surf.get_rect().fit(s_rect)
	
		self.scale = dest.width // surf.get_rect().width

		self.board_surf = pygame.transform.smoothscale(surf, dest.size)
		dest.center = self.screen.get_rect().center
		return dest

	def render_piece(self, piece):
		if piece is None:
			return

		surf = self.get_piece_surface(piece.type_short, piece.team)
		dest = tuple(map(lambda e: e[0]-e[1], zip(self.coords_to_pos(piece.pos),surf.get_rect().center))) # Centers the image

		# self.board_surf.blit(surf, dest)
		self.screen.blit(surf, dest)

	def render_pieces(self):
		for piece in self.board.iterate():
			self.render_piece(piece)

	def load_pieces(self):
		self.pieces = {}
		for name in 'RNBKQP':
			piece = Piece.from_name(name)
			self.pieces[name] = {}

			for color in 'WBR':
				path = os.path.join('assets', 'pieces', color, f'{color}-{piece.__name__.lower()}.png')
				surf = pygame.image.load(path)
				self.pieces[name][color] = surf

	def load_pieces(self): # TODO - Should delete when other pieces files are available
		self.pieces = {}
		for name in 'RNBKQP':
			piece = Piece.from_name(name)
			path = os.path.join('assets', 'pieces', f'white-{piece.__name__.lower()}.png')
			surf = pygame.transform.smoothscale_by(pygame.image.load(path), self.scale/2)

			self.pieces[name] = {'W': surf}

			for color, (fill, border) in COLORS.items():
				if color == 'W':
					continue
 
				surf = surf.copy()
				for x in range(surf.get_width()):
					for y in range(surf.get_height()):
						r, g, b, a = surf.get_at((x, y))
						if a > 0:
							if (r, g, b) == (255, 255, 255):
								surf.set_at((x, y), pygame.Color(fill))
							elif (r, b, g) == (0, 0, 0):
								surf.set_at((x, y), pygame.Color(border))


				self.pieces[name][color] = surf

	def get_piece_surface(self, name, color) -> pygame.Surface:
		return self.pieces[name][color]

	@cache
	def coords_to_pos(self, pos):
		"""
		Return position on screen for a given pos.
		"""
		# Doesn't work (yet)

		if isinstance(pos, str):
			pos = self.board.coords_to_index(pos)
		x, y = pos
		# if x >= 8:
		# 	x -= 4
		# if y >= 8:
		# 	y -= 4

		nx, ny = x-4, y-4
		r = math.sqrt(nx**2+ny**2)
		if nx == 0:
			teta = 0
		else:
			teta = math.atan(ny/nx)
  
		if nx < 0:
			teta = math.pi+teta

		# TODO -> Temporary stuff
		b_rect = self.board_surf.get_rect()
		b_size = b_rect.size
		b_center = b_rect.center
		out = nx/r*b_size[0]/2+b_center[0], ny/r*b_size[1]/2+b_center[1]
		return out

	def coords_to_pos(self, coords):
		x, y = coords
		# Find third of board
		# -> Equivalent of the team side
		third = (-1/2 - 2/3*(y//4))*math.pi

		# Find sixth of board <=> first branch angle
		sixth = third + (2*(x<4)-1)*1/6+math.pi

		# Find first branch length
		sixth_l = 1/8 # of the radius

		# Find the two sub vectors
		vec_a, vec_b = sixth + 1/6*math.pi, sixth - 1/6*math.pi

		# if x > 4:
		x, y = y, x
		l_a, l_b = abs(x)*1/4, abs(y)*1/4

		# Find total vector
		rect = self.board_surf.get_rect()
		r = rect.height/2
		cx, cy = self.screen.get_rect().center

		fx, fy = math.cos(sixth)*sixth_l, math.sin(sixth)*sixth_l
		pygame.draw.line(self.screen, 'black', (cx, cy), (fx*r+cx, fy*r+cy), 4)
		sax, say = math.cos(vec_a)*l_a, math.sin(vec_a)*l_a
		sbx, sby = math.cos(vec_b)*l_b, math.sin(vec_b)*l_b
		sx, sy = sax+sbx, say+sby
		pygame.draw.line(self.screen, 'blue', (fx*r+cx, fy*r+cy), ((fx+sx)*r+cx, (fy+sy)*r+cy), 4)
		tx, ty = -fx+sx, -fy+sy

		# Correct scale and centered
		rect = self.board_surf.get_rect()
		r = rect.height/2
		cx, cy = rect.center
		out = tx*r, ty*r

		return out

	def pos_to_coords(self, pos):
		# TODO
		return 'e5'

	def move(self, src, dst):
		piece = self.board[src]
		piece2 = self.board[dst]

		if piece.type == 'K' and piece2.type == 'R':
			# Castle
			# TODO
			pass

		self.board[src] = None
		if piece2 is not None:
			# TODO - Handle score or whatever
			pass

		self.board[dst] = piece

	def validate_move(self, src, dst):
		piece = self.board[src]
		if piece is None:
			return False

		if self.board.is_check(src, dst):
			return False

		moves = piece.list_moves()
		if dst in moves:
			piece2 = self.board[dst]
			if piece2 is not None and piece2.team == piece.team and not (piece.type == 'K' and piece2.type == 'R'):
				return False
			return True

		return False


if __name__ == "__main__":
	gui = GUI()
	gui.start()