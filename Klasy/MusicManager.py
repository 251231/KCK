import pygame
import os
from typing import Dict, Optional

class MusicManager:
    def __init__(self):
       
        pygame.mixer.init()
        self.current_music: Optional[str] = None
        self.music_volume: float = 0.7
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}
        self.sfx_volume: float = 0.5
        self.is_music_paused: bool = False
        
    def load_music(self, filepath: str) -> bool:
        
        try:
            if os.path.exists(filepath):
                pygame.mixer.music.load(filepath)
                self.current_music = filepath
                return True
            else:
                print(f"Plik {filepath} nie istnieje")
                return False
        except pygame.error as e:
            print(f"Błąd ładowania muzyki: {e}")
            return False
    
    def play_music(self, loops: int = -1, start: float = 0.0) -> bool:
       
        try:
            pygame.mixer.music.play(loops, start)
            self.is_music_paused = False
            return True
        except pygame.error as e:
            print(f"Błąd odtwarzania muzyki: {e}")
            return False
    
    def stop_music(self):
       
        pygame.mixer.music.stop()
        self.is_music_paused = False
    
    def pause_music(self):
   
        pygame.mixer.music.pause()
        self.is_music_paused = True
    
    def unpause_music(self):
       
        pygame.mixer.music.unpause()
        self.is_music_paused = False
    
    def set_music_volume(self, volume: float):
       
        volume = max(0.0, min(1.0, volume))  # Ograniczenie do zakresu 0-1
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)
    
    def get_music_volume(self) -> float:
       
        return self.music_volume
    
    def is_music_playing(self) -> bool:
        
        return pygame.mixer.music.get_busy() and not self.is_music_paused
    
    def load_sound_effect(self, name: str, filepath: str) -> bool:
        
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self.sfx_volume)
                self.sound_effects[name] = sound
                return True
            else:
                print(f"Plik {filepath} nie istnieje")
                return False
        except pygame.error as e:
            print(f"Błąd ładowania efektu dźwiękowego: {e}")
            return False
    
    def play_sound_effect(self, name: str, loops: int = 0) -> bool:
        
        if name in self.sound_effects:
            try:
                self.sound_effects[name].play(loops)
                return True
            except pygame.error as e:
                print(f"Błąd odtwarzania efektu: {e}")
                return False
        else:
            print(f"Efekt dźwiękowy '{name}' nie został załadowany")
            return False
    
    def stop_sound_effect(self, name: str):
       
        if name in self.sound_effects:
            self.sound_effects[name].stop()
    
    def stop_all_sound_effects(self):
        
        for sound in self.sound_effects.values():
            sound.stop()
    
    def set_sfx_volume(self, volume: float):
        
        volume = max(0.0, min(1.0, volume))
        self.sfx_volume = volume
        for sound in self.sound_effects.values():
            sound.set_volume(volume)
    
    def get_sfx_volume(self) -> float:
        
        return self.sfx_volume
    
    def cleanup(self):
        """Czyści zasoby audio"""
        self.stop_music()
        self.stop_all_sound_effects()
        self.sound_effects.clear()
        pygame.mixer.quit()


    