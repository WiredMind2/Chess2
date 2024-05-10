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
		self.update_group = pygame.sprite.Group()
		self.update_board = True

		self.board = Board()
		self.piece_sprites = pygame.sprite.Group()

	def start(self):
		pygame.init()
		pygame.freetype.init()
		self.screen = pygame.display.set_mode(SCREEN_SIZE)
		self.clock = pygame.time.Clock()
		self.font = pygame.font.SysFont('Comic Sans MS', 30) # TODO

		self.load_board()
		self.load_pieces()
		self.create_cache_cells()

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
		if cell is None:
			return

		if button == 1: # Left click
			piece = self.board[cell]
			print('Clicked on:', cell, piece)

			if self.selected is None:
				if piece is not None:
					if piece.team == self.team_turn or True:
						self.selected = cell
						self.update_board = True
			else:
				if self.validate_move(self.selected, cell):
					self.move(self.selected, cell)
				self.selected = None
				self.update_board = True


	def render(self):
		if self.update_board:
			self.update_board = False
			self.screen.fill("purple")
			self.render_board()

			self.piece_sprites.update()
			rects = self.piece_sprites.draw(self.screen)
			self.update_group.empty()

			pygame.display.update(rects)

	def render_board(self):
		dest = self.board_surf.get_rect()
		dest.center = self.screen.get_rect().center

		surf = self.board_surf.copy()
		if self.selected is not None:
			poly = self.cache[self.selected]
			poly = list(map(lambda e: (e+surf.get_rect().center).tuple(), poly))
			pygame.draw.polygon(surf, 'blue', poly)

		self.screen.blit(surf, dest)

	def load_pieces(self): 
		self.pieces = {}
		for piece in self.board.iterate():
			dest = self.coords_to_pos(piece.pos) + self.screen.get_rect().center # Centers the image
			sprite = PieceSprite(piece, dest.tuple(), self.scale, self.piece_sprites, self.update_group)
			# self.pieces[piece] = sprite

	def load_board(self):
		surf = pygame.image.load(os.path.join('assets', 'board.png'))
		s_rect = self.screen.get_rect()

		dest = surf.get_rect().fit(s_rect)
	
		self.scale = dest.width / surf.get_rect().width

		self.board_surf = pygame.transform.smoothscale(surf, dest.size)

	@cache
	def coords_to_pos(self, coords):
		DEBUG = False # To render a bunch of lines

		x, y = coords
		# Find third of board
		# -> Equivalent of the team side
		third = (1/2 + 2/3*(y//4))*math.pi

		# Find sixth of board <=> first branch angle
		sixth = (third + (2*((x>=4)^(y<4))-1)*1/6*math.pi)%(2*math.pi)

		# Find first branch length
		# sixth_l = 0 # of the radius
		# start = Vec2(math.cos(sixth), math.sin(sixth))*sixth_l
		start = Vec2(0, 0)

		x, y = y, x
		if y < 4:
			y = 3-y
		if x < 4:
			if y >= 4:
				x, y = 3-x, 4-y
			else:
				x, y = y, 3-x

		# Screen relative stuff -> have to do it here for debug
		rect = self.board_surf.get_rect()
		r = rect.height/2
		cx, cy = self.screen.get_rect().center


		if DEBUG:
			draw = lambda p, e, c=None: pygame.draw.line(self.screen, c or 'blue', ((p.x)*r+cx, (p.y)*r+cy), ((e.x)*r+cx, (e.y)*r+cy), 4)
			draw(Vec2(0, 0), start, 'black')

		l_s = 1
		off = 1/6*math.pi
		l_t = 1.15

		p1 = start
		p2 = Vec2(math.cos(sixth+off)*l_s, math.sin(sixth+off)*l_s)
		p3 = Vec2(math.cos(sixth-off)*l_s, math.sin(sixth-off)*l_s)
		p4 = Vec2(math.cos(sixth)*l_t, math.sin(sixth)*l_t)

		lx, ly = (abs(x)%4+1/2)/4, (abs(y)%4+1/2)/4

		if y<4:
			lx, ly = ly, lx

		a, b = (p3-p1)*lx, p2+(p4-p2)*lx
		c, d = (p2-p1)*ly, p3+(p4-p3)*ly

		if DEBUG:
			draw(a, b, 'gray')
			draw(c, d, 'gray')
			draw(p1, p2)
			draw(p1, p3)
			draw(p4, p2)
			draw(p4, p3)

		a1, b1 = b.y-a.y, a.x-b.x,
		a2, b2 = d.y-c.y, c.x-d.x
		c1, c2 = a1*a.x+b1*a.y, a2*c.x+b2*c.y

		det = (b.y-a.y)*(c.x-d.x) - (d.y-c.y)*(a.x-b.x)
		if det == 0:
			mid = start
		else:
			mid_x = (b2*c1 - b1*c2)/det
			mid_y = (a1*c2 - a2*c1)/det
			mid = Vec2(mid_x, mid_y)

		if DEBUG:
			print(f'{x:2} {y:2} {mid.x:6} {mid.y:6}')
			draw(start, mid, 'red')

		# Correct scale and centered
		rect = self.board_surf.get_rect()
		r = rect.height/2
		out = mid*r

		return out

	def pos_to_coords(self, click_pos):
		pos = Vec2(click_pos)-self.screen.get_rect().center
		out = None
		for coords, shape in self.cache.items():
			# Raycast check

			if raytracing(pos, shape):
				out = coords
		return out

	def create_cache_cells(self):
		DEBUG = False

		cache = {}
		for pos_x in range(8):
			for pos_y in range(12):
				if pos_y >= 4:
					pos = self.board.index_to_coords(pos_x, pos_y)
				else:
					pos = self.board.index_to_coords(7-pos_x, pos_y)

				# Find third of board
				# -> Equivalent of the team side
				third = (1/2 + 2/3*(pos_y//4))*math.pi

				# Find sixth of board <=> first branch angle
				sixth = (third + (2*(pos_x>=4)-1)*1/6*math.pi)%(2*math.pi)

				# Find first branch length
				# sixth_l = 0 # of the radius
				# start = Vec2(math.cos(sixth), math.sin(sixth))*sixth_l
				start = Vec2(0, 0)

				x, y = pos_y, pos_x
				if x < 4:
					x = 3-x
				if y < 4:
					y = 3-y

				# Screen relative stuff -> have to do it here for debug
				rect = self.board_surf.get_rect()
				r = rect.height/2

				l_s = 1
				off = 1/6*math.pi
				l_t = 1.15

				p1 = start
				p2 = Vec2(math.cos(sixth+off)*l_s, math.sin(sixth+off)*l_s)
				p3 = Vec2(math.cos(sixth-off)*l_s, math.sin(sixth-off)*l_s)
				p4 = Vec2(math.cos(sixth)*l_t, math.sin(sixth)*l_t)

				corners = []
				for dx in (0, 1):
					for dy in (1, 0):
						dy = dx^dy
						lx, ly = (abs(x)%4+dx)/4, (abs(y)%4+dy)/4

						if y<4:
							lx, ly = ly, lx

						a, b = (p3-p1)*lx, p2+(p4-p2)*lx
						c, d = (p2-p1)*ly, p3+(p4-p3)*ly

						a1, b1 = b.y-a.y, a.x-b.x,
						a2, b2 = d.y-c.y, c.x-d.x
						c1, c2 = a1*a.x+b1*a.y, a2*c.x+b2*c.y

						det = (b.y-a.y)*(c.x-d.x) - (d.y-c.y)*(a.x-b.x)
						if det == 0:
							mid = start
						else:
							mid_x = (b2*c1 - b1*c2)/det
							mid_y = (a1*c2 - a2*c1)/det
							mid = Vec2(mid_x, mid_y)

						# Correct scale and centered
						rect = self.board_surf.get_rect()
						r = rect.height/2
						out = mid*r

						corners.append(out)

				if DEBUG:
					pygame.draw.polygon(self.screen, 'blue', list(map(lambda e: (e+self.screen.get_rect().center).tuple(), corners)), 4)
					surf = self.font.render(pos, True, 'white')
					topleft = min(corners, key=sum)
					self.screen.blit(surf, (topleft+self.screen.get_rect().center+surf.get_rect().center).tuple())

				cache[pos] = corners

		self.cache = cache

	def move(self, src, dst):
		piece = self.board[src]
		piece2 = self.board[dst]
  
		print(f'Moving from {src} to {dst}')

		if piece.type == 'K' and piece2.type == 'R':
			# Castle
			# TODO
			pass

		self.board[src] = None
		if piece2 is not None:
			# TODO - Handle score or whatever
			piece2.pos = None

			sprite = self.pieces[piece2]
			sprite.kill()

		x, y = self.board.coords_to_index(dst)

		self.board[dst] = piece
		piece.pos = x, y

		# sprite = self.pieces[piece]
		sprite = piece.sprite
		
		center = self.coords_to_pos(piece.pos) + self.screen.get_rect().center
		sprite.move(center)
		self.update_group.add(sprite)

		self.update = True

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

class Vec2:
	"""Helper to work with coordinates"""
	def __init__(self, x, y=None):
		if y is None:
			x, y = x

		self.x, self.y = x, y

	def __add__(self, other):
		if isinstance(other, tuple):
			other = Vec2(other)
		return Vec2(self.x+other.x, self.y+other.y)

	def __sub__(self, other):
		if isinstance(other, tuple):
			other = Vec2(other)
		return Vec2(self.x-other.x, self.y-other.y)

	def __neg__(self):
		return Vec2(-self.x, -self.y)

	def __mul__(self, k):
		return Vec2(self.x*k, self.y*k)

	def __truediv__(self, k):
		return Vec2(self.x/k, self.y/k)

	def __repr__(self):
		return f'({self.x}, {self.y})'

	def __iter__(self):
		return iter((self.x, self.y))

	def tuple(self):
		return self.x, self.y


class PieceSprite(pygame.sprite.Sprite):
	def __init__(self, piece, pos, scale, *groups) -> None:
		super().__init__(*groups)
		self.piece = piece
		self.piece.sprite = self

		path = os.path.join('assets', 'pieces', f'white-{piece.__class__.__name__.lower()}.png')
		surf = pygame.image.load(path)

		if piece.team != 'W': # TODO - Should delete when other pieces images are available
			fill, border = COLORS[piece.team]

			surf = surf.copy()
			for x in range(surf.get_width()):
				for y in range(surf.get_height()):
					r, g, b, a = surf.get_at((x, y))
					if a > 0:
						if (r, g, b) == (255, 255, 255):
							surf.set_at((x, y), pygame.Color(fill))
						elif (r, b, g) == (0, 0, 0):
							surf.set_at((x, y), pygame.Color(border))

		self.image = pygame.transform.smoothscale_by(surf, scale/2)

		self.rect = self.image.get_rect()
		self.rect.center = pos

  
	def move(self, dst):	
		if isinstance(dst, Vec2):
			dst = dst.tuple()
		self.rect.center = dst

def raytracing(pos, poly):
	n = len(poly)
	inside = False

	p1 = poly[0]
	for i in range(n+1):
		p2 = poly[i % n]
		if pos.y > min(p1.y,p2.y):
			if pos.y <= max(p1.y,p2.y):
				if pos.x <= max(p1.x,p2.x):
					if p1.y != p2.y:
						xints = (pos.y-p1.y)*(p2.x-p1.x)/(p2.y-p1.y)+p1.x
					if p1.x == p2.x or pos.x <= xints:
						inside = not inside
		p1 = p2
	return inside

if __name__ == "__main__":
	gui = GUI()
	gui.start()