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
        
        # Animacje
        self.spinner_angle = 0
        self.text_alpha = 255
        self.text_fade_direction = -2
        
        # Teksty do wyświetlania podczas ładowania
        self.loading_messages = [
            "Inicjalizacja świata gry...",
            "Ładowanie zasobów...",
            "Przygotowywanie pokoi...",
            "Konfiguracja gracza...",
            "Finalizowanie ustawień...",
            "Wszystko gotowe!"
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
    
    def create_gradient_background(self):
        """Tworzy tło z gradientem"""
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            # Gradient od ciemnego niebieskiego do czarnego
            color_value = int(30 + (y / SCREEN_HEIGHT) * 20)
            blue_value = int(60 + (y / SCREEN_HEIGHT) * 40)
            color = (color_value, color_value, blue_value)
            pygame.draw.line(self.background, color, (0, y), (SCREEN_WIDTH, y))
    
    def update(self, delta_time):
        """Aktualizuje stan ekranu ładowania"""
        # Aktualizuj postęp
        if self.progress < self.max_progress:
            self.progress += self.loading_speed * delta_time
            if self.progress >= self.max_progress:
                self.progress = self.max_progress
                self.completed = True
        
        # Animacja spinnera
        self.spinner_angle += 180 * delta_time  # 180 stopni na sekundę
        if self.spinner_angle >= 360:
            self.spinner_angle -= 360
        
        # Animacja tekstu (pulsowanie)
        self.text_alpha += self.text_fade_direction
        if self.text_alpha <= 100:
            self.text_alpha = 100
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
    
    def draw_spinner(self, center_x, center_y, radius=30):
        """Rysuje animowany spinner ładowania"""
        # Główny okrąg
        pygame.draw.circle(screen, (100, 100, 150), (center_x, center_y), radius, 3)
        
        # Animowany łuk
        points = []
        for i in range(8):
            angle = math.radians(self.spinner_angle + i * 45)
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            alpha = 255 - (i * 30)  # Fade effect
            if alpha > 0:
                color = (150 + alpha // 3, 150 + alpha // 3, 255)
                pygame.draw.circle(screen, color, (int(x), int(y)), 4)
    
    def draw_progress_bar(self, x, y, width, height):
        """Rysuje pasek postępu"""
        # Tło paska
        pygame.draw.rect(screen, (50, 50, 80), (x, y, width, height), border_radius=height//2)
        pygame.draw.rect(screen, (100, 100, 150), (x, y, width, height), 3, border_radius=height//2)
        
        # Wypełnienie paska
        fill_width = int((self.progress / self.max_progress) * width)
        if fill_width > 0:
            # Gradient w pasku postępu
            for i in range(fill_width):
                progress_ratio = i / width
                color_r = int(50 + progress_ratio * 100)
                color_g = int(150 + progress_ratio * 50)
                color_b = int(255 - progress_ratio * 50)
                pygame.draw.rect(screen, (color_r, color_g, color_b), 
                               (x + i, y + 2, 1, height - 4))
        
        # Procent w tekście
        percent_text = self.loading_font.render(f"{int(self.progress)}%", True, WHITE)
        text_rect = percent_text.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(percent_text, text_rect)
    
    def draw_particles(self):
        """Rysuje dekoracyjne cząsteczki w tle"""
        current_time = time.time() - self.start_time
        for i in range(20):
            # Pozycja cząsteczki oparta na czasie i indeksie
            x = (50 + i * 60 + current_time * 30) % (SCREEN_WIDTH + 100) - 50
            y = 100 + math.sin(current_time + i) * 50 + i * 20
            
            if y < SCREEN_HEIGHT:
                alpha = int(128 + math.sin(current_time * 2 + i) * 64)
                size = 2 + int(math.sin(current_time + i * 0.5))
                color = (alpha // 2, alpha // 2, alpha)
                pygame.draw.circle(screen, color, (int(x), int(y)), size)
    
    def draw(self):
        """Główna funkcja rysowania"""
        # Tło
        screen.blit(self.background, (0, 0))
        
        # Cząsteczki w tle
        self.draw_particles()
        
        # Tytuł z efektem świecenia
        title_text = f"Witaj, {self.username}!"
        title_surface = self.title_font.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Efekt świecenia (rysuj tekst kilka razy z różnymi kolorami)
        glow_color = (100, 150, 255)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_surface = self.title_font.render(title_text, True, glow_color)
            screen.blit(glow_surface, (title_rect.x + offset[0], title_rect.y + offset[1]))
        
        screen.blit(title_surface, title_rect)
        
        # Spinner ładowania
        spinner_y = SCREEN_HEIGHT // 2 - 50
        self.draw_spinner(SCREEN_WIDTH // 2, spinner_y)
        
        # Pasek postępu
        progress_bar_width = 400
        progress_bar_height = 30
        progress_x = SCREEN_WIDTH // 2 - progress_bar_width // 2
        progress_y = SCREEN_HEIGHT // 2 + 50
        self.draw_progress_bar(progress_x, progress_y, progress_bar_width, progress_bar_height)
        
        # Aktualna wiadomość ładowania z efektem pulsowania
        current_message = self.get_current_message()
        message_color = (*WHITE[:3], int(self.text_alpha))  # Nie wszystkie pygame wspierają alpha w kolorze
        message_surface = self.message_font.render(current_message, True, WHITE)
        message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, progress_y + 60))
        
        # Efekt pulsowania poprzez zmianę rozmiaru
        pulse_scale = 1.0 + (self.text_alpha - 177.5) / 1000  # Subtelne pulsowanie
        if pulse_scale != 1.0:
            scaled_size = (int(message_surface.get_width() * pulse_scale), 
                          int(message_surface.get_height() * pulse_scale))
            message_surface = pygame.transform.scale(message_surface, scaled_size)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, progress_y + 60))
        
        screen.blit(message_surface, message_rect)
        
        # Dodatkowe informacje na dole
        if self.progress > 80:
            tip_text = "Przygotuj się na przygodę w świecie gry!"
            tip_surface = self.message_font.render(tip_text, True, (200, 200, 255))
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