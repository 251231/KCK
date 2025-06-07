from config import *
from StartScreen import StartScreen
from Game import Game
from Menu import menu_logowania
from LoadingScreen import LoadingScreen


if __name__ == "__main__":
    start_screen = StartScreen()
    start_screen.run()
    username = menu_logowania("assets/LoginMenu.png")
    if username:  # Jeśli użytkownik się zalogował
        # Ekran ładowania
        loading_screen = LoadingScreen(username)
        if loading_screen.run():  # Jeśli ładowanie zakończone sukcesem
            # Główna gra
            game = Game(username)
            game.run()
    
    pygame.quit()
