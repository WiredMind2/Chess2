import enum

BOARD_SIZE = 8

# PGN notation: K (king), Q (queen), R (rook), B (bishop), N (knight), P (pawn)
START_ROWS = ('RNBKQBNR', 'PPPPPPPP')
COLORS = {'W': ('#ffffff', '#000000'), 'B': ('#000000', '#ffffff'), 'R': ('#000000', '#ff0000')} # Not used
TEAMS = {'W': 'White', 'B': 'Black', 'R': 'Red'}

POPUP_SIZE = (500, 100)

# For how long can the engine compute the best move
MAX_SEARCH_TIME = 1 # seconds

class Dir(enum.Enum):
	UP = 0
	DOWN = 1
	LEFT = 2
	RIGHT = 3
 
REVERSE = {Dir.UP: Dir.DOWN, Dir.LEFT: Dir.RIGHT, Dir.DOWN: Dir.UP, Dir.RIGHT: Dir.LEFT}

SCREEN_SIZE = (1280, 720)
