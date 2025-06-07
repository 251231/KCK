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


class Game:
    def __init__(self, username):
        self.running = True
        self.clock = pygame.time.Clock()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, None, username)
        self.camera_x = 0
        self.camera_y = 0
        # Usunięte stary system czatu
        self.quit_button = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 70, 200, 50)
        self.ui = UserInterface(self.player)
        
        # Inicjalizacja pokoi
        self.init_rooms()
        self.current_room = self.rooms["MainRoom"]
        
        # Cooldown dla teleportacji (żeby nie teleportować się wielokrotnie)
        self.teleport_cooldown = 0

        # Dodatkowe atrybuty z DiceGame
        self.dice_game = DiceGame(self.player)
        self.in_dice_game = False

        self.cups_game = CupsGame(self.player)
        self.in_cups_game = False

        self.wheel_game = WheelOfFortuneGame(self.player)
        self.in_wheel_game = False

        self.automat_rect = pygame.Rect(1000, 700, 50, 50)
        self.cups_table_rect = pygame.Rect(800, 600, 60, 60)
        self.wheel_rect = pygame.Rect(600, 600, 60, 60)

        self.interaction_hint = None

    def init_rooms(self):
        self.rooms = {
            "MainRoom": MainRoom(),
            "GameRoom": GameRoom(),
            "RegisterRoom": RegisterRoom(),
            "FeeRoom": FeeRoom(),
            "DataRoom": DataRoom()
        }

    def is_in_any_interaction(self):
        """Sprawdza czy gracz jest w jakiejkolwiek interakcji (minigra lub rozmowa z NPC)"""
        # Sprawdź minigry
        if self.in_dice_game or self.in_cups_game:
            return True
        
        # Sprawdź czy jakiś NPC ma aktywne okno czatu
        for npc in self.current_room.npcs:
            if npc.chat_window.active:
                return True
        
        return False

    def update(self, dx, dy, delta_time):
        # Jeśli jesteśmy w interakcji, nie aktualizuj gry głównej
        if self.is_in_any_interaction():
            return
        
        if self.in_wheel_game:
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
        
        # Sprawdź teleportację (tylko jeśli cooldown minął)
        if self.teleport_cooldown <= 0:
            self.check_room_transitions()

        # Obsługa podpowiedzi interakcji
        if self.player.rect.colliderect(self.automat_rect.inflate(100, 100)):
            self.interaction_hint = "Naciśnij SPACJĘ, aby zagrać"
        elif self.player.rect.colliderect(self.cups_table_rect.inflate(100, 100)):
            self.interaction_hint = "Naciśnij SPACJĘ, aby zagrać w kubki"
        elif any(self.player.rect.colliderect(npc.rect.inflate(100, 100)) for npc in self.current_room.npcs):
            self.interaction_hint = "Naciśnij SPACJĘ, aby porozmawiać"
        elif self.player.rect.colliderect(self.wheel_rect.inflate(100, 100)):
            self.interaction_hint = "Naciśnij SPACJĘ, aby zakręcić kołem"
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
            print(f"Zmieniam pokój na: {room_name}, punkt wejścia: {entry_point}")
            
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
        # Jeśli jesteśmy w interakcji, nie obsługuj ruchu gracza
        if self.is_in_any_interaction():
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
        if self.in_dice_game:
            self.dice_game.draw()
            pygame.display.flip()
            return
        elif self.in_cups_game:
            self.cups_game.draw()
            pygame.display.flip()
            return
        if self.in_wheel_game and self.get_current_room_name() == "GameRoom":
            self.wheel_game.draw()
            pygame.display.flip()
            return
  
        # Jeśli jakiś NPC ma aktywne okno czatu, rysuj tylko okno czatu
        for npc in self.current_room.npcs:
            if npc.chat_window.active:
                npc.draw_chat_only()
                pygame.display.flip()
                return
        
        # Rysuj normalną grę tylko jeśli nie ma żadnych interakcji
        self.draw_main_game()
        pygame.display.flip()

    def draw_main_game(self):
        """Rysuje główną grę (pokój, gracza, UI itp.)"""
        # Rysuj tło pokoju
        self.current_room.draw(screen, self.camera_x, self.camera_y)
        
        
        
        self.player.draw(self.camera_x, self.camera_y)
        self.ui.draw()

        # Podpowiedzi interakcji
        if self.interaction_hint:
            hint_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 70, 400, 40)
            pygame.draw.rect(screen, (255, 255, 224), hint_box, border_radius=12)
            hint_text = font.render(self.interaction_hint, True, BLACK)
            screen.blit(hint_text, (hint_box.x + 20, hint_box.y + 10))
            
        # Rysuj stół z kubkami
        cups_table_screen_pos = (
            self.cups_table_rect.x - self.camera_x,
            self.cups_table_rect.y - self.camera_y
        )
        if (0 <= cups_table_screen_pos[0] <= SCREEN_WIDTH and 
            0 <= cups_table_screen_pos[1] <= SCREEN_HEIGHT):
            
            # Rysuj stół
            pygame.draw.rect(screen, (139, 69, 19), 
                           (*cups_table_screen_pos, self.cups_table_rect.width, self.cups_table_rect.height))
            pygame.draw.rect(screen, (101, 67, 33), 
                           (*cups_table_screen_pos, self.cups_table_rect.width, self.cups_table_rect.height), 3)
            
            # Dodaj tekst "KUBKI"
            table_text = font.render("KUBKI", True, (255, 215, 0))
            text_rect = table_text.get_rect(center=(
                cups_table_screen_pos[0] + self.cups_table_rect.width // 2,
                cups_table_screen_pos[1] + self.cups_table_rect.height // 2
            ))
            screen.blit(table_text, text_rect)

        # Rysuj strefę koła fortuny tylko w GameRoom
        if self.get_current_room_name() == "GameRoom":
            wheel_pos = (self.wheel_rect.x - self.camera_x, self.wheel_rect.y - self.camera_y)
            pygame.draw.rect(screen, (0, 100, 200), (*wheel_pos, self.wheel_rect.width, self.wheel_rect.height))
            wheel_text = font.render("KOŁO", True, (255, 255, 0))
            screen.blit(wheel_text, (wheel_pos[0], wheel_pos[1] - 20))


        # Debug info
        coords_text = font.render(f"X: {int(self.player.rect.x)}, Y: {int(self.player.rect.y)}", True, BLACK)
        screen.blit(coords_text, (10, 10))
        
        # Pokazuj aktualny pokój
        room_text = font.render(f"Pokój: {self.get_current_room_name()}", True, BLACK)
        screen.blit(room_text, (10, 40))
        
        # Pokazuj cooldown teleportacji (debug)
        if self.teleport_cooldown > 0:
            cooldown_text = font.render(f"Teleport cooldown: {self.teleport_cooldown:.1f}", True, BLACK)
            screen.blit(cooldown_text, (10, 70))

        # Przycisk quit
        pygame.draw.rect(screen, RED, self.quit_button)
        quit_text = font.render("Zakończ grę", True, WHITE)
        screen.blit(quit_text, (self.quit_button.x + 50, self.quit_button.y + 10))

        # Kursor myszy
        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if self.quit_button.collidepoint(mouse_pos) else pygame.SYSTEM_CURSOR_ARROW)

    def get_current_room_name(self):
        """Zwraca nazwę aktualnego pokoju"""
        for name, room in self.rooms.items():
            if room == self.current_room:
                return name
        return "Unknown"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.player.save_data()
                self.running = False

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
                    # Sprawdź czy gracz jest przy automacie
                    if self.player.rect.colliderect(self.automat_rect.inflate(100, 100)):
                        self.in_dice_game = True
                        self.dice_game.reset_game()
                    # Sprawdź czy gracz jest przy stole z kubkami
                    elif self.player.rect.colliderect(self.cups_table_rect.inflate(100, 100)):
                        self.in_cups_game = True
                        self.cups_game.reset_game()
                    elif (
                        self.get_current_room_name() == "GameRoom" and 
                        self.player.rect.colliderect(self.wheel_rect.inflate(100, 100))
                    ):
                        self.in_wheel_game = True
                        self.wheel_game.reset_game()


                    # Sprawdź interakcję z NPCs
                    else:
                        for npc in self.current_room.npcs:
                            if self.player.rect.colliderect(npc.rect.inflate(100, 100)):
                                npc.handle_interaction()
                                break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.quit_button.collidepoint(event.pos):
                    self.player.save_data()
                    self.running = False
                else:
                    self.ui.handle_todo_click(event.pos)