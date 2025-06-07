import pygame
import math
import time
from config import *

class LoadingScreen:
    def __init__(self, username="Gracz"):
        self.username = username
        self.start_time = time.time()
        self.progress = 0
        self.max_progress = 100
        self.loading_speed = 25  # Procent na sekundę
        self.completed = False
        
        # Ciepła paleta kolorów
        self.warm_colors = {
            'bg_dark': (45, 35, 25),          # Ciemny brąz
            'bg_medium': (80, 60, 40),        # Średni brąz
            'accent_warm': (255, 180, 100),   # Ciepły pomarańczowy
            'accent_gold': (255, 215, 120),   # Złoty
            'accent_red': (220, 120, 80),     # Ciepły czerwony
            'text_cream': (255, 245, 230),    # Kremowy
            'text_warm': (255, 220, 180),     # Ciepły biały
            'glow_orange': (255, 140, 60),    # Pomarańczowe świecenie
            'particle_warm': (255, 160, 80),  # Ciepłe cząsteczki
            'progress_start': (255, 120, 60), # Początek paska (pomarańczowy)
            'progress_end': (255, 200, 100),  # Koniec paska (złoty)
            'shadow_warm': (30, 20, 10)      # Ciepły cień
        }
        
        # Animacje
        self.text_alpha = 255
        self.text_fade_direction = -2
        
        # Animacja klatek ładowania
        self.animation_frames = []
        self.current_frame = 0
        self.frame_time = 0
        self.frame_duration = 0.1  # 100ms na klatkę (10 FPS)
        self.load_animation_frames()
        
        # Teksty do wyświetlania podczas ładowania
        self.loading_messages = [
            "Rozpalanie ogniska przygód...",
            "Ładowanie ciepłych wspomnień...",
            "Przygotowywanie przytulnych pokoi...",
            "Konfiguracja Twojej postaci...",
            "Finalizowanie magicznych ustawień...",
            "Wszystko gotowe do przygody!"
        ]
        
        # Tło gradientowe
        self.create_gradient_background()
        
        # Czcionki
        try:
            self.title_font = pygame.font.Font("assets/Czcionka.ttf", 48)
            self.loading_font = pygame.font.Font("assets/Czcionka.ttf", 24)
            self.message_font = pygame.font.Font("assets/Czcionka.ttf", 18)
        except:
            self.title_font = pygame.font.SysFont(None, 48)
            self.loading_font = pygame.font.SysFont(None, 24)
            self.message_font = pygame.font.SysFont(None, 18)
    
    def load_animation_frames(self):
        """Ładuje klatki animacji ładowania z ciepłymi kolorami"""
        self.animation_frames = []
        for i in range(1, 11):  # klatkaladowania1.png do klatkaladowania10.png
            try:
                frame_path = f"assets/klatkaladowania{i}.png"
                frame = pygame.image.load(frame_path)
                # Opcjonalnie: przeskaluj klatkę do odpowiedniego rozmiaru
                frame = pygame.transform.scale(frame, (64, 64))
                self.animation_frames.append(frame)
            except pygame.error as e:
                print(f"Nie można załadować klatki {frame_path}: {e}")
                # W przypadku błędu, stwórz ciepły placeholder
                placeholder = pygame.Surface((64, 64))
                placeholder.fill(self.warm_colors['bg_medium'])
                
                # Rysuj ciepły spinner
                angle = (i * 36) % 360  # 36 stopni na klatkę
                center = (32, 32)
                
                # Zewnętrzny krąg
                pygame.draw.circle(placeholder, self.warm_colors['accent_warm'], center, 28, 3)
                # Wewnętrzny krąg
                pygame.draw.circle(placeholder, self.warm_colors['accent_gold'], center, 20, 2)
                
                # Obracający się element
                x = center[0] + 20 * math.cos(math.radians(angle))
                y = center[1] + 20 * math.sin(math.radians(angle))
                pygame.draw.circle(placeholder, self.warm_colors['accent_red'], (int(x), int(y)), 4)
                
                self.animation_frames.append(placeholder)
        
        # Jeśli nie udało się załadować żadnych klatek, stwórz ciepłą animację
        if not self.animation_frames:
            for i in range(10):
                placeholder = pygame.Surface((64, 64))
                placeholder.fill(self.warm_colors['bg_dark'])
                
                # Gradient od środka
                for radius in range(30, 5, -2):
                    intensity = (30 - radius) / 25
                    color = (
                        int(self.warm_colors['accent_warm'][0] * intensity),
                        int(self.warm_colors['accent_warm'][1] * intensity),
                        int(self.warm_colors['accent_warm'][2] * intensity)
                    )
                    pygame.draw.circle(placeholder, color, (32, 32), radius, 2)
                
                # Obracający się punkt
                angle = (i * 36) % 360
                x = 32 + 22 * math.cos(math.radians(angle))
                y = 32 + 22 * math.sin(math.radians(angle))
                pygame.draw.circle(placeholder, self.warm_colors['accent_gold'], (int(x), int(y)), 3)
                
                self.animation_frames.append(placeholder)
    
    def create_gradient_background(self):
        """Tworzy tło z ciepłym gradientem"""
        try:
            self.background = pygame.image.load("assets/loading_screen1.png").convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            # Jeśli nie ma obrazka, stwórz ciepły gradient
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                # Gradient od ciemnego brązu do ciepłego pomarańczowego
                r = int(self.warm_colors['bg_dark'][0] + ratio * (self.warm_colors['bg_medium'][0] - self.warm_colors['bg_dark'][0]))
                g = int(self.warm_colors['bg_dark'][1] + ratio * (self.warm_colors['bg_medium'][1] - self.warm_colors['bg_dark'][1]))
                b = int(self.warm_colors['bg_dark'][2] + ratio * (self.warm_colors['bg_medium'][2] - self.warm_colors['bg_dark'][2]))
                pygame.draw.line(self.background, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        play_button_width = SCREEN_WIDTH * 0.3
        play_button_height = SCREEN_HEIGHT * 0.07
        play_button_x = (SCREEN_WIDTH - play_button_width) // 2
        play_button_y = SCREEN_HEIGHT * 0.6

        quit_button_width = SCREEN_WIDTH * 0.3
        quit_button_height = SCREEN_HEIGHT * 0.07
        quit_button_x = (SCREEN_WIDTH - quit_button_width) // 2
        quit_button_y = SCREEN_HEIGHT * 0.7

        self.play_button = pygame.Rect(play_button_x, play_button_y, play_button_width, play_button_height)
        self.quit_button = pygame.Rect(quit_button_x, quit_button_y, quit_button_width, quit_button_height)
    
    def update(self, delta_time):
        """Aktualizuje stan ekranu ładowania"""
        # Aktualizuj postęp
        if self.progress < self.max_progress:
            self.progress += self.loading_speed * delta_time
            if self.progress >= self.max_progress:
                self.progress = self.max_progress
                self.completed = True
        
        # Animacja klatek
        self.frame_time += delta_time
        if self.frame_time >= self.frame_duration:
            self.frame_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
        
        # Animacja tekstu (pulsowanie)
        self.text_alpha += self.text_fade_direction
        if self.text_alpha <= 150:
            self.text_alpha = 150
            self.text_fade_direction = 2
        elif self.text_alpha >= 255:
            self.text_alpha = 255
            self.text_fade_direction = -2
    
    def get_current_message(self):
        """Zwraca aktualną wiadomość na podstawie postępu"""
        message_index = int((self.progress / self.max_progress) * len(self.loading_messages))
        if message_index >= len(self.loading_messages):
            message_index = len(self.loading_messages) - 1
        return self.loading_messages[message_index]
    
    def draw_loading_animation(self, center_x, center_y):
        """Rysuje animację ładowania z klatek"""
        if self.animation_frames:
            current_frame_surface = self.animation_frames[self.current_frame]
            frame_rect = current_frame_surface.get_rect(center=(center_x, center_y))
            screen.blit(current_frame_surface, frame_rect)
    
    def draw_progress_bar(self, x, y, width, height):
        """Rysuje ciepły pasek postępu"""
        # Cień paska
        shadow_rect = (x + 2, y + 2, width, height)
        pygame.draw.rect(screen, self.warm_colors['shadow_warm'], shadow_rect, border_radius=height//2)
        
        # Tło paska
        pygame.draw.rect(screen, self.warm_colors['bg_dark'], (x, y, width, height), border_radius=height//2)
        pygame.draw.rect(screen, self.warm_colors['accent_warm'], (x, y, width, height), 3, border_radius=height//2)
        
        # Wypełnienie paska z ciepłym gradientem
        fill_width = int((self.progress / self.max_progress) * width)
        if fill_width > 0:
            # Ciepły gradient w pasku postępu
            for i in range(fill_width):
                progress_ratio = i / width
                # Interpolacja między ciepłymi kolorami
                r = int(self.warm_colors['progress_start'][0] + progress_ratio * 
                       (self.warm_colors['progress_end'][0] - self.warm_colors['progress_start'][0]))
                g = int(self.warm_colors['progress_start'][1] + progress_ratio * 
                       (self.warm_colors['progress_end'][1] - self.warm_colors['progress_start'][1]))
                b = int(self.warm_colors['progress_start'][2] + progress_ratio * 
                       (self.warm_colors['progress_end'][2] - self.warm_colors['progress_start'][2]))
                
                pygame.draw.rect(screen, (r, g, b), (x + i, y + 2, 1, height - 4))
        
        # Procent w tekście
        percent_text = self.loading_font.render(f"{int(self.progress)}%", True, self.warm_colors['text_cream'])
        text_rect = percent_text.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(percent_text, text_rect)
    
    def draw_particles(self):
        """Rysuje ciepłe dekoracyjne cząsteczki w tle"""
        current_time = time.time() - self.start_time
        for i in range(25):
            # Pozycja cząsteczki oparta na czasie i indeksie
            x = (50 + i * 60 + current_time * 20) % (SCREEN_WIDTH + 100) - 50
            y = 100 + math.sin(current_time * 0.5 + i * 0.3) * 80 + i * 25
            
            if y < SCREEN_HEIGHT and y > 0:
                # Ciepłe, pulsujące cząsteczki
                alpha_base = 128 + math.sin(current_time * 2 + i) * 64
                size = 2 + int(math.sin(current_time * 1.5 + i * 0.5) * 1.5)
                
                # Różne odcienie ciepłych kolorów
                if i % 3 == 0:
                    color = (int(alpha_base), int(alpha_base * 0.7), int(alpha_base * 0.4))
                elif i % 3 == 1:
                    color = (int(alpha_base * 0.9), int(alpha_base * 0.8), int(alpha_base * 0.3))
                else:
                    color = (int(alpha_base * 0.8), int(alpha_base * 0.6), int(alpha_base * 0.2))
                
                pygame.draw.circle(screen, color, (int(x), int(y)), max(1, size))
                
                # Dodatkowy efekt świecenia dla niektórych cząsteczek
                if i % 5 == 0:
                    glow_color = (color[0] // 3, color[1] // 3, color[2] // 3)
                    pygame.draw.circle(screen, glow_color, (int(x), int(y)), size + 2)
    
    def draw(self):
        """Główna funkcja rysowania"""
        # Tło
        screen.blit(self.background, (0, 0))
        
        # Cząsteczki w tle
        self.draw_particles()
        
        # Tytuł z ciepłym efektem świecenia
        title_text = f"Witaj, {self.username}!"
        title_surface = self.title_font.render(title_text, True, self.warm_colors['text_cream'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Ciepły efekt świecenia
        glow_color = self.warm_colors['glow_orange']
        for offset in [(3, 3), (-3, -3), (3, -3), (-3, 3), (0, 3), (0, -3)]:
            glow_surface = self.title_font.render(title_text, True, glow_color)
            screen.blit(glow_surface, (title_rect.x + offset[0], title_rect.y + offset[1]))
        
        screen.blit(title_surface, title_rect)
        
        # Animacja ładowania
        animation_y = SCREEN_HEIGHT // 2 - 50
        self.draw_loading_animation(SCREEN_WIDTH // 2, animation_y)
        
        # Ciepły pasek postępu
        progress_bar_width = 400
        progress_bar_height = 30
        progress_x = SCREEN_WIDTH // 2 - progress_bar_width // 2
        progress_y = SCREEN_HEIGHT // 2 + 50
        self.draw_progress_bar(progress_x, progress_y, progress_bar_width, progress_bar_height)
        
        # Aktualna wiadomość ładowania z ciepłym pulsowaniem
        current_message = self.get_current_message()
        message_surface = self.message_font.render(current_message, True, self.warm_colors['text_warm'])
        message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, progress_y + 60))
        
        # Efekt pulsowania z ciepłymi kolorami
        pulse_scale = 1.0 + (self.text_alpha - 200) / 1000
        if pulse_scale != 1.0:
            scaled_size = (int(message_surface.get_width() * pulse_scale), 
                          int(message_surface.get_height() * pulse_scale))
            message_surface = pygame.transform.scale(message_surface, scaled_size)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, progress_y + 60))
        
        screen.blit(message_surface, message_rect)
        
        # Dodatkowe informacje na dole z ciepłym kolorem
        if self.progress > 80:
            tip_text = "Przygotuj się na ciepłą przygodę w magicznym świecie!"
            tip_surface = self.message_font.render(tip_text, True, self.warm_colors['accent_gold'])
            tip_rect = tip_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(tip_surface, tip_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Główna pętla ekranu ładowania"""
        clock = pygame.time.Clock()
        
        while not self.completed:
            delta_time = clock.tick(60) / 1000.0
            
            # Obsługa zdarzeń (pozwól na zamknięcie gry)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
            
            self.update(delta_time)
            self.draw()
        
        # Po zakończeniu ładowania, pokaż przez chwilę komunikat "Gotowe!"
        time.sleep(0.5)
        return True