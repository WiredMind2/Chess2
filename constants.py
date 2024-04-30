import enum

BOARD_SIZE = 8

# PGN notation: K (king), Q (queen), R (rook), B (bishop), N (knight), P (pawn)
START_ROWS = ('RNBKQBNR', 'PPPPPPPP')

# For how long can the engine compute the best move
MAX_SEARCH_TIME = 5 # seconds

class Dir(enum.Enum):
	UP = 0
	DOWN = 1
	LEFT = 2
	RIGHT = 3
 
REVERSE = {Dir.UP: Dir.DOWN, Dir.LEFT: Dir.RIGHT, Dir.DOWN: Dir.UP, Dir.RIGHT: Dir.LEFT}
 