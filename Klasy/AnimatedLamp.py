import pygame
import os

class AnimatedLamp:
    def __init__(self, x, y, animation_speed=200, scale=1.0):
        """
        Animowana lampa ze świecznikami
    
        Args:
         x (int): pozycja X lampy
         y (int): pozycja Y lampy
            animation_speed (int): prędkość animacji w milisekundach między klatkami
            scale (float): skala wielkości (1.0 = normalna, 0.5 = połowa, 2.0 = podwójna)
        """
        self.x = x
        self.y = y
        self.animation_speed = animation_speed
        self.scale = scale
    
        # Ładowanie klatek animacji
        self.frames = []
        self.load_frames()
    
        # Stan animacji
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def load_frames(self):
        """Ładuje klatki animacji świecznika"""
        for i in range(1, 7):
            frame_path = f"assets/candelabrum_tall_{i}.png"
            if os.path.exists(frame_path):
                frame = pygame.image.load(frame_path).convert_alpha()
            
                # Skalowanie obrazu jeśli scale != 1.0
                if self.scale != 1.0:
                    original_size = frame.get_size()
                    new_size = (int(original_size[0] * self.scale), 
                            int(original_size[1] * self.scale))
                    frame = pygame.transform.scale(frame, new_size)
            
                self.frames.append(frame)
            else:
                print(f"Ostrzeżenie: Nie znaleziono pliku {frame_path}")
    
        if not self.frames:
            print("Błąd: Nie załadowano żadnych klatek animacji świecznika!")
            # Tworzymy pustą powierzchnię jako fallback
            size = int(64 * self.scale)
            empty_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            self.frames.append(empty_surface)
    
    def update(self):
        """Aktualizuje animację"""
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now
    
    def draw(self, surface, camera_x=0, camera_y=0):
        """
        Rysuje lampę na powierzchni
        
        Args:
            surface: powierzchnia pygame do rysowania
            camera_x: przesunięcie kamery X
            camera_y: przesunięcie kamery Y
        """
        if self.frames:
            # Pozycja na ekranie uwzględniająca kamerę
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y
            
            current_image = self.frames[self.current_frame]
            surface.blit(current_image, (screen_x, screen_y))
    
    def set_position(self, x, y):
        """Ustawia nową pozycję lampy"""
        self.x = x
        self.y = y
    
    def get_rect(self):
        """Zwraca prostokąt kolizji lampy"""
        if self.frames:
            current_image = self.frames[self.current_frame]
            return pygame.Rect(self.x, self.y, current_image.get_width(), current_image.get_height())
        return pygame.Rect(self.x, self.y, 64, 64)  # domyślny rozmiar
    
    def set_animation_speed(self, speed):
        """Zmienia prędkość animacji"""
        self.animation_speed = speed