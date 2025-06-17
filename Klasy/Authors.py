from Room import Room
from NPC import *

class Authors(Room):
    def __init__(self):
        super().__init__(
            bg_path="assets/Authors.png",  # Ścieżka do obrazka z autorami
            collision_path="assets/Authors.png",
            npcs=None,
            teleport_zones={},
            entry_points={"default": (1138, 350)}  # Niepotrzebne, ale wymagane przez klasę bazową
        )
        bg = pygame.image.load("assets/Authors.png").convert()
        self.scaled_background = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def update(self, game, dt):
        # Nie aktualizujemy gracza ani NPC – tylko obsługa powrotu ESC
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            game.change_room("MainRoom", entry_point="default")

    def draw(self, surface, camera_x, camera_y):
        # Rysujemy tylko tło (obrazek z autorami)
        surface.blit(self.scaled_background, (0, 0))

