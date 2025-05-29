from config import *
from UserInterface import UserInterface
from Player import Player
from NPC import NPC, get_ai_response


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
        coords_text = font.render(f"X: {x} Y: {y}", True, BLACK)
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