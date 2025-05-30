from config import *

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
        if os.path.exists("DataBase/user_data.json"):
            with open("DataBase/user_data.json", "r") as f:
                data = json.load(f)
                if self.name in data:
                    self.coins = data[self.name]["coins"]

    def save_data(self):
        data = {}
        if os.path.exists("DataBase/user_data.json"):
            with open("DataBase/user_data.json", "r") as f:
                data = json.load(f)

        data[self.name] = {"coins": self.coins}
        with open("DataBase/user_data.json", "w") as f:
            json.dump(data, f, indent=4)

    def move(self, dx, dy, delta_time, objects):
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length != 0:
            dx = (dx / length) * self.player_speed * delta_time * 100
            dy = (dy / length) * self.player_speed * delta_time * 100

        self.move_axis(dx, 0, objects)
        self.move_axis(0, dy, objects)

    def move_axis(self, dx, dy, objects):
        distance = math.hypot(dx, dy)
        if distance == 0:
            return

        step = 1  # krok 1 px dla dokładności (można użyć np. 0.5 dla większej precyzji)
        steps = int(distance // step)
        if steps == 0:
            steps = 1

        step_dx = dx / steps
        step_dy = dy / steps

        for _ in range(steps):
            self.rect.x += step_dx
            self.rect.y += step_dy
            if self.check_collision(objects):
                self.rect.x -= step_dx
                self.rect.y -= step_dy
                break 

    def check_collision(self, objects):
        for obj in objects:
            if self.rect.colliderect(obj):
                return True
        return False

    def draw(self, camera_x, camera_y):
        pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y - camera_y, self.player_size, self.player_size))