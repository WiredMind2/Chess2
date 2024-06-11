import GUI
from main_menu import MainMenu

if __name__ == "__main__":
	main_menu = MainMenu()
	teams = main_menu.start()
 
	gui = GUI.GUI(teams)
	gui.start()