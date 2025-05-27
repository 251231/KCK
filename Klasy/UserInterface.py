from config import *



USERS_DB_PATH = "../DataBase/users.json"
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
        if os.path.exists(f"../DataBase/user_{self.player.name}_todo.json"):
            with open(f"../DataBase/user_{self.player.name}_todo.json", "r") as f:
                self.todo_items = json.load(f)

    def save_todo(self):
        """Zapisuje listę zadań do pliku JSON."""
        with open(f"../DataBase/user_{self.player.name}_todo.json", "w") as f:
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



