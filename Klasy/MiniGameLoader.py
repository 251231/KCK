import pygame
import math
import time
from config import *

class MiniGameLoader:
    def __init__(self, game_name, player_name="Gracz"):
        self.game_name = game_name
        self.player_name = player_name
        self.start_time = time.time()
        self.progress = 0
        self.max_progress = 100
        self.loading_speed = 80  # Szybsze ładowanie dla minigier
        self.completed = False
        
        # Ciepła paleta kolorów (taka sama jak w głównym loaderze)
        self.warm_colors = {
            'bg_dark': (45, 35, 25),
            'bg_medium': (80, 60, 40),
            'accent_warm': (255, 180, 100),
            'accent_gold': (255, 215, 120),
            'accent_red': (220, 120, 80),
            'text_cream': (255, 245, 230),
            'text_warm': (255, 220, 180),
            'glow_orange': (255, 140, 60),
            'particle_warm': (255, 160, 80),
            'progress_start': (255, 120, 60),
            'progress_end': (255, 200, 100),
            'shadow_warm': (30, 20, 10)
        }
        
        # Różne teksty dla różnych minigier
        self.game_messages = {
            "dice": [
                "Przygotowywanie kostek...",
                "Aktywowanie szczęścia...",
                "Konfiguracja stołu do gry...",
                "Gotowe do rzutu!"
            ],
            "cups": [
                "Ustawianie kubków...",
                "Chowanie piłeczki...",
                "Mieszanie kubków...",
                "Czas na zgadywanie!"
            ],
            "wheel": [
                "Przygotowywanie koła fortuny...",
                "Smarowanie łożysk...",
                "Kalibracja nagród...",
                "Koło gotowe do kręcenia!"
            ]
        }
        
        # Animacje
        self.text_alpha = 255
        self.text_fade_direction = -2
        self.rotation_angle = 0
        
        # Tło gradientowe
        self.create_gradient_background()
        
        # Czcionki
        try:
            self.title_font = pygame.font.Font("assets/Czcionka.ttf", 36)
            self.loading_font = pygame.font.Font("assets/Czcionka.ttf", 20)
            self.message_font = pygame.font.Font("assets/Czcionka.ttf", 16)
        except:
            self.title_font = pygame.font.SysFont(None, 36)
            self.loading_font = pygame.font.SysFont(None, 20)
            self.message_font = pygame.font.SysFont(None, 16)
    
    def create_gradient_background(self):
        """Tworzy ciemniejsze tło z ciepłym gradientem dla minigier"""
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            # Ciemniejszy gradient dla minigier
            dark_color = (25, 20, 15)
            medium_color = (50, 40, 30)
            r = int(dark_color[0] + ratio * (medium_color[0] - dark_color[0]))
            g = int(dark_color[1] + ratio * (medium_color[1] - dark_color[1]))
            b = int(dark_color[2] + ratio * (medium_color[2] - dark_color[2]))
            pygame.draw.line(self.background, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def update(self, delta_time):
        """Aktualizuje stan ekranu ładowania"""
        # Aktualizuj postęp
        if self.progress < self.max_progress:
            self.progress += self.loading_speed * delta_time
            if self.progress >= self.max_progress:
                self.progress = self.max_progress
                self.completed = True
        
        # Animacja tekstu (pulsowanie)
        self.text_alpha += self.text_fade_direction
        if self.text_alpha <= 150:
            self.text_alpha = 150
            self.text_fade_direction = 2
        elif self.text_alpha >= 255:
            self.text_alpha = 255
            self.text_fade_direction = -2
        
        # Animacja rotacji
        self.rotation_angle += 120 * delta_time  # 120 stopni na sekundę
        if self.rotation_angle >= 360:
            self.rotation_angle -= 360
    
    def get_current_message(self):
        """Zwraca aktualną wiadomość na podstawie postępu"""
        messages = self.game_messages.get(self.game_name, ["Ładowanie gry..."])
        message_index = int((self.progress / self.max_progress) * len(messages))
        if message_index >= len(messages):
            message_index = len(messages) - 1
        return messages[message_index]
    
    def draw_loading_spinner(self, center_x, center_y):
        """Rysuje obracający się spinner specyficzny dla minigry"""
        if self.game_name == "dice":
            # Rysuj kostki
            size = 25
            for i, offset in enumerate([(0, 0), (30, 0), (-30, 0)]):
                x = center_x + offset[0]
                y = center_y + offset[1] + math.sin(time.time() * 3 + i) * 5
                
                # Kostka
                dice_rect = pygame.Rect(x - size//2, y - size//2, size, size)
                pygame.draw.rect(screen, self.warm_colors['accent_warm'], dice_rect, border_radius=5)
                pygame.draw.rect(screen, self.warm_colors['accent_gold'], dice_rect, 2, border_radius=5)
                
                # Kropki na kostce
                dots = [(x, y)] if i == 0 else [(x-5, y-5), (x+5, y+5)] if i == 1 else [(x-7, y-7), (x, y), (x+7, y+7)]
                for dot_x, dot_y in dots:
                    pygame.draw.circle(screen, self.warm_colors['text_cream'], (int(dot_x), int(dot_y)), 2)
        
        elif self.game_name == "cups":
            # Rysuj kubki
            for i in range(3):
                angle = self.rotation_angle + i * 120
                x = center_x + 25 * math.cos(math.radians(angle))
                y = center_y + 25 * math.sin(math.radians(angle))
                
                # Kubek
                cup_points = [
                    (x - 10, y + 15),
                    (x + 10, y + 15),
                    (x + 8, y - 15),
                    (x - 8, y - 15)
                ]
                pygame.draw.polygon(screen, self.warm_colors['accent_warm'], cup_points)
                pygame.draw.polygon(screen, self.warm_colors['accent_gold'], cup_points, 2)
        
        elif self.game_name == "wheel":
            # Rysuj koło fortuny
            radius = 35
            segments = 8
            for i in range(segments):
                start_angle = (i * 45 + self.rotation_angle) % 360
                end_angle = ((i + 1) * 45 + self.rotation_angle) % 360
                
                color = self.warm_colors['accent_warm'] if i % 2 == 0 else self.warm_colors['accent_gold']
                
                # Rysuj segment koła
                points = [
                    (center_x, center_y),
                    (center_x + radius * math.cos(math.radians(start_angle)),
                     center_y + radius * math.sin(math.radians(start_angle))),
                    (center_x + radius * math.cos(math.radians(end_angle)),
                     center_y + radius * math.sin(math.radians(end_angle)))
                ]
                pygame.draw.polygon(screen, color, points)
            
            # Środek koła
            pygame.draw.circle(screen, self.warm_colors['accent_red'], (center_x, center_y), 8)
        
        else:
            # Domyślny spinner
            for i in range(8):
                angle = self.rotation_angle + i * 45
                length = 20 + 10 * math.sin(math.radians(angle * 2))
                x = center_x + length * math.cos(math.radians(angle))
                y = center_y + length * math.sin(math.radians(angle))
                
                alpha = int(255 * (0.3 + 0.7 * (i / 7)))
                color = (*self.warm_colors['accent_warm'], alpha)
                pygame.draw.circle(screen, color[:3], (int(x), int(y)), 4)
    
    def draw_progress_bar(self, x, y, width, height):
        """Rysuje mniejszy pasek postępu dla minigier"""
        border_radius = height // 2
        
        # Cień paska
        shadow_rect = (x + 2, y + 2, width, height)
        pygame.draw.rect(screen, self.warm_colors['shadow_warm'], shadow_rect, border_radius=border_radius)
        
        # Tło paska
        pygame.draw.rect(screen, self.warm_colors['bg_dark'], (x, y, width, height), border_radius=border_radius)
        pygame.draw.rect(screen, self.warm_colors['accent_warm'], (x, y, width, height), 2, border_radius=border_radius)
        
        # Wypełnienie paska
        fill_width = int((self.progress / self.max_progress) * width)
        if fill_width > 0:
            progress_ratio = self.progress / self.max_progress
            r = int(self.warm_colors['progress_start'][0] + progress_ratio * 
                   (self.warm_colors['progress_end'][0] - self.warm_colors['progress_start'][0]))
            g = int(self.warm_colors['progress_start'][1] + progress_ratio * 
                   (self.warm_colors['progress_end'][1] - self.warm_colors['progress_start'][1]))
            b = int(self.warm_colors['progress_start'][2] + progress_ratio * 
                   (self.warm_colors['progress_end'][2] - self.warm_colors['progress_start'][2]))
            
            fill_color = (r, g, b)
            pygame.draw.rect(screen, fill_color, (x, y, fill_width, height), border_radius=border_radius)
        
        # Procent w tekście (mniejszy)
        percent_text = self.message_font.render(f"{int(self.progress)}%", True, self.warm_colors['text_cream'])
        text_rect = percent_text.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(percent_text, text_rect)
    
    def draw(self):
        """Główna funkcja rysowania"""
        # Tło
        screen.blit(self.background, (0, 0))
        
        # Delikatne cząsteczki w tle
        current_time = time.time() - self.start_time
        for i in range(15):
            x = (30 + i * 80 + current_time * 15) % (SCREEN_WIDTH + 50) - 25
            y = 80 + math.sin(current_time * 0.8 + i * 0.4) * 60 + i * 30
            
            if 0 < y < SCREEN_HEIGHT:
                alpha = 100 + math.sin(current_time * 1.5 + i) * 50
                size = 1 + int(math.sin(current_time + i * 0.3))
                color = (int(alpha * 0.8), int(alpha * 0.6), int(alpha * 0.3))
                pygame.draw.circle(screen, color, (int(x), int(y)), max(1, size))
        
        # Tytuł gry
        game_titles = {
            "dice": "Gra w Kości",
            "cups": "Gra w Kubki", 
            "wheel": "Koło Fortuny"
        }
        
        title_text = game_titles.get(self.game_name, "Minigra")
        title_surface = self.title_font.render(title_text, True, self.warm_colors['text_cream'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        
        # Efekt świecenia
        glow_color = self.warm_colors['glow_orange']
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_surface = self.title_font.render(title_text, True, glow_color)
            screen.blit(glow_surface, (title_rect.x + offset[0], title_rect.y + offset[1]))
        
        screen.blit(title_surface, title_rect)
        
        # Spinner specyficzny dla gry
        spinner_y = SCREEN_HEIGHT // 2 - 30
        self.draw_loading_spinner(SCREEN_WIDTH // 2, spinner_y)
        
        # Mniejszy pasek postępu
        progress_bar_width = 300
        progress_bar_height = 20
        progress_x = SCREEN_WIDTH // 2 - progress_bar_width // 2
        progress_y = SCREEN_HEIGHT // 2 + 40
        self.draw_progress_bar(progress_x, progress_y, progress_bar_width, progress_bar_height)
        
        # Wiadomość ładowania z pulsowaniem
        current_message = self.get_current_message()
        message_surface = self.message_font.render(current_message, True, self.warm_colors['text_warm'])
        message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, progress_y + 40))
        
        # Efekt pulsowania
        pulse_scale = 1.0 + (self.text_alpha - 200) / 1500
        if pulse_scale != 1.0:
            scaled_size = (int(message_surface.get_width() * pulse_scale), 
                          int(message_surface.get_height() * pulse_scale))
            message_surface = pygame.transform.scale(message_surface, scaled_size)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, progress_y + 40))
        
        screen.blit(message_surface, message_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Główna pętla ekranu ładowania minigry"""
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
        
        # Krótka pauza po zakończeniu
        time.sleep(0.3)
        return True