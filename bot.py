import functools
import heapq
import math
import multiprocessing
import os
import queue
from subprocess import PIPE, STDOUT, Popen
from sys import platform
import threading
import time

from constants import MAX_SEARCH_TIME
from mouv import Vec2


class Bot:
	def __init__(self, board, team):
		self.board: Board = board
		self.team = team

		if platform == "linux" or platform == "linux2":
			self.cmd = [
				"./stockfish/stockfish-ubuntu-x86-64-sse41-popcnt/stockfish/stockfish-ubuntu-x86-64-sse41-popcnt"
			]
		elif platform == "win32":
			self.cmd = [
				".\stockfish\stockfish-windows-x86-64-sse41-popcnt\stockfish\stockfish-windows-x86-64-sse41-popcnt.exe"
			]
		elif platform == "darwin":
			raise OSError("Désolé, MacOS n'est encore pas supporté pour ce robot.")

		self.cmd[0] = os.path.abspath(self.cmd[0])

		self.bot = None
		self.bots = {}
		self.start_all_bots()

		self.moves = {side: [] for side in "WBR"}

		print("Ready!")

	def multi_bot(func):
		@functools.wraps(func)
		def wrapped(self, *args, side=None, **kwargs):

			reset = side is not None or self.bot is None
			if side is None and self.bot is None:
				out = []
				for bot in self.bots.values():
					self.bot = bot  # That's ugly
					out.append(func(self, *args, **kwargs))
			else:
				if self.bot is None:
					self.bot = self.bots[side]  # That's ugly, but a little bit better
				out = func(self, *args, **kwargs)

			if reset:
				self.bot = None

			return out

		return wrapped

	def start_all_bots(self):
		if len(self.bots) > 0:
			# Resetting bots, need to kill the previous ones
			for side, bot in self.bots.items():
				bot.kill()

		self.bots = {
			side: Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT) for side in "WBR"
		}

		self.engine_ready = {side: False for side in "WBR"}

		for side in "WBR":
			self.start_bot(side)

	def reset_bot(self, running):
		for team, is_running in running.items():
			if is_running is True:
				print('Resetting bot', team)
				running[team] = False
				self.bots[team].kill()

				self.bots[team] = Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
				self.engine_ready[team] = False
				self.start_bot(team)

	def start_bot(self, side):
		init = self.read_command(side)  # Stockfish 16.1 by whatever
		if b'GLIB' in init:
			# There is some stuff missing
			raise FileNotFoundError('GLIBCXX is missing!')

		self.write_command("uci", side=side)

		# self.write_command('setoption name UCI_Elo value 3190') # Make a monster?
		self.write_command(
			f"setoption name Threads value {multiprocessing.cpu_count()//3}", side=side
		)  # Make a MONSTER

		self.wait_for_engine(side, uci=True)

	def parse_commands(self, iterate=False, side=None, force=False, is_eval=False):
		def iterator():
			scores = {}
			while force or self.engine_ready[side] is True:
				line = self.read_command(side=side)

				if len(line) == 0:
					if not self.is_alive(side):
						# Process crashed
						self.reset_bot({side: True})
						break
					continue

				# print('[STOCKFISH stdout]', side, line.decode())

				cmd, *args = line.split(b" ", 1)
				args = args[0] if args else None

				if cmd == b"id":
					pass  # IDC

				elif cmd == b"option":
					# if side == "W":
					# 	print(line.decode('utf-8'))
					pass  # IDC

				elif cmd == b"uciok":
					self.engine_ready[side] = "uci"
					break  # Engine is almost ready

				elif cmd == b"readyok":
					self.engine_ready[side] = True
					break  # Engine is ready

				elif cmd == b"info":
					args = args.split(b" ")

					if args[0] == b'string':
						if is_eval:
							line = self.read_command(side=side)
							while not line.startswith(b"Final evaluation"):
								line = self.read_command(side=side)
							score = line.split(b" ", 2)[2].strip().split(b" ", 1)[0]
							if score == b"none":
								score = None
							else:
								score = float(score)
							yield score
							break

					while args:
						key = args.pop(0)
						if key in {b"currmove", b"currmovenumber"}:
							args.pop(0)
							break  # Just skip

						elif key == b"evaluation":
							# Ignore
							args.pop(0)
							args.pop(0)

						elif key == b"score":
							key2 = args.pop(0)
							if key2 in {b"cp", b"mate"}:

								scores['cached'] = int(args.pop(0)), key2 == b"mate"

							if args and args[0] in {b"lowerbound", b"upperbound"}:
								args.pop(0)  # ignore

						elif key == b"pv":
							best = args
							if scores.get('cached', None) is not None:
								scores[best[0]] = scores['cached']
								scores['cached'] = None
							args = []

							# if iterate:
							# 	yield best, scores.get(best[0], None)
							# break

						else:
							# Ignore
							args.pop(0)

				elif cmd == b"bestmove":
					best = args.split(b" ")
					if len(best) > 1:
						best = [best[0], best[2]]  # Ponder move

					# print('[STOCKFISH stdout]', side, line.decode())

					if best[0] == b'(none)':
						best = [False]

					yield best, scores.get(best[0], (0, False))
					break

				elif cmd == b'Stockfish':
					# Bot just got reset, ignore
					return

				else:
					print(line)
					pass
			
			pass

		if iterate:
			return iterator()

		else:
			return list(iterator())

	def write_command(self, command, side):
		"""
		Writes the command to the terminal process.
		"""
		bot = self.bots[side]
		bot.stdin.write((command + "\n").encode())
		bot.stdin.flush()

	def read_command(self, side):
		return self.bots[side].stdout.readline().strip()

	def is_alive(self, side):
		return self.bots[side].poll() is None

	def wait_for_engine(self, side, uci=False):
		value = "uci" if uci else True
		while self.engine_ready[side] != value:
			self.parse_commands(side=side, force=True)

	def get_move(self):
		boards = self.board_to_fen()
		que = queue.Queue()

		def wrapper(side):
			ok = False
			for moves in self.parse_commands(iterate=True, side=side):
				que.put((side, moves))
				ok = True

			if ok is False:
				# while self.engine_ready[side] is not True:
				# 	# The engine crashed and is rebooting
				# 	time.sleep(0.01)
				pass

			que.put(None)
			running[side] = False

		for side, board, moves in boards:
			self.engine_ready[side] = False
			if not ('k' in board and 'K' in board):
				# One king is missing, ignore this board
				# There will always be at least one board with both kings so it's fine
				continue

			self.write_command("ucinewgame", side)
			self.write_command("isready", side)
			self.wait_for_engine(side)

			cmd = "position fen " + board
			self.write_command(cmd, side=side)
			# print(side, cmd)

			searchmoves = (' searchmoves ' + ' '.join(moves)) if moves else ''
			cmd = f"go movetime {MAX_SEARCH_TIME*100}{searchmoves}"
			# print(side, cmd)
			self.write_command(
				cmd, side=side
			)  # To ensure that they all start at almost the same time

		running = {}
		for side in "WBR":
			if self.engine_ready[side] is True:
				running[side] = True
				threading.Thread(target=wrapper, args=(side,)).start()
			else:
				running[side] = False

		# best = -math.inf, None
		best = []
		while any(running.values()) or not que.empty():
			try:
				data = que.get(timeout=MAX_SEARCH_TIME+0.2)
			except queue.Empty:
				# Timeout, we probably sent a corrupted FEN string
				# Since the bot is stuck, we need to reset it

				break

			if data is None:
				# Thread finished
				continue

			side, (moves, (score, mate)) = data

			if moves[0] is False:
				# The engine didn't have enough time to find a move
				continue

			src, dst = self.move_to_index(moves[0], side) # We only care about the first move

			cell = self.board.index_to_coords(*src)
			piece = self.board[cell]
			if piece is not None and piece.team == self.team:
				# Move is for current team
				if mate:
					# Forced mate, technically no need to think anymore but it could be an illegal move so yeah
					heapq.heappush(best, (-math.inf, (src, dst)))
					# return src, dst
				else:
					if score > 0: #best[0]:
						# best = score, (src, dst)
						heapq.heappush(best, (-score, (src, dst)))
					# elif self.rotate_team(side) == self.team and score == best[0]:
					# 	# For two moves with equal scores, the one on our own side will be more accurate
					# 	best = score, (src, dst)
			else:
				# Something went wrong
				# print(f'Illegal move: {cell}->{self.board.index_to_coords(*dst)}')
				pass
				# Most likely just picked a piece from the opponent team currently merged with us on that side
				# Just ignore it and get the next move

		# if best[1] is None:
		# return best[1]
		while best:
			out = heapq.heappop(best)[1]
			yield out

		# Get a random move
		for move in self.iterate_random_moves():
			yield move

	def move_to_index(self, move, side):
		out = []
		for coords in (move[:2], move[2:]):
			if not coords.decode()[-1].isnumeric():
				coords = coords[:-1] # Sometim
			coords = self.boardpos_to_index(coords, side)
			out.append(coords)

		return out

	def boardpos_to_index(self, coords, side):
		if not isinstance(coords, str):
			coords = coords.decode()

		index = Vec2(self.board.coords_to_index(coords))
		# Convert back from normal 2 player board to a 3 player (rotated /!\) board

		if side == "W":
			if index.y >= 4:
				if index.x >= 4:
					# Just have to move the right side
					index.y += 4

		elif side == "B":
			if index.y < 4 and index.x > 4:
				# Send white half to red side
				index.x, index.y = 14-index.x, 7-index.y

		elif side == "R":
			if index.y < 4:
				if index.x < 4:
					# Send white half to black side
					index.x, index.y = 7-index.x, 7-index.y
			else:
				index.y += 4


		return self.rotate_coords(index)

	def rotate_coords(self, coords, team=None):
		# Rotate back the coordinates
		# rotations = "WBR".index(self.rotate_team(self.team)) # num of clockwise rotations
		rotations = "WBR".index(team or self.team)

		c = coords.copy()

		for i in range(rotations):
			if c.y < 4:
				# White -> Black
				c.y = 7 - c.y
				c.x = 7 - c.x
			elif c.y < 8:
				# Black -> Red
				c.y += 4
			else:
				# Red -> White
				c.x = 7-c.x
				c.y = 11 - c.y
				# c.x = 7 - c.x

		return c

	def board_to_fen(self, board=None):
		
		board = self.rotate_board(board)

		def iterator_white():
			yield None # Allies

			# Half of black side, half of red side
			for i in range(4):
				for off in (4, 8):
					for j in range(4):
						yield 3 - i + off, (j + off - 4)
				yield False, True

			# White side
			for i in range(4):
				for j in range(8):
					yield 3-i, j

				yield i == 3, True

		def iterator_black():
			yield 'R' # Allies

			# Black side
			for i in range(4):
				for j in range(8):
					yield 7 - i, j
				yield False, True
	 
			for i in range(4):
				# Half of white side
				for j in range(4):
					yield 3-i, j
				# Half of red side
				for j in range(4):
					yield 8 + i, 3 - j

				yield i == 3, True

		def iterator_red():
			yield 'B' # Allies

			# Red side
			for i in range(4):
				for j in range(8):
					yield 11 - i, j

				yield False, True

			for i in range(4):
				# Half of black side
				for j in range(4):
					yield 4 + i, 7 - j
				# Half of white side
				for j in range(4):
					yield 3 - i, j + 4

				yield i == 3, True

		iterators = dict(zip("WBR", [iterator_white, iterator_black, iterator_red]))

		out = []
		for side, iterator in iterators.items():
			board_repr = ""
			spaces = 0
			iterator = iterator()
			allies = next(iterator)
			if allies is not None:
				allies = self.rotate_team(allies)
			moves = []

			for i, j in iterator:
				if isinstance(i, bool):
					if j is True:
						if spaces > 0:
							board_repr += str(spaces)
							spaces = 0
						if i is False:
							board_repr += "/"
				else:
					cell = board[i][j]
					if cell is None:
						spaces += 1
					else:
						if spaces > 0:
							board_repr += str(spaces)
							spaces = 0

						piece, p_team = cell.type_short, cell.team
						if p_team == self.team or (allies is not None and p_team == allies):
							if p_team == self.team and side != self.team:
								moves.extend(self.get_moves(cell))

							piece = piece.upper()
						else:
							piece = piece.lower()  # Just in case

						board_repr += piece

			board_repr += " w"  # Always consider that it is white's turn

			# Castle
			board_repr += " -"  # KQkq

			# En passant
			board_repr += " -"  # e3

			# Halfmove / Fullmove counters
			board_repr += " 2 1"  # Stupid rule

			out.append((side, board_repr, moves))

		# for i in range(3):
		# 	print(out[i][1])
		return out

	def rotate_board(self, board=None):
		if board is None:
			board = self.board.board
		if self.team == "W":
			return board
		else:
			w, b, r = [board[4 * i : 4 * (i + 1)] for i in range(3)]
			rotate = lambda board: list(
				reversed(list(map(lambda e: list(reversed(e)), board)))
			)
			w = rotate(w)
			if self.team == "B":
				return rotate(b) + r + w
			elif self.team == "R":
				return rotate(r) + w + b

	def rotate_team(self, team):
		return "WBR"[sum(map(lambda s: "WBR".index(s), (team, self.team))) % 3]

	def get_moves(self, piece):
		def to_two_player_board(coords):
			team = dict(zip('WBR', 'WRB'))[self.team]
   
			if isinstance(coords, str):
				coords = self.board.coords_to_index(coords)

			if not isinstance(coords, Vec2):
				coords = Vec2(*coords)

			rot = self.rotate_coords(coords, team)

			# We can then assume that all moves are always seen as if it was white's turn (even if it's not true)

			if rot.y < 4:
				# White side
				return rot
			elif rot.y < 8:
				# Black side
				if rot.x < 4:
					# Left
					return rot
				else:
					# Right
					return False
			elif rot.y < 12:
				# Red side
				if rot.x < 4:
					# Left
					return False
				else:
					# Right
					rot.y -= 4
					return rot
			else:
				return False

		src = to_two_player_board(piece.pos)
		if src is False:
			return []
		src = self.board.index_to_coords(src.tuple(), two_players=True)

		moves = []

		for dst in piece.list_moves():
			dst = to_two_player_board(dst)
			if dst is not False:
				dst = self.board.index_to_coords(dst.tuple(), two_players=True)
				moves.append(src + dst)

		return moves

	def iterate_random_moves(self):
		best = []
		for piece in self.board.iterate():
			if piece.team == self.team:
				moves = piece.list_moves()
				if moves:
					for move in moves:
						new_board = self.board.copy()
						new_board.move(self.board.index_to_coords(piece.pos), move)
						score = self.get_board_score(new_board)
						heapq.heappush(best, (tuple(sorted([-s for _,s in score if s is not None])), (piece.pos, self.board.coords_to_index(move))))
		while best:
			score, move = heapq.heappop(best)
			yield move

	def get_board_score(self, board):
		boards = self.board_to_fen(board.board)
		que = queue.Queue()

		def wrapper(side):
			ok = False
			for moves in self.parse_commands(iterate=True, side=side, is_eval=True):
				que.put((side, moves))
				ok = True

			if ok is False:
				while self.engine_ready[side] is not True:
					# The engine crashed and is rebooting
					time.sleep(0.01)
				else:
					print('------------------Nothing returned!!', side)
				pass

			que.put(None)
			running[side] = False

		for side, board, moves in boards:
			self.engine_ready[side] = False
			if not ('k' in board and 'K' in board):
				# One king is missing, ignore this board
				# There will always be at least one board with both kings so it's fine
				continue

			self.write_command("ucinewgame", side)
			self.write_command("isready", side)
			self.wait_for_engine(side)

			cmd = "position fen " + board
			self.write_command(cmd, side=side)

			cmd = f"eval"
			self.write_command(
				cmd, side=side
			)  # To ensure that they all start at almost the same time

		running = {}
		for side in "WBR":
			if self.engine_ready[side] is True:
				running[side] = True
				threading.Thread(target=wrapper, args=(side,)).start()
			else:
				running[side] = False

		scores = []
		while any(running.values()) or not que.empty():
			try:
				data = que.get(timeout=MAX_SEARCH_TIME+0.2)
			except queue.Empty:
				# Timeout, we probably sent a corrupted FEN string
				# Since the bot is stuck, we need to reset it

				break

			if data is None:
				# Thread finished
				continue

			scores.append(data)

		return scores

if __name__ == "__main__":
	from board import Board

	board = Board()

	# Test mouvements du robot
	for team in 'WBR':
		bot = Bot(board, team)
		src, dst = list(map(lambda e: bot.board.index_to_coords(*e), bot.move_to_index('d2d4', team)))
		print(team, src, dst)


	# Test get_move
	move = bot.get_move() 

	# Test fonction boardpos_to_index: conversion d'un plateau deux joueurs en un plateau trois joueurs
	bots = {team: Bot(board, team) for team in 'WBR'}
	tests = [ #team, side, org, out
		['R', 'W', 'c2', 'f11'],
		['R', 'W', 'c4', 'f9'],
		['R', 'B', 'c2', 'f11'],
		['R', 'B', 'c4', 'f9'],
		['R', 'R', 'f2', 'j11'],
		['R', 'R', 'f4', 'j9'],
		['W', 'R', 'b3', 'k6'],
		['W', 'R', 'b6', 'k10'],
		['W', 'R', 'b5', 'k9'],
		['W', 'B', 'g5', 'k5'],
		['W', 'B', 'g6', 'k6'],
		['W', 'R', 'h5', 'h9'],
		['B', 'W', 'f3', 'c6'],
	]

	for team, side, org, out in tests:
		out2 = bots[team].board.index_to_coords(bots[team].boardpos_to_index(org, side))
		if out != out2:
			print(f"Error: {team}, {side}, {org}, {out} != {out2}")
			pass


	# Test iterate_random_moves()
	bot = bots['R']
	print(list(bot.iterate_random_moves()))
 
	print('All test passed!')
