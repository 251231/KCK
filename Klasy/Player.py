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
        # Oblicz rzeczywisty ruch z normalizacją
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length == 0:
            return
            
        # Normalizuj wektor ruchu
        dx = (dx / length) * self.player_speed * delta_time * 100
        dy = (dy / length) * self.player_speed * delta_time * 100

        # Sprawdź kolizję w osi X
        self.move_axis(dx, 0, collision_map_check, objects)
        
        # Sprawdź kolizję w osi Y
        self.move_axis(0, dy, collision_map_check, objects)

    def move_axis(self, dx, dy, collision_map_check, objects):
        """Porusza gracza w jednej osi z dokładnym sprawdzaniem kolizji"""
        if dx == 0 and dy == 0:
            return
            
        # Zapisz aktualną pozycję
        old_x = self.rect.x
        old_y = self.rect.y
        
        # Oblicz nową pozycję
        new_x = old_x + dx
        new_y = old_y + dy
        
        # Ustaw nową pozycję
        self.rect.x = new_x
        self.rect.y = new_y
        
        # Sprawdź kolizje
        collision_detected = False
        
        # 1. Sprawdź kolizje z mapą (czarne piksele)
        if collision_map_check:
            # Sprawdź kilka punktów gracza (rogi prostokąta)
            collision_points = [
                (self.rect.x, self.rect.y),  # lewy górny róg
                (self.rect.x + self.player_size - 1, self.rect.y),  # prawy górny róg
                (self.rect.x, self.rect.y + self.player_size - 1),  # lewy dolny róg
                (self.rect.x + self.player_size - 1, self.rect.y + self.player_size - 1)  # prawy dolny róg
            ]
            
            for point_x, point_y in collision_points:
                if collision_map_check(point_x, point_y):
                    collision_detected = True
                    break
        
        # 2. Sprawdź kolizje z obiektami
        if not collision_detected and objects:
            collision_detected = self.check_collision(objects)
        
        # Jeśli wykryto kolizję, cofnij ruch
        if collision_detected:
            self.rect.x = old_x
            self.rect.y = old_y

    def check_collision(self, objects):
        """Sprawdza kolizję z listą obiektów"""
        for obj in objects:
            if self.rect.colliderect(obj):
                return True
        return False

    def draw(self, camera_x, camera_y):
        pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y - camera_y, self.player_size, self.player_size))