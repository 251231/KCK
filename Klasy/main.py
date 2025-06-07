from config import *
from StartScreen import StartScreen
from Game import Game
from Menu import menu_logowania
from LoadingScreen import LoadingScreen
from MusicManager import MusicManager

if __name__ == "__main__":
    start_screen = StartScreen()
    music_manager = MusicManager()
    
    # Przykładowe użycie (odkomentuj gdy masz pliki audio)
    
    # Ładowanie i odtwarzanie muzyki tła
    music_manager.load_music("assets/GameDziekanat_sound2.mp3")
    music_manager.set_music_volume(0.1)
    music_manager.set_sfx_volume(0.1)
    music_manager.play_music()
   
    
    
   
    
    start_screen.run()
    username = menu_logowania("assets/LoginMenu.png")
    if username:  # Jeśli użytkownik się zalogował
        # Ekran ładowania
        loading_screen = LoadingScreen(username)
        if loading_screen.run():  # Jeśli ładowanie zakończone sukcesem
            # Główna gra
            music_manager.load_music("assets/GameDziekanat_sound1.mp3")
            music_manager.set_music_volume(0.1)
            music_manager.set_sfx_volume(0.1)
            music_manager.play_music()
            game = Game(username)
            game.run()
    music_manager.cleanup()
    pygame.quit()
