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

    def move(self, dx, dy, delta_time, objects, collision_map_check=None):
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length != 0:
            dx = (dx / length) * self.player_speed * delta_time * 100
            dy = (dy / length) * self.player_speed * delta_time * 100

        # Sprawdź kolizję X
        new_x = self.rect.x + dx
        if collision_map_check:
            # Sprawdź kilka punktów gracza (rogi prostokąta)
            collision_x = (
                collision_map_check(new_x, self.rect.y) or
                collision_map_check(new_x + self.player_size, self.rect.y) or
                collision_map_check(new_x, self.rect.y + self.player_size) or
                collision_map_check(new_x + self.player_size, self.rect.y + self.player_size)
            )
            if not collision_x:
                self.rect.x = new_x
        else:
            self.rect.x = new_x
            if self.check_collision(objects):
                self.rect.x -= dx

        # Sprawdź kolizję Y
        new_y = self.rect.y + dy
        if collision_map_check:
            collision_y = (
                collision_map_check(self.rect.x, new_y) or
                collision_map_check(self.rect.x + self.player_size, new_y) or
                collision_map_check(self.rect.x, new_y + self.player_size) or
                collision_map_check(self.rect.x + self.player_size, new_y + self.player_size)
            )
            if not collision_y:
                self.rect.y = new_y
        else:
            self.rect.y = new_y
            if self.check_collision(objects):
                self.rect.y -= dy

    def check_collision(self, objects):
        for obj in objects:
            if self.rect.colliderect(obj):
                return True
        return False

    def draw(self, camera_x, camera_y):
        pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y - camera_y, self.player_size, self.player_size))