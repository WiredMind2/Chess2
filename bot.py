import copy
import functools
from itertools import chain
import multiprocessing
import os
import queue
from subprocess import PIPE, STDOUT, Popen
from sys import platform
import threading
import time

from constants import MAX_SEARCH_TIME


class Bot:
	def __init__(self, board, team):
		self.board = board
		self.team = team

		if platform == "linux" or platform == "linux2":
			cmd = ['./stockfish/stockfish-ubuntu-x86-64-sse41-popcnt/stockfish/stockfish-ubuntu-x86-64-sse41-popcnt']
		elif platform == "win32":
			cmd = ['.\stockfish\stockfish-windows-x86-64-sse41-popcnt\stockfish\stockfish-windows-x86-64-sse41-popcnt.exe']
		elif platform == "darwin":
			raise OSError('Désolé, MacOS n\'est encore pas supporté.')

		cmd[0] = os.path.abspath(cmd[0])

		self.bot = None
		self.bots = {side: Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT) for side in 'WBR'}

		self.engine_ready = {side: False for side in 'WBR'}

		for side in 'WBR':
			self.start_bot(side)

		print('Ready!')

	def multi_bot(func):
		@functools.wraps(func)
		def wrapped(self, *args, side=None, **kwargs):
			
			reset = side is not None or self.bot is None
			if side is None and self.bot is None:
				out = []
				for bot in self.bots.values():
					self.bot = bot # That's ugly
					out.append(func(self, *args, **kwargs))
			else:
				if self.bot is None:
					self.bot = self.bots[side] # That's ugly, but a little bit better
				out = func(self, *args, **kwargs)

			if reset:
				self.bot = None

			return out
		return wrapped

	def start_bot(self, side):
		self.read_command(side) # Stockfish 16.1 by whatever
		self.write_command('uci', side=side)

		# self.write_command('setoption name UCI_Elo value 3190') # Make a monster
		self.write_command(f'setoption name Threads value {multiprocessing.cpu_count()//3}', side=side) # Make a MONSTER

		while not self.engine_ready[side]:
			self.parse_commands(side=side)

	def parse_commands(self, iterate=False, side=None):
		def iterator():
			while True:
				line = self.read_command(side=side) # id name whatever
				if len(line) == 0:
					continue

				if line is None:
					break

				cmd, *args = line.split(b' ', 1)
				args = args[0] if args else None


				if cmd == b'id':
					pass # IDC
				elif cmd == b'option':
					# if side == "W":
					# 	print(line.decode('utf-8'))
					pass # IDC
				elif cmd == b'uciok':
					self.write_command('ucinewgame', side)
					self.engine_ready[side] = True
					break # Engine is ready
				elif cmd == b'info':
					args = args.split(b' ')
					while args:
						key = args.pop(0)
						if key in {b'currmove', b'currmovenumber'}:
							args.pop(0)
							break # Just skip
						elif key == b'evaluation':
							# Ignore
							args.pop(0)
							args.pop(0)
						elif key == b'score':
							key2 = args.pop(0)
							if key2 in {b'cp', b'mate'}:
								args.pop(0) # ignore
							if args[0] in {b'lowerbound', b'upperbound'}:
								args.pop(0) # ignore
						elif key == b'pv':
							best = args
							if iterate:
								yield best
							break
						else:
							# Ignore
							args.pop(0)
				elif cmd == b'bestmove':
					best = args.split(b' ')
					if len(best) > 1:
						best = [best[0], best[2]] # Ponder move
					yield best
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

	def get_move(self):
		boards = self.board_to_fen()
		que = queue.Queue()

		def wrapper(side):
			for moves in self.parse_commands(iterate=True, side=side):
				que.put((side, moves))

			running[side] = False

		for side, board in boards:
			self.write_command('position ' + board, side=side)

			self.write_command(f'go movetime {MAX_SEARCH_TIME*1000}', side=side) # To ensure that they all start at almost the same time

		running = {}
		for side in 'WBR':
			threading.Thread(target=wrapper, args=(side,)).start()
			running[side] = True

		best = {}
		while all(running.values()):
			side, moves = que.get()
			best[side] = moves

		# TODO -> Exploit more data / score etc
		move = best['W'][0]

		return move

	def board_to_fen(self):
		board = self.rotate_board()

		def iterator_white():
			# White side
			for i in range(4):
				for j in range(8):
					yield i, j

			# Half of black side, half of red side
			for i in range(4):
				for off in (0, 4):
					for j in range(4):
						yield i+off+4, j+off

		def iterator_black():
			for i in range(4):
				# Half of white side
				for j in range(4):
					yield i, j
				# Half of red side
				for j in range(4):
					yield 11-i, 3-j

			# Black side
			for i in range(4):
				for j in range(8):
					yield i+4, j
     
		def iterator_red():
			for i in range(4):
				# Half of black side
				for j in range(4):
					yield 7-i, 7-j
				# Half of white side
				for j in range(4):
					yield i, j+4

			# Red side
			for i in range(4):
				for j in range(8):
					yield i+8, j

		iterators = dict(zip('WBR', [iterator_white, iterator_black, iterator_red]))

		out = []
		for side, iterator in iterators.items():
			board_repr = ''
			spaces = 0
			for i, j in iterator():
				cell = board[i][j]
				if cell is None:
					spaces += 1
				else:
					if spaces > 0:
						board_repr += str(spaces)
						spaces = 0
					piece, p_team = cell.type[0], cell.team
					if p_team == self.team:
						piece = piece.upper()
					else:
						piece = piece.lower() # Just in case

					board_repr += piece
			if spaces > 0:
				board_repr += str(spaces)

			board_repr += " w" # Always consider that it is white's turn

			# Castle -> TODO
			board_repr += " -" # KQkq

			# En passant -> TODO
			board_repr += " -" # e3
	
			# Halfmove / Fullmove counters
			board_repr += " 2 1" # Stupid rule

			out.append((side, board_repr))

		return out

	def rotate_board(self):
		if self.team == "W":
			return self.board.board
		elif self.team == "B": # TODO
			return 
		elif self.team == "R":
			return 

if __name__ == "__main__":
	from board import Board
	board = Board()
	bot = Bot(board, 'W')
	
	bot.get_move()