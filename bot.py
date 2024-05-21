import functools
import multiprocessing
import os
import queue
from subprocess import PIPE, STDOUT, Popen
from sys import platform
import threading

from constants import MAX_SEARCH_TIME
from mouv import Vec2


class Bot:
	def __init__(self, board, team):
		self.board: Board = board
		self.team = team

		if platform == "linux" or platform == "linux2":
			cmd = [
				"./stockfish/stockfish-ubuntu-x86-64-sse41-popcnt/stockfish/stockfish-ubuntu-x86-64-sse41-popcnt"
			]
		elif platform == "win32":
			cmd = [
				".\stockfish\stockfish-windows-x86-64-sse41-popcnt\stockfish\stockfish-windows-x86-64-sse41-popcnt.exe"
			]
		elif platform == "darwin":
			raise OSError("Désolé, MacOS n'est encore pas supporté.")

		cmd[0] = os.path.abspath(cmd[0])

		self.bot = None
		self.bots = {
			side: Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT) for side in "WBR"
		}

		self.engine_ready = {side: False for side in "WBR"}
  
		self.moves = {side: [] for side in "WBR"}

		for side in "WBR":
			self.start_bot(side)

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

	def start_bot(self, side):
		self.read_command(side)  # Stockfish 16.1 by whatever
		self.write_command("uci", side=side)

		# self.write_command('setoption name UCI_Elo value 3190') # Make a monster?
		self.write_command(
			f"setoption name Threads value {multiprocessing.cpu_count()//3}", side=side
		)  # Make a MONSTER

		self.wait_for_engine(side, uci=True)

	def parse_commands(self, iterate=False, side=None):
		def iterator():
			scores = {}
			while True:
				line = self.read_command(side=side)  # id name whatever

				if len(line) == 0:
					continue

				print('[STOCKFISH stdout]', side, line.decode())

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

							if args[0] in {b"lowerbound", b"upperbound"}:
								args.pop(0)  # ignore

						elif key == b"pv":
							best = args
							if scores.get('cached', None) is not None:
								scores[best[0]] = scores['cached']
								scores['cached'] = None

							if iterate:
								yield best, scores.get(best[0], None)
							break

						else:
							# Ignore
							args.pop(0)

				elif cmd == b"bestmove":
					best = args.split(b" ")
					if len(best) > 1:
						best = [best[0], best[2]]  # Ponder move

					yield best, scores.get(best[0], None)
					break

				else:
					print(line)
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

	def wait_for_engine(self, side, uci=False):
		value = "uci" if uci else True
		while self.engine_ready[side] != value:
			self.parse_commands(side=side)

	def get_move(self):
		boards = self.board_to_fen()
		que = queue.Queue()

		def wrapper(side):
			for moves in self.parse_commands(iterate=True, side=side):
				que.put((side, moves))

			que.put(None)
			running[side] = False

		for side, board in boards:
			self.engine_ready[side] = False
			self.write_command("ucinewgame", side)
			self.write_command("isready", side)
			self.wait_for_engine(side)

			self.write_command("position " + board, side=side)

			self.write_command(
				f"go movetime {MAX_SEARCH_TIME*100}", side=side
			)  # To ensure that they all start at almost the same time

		running = {}
		for side in "WBR":
			running[side] = True
			threading.Thread(target=wrapper, args=(side,)).start()

		best = 0, None
		while any(running.values()):
			data = que.get()
			if data is None:
				# Thread returned nothing
				continue

			side, (moves, (score, mate)) = data

			src, dst = self.move_to_index(moves[0], side) # We only care about the first move

			cell = self.board.index_to_coords(*src)
			piece = self.board[cell]
			if piece is not None and piece.team == self.team:
				# Move is for current team
				if mate:
					# Forced mate, no need to think anymore
					return src, dst
				else:
					if score > best[0]:
						best = score, (src, dst)
					elif self.rotate_team(side) == self.team and score == best[0]:
						# For two moves with equal scores, the one on our own side will be more accurate
						best = score, (src, dst)
			else:
				# Something went wrong
				pass
		return best[1] or (None, None)

	def move_to_index(self, move, side):
		out = []
		move = move.decode()
		for coords in (move[:2], move[2:]):
			coords = Vec2(self.board.coords_to_index(coords))
			# Convert back from normal 2 player board to a 3 player (rotated /!\) board
			if coords.y > 4:
				if coords.x < 4:
					# Black
					coords.x = 7 - coords.x
				else:
					# White
					coords.x = 11 - coords.x

			# Rotate back the coordinates
			# rotations = "WBR".index(self.rotate_team(self.team)) # num of clockwise rotations
			rotations = "WBR".index(self.team)

			for i in range(rotations):
				if coords.y < 4:
					# White -> Black
					coords.y = 7 - coords.y
					# TODO (?) Swap sides?
				elif coords.y < 8:
					# Black -> Red
					coords.y += 4
				else:
					# Red -> White
					coords.y = 11 - coords.y

			out.append(coords)

		return out

	def board_to_fen(self):
		board = self.rotate_board()

		def iterator_white():
			yield None # Allies

			# Half of black side, half of red side
			for i in range(4):
				for off in (4, 8):
					for j in range(4):
						yield 3 - i + off, 11 - (j + off)
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

		iterators = dict(zip(map(self.rotate_team, "WBR"), [iterator_white, iterator_black, iterator_red]))

		out = []
		for side, iterator in iterators.items():
			board_repr = ""
			spaces = 0
			iterator = iterator()
			allies = next(iterator)
			if allies is not None:
				allies = self.rotate_team(allies)

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
							piece = piece.upper()
						else:
							piece = piece.lower()  # Just in case

						board_repr += piece

			board_repr += " w"  # Always consider that it is white's turn

			# Castle -> TODO
			board_repr += " -"  # KQkq

			# En passant -> TODO
			board_repr += " -"  # e3

			# Halfmove / Fullmove counters
			board_repr += " 2 1"  # Stupid rule

			out.append((side, board_repr))

		# for i in range(3):
		# 	print(out[i][1])
		return out

	def rotate_board(self):
		if self.team == "W":
			return self.board.board
		else:
			w, b, r = [self.board.board[4 * i : 4 * (i + 1)] for i in range(3)]
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

if __name__ == "__main__":
	from board import Board

	board = Board()
	bot = Bot(board, "B")

	move = bot.get_move()
	pass
