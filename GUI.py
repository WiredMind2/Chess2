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

		cell = self.coords_to_cell(pos)

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

		# self.screen.fill("purple")
		self.render_board()
		piece = self.board.get(11, 0)
		self.render_piece(piece)

	def render_board(self):
		surf = pygame.image.load(os.path.join('assets', 'board.png'))
		s_rect = self.screen.get_rect()

		dest = surf.get_rect().fit(s_rect)
	
		self.scale = dest.width // surf.get_rect().width

		surf = pygame.transform.smoothscale(surf, dest.size)
		dest.center = self.screen.get_rect().center

		self.screen.blit(surf, dest)

	def render_piece(self, piece):
		if piece is None:
			return

		dest = self.cell_to_coords(piece.pos)
		surf = self.get_piece_surface(piece.type[0], piece.team)
		self.screen.blit(surf, dest)

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

	def get_piece_surface(self, name, color):
		return self.pieces[name][color]

	def cell_to_coords(self, pos):
		# TODO
		return self.screen.get_rect().center

	def coords_to_cell(self, pos):
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