from config import *
import os
import json
import pygame
import math

USERS_DB_PATH = "DataBase/users.json"

class UserInterface:
    def __init__(self, player):
        self.player = player
        self.todo_visible = False
        self.todo_items = []
        self.game_paused = False  # Nowa zmienna do kontroli pauzy
        
        self.todo_button = pygame.Rect(SCREEN_WIDTH - 308, 168, 294, 70)
        self.todo_input_box = pygame.Rect(SCREEN_WIDTH - 434, 266, 392, 49)
        self.todo_input_text = ''
        self.todo_input_active = False
        
        self.colors = {
            'panel_bg': (58, 42, 75),
            'panel_border': (141, 96, 59),
            'panel_highlight': (232, 193, 112),
            'panel_shadow': (25, 18, 31),
            'text_primary': (255, 255, 255),
            'text_secondary': (200, 200, 200),
            'text_accent': (255, 215, 0),
            'text_dark': (58, 42, 75),
            'btn_primary': (78, 74, 78),
            'btn_primary_hover': (98, 94, 98),
            'btn_accent': (184, 111, 80),
            'btn_accent_hover': (204, 131, 100),
            'btn_danger': (150, 54, 52),
            'btn_danger_hover': (170, 74, 72),
            'todo_bg': (45, 32, 58),
            'todo_item_even': (65, 52, 78),
            'todo_item_odd': (75, 62, 88),
            'input_bg': (240, 230, 200),
            'input_border': (141, 96, 59),
            'input_active': (255, 215, 0),
            'health_green': (76, 175, 80),
            'mana_blue': (33, 150, 243),
            'exp_purple': (156, 39, 176),
            'overlay': (0, 0, 0, 128),  # Półprzezroczysty overlay
        }
        
        self.init_assets()
        self.load_todo()
        
        self.todo_slide_offset = 0
        self.target_slide_offset = 0
        self.animation_speed = 0.15
        self.button_animations = {}
        
        self.clear_all_button = pygame.Rect(0, 0, 140, 42)
        
        self.sparkles = []
        self.coin_rotation = 0
        
    def init_assets(self):
        self.fonts = {}
        try:
            self.fonts['large'] = pygame.font.Font("assets/Czcionka.ttf", 34)
            self.fonts['medium'] = pygame.font.Font("assets/Czcionka.ttf", 25)
            self.fonts['small'] = pygame.font.Font("assets/Czcionka.ttf", 20)
            self.fonts['tiny'] = pygame.font.Font("assets/Czcionka.ttf", 17)
        except (FileNotFoundError, pygame.error):
            print("Własna czcionka nie znaleziona, używam systemowej")
            try:
                self.fonts['large'] = pygame.font.Font(None, 34)
                self.fonts['medium'] = pygame.font.Font(None, 25)
                self.fonts['small'] = pygame.font.Font(None, 20)
                self.fonts['tiny'] = pygame.font.Font(None, 17)
            except:
                try:
                    self.fonts['large'] = font
                    self.fonts['medium'] = font
                    self.fonts['small'] = font
                    self.fonts['tiny'] = font
                except NameError:
                    self.fonts['large'] = pygame.font.Font(None, 34)
                    self.fonts['medium'] = pygame.font.Font(None, 25)
                    self.fonts['small'] = pygame.font.Font(None, 20)
                    self.fonts['tiny'] = pygame.font.Font(None, 17)
        
        self.images = {}
        try:
            self.images['coin'] = pygame.image.load("assets/images/coin.png")
            self.images['coin'] = pygame.transform.scale(self.images['coin'], (28, 28))
            
            self.images['panel_corner'] = pygame.image.load("assets/images/panel_corner.png")
            self.images['panel_corner'] = pygame.transform.scale(self.images['panel_corner'], (11, 11))
            
            self.images['todo_icon'] = pygame.image.load("assets/images/scroll.png")
            self.images['todo_icon'] = pygame.transform.scale(self.images['todo_icon'], (22, 22))
            
            self.images['checkbox_empty'] = pygame.image.load("assets/images/checkbox_empty.png")
            self.images['checkbox_empty'] = pygame.transform.scale(self.images['checkbox_empty'], (22, 22))
            
            self.images['delete_icon'] = pygame.image.load("assets/images/x_icon.png")
            self.images['delete_icon'] = pygame.transform.scale(self.images['delete_icon'], (17, 17))
            
        except (FileNotFoundError, pygame.error):
            print("Niektóre grafiki nie zostały znalezione, używam prostych kształtów")
            self.create_fallback_graphics()
    
    def create_fallback_graphics(self):
        coin_surface = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(coin_surface, self.colors['text_accent'], (3, 3, 22, 22))
        pygame.draw.ellipse(coin_surface, self.colors['panel_border'], (3, 3, 22, 22), 3)
        pygame.draw.ellipse(coin_surface, self.colors['text_accent'], (8, 8, 11, 11))
        self.images['coin'] = coin_surface
        
        todo_surface = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.rect(todo_surface, (240, 230, 200), (3, 1, 17, 20))
        pygame.draw.rect(todo_surface, self.colors['panel_border'], (3, 1, 17, 20), 1)
        for i in range(3):
            pygame.draw.line(todo_surface, self.colors['text_dark'], (6, 6 + i*4), (17, 6 + i*4), 1)
        self.images['todo_icon'] = todo_surface
        
        checkbox_surface = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.rect(checkbox_surface, self.colors['input_bg'], (3, 3, 17, 17))
        pygame.draw.rect(checkbox_surface, self.colors['panel_border'], (3, 3, 17, 17), 3)
        self.images['checkbox_empty'] = checkbox_surface
        
        x_surface = pygame.Surface((17, 17), pygame.SRCALPHA)
        pygame.draw.line(x_surface, self.colors['btn_danger'], (3, 3), (14, 14), 3)
        pygame.draw.line(x_surface, self.colors['btn_danger'], (14, 3), (3, 14), 3)
        self.images['delete_icon'] = x_surface

    def draw_pixelart_border(self, surface, rect, border_color, bg_color=None, thickness=4):
        if bg_color:
            pygame.draw.rect(surface, bg_color, rect)
        
        pygame.draw.rect(surface, border_color, rect, thickness)
        
        inner_rect = pygame.Rect(rect.x + thickness, rect.y + thickness, 
                               rect.width - 2*thickness, rect.height - 2*thickness)
        if inner_rect.width > 0 and inner_rect.height > 0:
            highlight_color = tuple(min(255, c + 40) for c in border_color)
            pygame.draw.rect(surface, highlight_color, inner_rect, 1)
        
        corner_size = 8
        corners = [
            (rect.x, rect.y),
            (rect.right - corner_size, rect.y),
            (rect.x, rect.bottom - corner_size),
            (rect.right - corner_size, rect.bottom - corner_size)
        ]
        
        for corner_pos in corners:
            corner_rect = pygame.Rect(corner_pos[0], corner_pos[1], corner_size, corner_size)
            pygame.draw.rect(surface, self.colors['panel_highlight'], corner_rect)

    def get_font(self, size='medium'):
        try:
            return self.fonts[size]
        except (KeyError, AttributeError):
            try:
                return font
            except NameError:
                return pygame.font.Font(None, 25)

    def draw_rpg_button(self, surface, rect, text, is_hovered=False, button_type='primary', icon=None):
        if button_type == 'primary':
            base_color = self.colors['btn_primary']
            hover_color = self.colors['btn_primary_hover']
            text_color = self.colors['text_primary']
        elif button_type == 'accent':
            base_color = self.colors['btn_accent']
            hover_color = self.colors['btn_accent_hover']
            text_color = self.colors['text_primary']
        elif button_type == 'danger':
            base_color = self.colors['btn_danger']
            hover_color = self.colors['btn_danger_hover']
            text_color = self.colors['text_primary']
        
        offset = 3 if is_hovered else 0
        button_rect = pygame.Rect(rect.x, rect.y + offset, rect.width, rect.height - offset)
        
        shadow_rect = pygame.Rect(rect.x + 4, rect.y + 7, rect.width, rect.height - 3)
        pygame.draw.rect(surface, self.colors['panel_shadow'], shadow_rect)
        
        color = hover_color if is_hovered else base_color
        self.draw_pixelart_border(surface, button_rect, self.colors['panel_border'], color, 3)
        
        content_x = button_rect.x + 11
        if icon and icon in self.images:
            surface.blit(self.images[icon], (content_x, button_rect.y + (button_rect.height - 22) // 2))
            content_x += 28
        
        text_surface = self.get_font('medium').render(text, False, text_color)
        text_shadow = self.get_font('medium').render(text, False, self.colors['panel_shadow'])
        text_y = button_rect.y + (button_rect.height - text_surface.get_height()) // 2
        
        surface.blit(text_shadow, (content_x + 1, text_y + 1))
        surface.blit(text_surface, (content_x, text_y))

    def draw_rpg_panel(self, surface, rect, title="", panel_type='main'):
        shadow_rect = pygame.Rect(rect.x + 6, rect.y + 6, rect.width, rect.height)
        pygame.draw.rect(surface, self.colors['panel_shadow'], shadow_rect)
        
        bg_color = self.colors['panel_bg'] if panel_type == 'main' else self.colors['todo_bg']
        self.draw_pixelart_border(surface, rect, self.colors['panel_border'], bg_color, 4)
        
        if rect.width > 140 and rect.height > 70:
            ornament_y = rect.y + 21
            pygame.draw.line(surface, self.colors['panel_highlight'], 
                           (rect.x + 21, ornament_y), (rect.right - 21, ornament_y), 1)
            
            ornament_y = rect.bottom - 21
            pygame.draw.line(surface, self.colors['panel_highlight'], 
                           (rect.x + 21, ornament_y), (rect.right - 21, ornament_y), 1)
        
        if title:
            title_width = len(title) * 17 + 42
            title_bg = pygame.Rect(rect.x + 21, rect.y - 17, title_width, 34)
            
            self.draw_pixelart_border(surface, title_bg, self.colors['panel_border'], 
                                    self.colors['panel_highlight'], 3)
            
            title_shadow = self.get_font('medium').render(title, False, self.colors['panel_shadow'])
            title_text = self.get_font('medium').render(title, False, self.colors['text_dark'])
            
            title_x = title_bg.x + 21
            title_y = title_bg.y + 6
            
            surface.blit(title_shadow, (title_x + 1, title_y + 1))
            surface.blit(title_text, (title_x, title_y))

    def draw_animated_coin(self, surface, x, y):
        self.coin_rotation += 3
        if self.coin_rotation >= 360:
            self.coin_rotation = 0
        
        scale_factor = abs(math.cos(math.radians(self.coin_rotation)))
        if scale_factor < 0.1:
            scale_factor = 0.1
        
        coin_img = self.images['coin']
        scaled_width = int(coin_img.get_width() * scale_factor)
        scaled_coin = pygame.transform.scale(coin_img, (scaled_width, coin_img.get_height()))
        
        coin_x = x - scaled_coin.get_width() // 2
        surface.blit(scaled_coin, (coin_x, y))

    def update_animations(self):
        if self.todo_visible:
            self.target_slide_offset = 0
        else:
            self.target_slide_offset = -490
        
        diff = self.target_slide_offset - self.todo_slide_offset
        if abs(diff) > 1:
            self.todo_slide_offset += diff * self.animation_speed
        else:
            self.todo_slide_offset = self.target_slide_offset

    def load_todo(self):
        try:
            if os.path.exists(f"DataBase/user_{self.player.name}_todo.json"):
                with open(f"DataBase/user_{self.player.name}_todo.json", "r", encoding='utf-8') as f:
                    self.todo_items = json.load(f)
        except Exception as e:
            print(f"Błąd wczytywania TODO: {e}")
            self.todo_items = []

    def save_todo(self):
        try:
            os.makedirs("DataBase", exist_ok=True)
            with open(f"DataBase/user_{self.player.name}_todo.json", "w", encoding='utf-8') as f:
                json.dump(self.todo_items, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd zapisywania TODO: {e}")

    def is_game_paused(self):
        """Sprawdza czy gra powinna być wstrzymana"""
        return self.todo_visible

    def draw_pause_overlay(self, surface):
        """Rysuje półprzezroczysty overlay gdy gra jest wstrzymana"""
        if self.todo_visible:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (0, 0))
            
            # Tekst informujący o pauzie
            pause_text = self.get_font('large').render("GRA WSTRZYMANA", False, self.colors['text_accent'])
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            
            # Cień dla tekstu
            pause_shadow = self.get_font('large').render("GRA WSTRZYMANA", False, self.colors['panel_shadow'])
            shadow_rect = pause_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 52))
            
            surface.blit(pause_shadow, shadow_rect)
            surface.blit(pause_text, text_rect)

    def draw(self):
        self.update_animations()
        
        # Jeśli TODO jest widoczne, rysuj overlay pauzy
        if self.todo_visible:
            self.draw_pause_overlay(screen)
        
        player_panel = pygame.Rect(SCREEN_WIDTH - 350, 14, 336, 140)
        self.draw_rpg_panel(screen, player_panel, "BOHATER", 'main')
        
        name_text = self.get_font('medium').render(f"{self.player.name}", False, self.colors['text_accent'])
        coins_text = self.get_font('small').render(f"Złoto: {self.player.coins}", False, self.colors['text_primary'])
        
        screen.blit(name_text, (player_panel.x + 21, player_panel.y + 35))
        screen.blit(coins_text, (player_panel.x + 21, player_panel.y + 70))
        
        coin_x = player_panel.x + 21 + coins_text.get_width() + 14
        coin_y = player_panel.y + 67
        self.draw_animated_coin(screen, coin_x, coin_y)
        
        mouse_pos = pygame.mouse.get_pos()
        button_hover = self.todo_button.collidepoint(mouse_pos)
        
        self.draw_rpg_button(screen, self.todo_button, "ZADANIA", button_hover, 'accent', 'todo_icon')
        
        if self.todo_visible or self.todo_slide_offset > -420:
            self.draw_todo_panel(mouse_pos)
        # if hasattr(self.player, 'speed_boost_timer') and self.player.speed_boost_timer > 0:
        #     boost_seconds = int(self.player.speed_boost_timer / 1000)
        #     boost_text = font.render(f"Boost kawy: {boost_seconds}s", True, GREEN)
        #     screen.blit(boost_text, (10, 70))

    def draw_todo_panel(self, mouse_pos):
        panel_height = min(700, len(self.todo_items) * 56 + 392)
        todo_panel_x = SCREEN_WIDTH - 476 + self.todo_slide_offset
        todo_panel_y = 252
        todo_panel = pygame.Rect(todo_panel_x, todo_panel_y, 462, panel_height)
        
        self.draw_rpg_panel(screen, todo_panel, "KSIĘGA ZADAŃ", 'todo')
        
        input_rect = pygame.Rect(todo_panel.x + 21, todo_panel.y + 56, 420, 56)
        input_bg_color = self.colors['input_bg']
        input_border_color = self.colors['input_active'] if self.todo_input_active else self.colors['input_border']
        
        self.draw_pixelart_border(screen, input_rect, input_border_color, input_bg_color, 3)
        
        display_text = self.todo_input_text
        if len(display_text) > 49:
            display_text = display_text[:49] + "..."
        
        cursor = "|" if self.todo_input_active and pygame.time.get_ticks() % 1000 < 500 else ""
        input_text = self.get_font('small').render(display_text + cursor, False, self.colors['text_dark'])
        screen.blit(input_text, (input_rect.x + 14, input_rect.y + 17))
        
        if not self.todo_input_text and not self.todo_input_active:
            placeholder = self.get_font('small').render("Wpisz nowe zadanie...", False, (120, 120, 120))
            screen.blit(placeholder, (input_rect.x + 14, input_rect.y + 17))
        
        if self.todo_items:
            self.clear_all_button = pygame.Rect(todo_panel.x + 280, todo_panel.y + 126, 161, 49)
            clear_hover = self.clear_all_button.collidepoint(mouse_pos)
            self.draw_rpg_button(screen, self.clear_all_button, "WYCZYŚĆ", clear_hover, 'danger')
        
        self.draw_todo_list(todo_panel, mouse_pos)

    def draw_todo_list(self, todo_panel, mouse_pos):
        max_visible_items = min(10, (todo_panel.height - 224) // 56)
        
        for i, item in enumerate(self.todo_items[:max_visible_items]):
            item_y = todo_panel.y + 196 + i * 56
            item_rect = pygame.Rect(todo_panel.x + 21, item_y, 364, 49)
            
            if item_rect.bottom > todo_panel.bottom - 28:
                break
            
            bg_color = self.colors['todo_item_even'] if i % 2 == 0 else self.colors['todo_item_odd']
            self.draw_pixelart_border(screen, item_rect, self.colors['panel_border'], bg_color, 1)
            
            checkbox_rect = pygame.Rect(item_rect.x + 11, item_rect.y + 14, 22, 22)
            screen.blit(self.images['checkbox_empty'], checkbox_rect)
            
            display_text = item
            if len(display_text) > 39:
                display_text = display_text[:39] + "..."
            
            text_shadow = self.get_font('small').render(display_text, False, self.colors['panel_shadow'])
            item_text = self.get_font('small').render(display_text, False, self.colors['text_primary'])
            
            text_x = item_rect.x + 45
            text_y = item_rect.y + 17
            
            screen.blit(text_shadow, (text_x + 1, text_y + 1))
            screen.blit(item_text, (text_x, text_y))
            
            delete_btn_rect = pygame.Rect(item_rect.right + 11, item_rect.y + 11, 34, 34)
            delete_hover = delete_btn_rect.collidepoint(mouse_pos)
            
            delete_color = self.colors['btn_danger_hover'] if delete_hover else self.colors['btn_danger']
            self.draw_pixelart_border(screen, delete_btn_rect, self.colors['panel_border'], delete_color, 1)
            
            icon_x = delete_btn_rect.x + (delete_btn_rect.width - 17) // 2
            icon_y = delete_btn_rect.y + (delete_btn_rect.height - 17) // 2
            screen.blit(self.images['delete_icon'], (icon_x, icon_y))
        
        hidden_count = len(self.todo_items) - max_visible_items
        if hidden_count > 0:
            more_text = self.get_font('small').render(f"...i {hidden_count} więcej zadań", 
                                                 False, self.colors['text_accent'])
            screen.blit(more_text, (todo_panel.x + 21, todo_panel.bottom - 35))

    def handle_todo_click(self, pos):
        if self.todo_button.collidepoint(pos):
            self.todo_visible = not self.todo_visible
            self.game_paused = self.todo_visible  # Aktualizuj stan pauzy
            return True
        elif self.todo_visible:
            todo_panel_x = SCREEN_WIDTH - 476 + self.todo_slide_offset
            
            actual_input_rect = pygame.Rect(todo_panel_x + 21, 308, 420, 56)
            if actual_input_rect.collidepoint(pos):
                self.todo_input_active = True
                return True
            
            if self.todo_items and self.clear_all_button.collidepoint(pos):
                self.clear_all_todos()
                return True
            
            panel_height = min(700, len(self.todo_items) * 56 + 392)
            max_visible_items = min(10, (panel_height - 224) // 56)
            
            for i in range(min(len(self.todo_items), max_visible_items)):
                item_y = 252 + 196 + i * 56
                delete_btn_rect = pygame.Rect(todo_panel_x + 21 + 364 + 11, item_y + 11, 34, 34)
                
                if delete_btn_rect.collidepoint(pos):
                    self.remove_todo_item(i)
                    return True
            
            self.todo_input_active = False
        else:
            self.todo_input_active = False
        return False

    def add_todo_item(self):
        if self.todo_input_text.strip():
            self.todo_items.append(self.todo_input_text.strip())
            self.todo_input_text = ''
            self.save_todo()
            self.todo_input_active = False

    def remove_todo_item(self, index):
        if 0 <= index < len(self.todo_items):
            self.todo_items.pop(index)
            self.save_todo()

    def clear_all_todos(self):
        self.todo_items.clear()
        self.save_todo()

    def handle_todo_event(self, event):
        if event.type == pygame.KEYDOWN and self.todo_input_active:
            if event.key == pygame.K_RETURN:
                self.add_todo_item()
            elif event.key == pygame.K_BACKSPACE:
                self.todo_input_text = self.todo_input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.todo_input_active = False
                self.todo_visible = False
                self.game_paused = False
            else:
                if len(self.todo_input_text) < 84:
                    self.todo_input_text += event.unicode
        elif event.type == pygame.KEYDOWN and self.todo_visible:
            if event.key == pygame.K_ESCAPE:
                self.todo_visible = False
                self.game_paused = False
                self.todo_input_active = False