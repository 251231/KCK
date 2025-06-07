from config import *
import os
import json

USERS_DB_PATH = "DataBase/users.json"

class UserInterface:
    def __init__(self, player):
        self.player = player
        self.todo_visible = False
        self.todo_items = []
        # Przesunięty przycisk niżej, żeby nie nachodzić na panel gracza
        self.todo_button = pygame.Rect(SCREEN_WIDTH - 220, 120, 210, 50)
        # Przesunięte pole input zgodnie z nową pozycją panelu
        self.todo_input_box = pygame.Rect(SCREEN_WIDTH - 310, 190, 280, 35)
        self.todo_input_text = ''
        self.todo_input_active = False
        self.load_todo()
        
        # Kolory w stylu pixel art
        self.colors = {
            'bg_dark': (45, 45, 65),
            'bg_light': (85, 85, 105),
            'accent': (255, 205, 100),
            'accent_dark': (200, 150, 50),
            'text_light': (240, 240, 240),
            'text_dark': (50, 50, 70),
            'success': (100, 200, 100),
            'border': (120, 120, 140),
            'input_bg': (230, 230, 240),
            'shadow': (30, 30, 40)
        }
        
        # Zmienne do animacji
        self.todo_slide_offset = 0
        self.target_slide_offset = 0
        self.button_hover = False
        self.animation_speed = 8

    def load_todo(self):
        """Wczytuje listę zadań z pliku JSON dla danego użytkownika."""
        if os.path.exists(f"DataBase/user_{self.player.name}_todo.json"):
            with open(f"DataBase/user_{self.player.name}_todo.json", "r") as f:
                self.todo_items = json.load(f)

    def save_todo(self):
        """Zapisuje listę zadań do pliku JSON."""
        with open(f"DataBase/user_{self.player.name}_todo.json", "w") as f:
            json.dump(self.todo_items, f, indent=4)

    def draw_pixel_border(self, surface, rect, color, thickness=2):
        """Rysuje pixelową ramkę wokół prostokąta."""
        # Górna i dolna linia
        pygame.draw.rect(surface, color, (rect.x, rect.y, rect.width, thickness))
        pygame.draw.rect(surface, color, (rect.x, rect.y + rect.height - thickness, rect.width, thickness))
        # Lewa i prawa linia
        pygame.draw.rect(surface, color, (rect.x, rect.y, thickness, rect.height))
        pygame.draw.rect(surface, color, (rect.x + rect.width - thickness, rect.y, thickness, rect.height))

    def draw_button(self, surface, rect, text, base_color, hover_color, text_color, is_hovered=False):
        """Rysuje przycisk w stylu pixel art z efektem 3D."""
        # Cień
        shadow_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
        pygame.draw.rect(surface, self.colors['shadow'], shadow_rect)
        
        # Główny przycisk
        color = hover_color if is_hovered else base_color
        pygame.draw.rect(surface, color, rect)
        
        # Ramka przycisku (efekt 3D)
        self.draw_pixel_border(surface, rect, self.colors['border'], 2)
        
        # Wewnętrzna jasna ramka (highlight)
        inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
        highlight_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.rect(surface, highlight_color, (inner_rect.x, inner_rect.y, inner_rect.width, 2))
        pygame.draw.rect(surface, highlight_color, (inner_rect.x, inner_rect.y, 2, inner_rect.height))
        
        # Tekst
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

    def draw_panel(self, surface, rect, title=""):
        """Rysuje panel w stylu pixel art."""
        # Cień panelu
        shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
        pygame.draw.rect(surface, self.colors['shadow'], shadow_rect)
        
        # Główny panel
        pygame.draw.rect(surface, self.colors['bg_light'], rect)
        
        # Ramka panelu
        self.draw_pixel_border(surface, rect, self.colors['border'], 3)
        
        # Wewnętrzna ramka
        inner_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, rect.height - 6)
        self.draw_pixel_border(surface, inner_rect, self.colors['accent'], 1)
        
        # Tytuł panelu
        if title:
            title_bg = pygame.Rect(rect.x + 10, rect.y - 10, len(title) * 12 + 20, 25)
            pygame.draw.rect(surface, self.colors['accent'], title_bg)
            self.draw_pixel_border(surface, title_bg, self.colors['accent_dark'], 2)
            
            title_text = font.render(title, True, self.colors['text_dark'])
            title_pos = (title_bg.x + 10, title_bg.y + 5)
            surface.blit(title_text, title_pos)

    def update_animations(self):
        """Aktualizuje animacje interfejsu."""
        # Animacja wysuwania To-Do panelu
        if self.todo_visible:
            self.target_slide_offset = 0
        else:
            self.target_slide_offset = -350  # Zmniejszony offset dla lepszej animacji
            
        # Płynna animacja
        diff = self.target_slide_offset - self.todo_slide_offset
        if abs(diff) > 1:
            self.todo_slide_offset += diff * 0.15
        else:
            self.todo_slide_offset = self.target_slide_offset

    def draw(self):
        """Rysuje interfejs użytkownika i listę zadań."""
        self.update_animations()
        
        # Panel z danymi gracza - pozycja bez zmian
        player_panel = pygame.Rect(SCREEN_WIDTH - 240, 10, 230, 100)
        self.draw_panel(screen, player_panel, "GRACZ")
        
        # Dane gracza wewnątrz panelu
        name_text = font.render(f"{self.player.name}", True, self.colors['text_light'])
        coins_text = font.render(f"Monety: {self.player.coins}", True, self.colors['accent'])
        
        screen.blit(name_text, (player_panel.x + 15, player_panel.y + 30))
        screen.blit(coins_text, (player_panel.x + 15, player_panel.y + 60))
        
        # Ikona monet (prosty pixel art)
        coin_rect = pygame.Rect(player_panel.x + 180, player_panel.y + 58, 16, 16)
        pygame.draw.ellipse(screen, self.colors['accent'], coin_rect)
        pygame.draw.ellipse(screen, self.colors['accent_dark'], coin_rect, 2)
        
        # Przycisk To-Do List - przesunięty niżej
        mouse_pos = pygame.mouse.get_pos()
        self.button_hover = self.todo_button.collidepoint(mouse_pos)
        
        self.draw_button(screen, self.todo_button, "📋 TO-DO LIST", 
                        self.colors['bg_dark'], self.colors['accent_dark'], 
                        self.colors['text_light'], self.button_hover)

        # Panel To-Do List (z animacją) - skorygowana pozycja
        if self.todo_visible or self.todo_slide_offset > -300:
            # Obliczamy dynamiczną wysokość panelu na podstawie liczby zadań
            panel_height = min(500, len(self.todo_items) * 35 + 200)  # Zwiększona minimalna wysokość
            todo_panel_x = SCREEN_WIDTH - 330 + self.todo_slide_offset
            todo_panel_y = 180  # Przesunięty niżej, żeby nie nachodzić na przycisk
            todo_panel = pygame.Rect(todo_panel_x, todo_panel_y, 320, panel_height)
            
            self.draw_panel(screen, todo_panel, "ZADANIA")
            
            # Pole wprowadzania - pozycja względem panelu
            input_rect = pygame.Rect(todo_panel.x + 15, todo_panel.y + 40, 290, 35)
            
            # Tło pola input
            pygame.draw.rect(screen, self.colors['input_bg'], input_rect)
            self.draw_pixel_border(screen, input_rect, self.colors['border'], 2)
            
            if self.todo_input_active:
                # Aktywne pole - pomarańczowa ramka
                self.draw_pixel_border(screen, input_rect, self.colors['accent'], 2)
            
            # Tekst w polu input
            input_display_text = self.todo_input_text
            if len(input_display_text) > 32:  # Skrócenie tekstu jeśli za długi
                input_display_text = input_display_text[:32] + "..."
                
            input_surface = font.render(input_display_text + "|" if self.todo_input_active else input_display_text, 
                                      True, self.colors['text_dark'])
            screen.blit(input_surface, (input_rect.x + 8, input_rect.y + 8))
            
            # Placeholder text
            if not self.todo_input_text and not self.todo_input_active:
                placeholder = font.render("Wpisz nowe zadanie...", True, (150, 150, 150))
                screen.blit(placeholder, (input_rect.x + 8, input_rect.y + 8))
            
            # Lista zadań - skorygowane pozycje
            max_visible_items = min(10, (panel_height - 120) // 35)  # Dynamiczna liczba widocznych zadań
            for i, item in enumerate(self.todo_items[:max_visible_items]):
                item_y = todo_panel.y + 90 + i * 35
                item_rect = pygame.Rect(todo_panel.x + 15, item_y, 290, 30)
                
                # Sprawdzenie czy zadanie nie wychodzi poza panel
                if item_rect.bottom > todo_panel.bottom - 30:
                    break
                
                # Tło zadania (na przemian)
                bg_color = self.colors['bg_dark'] if i % 2 == 0 else self.colors['bg_light']
                pygame.draw.rect(screen, bg_color, item_rect)
                self.draw_pixel_border(screen, item_rect, self.colors['border'], 1)
                
                # Checkbox (prosty kwadracik)
                checkbox = pygame.Rect(item_rect.x + 8, item_rect.y + 8, 14, 14)
                pygame.draw.rect(screen, self.colors['input_bg'], checkbox)
                self.draw_pixel_border(screen, checkbox, self.colors['border'], 1)
                
                # Tekst zadania - skrócony jeśli za długi
                display_text = item
                if len(display_text) > 38:
                    display_text = display_text[:38] + "..."
                    
                item_text = font.render(display_text, True, self.colors['text_light'])
                screen.blit(item_text, (item_rect.x + 30, item_rect.y + 8))
            
            # Informacja o liczbie zadań - tylko jeśli są ukryte zadania
            hidden_count = len(self.todo_items) - max_visible_items
            if hidden_count > 0:
                more_text = font.render(f"...i {hidden_count} więcej", 
                                      True, self.colors['accent'])
                screen.blit(more_text, (todo_panel.x + 15, todo_panel.bottom - 25))

    def handle_todo_click(self, pos):
        """Obsługuje kliknięcia związane z To-Do listą."""
        if self.todo_button.collidepoint(pos):
            self.todo_visible = not self.todo_visible
            return True
        elif self.todo_visible:
            # Sprawdzenie kliknięcia w pole input - używamy rzeczywistej pozycji
            todo_panel_x = SCREEN_WIDTH - 330 + self.todo_slide_offset
            actual_input_rect = pygame.Rect(todo_panel_x + 15, 220, 290, 35)
            
            if actual_input_rect.collidepoint(pos):
                self.todo_input_active = True
                return True
            else:
                self.todo_input_active = False
        else:
            self.todo_input_active = False
        return False

    def add_todo_item(self):
        """Dodaje nowe zadanie do listy."""
        if self.todo_input_text.strip():
            self.todo_items.append(self.todo_input_text.strip())
            self.todo_input_text = ''
            self.save_todo()
            self.todo_input_active = False

    def handle_todo_event(self, event):
        """Obsługuje zdarzenia klawiatury dla To-Do listy."""
        if event.type == pygame.KEYDOWN and self.todo_input_active:
            if event.key == pygame.K_RETURN:
                self.add_todo_item()
            elif event.key == pygame.K_BACKSPACE:
                self.todo_input_text = self.todo_input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.todo_input_active = False
            else:
                if len(self.todo_input_text) < 50:  # Limit znaków
                    self.todo_input_text += event.unicode