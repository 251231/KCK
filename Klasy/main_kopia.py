import math
import pygame
import sys
import json
import os
import openai
from openai import OpenAI

# Konfiguracja API OpenAI

openai.api_key = "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"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

player_speed = 7
player_size = 40

pygame.init()
font = pygame.font.SysFont('Arial', 24)

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GameDziekanat")



class StartScreen:
    def __init__(self):
        self.background = pygame.image.load("tlo2.png").convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.play_button = pygame.Rect(580, 500, 400, 55)
        self.quit_button = pygame.Rect(480, 580, 400, 55)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_button.collidepoint(event.pos):
                        return "play"
                    if self.quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

            screen.blit(self.background, (0, 0))

            mouse_pos = pygame.mouse.get_pos()
            if self.play_button.collidepoint(mouse_pos) or self.quit_button.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            pygame.display.flip()

class UserInterface:
    def __init__(self, player):
        self.player = player
        self.todo_visible = False
        self.todo_items = []
        self.todo_button = pygame.Rect(SCREEN_WIDTH - 210, 100, 200, 40)
        self.todo_input_box = pygame.Rect(SCREEN_WIDTH - 210, 150, 200, 40)
        self.todo_input_text = ''
        self.todo_input_active = False
        self.load_todo()

    def load_todo(self):
        """Wczytuje listę zadań z pliku JSON dla danego użytkownika."""
        if os.path.exists(f"user_{self.player.name}_todo.json"):
            with open(f"user_{self.player.name}_todo.json", "r") as f:
                self.todo_items = json.load(f)

    def save_todo(self):
        """Zapisuje listę zadań do pliku JSON."""
        with open(f"user_{self.player.name}_todo.json", "w") as f:
            json.dump(self.todo_items, f, indent=4)

    def draw(self):
        """Rysuje interfejs użytkownika i listę zadań."""
        # Wyświetl dane gracza po prawej stronie ekranu
        name_text = font.render(f"Gracz: {self.player.name}", True, BLACK)
        coins_text = font.render(f"Monety: {self.player.coins}", True, BLACK)

        # Obliczamy pozycje tak, żeby napisy były przy prawej krawędzi
        name_pos = (SCREEN_WIDTH - name_text.get_width() - 20, 20)
        coins_pos = (SCREEN_WIDTH - coins_text.get_width() - 20, 50)

        screen.blit(name_text, name_pos)
        screen.blit(coins_text, coins_pos)

        # Przycisk To-Do List
        pygame.draw.rect(screen, BLUE, self.todo_button)
        todo_button_text = font.render("To-Do List", True, WHITE)
        screen.blit(todo_button_text, (self.todo_button.x + 50, self.todo_button.y + 10))

        if self.todo_visible:
            # Tło listy zadań
            pygame.draw.rect(screen, (230, 230, 230), (SCREEN_WIDTH - 220, 140, 220, 300))

            # Pole wprowadzania nowego zadania
            pygame.draw.rect(screen, WHITE, self.todo_input_box, 2)
            input_surface = font.render(self.todo_input_text, True, BLACK)
            screen.blit(input_surface, (self.todo_input_box.x + 5, self.todo_input_box.y + 5))

            # Wyświetlanie istniejących zadań
            for i, item in enumerate(self.todo_items):
                item_text = font.render(f"{i + 1}. {item}", True, BLACK)
                screen.blit(item_text, (SCREEN_WIDTH - 210, 200 + i * 30))

    def handle_todo_click(self, pos):
        """Obsługuje kliknięcia związane z To-Do listą."""
        if self.todo_button.collidepoint(pos):
            self.todo_visible = not self.todo_visible
            return True
        elif self.todo_input_box.collidepoint(pos):
            self.todo_input_active = True
            return True
        return False

    def add_todo_item(self):
        """Dodaje nowe zadanie do listy."""
        if self.todo_input_text.strip():
            self.todo_items.append(self.todo_input_text)
            self.todo_input_text = ''
            self.save_todo()

    def handle_todo_event(self, event):
        """Obsługuje zdarzenia klawiatury dla To-Do listy."""
        if event.type == pygame.KEYDOWN and self.todo_input_active:
            if event.key == pygame.K_RETURN:
                self.add_todo_item()
            elif event.key == pygame.K_BACKSPACE:
                self.todo_input_text = self.todo_input_text[:-1]
            else:
                self.todo_input_text += event.unicode


def get_ai_response(user_input):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # lub "gpt-4" jeśli masz dostęp
        messages=[
            {"role": "system", "content": "Jesteś pomocnym NPC w grze."},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()


class NPC:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)

    def draw(self, camera_x, camera_y):
        pygame.draw.rect(screen, YELLOW, (self.rect.x - camera_x, self.rect.y - camera_y, 40, 40))

class Player:
    def __init__(self, x, y, texture, username):
        self.x = x
        self.y = y
        self.name = username
        self.texture = texture
        self.player_speed = player_speed
        self.player_size = player_size
        self.rect = pygame.Rect(self.x, self.y, self.player_size, self.player_size)
        self.coins = 0
        self.load_data()

    def load_data(self):
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r") as f:
                data = json.load(f)
                if self.name in data:
                    self.coins = data[self.name]["coins"]

    def save_data(self):
        data = {}
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r") as f:
                data = json.load(f)

        data[self.name] = {"coins": self.coins}
        with open("user_data.json", "w") as f:
            json.dump(data, f, indent=4)

    def move(self, dx, dy, delta_time, objects):
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length != 0:
            dx = (dx / length) * self.player_speed * delta_time * 100
            dy = (dy / length) * self.player_speed * delta_time * 100

        self.rect.x += dx
        if self.check_collision(objects):
            self.rect.x -= dx
        self.rect.y += dy
        if self.check_collision(objects):
            self.rect.y -= dy

    def check_collision(self, objects):
        for obj in objects:
            if self.rect.colliderect(obj):
                return True
        return False

    def draw(self, camera_x, camera_y):
        pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y - camera_y, self.player_size, self.player_size))

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
        self.quit_button = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 70, 200,
                                       50)
        self.ui = UserInterface(self.player)

    def update(self, dx, dy, delta_time):
        """Aktualizacja gry (ruch gracza i kolizje)."""
        self.player.move(dx, dy, delta_time, self.objects)
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
        pygame.draw.rect(screen, (200, 200, 200), (50, SCREEN_HEIGHT - 250, SCREEN_WIDTH - 100, 200))
        y = SCREEN_HEIGHT - 240
        for line in self.chat_history[-5:]:
            line_text = font.render(line, True, BLACK)
            screen.blit(line_text, (60, y))
            y += 30
        input_text = font.render("Ty: " + self.chat_input, True, BLACK)
        screen.blit(input_text, (60, y))

    def run(self):
        while self.running:
            while self.running:
                delta_time = self.clock.tick(60) / 1000  # Czas między klatkami w sekundach
                self.handle_events()
                dx, dy = self.handle_input()
                self.update(dx, dy, delta_time)
                self.draw()

    def draw(self):
        screen.fill(WHITE)
        for obj in self.objects:
            pygame.draw.rect(screen, BLUE, obj)
        for npc in self.npcs:
            npc.draw(self.camera_x, self.camera_y)
        self.player.draw(self.camera_x, self.camera_y)
        self.ui.draw()
        if self.chat_mode:
            self.draw_chat()

        x, y = int(self.player.rect.x), int(self.player.rect.y)
        coords_text = font.render(f"X: {x}, Y: {y}", True, BLACK)
        screen.blit(coords_text, (10, 10))

        pygame.draw.rect(screen, RED, self.quit_button)
        quit_text = font.render("Zakończ grę", True, WHITE)
        screen.blit(quit_text, (self.quit_button.x + 50, self.quit_button.y + 10))

        mouse_pos = pygame.mouse.get_pos()  # Pobieramy pozycję kursora
        if self.quit_button.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # Zmiana kursora na łapkę
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.player.save_data()
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.chat_mode:
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
                    # Tryb normalny: obsługa UI i interakcji
                    self.ui.handle_todo_event(event)
                    if event.key == pygame.K_SPACE:
                        for npc in self.npcs:
                            if self.player.rect.colliderect(npc.rect.inflate(100, 100)):
                                self.chat_mode = True
                                self.chat_history.append("NPC: Witaj studencie! W czym mogę pomóc?")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.quit_button.collidepoint(event.pos):
                    self.player.save_data()
                    self.running = False
                else:
                    self.ui.handle_todo_click(event.pos)


def menu_logowania():
    input_box = pygame.Rect(600, 400, 300, 50)
    login_button = pygame.Rect(600, 470, 300, 50)
    color_inactive = pygame.Color('gray15')
    color_active = pygame.Color('lightskyblue3')
    button_color = pygame.Color('green')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                if login_button.collidepoint(event.pos) and text.strip():
                    done = True
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    return text
                color = color_active if active else color_inactive
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and text.strip():
                    done = True
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        # Rysuj pole tekstowe
        txt_surface = font.render(text, True, WHITE)
        input_box.w = max(300, txt_surface.get_width() + 10)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 10))
        pygame.draw.rect(screen, color, input_box, 2)

        # Rysuj przycisk logowania
        pygame.draw.rect(screen, button_color, login_button)
        button_text = font.render("ZALOGUJ", True, BLACK)
        screen.blit(button_text, (login_button.x + 90, login_button.y + 10))

        # Instrukcja
        info = font.render("Podaj login", True, YELLOW)
        screen.blit(info, (600, 350))
        mouse_pos = pygame.mouse.get_pos()

        mouse_pos = pygame.mouse.get_pos()
        if input_box.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)  # Tekstowy
        elif login_button.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # Łapka
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Normalna strzałka
        pygame.display.flip()

if __name__ == "__main__":
    start_screen = StartScreen()
    start_screen.run()
    username = menu_logowania()
    game = Game(username)
    game.run()
    pygame.quit()
