import pygame

# couleur
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
# coordonnées pour les buttons
start_button_rect = pygame.Rect(281, 280, 150, 50)
red_choice_rect = pygame.Rect(600, 310, 20, 20)
black_choice_rect = pygame.Rect(600, 373, 20, 20)
white_choice_rect = pygame.Rect(600, 433, 20, 20)

class MainMenu:
	def __init__(self) -> None:
		pygame.init()

		# Désigne la screen
		self.screen = pygame.display.set_mode((685, 465))

		self.background = pygame.image.load('assets/game start page.png')

		self.running = True
		self.settings = {'W': True, 'B': False, 'R': False}

	def draw_screen(self):
		self.screen.fill(WHITE)
		self.screen.blit(self.background, (0, 0))
		
		# Start
		# pygame.draw.rect(screen, RED, start_button_rect)
		
		# Dessiner une boîte de sélection
		pygame.draw.rect(self.screen, BLACK, red_choice_rect, 2)
		pygame.draw.rect(self.screen, BLACK, black_choice_rect, 2)
		pygame.draw.rect(self.screen, BLACK, white_choice_rect, 2)
		
		# Afficher l'état de la case à cocher
		cases = [
			('R', red_choice_rect),
			('B', black_choice_rect),
			('W', white_choice_rect),
		]
		for team, rect in cases:
			col = BLACK if self.settings[team] else WHITE
			pygame.draw.circle(self.screen, col, rect.center, 10)

		pygame.display.flip()

	def start(self):
		actions = [
			(start_button_rect, self.start_game),
			(white_choice_rect, self.change_settings('W')),
			(black_choice_rect, self.change_settings('B')),
			(red_choice_rect, self.change_settings('R')),
		]
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					self.running = False
				
				if event.type == pygame.MOUSEBUTTONDOWN:
					for rect, action in actions:
						if rect.collidepoint(event.pos):
							action()

			self.draw_screen()
		return self.settings

	def change_settings(self, team):
		def wrapper():
			self.settings[team] = not self.settings[team]
		return wrapper

	def start_game(self):
		print("Game started with settings:", self.settings)
		self.running = False


if __name__ == "__main__":
	main_menu = MainMenu()
	main_menu.start()