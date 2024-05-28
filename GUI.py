from functools import cache
import math
import os
import pygame

from board import Board
from bot import Bot
from constants import COLORS, POPUP_SIZE, SCREEN_SIZE, TEAMS
from mouv import Vec2
from pieces import Piece

class GUI:
	def __init__(self, playable) -> None:
		self.running = False
		self.scale = 1
		self.selected = None
		self.possibilities = []
		self.team_turn = 'W'
		self.playable_teams = playable
		self.bots = {}
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

		self.init_bots()

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

			if not self.update_board: # Let it render once
				if self.playable_teams[self.team_turn] is False:
					self.play_bot()

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

			if self.playable_teams[self.team_turn] is True:
				if piece is not None and piece.team == self.team_turn:
					self.selected = cell
					self.possibilities = piece.list_moves()
				else:
					if self.selected is not None:
						if self.validate_move(self.selected, cell):
							self.move(self.selected, cell)	

							teams = list(COLORS)
							i = teams.index(self.team_turn)
							self.team_turn = teams[(i+1)%3]

						self.selected = None
						self.possibilities = []
				self.update_board = True

	def play_bot(self):
		# input('Check')
		bot = self.bots[self.team_turn] # Should always be defined
		src, dst = bot.get_move()
		if src is None: # and dst is None
			raise Exception(f'Bot {self.team_turn} couldn\'t find a move to play!')

		a, b = self.board.index_to_coords(*src), self.board.index_to_coords(*dst)

		if self.validate_move(a, b):
			self.move(a, b)

			teams = list(COLORS)
			i = teams.index(self.team_turn)
			self.team_turn = teams[(i+1)%3]
		else:
			print(f'Bot {self.team_turn} played an illegal move?? -> {a, b}')
			pass
			src, dst = bot.get_move()
			a, b = self.board.index_to_coords(*src), self.board.index_to_coords(*dst)
			pass

		self.update_board = True

	def render(self):
		if self.update_board:
			self.update_board = False
			self.screen.fill("purple")
			self.render_board()

			# self.piece_sprites.update()
			rects = self.piece_sprites.draw(self.screen)
			self.update_group.empty()

			pygame.display.update(rects)

	def render_board(self):
		dest = self.board_surf.get_rect()
		dest.center = self.screen.get_rect().center

		surf = self.board_surf.copy()
  
		cells = []
		if self.selected is not None:
			cells.append((self.selected, 'blue'))

		if self.possibilities:
			for cell in self.possibilities:
				cells.append((cell, 'green'))

		if cells:
			for cell, color in cells:
				poly = self.cache[cell]
				poly = list(map(lambda e: (e+surf.get_rect().center).tuple(), poly))
				pygame.draw.polygon(surf, color, poly)

		self.screen.blit(surf, dest)

	def load_pieces(self): 
		self.pieces = {}
		for piece in self.board.iterate():
			dest = self.coords_to_pos(piece.pos) + self.screen.get_rect().center # Centers the image
			sprite = PieceSprite(piece, dest.tuple(), self.scale, self.piece_sprites, self.update_group)
			# No need to save it since it's already in the sprite group
			# self.pieces[piece] = sprite

	def load_board(self):
		surf = pygame.image.load(os.path.join('assets', 'board.png'))
		s_rect = self.screen.get_rect()

		dest = surf.get_rect().fit(s_rect)
	
		self.scale = dest.width / surf.get_rect().width

		self.board_surf = pygame.transform.smoothscale(surf, dest.size)

	def init_bots(self):
		for team, playable in self.playable_teams.items():
			if not playable:
				bot = Bot(self.board, team)
				self.bots[team] = bot
				print(f'Initialized bot for {team} team')

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

		if piece.type == 'K' and piece2.type == 'R' and piece.team == piece2.team:
			# Castle

			# TODO - Actually this doesn't work
			p1 = self.board.coords_to_index(dst)
			p2 = self.board.coords_to_index(src)

			self.board[dst] = piece
			self.board[src] = piece2
			piece.pos = p1
			piece2.pos = p2

			sprite = piece2.sprite
			
			center = self.coords_to_pos(piece2.pos) + self.screen.get_rect().center
			sprite.move(center)
			self.update_group.add(sprite)
		else:
			self.board[src] = None
			if piece2 is not None:
				# TODO - Handle score or whatever
				piece2.pos = None

				sprite = piece2.sprite
				sprite.kill()

			x, y = self.board.coords_to_index(dst)

			self.board[dst] = piece
			piece.pos = x, y

		if piece.check_promotion() is True:
			choice = self.promotion_popup()
			piece.promote(choice) # If check_promotion is True then this exists

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

	def promotion_popup(self):
		# We're going to override the mainloop here
		# This is a bad idea, but we're pro here so it's fine.

		# Draw popup
		popup = pygame.Surface(POPUP_SIZE)
		choices = 'QRNB'
		borders = 10
		cell_size = (POPUP_SIZE[0]-borders)/len(choices)-borders, POPUP_SIZE[1]-borders*2
		sprites = []
		cell_rects = {}
		for i, choice in enumerate(choices):
			topleft = (POPUP_SIZE[0]-borders)*i/len(choices) + borders, borders
			cell_rect = pygame.Rect((topleft, cell_size))
			pygame.draw.rect(popup, 'gray', cell_rect)
   
			cell_rects[choice] = cell_rect

			piece = Piece.from_name(choice)(self.team_turn, None, None)
			sprite = PieceSprite(piece, (0, 0), self.scale)
			surf = sprite.image
			rect = surf.get_rect()
			rect.center = cell_rect.center

			sprites.append((surf, rect))

		popup.blits(sprites)
		main_rect = popup.get_rect()
		main_rect.center = self.screen.get_rect().center
  
		self.screen.blit(popup, main_rect.topleft)

		pygame.display.flip()

		# Override mainloop to force pause EVERYTHING, without crashing the game
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False

				if event.type == pygame.MOUSEBUTTONDOWN:
					# Mouse click
					if event.button == 1:
						x, y = list(map(lambda e: e[0]-e[1], zip(event.pos, main_rect.topleft)))
						for choice, rect in cell_rects.items():
							if rect.collidepoint(x, y) is True:
								print(f'Promotion choice: {choice}')
								self.update_board = True
								return choice

			# Nothing changes until we got a valid click, so no need to refresh the screen
			self.clock.tick(60)

class PieceSprite(pygame.sprite.Sprite):
	def __init__(self, piece, pos, scale, *groups) -> None:
		super().__init__(*groups)
		self.piece = piece
		self.piece.sprite = self
		self.scale = scale

		self.update_image()

		self.rect = self.image.get_rect()
		self.rect.center = pos

	def update_image(self):
		full_team = TEAMS[self.piece.team]
		path = os.path.join('assets', 'pieces', f'{full_team}-{self.piece.__class__.__name__.lower()}.png')
		surf = pygame.image.load(path)

		self.image = pygame.transform.smoothscale_by(surf, self.scale/2)

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
	gui = GUI({'W': True, 'R': False, 'B': False, })
	gui.start()