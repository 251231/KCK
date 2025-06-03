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

class Game:
    def __init__(self, username):
        self.running = True
        self.clock = pygame.time.Clock()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, None, username)
        self.camera_x = 0
        self.camera_y = 0
        self.chat_mode = False
        self.chat_history = []
        self.chat_input = ""
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

        self.automat_rect = pygame.Rect(1000, 700, 50, 50)
        self.cups_table_rect = pygame.Rect(800, 600, 60, 60)
        self.interaction_hint = None

    def init_rooms(self):
        self.rooms = {
            "MainRoom": MainRoom(),
            "GameRoom": GameRoom(),
            "RegisterRoom": RegisterRoom(),
            "FeeRoom": FeeRoom(),
            "DataRoom": DataRoom()
        }

    def update(self, dx, dy, delta_time):
        # Aktualizuj cooldown teleportacji
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= delta_time
            
        # Porusz gracza
        self.player.move(dx, dy, delta_time, self.current_room.objects, self.current_room.check_collision)
        
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
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
        return dx, dy

    def draw_chat(self):
        chat_box = pygame.Rect(50, SCREEN_HEIGHT - 250, SCREEN_WIDTH - 100, 200)
        pygame.draw.rect(screen, (200, 200, 200), chat_box, border_radius=12)
        y = SCREEN_HEIGHT - 240
        for line in self.wrap_chat_text(self.chat_history[-5:], SCREEN_WIDTH - 120):
            line_text = font.render(line, True, BLACK)
            screen.blit(line_text, (60, y))
            y += 30
        input_text = font.render("Ty: " + self.chat_input, True, BLACK)
        screen.blit(input_text, (60, y))

    def wrap_chat_text(self, lines, max_width):
        wrapped_lines = []
        for line in lines:
            words = line.split()
            wrapped = ""
            for word in words:
                test_line = wrapped + word + " "
                if font.size(test_line)[0] > max_width:
                    wrapped_lines.append(wrapped.strip())
                    wrapped = word + " "
                else:
                    wrapped = test_line
            if wrapped:
                wrapped_lines.append(wrapped.strip())
        return wrapped_lines

    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000
            self.handle_events()
            dx, dy = self.handle_input()
            self.update(dx, dy, delta_time)
            self.draw()

    def draw(self):
        # Rysuj tło pokoju
        self.current_room.draw(screen, self.camera_x, self.camera_y)
        self.player.draw(self.camera_x, self.camera_y)
        self.ui.draw()

        if self.chat_mode:
            self.draw_chat()

        # Podpowiedzi interakcji i gra w kości
        if self.interaction_hint and not self.in_dice_game and not self.in_cups_game:
            hint_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 70, 400, 40)
            pygame.draw.rect(screen, (255, 255, 224), hint_box, border_radius=12)
            hint_text = font.render(self.interaction_hint, True, BLACK)
            screen.blit(hint_text, (hint_box.x + 20, hint_box.y + 10))

        if self.in_dice_game:
            self.dice_game.draw()
        elif self.in_cups_game:
            self.cups_game.draw()
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

        pygame.display.flip()

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

            elif event.type == pygame.KEYDOWN:
                # ZMODYFIKUJ: Obsługa gier
                if self.in_dice_game:
                    self.dice_game.handle_event(event)
                    if not self.dice_game.in_game:
                        self.in_dice_game = False
                elif self.in_cups_game:
                    # DODAJ: Obsługa gry w kubki
                    self.cups_game.handle_event(event)
                    if not self.cups_game.in_game:
                        self.in_cups_game = False
                elif self.chat_mode:
                    if event.key == pygame.K_RETURN:
                        if self.chat_input.strip():
                            self.chat_history.append("Ty: " + self.chat_input)
                            response = get_ai_response(self.chat_input)
                            self.chat_history.append("NPC: " + response)
                            self.chat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.chat_input = self.chat_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.chat_mode = False
                    else:
                        self.chat_input += event.unicode
                else:
                    self.ui.handle_todo_event(event)
                    if event.key == pygame.K_SPACE:
                        if self.player.rect.colliderect(self.automat_rect.inflate(100, 100)):
                            self.in_dice_game = True
                            self.dice_game.reset_game()
                        elif self.player.rect.colliderect(self.cups_table_rect.inflate(100, 100)):
                            self.in_cups_game = True
                            self.cups_game.reset_game()
                        for npc in self.current_room.npcs:
                            if self.player.rect.colliderect(npc.rect.inflate(100, 100)):
                                self.chat_mode = True
                                self.chat_history.append("NPC: Witaj studencie! W czym mogę pomóc?")
                                break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.in_dice_game:
                    self.dice_game.handle_event(event)
                    if not self.dice_game.in_game:
                        self.in_dice_game = False
                elif self.in_cups_game:
                    self.cups_game.handle_event(event)
                    if not self.cups_game.in_game:
                        self.in_cups_game = False
                elif self.quit_button.collidepoint(event.pos):
                    self.player.save_data()
                    self.running = False
                else:
                    self.ui.handle_todo_click(event.pos)

            # Handle other events for games (removed the problematic line)
            elif self.in_dice_game:
                self.dice_game.handle_event(event)
            elif self.in_cups_game:
                # Fixed: Use handle_event instead of handle_timer_event
                self.cups_game.handle_event(event)