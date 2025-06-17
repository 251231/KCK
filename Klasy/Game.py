import math
import pygame
import sys
import json
import os
from config import *
from UserInterface import UserInterface
from Player import Player
from NPC import NPC, get_ai_response
from GameRoom import GameRoom
from RegisterRoom import RegisterRoom
from MainRoom import MainRoom
from FeeRoom import FeeRoom
from DataRoom import DataRoom
from Room import Room
from DiceGame import DiceGame
from CupsGame import CupsGame
from WheelOfFortuneGame import WheelOfFortuneGame
from MiniGameLoader import MiniGameLoader
from PsychologistRoom import PsychologistRoom
from AnimatedModels import AnimatedLamp
from Authors import Authors 
from CoffeeMachine import CoffeeMachine
from Beetle import *


class Game:
    def __init__(self, username, music_manager=None):
        self.running = True
        self.clock = pygame.time.Clock()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, None, username)
        self.camera_x = 0
        self.camera_y = 0
        self.ui = UserInterface(self.player)
        
        # Dodaj referencję do MusicManager
        self.music_manager = music_manager
        
        # Inicjalizacja pokoi
        self.init_rooms()
        self.current_room = self.rooms["MainRoom"]
        
        # Cooldown dla teleportacji
        self.teleport_cooldown = 0

        # Minigry
        self.beetle_game = BeetleRaceGame(self.player)
        self.in_beetle_game = False
        self.beetle_table_rect = pygame.Rect(787, 400, 60, 60)

        self.dice_game = DiceGame(self.player)
        self.in_dice_game = False
        self.cups_game = CupsGame(self.player)
        self.in_cups_game = False
        self.wheel_game = WheelOfFortuneGame(self.player)
        self.in_wheel_game = False

        
        self.automat_rect = pygame.Rect(369, 433, 50, 50)
        self.cups_table_rect = pygame.Rect(1207, 408, 60, 60)
        self.wheel_rect = pygame.Rect(880, 960, 60, 60)
        self.interaction_hint = None

        # Menu pauzy
        self.paused = False
        self.pause_menu_tab = "main"
        self.menu_scale = 0.0  # Skala menu (0.0 = niewidoczne, 1.0 = pełny rozmiar)
        self.menu_alpha = 0    # Przezroczystość menu (0-255)
        self.menu_target_scale = 0.0  # Docelowa skala
        self.menu_target_alpha = 0 
        
        # Ustaw początkową głośność na podstawie MusicManager
        if self.music_manager:
            self.music_volume = self.music_manager.get_music_volume()
        else:
            self.music_volume = 0.5
            
        # Animacje menu
        self.menu_animation_time = 0
        self.selected_button = 0  # Indeks aktualnie wybranego przycisku
        
        self.init_pause_menu()
        self.init_rpg_fonts()
        self.player_near_coffee_machine = False

    def init_rpg_fonts(self):
        """Inicjalizuje czcionki w stylu RPG"""
        # TUTAJ ZMIEŃ NA SWOJĄ CZCIONKĘ
        self.rpg_font_large = pygame.font.Font("assets/Czcionka.ttf", 32)
        try:
            # Spróbuj załadować czcionkę pixel art (zmień ścieżkę na swoją)
            self.rpg_font_large = pygame.font.Font("assets/Czcionka.ttf", 48)  # Tytuły
            self.rpg_font_medium = pygame.font.Font("assets/Czcionka.ttf", 32)  # Przyciski
            self.rpg_font_small = pygame.font.Font("assets/Czcionka.ttf", 24)   # Tekst pomocniczy
        except:
            # Fallback do domyślnych czcionek
            self.rpg_font_large = pygame.font.Font(None, 48)
            self.rpg_font_medium = pygame.font.Font(None, 32)
            self.rpg_font_small = pygame.font.Font(None, 24)

    def init_pause_menu(self):
        """Inicjalizuje elementy menu pauzy w stylu RPG"""
        menu_width = 500
        menu_height = 600
        self.pause_menu_rect = pygame.Rect(
            (SCREEN_WIDTH - menu_width) // 2,
            (SCREEN_HEIGHT - menu_height) // 2,
            menu_width,
            menu_height
        )
        
        # Przyciski głównego menu - większe i bardziej stylowe
        button_width = 350
        button_height = 60
        button_x = self.pause_menu_rect.centerx - button_width // 2
        button_spacing = 80
        
        start_y = self.pause_menu_rect.y + 150
        
        self.resume_button = pygame.Rect(button_x, start_y, button_width, button_height)
        self.volume_button = pygame.Rect(button_x, start_y + button_spacing, button_width, button_height)
        self.controls_button = pygame.Rect(button_x, start_y + button_spacing * 2, button_width, button_height)
        self.exit_button = pygame.Rect(button_x, start_y + button_spacing * 3, button_width, button_height)
        
        # Lista przycisków dla nawigacji klawiaturą
        self.main_menu_buttons = [
            self.resume_button,
            self.volume_button, 
            self.controls_button,
            self.exit_button
        ]
        
        # Przycisk powrotu
        self.back_button = pygame.Rect(button_x, self.pause_menu_rect.y + 520, button_width, button_height)
        
        # Suwak głośności - bardziej stylowy
        slider_width = 300
        self.volume_slider_rect = pygame.Rect(
            self.pause_menu_rect.centerx - slider_width // 2,
            self.pause_menu_rect.y + 250,
            slider_width,
            30
        )
        self.volume_handle_rect = pygame.Rect(0, 0, 25, 40)
        self.update_volume_handle()
        self.dragging_volume = False

    def draw_ornate_border(self, surface, rect, thickness=8):
        """Rysuje ozdobną ramkę w stylu RPG"""
        # Zewnętrzna ramka
        pygame.draw.rect(surface, (101, 67, 33), rect, thickness)  # Brązowy
        pygame.draw.rect(surface, (160, 130, 80), rect, thickness//2)  # Złoty
        
        # Narożniki - małe kwadraty
        corner_size = thickness * 2
        corners = [
            rect.topleft,
            (rect.topright[0] - corner_size, rect.topright[1]),
            (rect.bottomleft[0], rect.bottomleft[1] - corner_size),
            (rect.bottomright[0] - corner_size, rect.bottomright[1] - corner_size)
        ]
        
        for corner in corners:
            corner_rect = pygame.Rect(corner[0], corner[1], corner_size, corner_size)
            pygame.draw.rect(surface, (160, 130, 80), corner_rect)
            pygame.draw.rect(surface, (101, 67, 33), corner_rect, 2)

    def draw_rpg_button_animated(self, surface, rect, text, is_selected=False, is_hovered=False, 
                           color_theme="blue", scale_factor=1.0):
        """Rysuje przycisk w stylu RPG z animacją"""
        # ... (kod kolorów bez zmian)
        color_themes = {
            "blue": {
                "bg": (30, 60, 120) if not (is_selected or is_hovered) else (50, 90, 180),
                "border": (100, 150, 255),
                "text": (255, 255, 255),
                "selected_glow": (150, 200, 255)
            },
            "green": {
                "bg": (40, 100, 40) if not (is_selected or is_hovered) else (60, 140, 60),
                "border": (100, 200, 100),
                "text": (255, 255, 255),
                "selected_glow": (150, 255, 150)
            },
            "red": {
                "bg": (120, 30, 30) if not (is_selected or is_hovered) else (180, 50, 50),
                "border": (255, 100, 100),
                "text": (255, 255, 255),
                "selected_glow": (255, 150, 150)
            },
            "yellow": {
                "bg": (100, 80, 20) if not (is_selected or is_hovered) else (140, 120, 40),
                "border": (200, 180, 80),
                "text": (255, 255, 255),
                "selected_glow": (255, 240, 150)
            }
        }
    
        theme = color_themes.get(color_theme, color_themes["blue"])
    
        # Stwórz powierzchnię przycisku z przezroczystością
        button_surface = pygame.Surface((rect.width, rect.height))
        button_surface.set_alpha(int(self.menu_alpha))
    
        # Efekt świecenia dla wybranego przycisku
        if is_selected:
            glow_size = max(10, int(20 * scale_factor))
            glow_rect = pygame.Rect(0, 0, rect.width + glow_size, rect.height + glow_size)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height))
            glow_surface.set_alpha(int(100 * (self.menu_alpha / 255)))
            glow_surface.fill(theme["selected_glow"])
            surface.blit(glow_surface, (rect.x - glow_size//2, rect.y - glow_size//2))
    
        # Główny przycisk
        pygame.draw.rect(button_surface, theme["bg"], (0, 0, rect.width, rect.height))
    
        # Ramka przycisku
        border_thickness = max(1, int((4 if is_selected else 3) * scale_factor))
        pygame.draw.rect(button_surface, theme["border"], (0, 0, rect.width, rect.height), border_thickness)
    
        # Wewnętrzna ramka dla głębi
        if scale_factor > 0.5:
            inner_rect = pygame.Rect(4, 4, rect.width - 8, rect.height - 8)
            pygame.draw.rect(button_surface, theme["border"], inner_rect, 1)
    
        # Tekst z przeskalowaną czcionką
        font_size = max(12, int(32 * scale_factor))
        try:
            scaled_font = pygame.font.Font("assets/Czcionka.ttf", font_size)
        except:
            scaled_font = pygame.font.Font(None, font_size)
    
        text_surface = scaled_font.render(text, True, theme["text"])
        text_rect = text_surface.get_rect(center=(rect.width//2, rect.height//2))
        button_surface.blit(text_surface, text_rect)
    
        # Narysuj przycisk na głównej powierzchni
        surface.blit(button_surface, rect.topleft)

    def update_volume_handle(self):
        """Aktualizuje pozycję suwaka głośności"""
        handle_x = self.volume_slider_rect.x + int(self.music_volume * (self.volume_slider_rect.width - self.volume_handle_rect.width))
        self.volume_handle_rect.centerx = handle_x + self.volume_handle_rect.width // 2
        self.volume_handle_rect.centery = self.volume_slider_rect.centery

    def init_rooms(self):
        self.rooms = {
            "MainRoom": MainRoom(),
            "GameRoom": GameRoom(),
            "RegisterRoom": RegisterRoom(),
            "FeeRoom": FeeRoom(),
            "DataRoom": DataRoom(),
            "PsychologistRoom": PsychologistRoom(),
            "Authors":Authors()
        }

    def is_in_any_interaction(self):
        """Sprawdza czy gracz jest w jakiejkolwiek interakcji (minigra, rozmowa z NPC, lub wpłaty)"""
        # Sprawdź minigry
        if self.in_dice_game or self.in_cups_game or self.in_wheel_game or self.in_beetle_game:
            return True
        
        # Sprawdź czy jakiś NPC ma aktywne okno czatu
        for npc in self.current_room.npcs:
            if npc.chat_window.active:
                return True
        
        # Sprawdź czy interfejs wpłat jest aktywny w FeeRoom
        if isinstance(self.current_room, FeeRoom) and self.current_room.fee_interface_active:
            return True
        
        return False
    def update_menu_animation(self, delta_time):
        """Aktualizuje animację menu pauzy"""
        animation_speed = 8.0  # Szybkość animacji (wyższe = szybsze)
    
    # Płynne przejście skali
        if abs(self.menu_scale - self.menu_target_scale) > 0.01:
            self.menu_scale += (self.menu_target_scale - self.menu_scale) * animation_speed * delta_time
        else:
            self.menu_scale = self.menu_target_scale
    
    # Płynne przejście przezroczystości
        if abs(self.menu_alpha - self.menu_target_alpha) > 1:
            self.menu_alpha += (self.menu_target_alpha - self.menu_alpha) * animation_speed * delta_time
        else:
         self.menu_alpha = self.menu_target_alpha

    def update(self, dx, dy, delta_time):
        # Jeśli gra jest spauzowana, nie aktualizuj gry głównej
        if self.paused:
        # DODANE: Aktualizuj animację menu
            self.update_menu_animation(delta_time)
            return
    # DODANE: Aktualizuj animację menu również gdy gra nie jest spauzowana
        self.update_menu_animation(delta_time)
        if self.in_beetle_game:
            self.beetle_game.update(delta_time)
        # Jeśli jesteśmy w interakcji, nie aktualizuj gry głównej
        if self.is_in_any_interaction():
            # Aktualizuj tylko FeeRoom jeśli jego interfejs jest aktywny
            if isinstance(self.current_room, FeeRoom):
                self.current_room.update(self, delta_time)
            return
        
        # Aktualizuj cooldown teleportacji
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= delta_time
            
        # Porusz gracza
        self.player.move(dx, dy, delta_time, self.current_room.objects, self.current_room.check_collision)
        
        # Aktualizuj NPCs w aktualnym pokoju
        for npc in self.current_room.npcs:
            npc.update()
        # Aktualizuj kamerę
        self.update_camera()
        if hasattr(self.current_room, 'update'):
            self.current_room.update(self, delta_time)
                
        if isinstance(self.current_room, MainRoom):
            self.handle_coffee_machine_interaction()
        if isinstance(self.current_room, MainRoom) and hasattr(self.current_room, 'coffee_machine'):
            self.current_room.coffee_machine.update_player_speed_boost(self.player, delta_time)
        # Sprawdź teleportację (tylko jeśli cooldown minął)
        if self.teleport_cooldown <= 0:
            self.check_room_transitions()

        # Obsługa podpowiedzi interakcji
        self.update_interaction_hints()
        
    def update_interaction_hints(self):
        """Aktualizuje podpowiedzi interakcji"""
        
        if self.get_current_room_name() == "DataRoom" or self.get_current_room_name() == "RegisterRoom":
            return

        if self.player.rect.colliderect(self.automat_rect.inflate(100, 100)) and self.get_current_room_name() == "GameRoom":
            self.interaction_hint = "Naciśnij SPACJĘ, aby zagrać w kości"
        elif self.player.rect.colliderect(self.cups_table_rect.inflate(100, 100)) and self.get_current_room_name() == "GameRoom":
            self.interaction_hint = "Naciśnij SPACJĘ, aby zagrać w kubki"
        elif any(self.player.rect.colliderect(npc.rect.inflate(100, 100)) for npc in self.current_room.npcs) :
            self.interaction_hint = "Naciśnij SPACJĘ, aby porozmawiać"
        elif self.player.rect.colliderect(self.wheel_rect.inflate(100, 100))and self.get_current_room_name() == "GameRoom":
            self.interaction_hint = "Naciśnij SPACJĘ, aby zakręcić kołem"
        elif isinstance(self.current_room, FeeRoom) and self.current_room.check_fee_interaction(self.player):
            self.interaction_hint = "Naciśnij SPACJĘ, aby wypłacić monety"
        elif self.player.rect.colliderect(self.beetle_table_rect.inflate(100, 100)) and self.get_current_room_name() == "GameRoom":
            self.interaction_hint = "Naciśnij SPACJĘ, aby zagrać w beetle"
        else:
            self.interaction_hint = None
        
    def update_camera(self):
        """Aktualizuje pozycję kamery"""
        self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_y = self.player.rect.centery - SCREEN_HEIGHT // 2
        
        # Ogranicz kamerę do granic mapy
        bg_width, bg_height = self.current_room.map_background.get_size()
        self.camera_x = max(0, min(self.camera_x, bg_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, bg_height - SCREEN_HEIGHT))

    def check_room_transitions(self):
        """Sprawdza czy gracz stoi na strefie teleportacji"""
        px = int(self.player.rect.centerx)
        py = int(self.player.rect.centery)
        
        teleport_info = self.current_room.check_teleport(px, py)
        if teleport_info:
            new_room, entry_point = teleport_info
            self.change_room(new_room, entry_point)

    def change_room(self, room_name, entry_point="default"):
        """Zmienia pokój i ustawia gracza w odpowiednim miejscu"""
        if room_name in self.rooms:
            
            # Zmień pokój
            self.current_room = self.rooms[room_name]
            
            # Ustaw gracza w odpowiednim punkcie wejścia
            if entry_point in self.current_room.entry_points:
                spawn_x, spawn_y = self.current_room.entry_points[entry_point]
            else:
                spawn_x, spawn_y = self.current_room.entry_points["default"]
            
            self.player.rect.x = spawn_x
            self.player.rect.y = spawn_y
            
            # Ustaw cooldown teleportacji (żeby nie teleportować się od razu z powrotem)
            self.teleport_cooldown = 1.0  # 1 sekunda cooldown
            
            # Aktualizuj kamerę
            self.update_camera()

    def handle_input(self):
        # Jeśli gra jest spauzowana lub jesteśmy w interakcji, nie obsługuj ruchu gracza
        if self.paused or self.is_in_any_interaction():
            return 0, 0
            
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
        return dx, dy

    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000
            self.handle_events()
            dx, dy = self.handle_input()
            self.update(dx, dy, delta_time)
            self.draw()

    def draw(self):
        # Wyczyść ekran
        screen.fill(BLACK)
        
        # Jeśli jesteśmy w minigre, rysuj tylko minigrę
        if self.in_dice_game and self.get_current_room_name() == "GameRoom":
            self.dice_game.draw()
            if self.paused:
                self.draw_pause_menu()
            pygame.display.flip()
            return
        elif self.in_cups_game and self.get_current_room_name() == "GameRoom":
            self.cups_game.draw()
            if self.paused:
                self.draw_pause_menu()
            pygame.display.flip()
            return
        elif self.in_wheel_game and self.get_current_room_name() == "GameRoom":
            self.wheel_game.draw()
            if self.paused:
                self.draw_pause_menu()
            pygame.display.flip()
            return
        elif self.in_beetle_game:
            self.beetle_game.draw()
            if self.paused:
                self.draw_pause_menu()
            pygame.display.flip()
            return
        if hasattr(self.player, 'speed_boost_timer') and self.player.speed_boost_timer > 0:
            boost_seconds = int(self.player.speed_boost_timer / 1000)
            font = pygame.font.Font(None, 32)
            boost_text = font.render(f"Boost kawy: {boost_seconds}s", True, GREEN)
            screen.blit(boost_text, (10, 50))
        # Jeśli jakiś NPC ma aktywne okno czatu, rysuj tylko okno czatu
        for npc in self.current_room.npcs:
            if npc.chat_window.active:
                npc.draw_chat_only()
                if self.paused:
                    self.draw_pause_menu()
                pygame.display.flip()
                return
        
        # Jeśli interfejs wpłat jest aktywny, rysuj go
        if isinstance(self.current_room, FeeRoom) and self.current_room.fee_interface_active:
            self.draw_main_game()  # To rysuje grę PLUS interfejs FeeRoom
            if self.paused:
                self.draw_pause_menu()
            pygame.display.flip()
            return
        
        # Rysuj normalną grę tylko jeśli nie ma żadnych interakcji

        self.draw_main_game()
        
        # Rysuj menu pauzy na wierzchu wszystkiego
        if self.paused:
            self.draw_pause_menu()
            
        pygame.display.flip()

    def draw_main_game(self):
        """Rysuje główną grę (pokój, gracza, UI itp.)"""
        # Rysuj tło pokoju
        self.current_room.draw(screen, self.camera_x, self.camera_y)

        if not isinstance(self.current_room, Authors):
            if not (
                (hasattr(self.current_room, "showing_chart") and self.current_room.showing_chart) or 
                (hasattr(self.current_room, "showing_image") and self.current_room.showing_image)
            ):
                self.player.draw(self.camera_x, self.camera_y)
                self.ui.draw()

        # Podpowiedzi interakcji
        if self.interaction_hint and not self.paused:
            hint_text = font.render(self.interaction_hint, True, BLACK)
            hint_box = hint_text.get_rect()
            hint_box.inflate_ip(40, 20)  # powiększamy prostokąt wokół tekstu

            hint_box.centerx = SCREEN_WIDTH // 2
            hint_box.bottom = SCREEN_HEIGHT - 30

            pygame.draw.rect(screen, (255, 255, 255), hint_box, border_radius=12)  # białe obramowanie
            screen.blit(hint_text, (hint_box.x + 20, hint_box.y + 10))
            
        # Rysuj stół z kubkami
        # if self.get_current_room_name() == "GameRoom":
        #     cups_table_screen_pos = (
        #         self.cups_table_rect.x - self.camera_x,
        #         self.cups_table_rect.y - self.camera_y
        #     )
        #     if (0 <= cups_table_screen_pos[0] <= SCREEN_WIDTH and 
        #         0 <= cups_table_screen_pos[1] <= SCREEN_HEIGHT):
                
        #         # Rysuj stół
        #         pygame.draw.rect(screen, (139, 69, 19), 
        #                     (*cups_table_screen_pos, self.cups_table_rect.width, self.cups_table_rect.height))
        #         pygame.draw.rect(screen, (101, 67, 33), 
        #                     (*cups_table_screen_pos, self.cups_table_rect.width, self.cups_table_rect.height), 3)
                
        #         # Dodaj tekst "KUBKI"
        #         table_text = font.render("KUBKI", True, (255, 215, 0))
        #         text_rect = table_text.get_rect(center=(
        #             cups_table_screen_pos[0] + self.cups_table_rect.width // 2,
        #             cups_table_screen_pos[1] + self.cups_table_rect.height // 2
        #         ))
        #         screen.blit(table_text, text_rect)

        # if self.get_current_room_name() == "GameRoom":
        #     dice_table_screen_pos = (
        #         self.dice_table_rect.x - self.camera_x,
        #         self.dice_table_rect.y - self.camera_y
        #     )
        #     if (0 <= dice_table_screen_pos[0] <= SCREEN_WIDTH and 
        #         0 <= dice_table_screen_pos[1] <= SCREEN_HEIGHT):
                
        #         # Rysuj stół do gry w kości
        #         pygame.draw.rect(screen, (139, 69, 19), 
        #                     (*dice_table_screen_pos, self.dice_table_rect.width, self.dice_table_rect.height))
        #         pygame.draw.rect(screen, (101, 67, 33), 
        #                     (*dice_table_screen_pos, self.dice_table_rect.width, self.dice_table_rect.height), 3)
                
        #         # Dodaj tekst "KOŚCI"
        #         table_text = font.render("KOŚCI", True, (255, 215, 0))
        #         text_rect = table_text.get_rect(center=(
        #             dice_table_screen_pos[0] + self.dice_table_rect.width // 2,
        #             dice_table_screen_pos[1] + self.dice_table_rect.height // 2
        #         ))
        #         screen.blit(table_text, text_rect)

        # Rysuj strefę koła fortuny tylko w GameRoom
        # if self.get_current_room_name() == "GameRoom":
        #     wheel_pos = (self.wheel_rect.x - self.camera_x, self.wheel_rect.y - self.camera_y)
        #     pygame.draw.rect(screen, (0, 100, 200), (*wheel_pos, self.wheel_rect.width, self.wheel_rect.height))
        #     wheel_text = font.render("KOŁO", True, (255, 255, 0))
        #     screen.blit(wheel_text, (wheel_pos[0], wheel_pos[1] - 20))

        # Debug info (tylko gdy nie ma pauzy)
        if not self.paused:
            coords_text = font.render(f"X: {int(self.player.rect.x)} Y: {int(self.player.rect.y)}", True, BLACK)
            screen.blit(coords_text, (10, 10))
            
        # Pokazuj aktualny pokój
        room_text = font.render(f"Pokój: {self.get_current_room_name()}", True, BLACK)
        screen.blit(room_text, (10, 40))
        
        
        # Pokazuj cooldown teleportacji (debug)
        if self.teleport_cooldown > 0:
            cooldown_text = font.render(f"Teleport cooldown: {self.teleport_cooldown:.1f}", True, BLACK)
            screen.blit(cooldown_text, (10, 100))

        # Przycisk quit (tylko gdy nie ma pauzy)


        # Kursor myszy
        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    def draw_main_pause_menu_rpg_animated(self, scale_factor):
        """Rysuje główne menu pauzy w stylu RPG z animacją"""
        if scale_factor < 0.1:
            return
    
    # Animowany tytuł
        title_offset = math.sin(self.menu_animation_time * 2) * 3 * scale_factor
    
    # Skaluj czcionkę
        font_size = max(16, int(48 * scale_factor))
        try:
            scaled_font = pygame.font.Font("assets/Czcionka.ttf", font_size)
        except:
            scaled_font = pygame.font.Font(None, font_size)
    
        title = scaled_font.render("~ MENU PAUZY ~", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.pause_menu_rect.centerx, 
                                       self.pause_menu_rect.y + int(60 * scale_factor) + title_offset))
    
    # Cień tytułu
        shadow_offset = max(1, int(3 * scale_factor))
        shadow = scaled_font.render("~ MENU PAUZY ~", True, (100, 80, 0))
        shadow_rect = shadow.get_rect(center=(title_rect.centerx + shadow_offset, 
                                         title_rect.centery + shadow_offset))
    
    # Ustaw przezroczystość
        title.set_alpha(int(self.menu_alpha))
        shadow.set_alpha(int(self.menu_alpha * 0.7))
    
        screen.blit(shadow, shadow_rect)
        screen.blit(title, title_rect)
    
    # Przeskalowane przyciski
        if scale_factor > 0.3:  # Rysuj przyciski tylko gdy są wystarczająco duże
            button_width = int(350 * scale_factor)
            button_height = int(60 * scale_factor)
            button_x = self.pause_menu_rect.centerx - button_width // 2
            button_spacing = int(80 * scale_factor)
        
            start_y = self.pause_menu_rect.y + int(150 * scale_factor)
        
        # Aktualizuj pozycje przycisków
            scaled_buttons = [
                pygame.Rect(button_x, start_y, button_width, button_height),
                pygame.Rect(button_x, start_y + button_spacing, button_width, button_height),
                pygame.Rect(button_x, start_y + button_spacing * 2, button_width, button_height),
                pygame.Rect(button_x, start_y + button_spacing * 3, button_width, button_height)
            ]
        
            button_data = [
                ("Powrót do gry", "green"),
                ("Ustawienia dźwięku", "blue"),
                ("Sterowanie", "yellow"),
                ("Opuść grę", "red")
            ]
        
            mouse_pos = pygame.mouse.get_pos()
        
            for i, ((text, color_theme), button_rect) in enumerate(zip(button_data, scaled_buttons)):
                is_selected = (i == self.selected_button)
                is_hovered = button_rect.collidepoint(mouse_pos)
                self.draw_rpg_button_animated(screen, button_rect, text, is_selected, is_hovered, 
                                        color_theme, scale_factor)
        
    def draw_pause_menu(self):
        """Rysuje menu pauzy w stylu RPG z animacją"""
        # Jeśli menu jest całkowicie niewidoczne, nie rysuj go
        if self.menu_alpha <= 0:
            return
    
        # Animacja pojawiania się menu
        self.menu_animation_time += self.clock.get_time() / 1000.0
    
        # Półprzezroczyste tło z efektem - ZMIENIONE: dodano animację przezroczystości
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay_alpha = int(150 * (self.menu_alpha / 255))
        overlay.set_alpha(overlay_alpha)
    
        # Gradient tła
        for y in range(SCREEN_HEIGHT):
            alpha = int(overlay_alpha * (y / SCREEN_HEIGHT))
            color = (0, 0, 20)
            pygame.draw.line(overlay, color, (0, y), (SCREEN_WIDTH, y))
    
        screen.blit(overlay, (0, 0))
    
    # DODANE: Oblicz rozmiar i pozycję menu na podstawie skali
        scaled_width = int(self.pause_menu_rect.width * self.menu_scale)
        scaled_height = int(self.pause_menu_rect.height * self.menu_scale)
    
    # Wycentruj przeskalowane menu
        scaled_x = (SCREEN_WIDTH - scaled_width) // 2
        scaled_y = (SCREEN_HEIGHT - scaled_height) // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
    
    # Jeśli menu jest za małe, nie rysuj go
        if scaled_width < 10 or scaled_height < 10:
            return
    
    # Główne tło menu z teksturą - ZMIENIONE: używaj przeskalowanego rozmiaru
        menu_bg = pygame.Surface((scaled_width, scaled_height))
        menu_bg.set_alpha(int(self.menu_alpha))
    
    # Gradient tła menu
        for y in range(scaled_height):
            progress = y / scaled_height
            color_r = int(40 + progress * 20)
            color_g = int(30 + progress * 15)
            color_b = int(60 + progress * 30)
            pygame.draw.line(menu_bg, (color_r, color_g, color_b), (0, y), (scaled_width, y))
    
        screen.blit(menu_bg, scaled_rect.topleft)
    
    # Ozdobna ramka - ZMIENIONE: używaj przeskalowanego prostokąta
        if self.menu_scale > 0.3:  # Rysuj ramkę tylko gdy menu jest wystarczająco duże
            self.draw_ornate_border(screen, scaled_rect)
    
    # DODANE: Przeskaluj wszystkie elementy menu
        scale_factor = self.menu_scale
    
    # Tymczasowo zmień rozmiary przycisków dla animacji
        original_pause_rect = self.pause_menu_rect
        self.pause_menu_rect = scaled_rect
    
    # Rysuj odpowiednie menu z przezroczystością
        if self.pause_menu_tab == "main":
            self.draw_main_pause_menu_rpg_animated(scale_factor)
        elif self.pause_menu_tab == "volume":
            self.draw_volume_menu_rpg()
        elif self.pause_menu_tab == "controls":
            self.draw_controls_menu_rpg()
    
    # Przywróć oryginalny rozmiar
        self.pause_menu_rect = original_pause_rect

    def draw_main_pause_menu_rpg(self):
        """Rysuje główne menu pauzy w stylu RPG"""
        # Animowany tytuł
        title_offset = math.sin(self.menu_animation_time * 2) * 3
        title = self.rpg_font_large.render("~ MENU PAUZY ~", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.pause_menu_rect.centerx, self.pause_menu_rect.y + 60 + title_offset))
        
        # Cień tytułu
        shadow = self.rpg_font_large.render("~ MENU PAUZY ~", True, (100, 80, 0))
        shadow_rect = shadow.get_rect(center=(title_rect.centerx + 3, title_rect.centery + 3))
        screen.blit(shadow, shadow_rect)
        screen.blit(title, title_rect)
        
        # Przyciski z różnymi kolorami
        button_data = [
            (self.resume_button, "Powrót do gry", "green"),
            (self.volume_button, "Ustawienia dźwięku", "blue"),
            (self.controls_button, "Sterowanie", "yellow"),
            (self.exit_button, "Opuść grę", "red")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (button_rect, text, color_theme) in enumerate(button_data):
            is_selected = (i == self.selected_button)
            is_hovered = button_rect.collidepoint(mouse_pos)
            self.draw_rpg_button_animated(screen, button_rect, text, is_selected, is_hovered, color_theme)

    def draw_volume_menu_rpg(self):
        """Rysuje menu głośności w stylu RPG"""
        # Tytuł
        title = self.rpg_font_large.render("~ USTAWIENIA DŹWIĘKU ~", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.pause_menu_rect.centerx, self.pause_menu_rect.y + 60))
        
        shadow = self.rpg_font_large.render("~ USTAWIENIA DŹWIĘKU ~", True, (100, 80, 0))
        shadow_rect = shadow.get_rect(center=(title_rect.centerx + 2, title_rect.centery + 2))
        screen.blit(shadow, shadow_rect)
        screen.blit(title, title_rect)
        
        # Wartość głośności z animacją
        volume_percent = int(self.music_volume * 100)
        volume_color = (100, 255, 100) if volume_percent > 50 else (255, 255, 100) if volume_percent > 20 else (255, 100, 100)
        volume_text = self.rpg_font_medium.render(f"Głośność muzyki: {volume_percent}%", True, volume_color)
        volume_rect = volume_text.get_rect(center=(self.pause_menu_rect.centerx, self.pause_menu_rect.y + 180))
        screen.blit(volume_text, volume_rect)
        
        # Stylowy suwak głośności
        # Tło suwaka
        slider_bg = pygame.Rect(self.volume_slider_rect.x - 10, self.volume_slider_rect.y - 5, 
                               self.volume_slider_rect.width + 20, self.volume_slider_rect.height + 10)
        pygame.draw.rect(screen, (60, 40, 20), slider_bg, border_radius=15)
        pygame.draw.rect(screen, (120, 90, 60), slider_bg, 3, border_radius=15)
        
        # Pasek suwaka
        pygame.draw.rect(screen, (40, 40, 40), self.volume_slider_rect, border_radius=10)
        
        # Wypełnienie suwaka (pokazuje aktualną głośność)
        fill_width = int(self.volume_slider_rect.width * self.music_volume)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.volume_slider_rect.x, self.volume_slider_rect.y, 
                                  fill_width, self.volume_slider_rect.height)
            gradient_color = (100 + int(self.music_volume * 155), 
                            255 - int(self.music_volume * 100), 
                            50)
            pygame.draw.rect(screen, gradient_color, fill_rect, border_radius=10)
        
        # Uchwyt suwaka
        handle_glow = self.volume_handle_rect.inflate(10, 10)
        pygame.draw.ellipse(screen, (255, 255, 150, 100), handle_glow)
        pygame.draw.ellipse(screen, (200, 150, 50), self.volume_handle_rect)
        pygame.draw.ellipse(screen, (255, 200, 100), self.volume_handle_rect, 3)
        
        # Przycisk powrotu
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.back_button.collidepoint(mouse_pos)
        self.draw_rpg_button_animated(screen, self.back_button, "Powrót", False, is_hovered, "blue")

    def draw_controls_menu_rpg(self):
        """Rysuje menu sterowania w stylu RPG"""
        # Tytuł
        title = self.rpg_font_large.render("~ STEROWANIE ~", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.pause_menu_rect.centerx, self.pause_menu_rect.y + 60))
        
        shadow = self.rpg_font_large.render("~ STEROWANIE ~", True, (100, 80, 0))
        shadow_rect = shadow.get_rect(center=(title_rect.centerx + 2, title_rect.centery + 2))
        screen.blit(shadow, shadow_rect)
        screen.blit(title, title_rect)
        
        # Lista kontrolek w ramkach
        controls = [
            ("WASD lub Strzałki", "Poruszanie postacią"),
            ("SPACJA", "Interakcja z obiektami"),
            ("ESC", "Menu pauzy"),
            ("Mysz", "Interfejs użytkownika")
        ]
        
        y_start = self.pause_menu_rect.y + 140
        for i, (key, description) in enumerate(controls):
            y_pos = y_start + i * 70
            
            # Ramka dla każdej kontrolki
            control_rect = pygame.Rect(self.pause_menu_rect.x + 30, y_pos, 
                                     self.pause_menu_rect.width - 60, 55)
            
            # Tło kontrolki
            bg_color = (40, 60, 100) if i % 2 == 0 else (60, 40, 100)
            pygame.draw.rect(screen, bg_color, control_rect, border_radius=10)
            pygame.draw.rect(screen, (150, 150, 200), control_rect, 2, border_radius=10)
            
            # Tekst klawisza
            key_text = self.rpg_font_medium.render(key, True, (255, 255, 100))
            key_rect = key_text.get_rect(left=control_rect.x + 15, centery=control_rect.centery - 8)
            screen.blit(key_text, key_rect)
            
            # Opis
            desc_text = self.rpg_font_small.render(description, True, (200, 200, 255))
            desc_rect = desc_text.get_rect(left=control_rect.x + 15, centery=control_rect.centery + 12)
            screen.blit(desc_text, desc_rect)
        
        # Przycisk powrotu
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.back_button.collidepoint(mouse_pos)
        self.draw_rpg_button_animated(screen, self.back_button, "Powrót", False, is_hovered, "blue")

    def get_current_room_name(self):
        """Zwraca nazwę aktualnego pokoju"""
        for name, room in self.rooms.items():
            if room == self.current_room:
                return name
        return "Unknown"
    def handle_pause_menu_keyboard(self, event):
        """Obsługuje nawigację klawiaturą w menu"""
        if event.type == pygame.KEYDOWN:
            if self.pause_menu_tab == "main":
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_button = (self.selected_button - 1) % len(self.main_menu_buttons)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_button = (self.selected_button + 1) % len(self.main_menu_buttons)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Aktywuj wybrany przycisk
                    if self.selected_button == 0:  # Resume
                        self.paused = False
                    elif self.selected_button == 1:  # Volume
                        self.pause_menu_tab = "volume"
                    elif self.selected_button == 2:  # Controls
                        self.pause_menu_tab = "controls"
                    elif self.selected_button == 3:  # Exit
                        self.player.save_data()
                        self.running = False

    def handle_pause_menu_events(self, event):
        """Obsługuje zdarzenia w menu pauzy"""
        # Dodaj obsługę klawiatury
        self.handle_pause_menu_keyboard(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.pause_menu_tab == "main":
                if self.resume_button.collidepoint(event.pos):
                    self.paused = False
                elif self.volume_button.collidepoint(event.pos):
                    self.pause_menu_tab = "volume"
                elif self.controls_button.collidepoint(event.pos):
                    self.pause_menu_tab = "controls"
                elif self.exit_button.collidepoint(event.pos):
                    self.player.save_data()
                    self.running = False
                    
            elif self.pause_menu_tab == "volume":
                if self.back_button.collidepoint(event.pos):
                    self.pause_menu_tab = "main"
                elif self.volume_slider_rect.collidepoint(event.pos):
                    self.dragging_volume = True
                    
            elif self.pause_menu_tab == "controls":
                if self.back_button.collidepoint(event.pos):
                    self.pause_menu_tab = "main"
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_volume = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_volume and self.pause_menu_tab == "volume":
                # Aktualizuj pozycję suwaka
                relative_x = event.pos[0] - self.volume_slider_rect.x
                self.music_volume = max(0, min(1, relative_x / self.volume_slider_rect.width))
                self.update_volume_handle()
                
                # Rzeczywista zmiana głośności
                if self.music_manager:
                    self.music_manager.set_music_volume(self.music_volume)
                else:
                    pygame.mixer.music.set_volume(self.music_volume)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.player.save_data()
                self.running = False

            # Obsługa ESC dla menu pauzy - PRIORYTET NAJWYŻSZY
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Jeśli jest aktywny interfejs FeeRoom, zamknij go
                if isinstance(self.current_room, FeeRoom) and self.current_room.fee_interface_active:
                    self.current_room.close_fee_interface()
                    continue
            
            # Inaczej obsłuż menu pauzy
                if self.paused:
                    if self.pause_menu_tab != "main":
                        self.pause_menu_tab = "main"
                    else:
                    # ZMIENIONE: Zamiast natychmiastowego zamknięcia, ustaw animację
                        self.paused = False
                        self.menu_target_scale = 0.0
                        self.menu_target_alpha = 0
                else:
                # ZMIENIONE: Zamiast natychmiastowego otwarcia, ustaw animację
                    self.paused = True
                    self.pause_menu_tab = "main"
                    self.menu_target_scale = 1.0
                    self.menu_target_alpha = 255
                continue

            # Jeśli gra jest spauzowana, obsługuj tylko menu pauzy
            if self.paused:
                self.handle_pause_menu_events(event)
                continue

            # Obsługa interfejsu FeeRoom ma wysoki priorytet (ale niższy niż ESC)
            if isinstance(self.current_room, FeeRoom) and self.current_room.fee_interface_active:
                if self.current_room.handle_fee_event(event, self.player):
                    continue

            # Obsługa wydarzeń w zależności od stanu gry
            if self.in_dice_game:
                self.dice_game.handle_event(event)
                if not self.dice_game.in_game:
                    self.in_dice_game = False
                continue
                
            elif self.in_cups_game:
                self.cups_game.handle_event(event)
                if not self.cups_game.in_game:
                    self.in_cups_game = False
                continue
            
            elif self.in_wheel_game:
                self.wheel_game.handle_event(event)
                if not self.wheel_game.in_game:
                    self.in_wheel_game = False
                continue
            elif self.in_beetle_game:
                self.beetle_game.handle_event(event)
                if not self.beetle_game.in_game:
                    self.in_beetle_game = False
                continue
            # Sprawdź czy jakiś NPC ma aktywne okno czatu
            any_npc_handled = False
            for npc in self.current_room.npcs:
                if npc.chat_window.active and npc.handle_event(event):
                    any_npc_handled = True
                    break

            # Jeśli NPC obsłużył zdarzenie, nie przetwarzaj dalej
            if any_npc_handled:
                continue

            # Obsługa wydarzeń gry głównej
            if event.type == pygame.KEYDOWN:
                self.ui.handle_todo_event(event)
                if event.key == pygame.K_SPACE:
                    # Sprawdź czy gracz jest przy strefie wpłat w FeeRoom
                    if isinstance(self.current_room, FeeRoom) and self.current_room.check_fee_interaction(self.player):
                        self.current_room.handle_fee_interaction(self.player)
                        
                    # Sprawdź czy gracz jest przy automacie
                    elif self.player.rect.colliderect(self.automat_rect.inflate(100, 100)):
                        self.start_minigame_with_loader("dice")
                        
                    # Sprawdź czy gracz jest przy stole z kubkami
                    elif self.player.rect.colliderect(self.cups_table_rect.inflate(100, 100)):
                        self.start_minigame_with_loader("cups")
                        
                    elif (
                        self.get_current_room_name() == "GameRoom" and 
                        self.player.rect.colliderect(self.wheel_rect.inflate(100, 100))
                    ):
                        self.start_minigame_with_loader("wheel")
                    elif self.player.rect.colliderect(self.beetle_table_rect.inflate(100, 100)):
                        self.start_minigame_with_loader("beetle")    
                    if isinstance(self.current_room, MainRoom) and self.player_near_coffee_machine:
                        if hasattr(self.current_room, 'coffee_machine'):
                            success = self.current_room.coffee_machine.try_buy_coffee(self.player)
                            if success:
                                print(f"Gracz kupił kawę! Pozostało monet: {self.player.coins}")
                    # Sprawdź interakcję z NPCs
                    else:
                        for npc in self.current_room.npcs:
                            if self.player.rect.colliderect(npc.rect.inflate(100, 100)):
                                npc.handle_interaction()
                                break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.ui.handle_todo_click(event.pos)
                    
    def start_minigame_with_loader(self, game_type):
        """Uruchamia minigrę z ekranem ładowania"""
        # Stwórz i uruchom ekran ładowania
        loader = MiniGameLoader(game_type, self.player.name)
        
        # Uruchom ekran ładowania
        if loader.run():
            # Po zakończeniu ładowania, uruchom odpowiednią minigrę
            if game_type == "dice":
                self.in_dice_game = True
                self.dice_game.reset_game()
            elif game_type == "cups":
                self.in_cups_game = True
                self.cups_game.reset_game()
            elif game_type == "wheel":
                self.in_wheel_game = True
                self.wheel_game.reset_game()
            elif game_type == "beetle":
                self.in_beetle_game = True
                self.beetle_game.reset_game()

    def handle_coffee_machine_interaction(self):
        """Obsługuje interakcje z automatem kawy w MainRoom"""
        if hasattr(self.current_room, 'coffee_machine'):
            is_near = self.current_room.coffee_machine.is_player_near(
                self.player.rect.x, self.player.rect.y)
            
            if is_near and not self.player_near_coffee_machine:
                # Gracz zbliżył się do automatu
                self.current_room.coffee_machine.show_interaction_prompt()
                self.player_near_coffee_machine = True
            elif not is_near and self.player_near_coffee_machine:
                # Gracz oddalił się od automatu
                self.current_room.coffee_machine.hide_interaction_prompt()
                self.player_near_coffee_machine = False