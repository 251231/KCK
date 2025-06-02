import math
import pygame
import sys
import json
import os
from config import *
from UserInterface import UserInterface
from Player import Player
from NPC import NPC, get_ai_response
from DiceGame import DiceGame

class Game:
    def __init__(self, username):
        self.running = True
        self.clock = pygame.time.Clock()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, None, username)
        self.camera_x = 0
        self.camera_y = 0
        self.objects = []
        self.npcs = [NPC(800, 600)]
        self.create_objects()
        self.chat_mode = False
        self.chat_history = []
        self.chat_input = ""
        self.quit_button = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 70, 200, 50)
        self.ui = UserInterface(self.player)
        original_bg = pygame.image.load("assets/Glowna_mapa.png").convert()
        original_width, original_height = original_bg.get_size()
        scaled_bg = pygame.transform.scale(original_bg, (SCREEN_WIDTH, original_height))
        self.map_background = scaled_bg
        self.dice_game = DiceGame(self.player)
        self.in_dice_game = False
        self.automat_rect = pygame.Rect(1000, 700, 50, 50)
        self.interaction_hint = None

    def update(self, dx, dy, delta_time):
        self.player.move(dx, dy, delta_time, self.objects)
        self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_y = self.player.rect.centery - SCREEN_HEIGHT // 2

        bg_width, bg_height = self.map_background.get_size()
        self.camera_x = max(0, min(self.camera_x, bg_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, bg_height - SCREEN_HEIGHT))

        if self.player.rect.colliderect(self.automat_rect.inflate(100, 100)):
            self.interaction_hint = "Naciśnij SPACJĘ, aby zagrać"
        elif any(self.player.rect.colliderect(npc.rect.inflate(100, 100)) for npc in self.npcs):
            self.interaction_hint = "Naciśnij SPACJĘ, aby porozmawiać"
        else:
            self.interaction_hint = None

    def create_objects(self):
        self.objects.append(pygame.Rect(300, 300, 50, 50))
        self.objects.append(pygame.Rect(600, 400, 60, 60))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]: dx = -1
        if keys[pygame.K_RIGHT]: dx = 1
        if keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_DOWN]: dy = 1
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
        screen.blit(self.map_background, (0, 0), area=pygame.Rect(self.camera_x, self.camera_y, SCREEN_WIDTH, SCREEN_HEIGHT))

        for obj in self.objects:
            pygame.draw.rect(screen, BLUE, pygame.Rect(
                obj.x - self.camera_x,
                obj.y - self.camera_y,
                obj.width,
                obj.height
            ))

        for npc in self.npcs:
            npc.draw(self.camera_x, self.camera_y)

        pygame.draw.rect(screen, (255, 165, 0), (
            self.automat_rect.x - self.camera_x,
            self.automat_rect.y - self.camera_y,
            self.automat_rect.width,
            self.automat_rect.height
        ))

        self.player.draw(self.camera_x, self.camera_y)
        self.ui.draw()

        if self.chat_mode:
            self.draw_chat()

        if self.interaction_hint and not self.in_dice_game:
            hint_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 70, 400, 40)
            pygame.draw.rect(screen, (255, 255, 224), hint_box, border_radius=12)
            hint_text = font.render(self.interaction_hint, True, BLACK)
            screen.blit(hint_text, (hint_box.x + 20, hint_box.y + 10))

        if self.in_dice_game:
            self.dice_game.draw()

        coords_text = font.render(f"X: {int(self.player.rect.x)}, Y: {int(self.player.rect.y)}", True, BLACK)
        screen.blit(coords_text, (10, 10))

        pygame.draw.rect(screen, RED, self.quit_button)
        quit_text = font.render("Zakończ grę", True, WHITE)
        screen.blit(quit_text, (self.quit_button.x + 50, self.quit_button.y + 10))

        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if self.quit_button.collidepoint(mouse_pos) else pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.player.save_data()
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.in_dice_game:
                    # Przekaż zdarzenie do gry w kości
                    self.dice_game.handle_event(event)
                    # Sprawdź czy gracz chce wyjść z gry
                    if not self.dice_game.in_game:
                        self.in_dice_game = False
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
                        for npc in self.npcs:
                            if self.player.rect.colliderect(npc.rect.inflate(100, 100)):
                                self.chat_mode = True
                                self.chat_history.append("NPC: Witaj studencie! W czym mogę pomóc?")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.in_dice_game:
                    # Przekaż zdarzenie myszy do gry w kości
                    self.dice_game.handle_event(event)
                    # Sprawdź czy gracz chce wyjść z gry
                    if not self.dice_game.in_game:
                        self.in_dice_game = False
                elif self.quit_button.collidepoint(event.pos):
                    self.player.save_data()
                    self.running = False
                else:
                    self.ui.handle_todo_click(event.pos)

            # Obsługa zdarzeń timera dla animacji gry w kości
            elif self.in_dice_game:
                self.dice_game.handle_event(event)