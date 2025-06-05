from config import *
from StartScreen import StartScreen
from Game import Game
from Menu import menu_logowania

if __name__ == "__main__":
    start_screen = StartScreen()
    start_screen.run()
    username = menu_logowania("assets/LoginMenu.png")
    game = Game(username)
    game.run()
    pygame.quit()
