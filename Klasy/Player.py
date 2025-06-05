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
        
        # Animacja
        self.animation_frames = []
        self.current_frame = 0
        self.animation_speed = 0.3  # Szybkość animacji (im mniej tym szybciej)
        self.animation_timer = 0
        self.is_moving = False
        self.facing_right = True
        
        # Wczytaj klatki animacji
        self.load_animation_frames()
        self.load_data()

    def load_animation_frames(self):
        """Wczytuje 8 klatek animacji z plików klatka1.png do klatka8.png"""
        try:
            for i in range(1, 9):  # klatka1 do klatka8
                frame_path = f"assets/klatka{i}.png"  # Zakładam że pliki są w głównym folderze
                if os.path.exists(frame_path):
                    frame = pygame.image.load(frame_path).convert_alpha()
                    # Przeskaluj klatkę do rozmiaru gracza
                    frame = pygame.transform.scale(frame, (self.player_size, self.player_size))
                    self.animation_frames.append(frame)
                else:
                    print(f"Ostrzeżenie: Nie znaleziono pliku {frame_path}")
                    # Stwórz prostą klatkę zastępczą
                    placeholder = pygame.Surface((self.player_size, self.player_size))
                    placeholder.fill(GREEN)
                    self.animation_frames.append(placeholder)
        except Exception as e:
            print(f"Błąd podczas wczytywania klatek animacji: {e}")
            # Stwórz domyślne klatki jeśli nie udało się wczytać
            self.create_default_frames()

    def create_default_frames(self):
        """Tworzy domyślne klatki animacji jeśli nie udało się wczytać plików"""
        self.animation_frames = []
        for i in range(8):
            frame = pygame.Surface((self.player_size, self.player_size))
            # Różne odcienie zieleni dla każdej klatki
            green_shade = (0, 255 - i * 20, 0)
            frame.fill(green_shade)
            self.animation_frames.append(frame)

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
        # Sprawdź czy gracz się porusza
        self.is_moving = (dx != 0 or dy != 0)
        
        # Ustaw kierunek patrzenia
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
        
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
        
        # Aktualizuj animację
        self.update_animation(delta_time)

    def update_animation(self, delta_time):
        """Aktualizuje animację postaci"""
        if self.is_moving and len(self.animation_frames) > 0:
            self.animation_timer += delta_time
            
            # Zmień klatkę gdy timer przekroczy próg
            if self.animation_timer >= self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                self.animation_timer = 0
        else:
            # Gdy nie porusza się, ustaw pierwszą klatkę
            self.current_frame = 0
            self.animation_timer = 0

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
        """Rysuje gracza z animacją"""
        if len(self.animation_frames) > 0:
            # Pobierz aktualną klatkę animacji
            current_sprite = self.animation_frames[self.current_frame]
            
            # Odbij sprite jeśli gracz idzie w lewo
            if not self.facing_right:
                current_sprite = pygame.transform.flip(current_sprite, True, False)
            
            # Narysuj sprite
            screen.blit(current_sprite, (self.rect.x - camera_x, self.rect.y - camera_y))
        else:
            # Fallback - rysuj prostokąt jeśli nie ma sprite'ów
            pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y - camera_y, self.player_size, self.player_size))

    def set_animation_speed(self, speed):
        """Pozwala zmienić szybkość animacji"""
        self.animation_speed = speed

    def get_animation_info(self):
        """Zwraca informacje o animacji (do debugowania)"""
        return {
            "current_frame": self.current_frame + 1,
            "total_frames": len(self.animation_frames),
            "is_moving": self.is_moving,
            "facing_right": self.facing_right,
            "animation_timer": self.animation_timer
        }