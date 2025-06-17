from Room import Room
from NPC import *
from AnimatedModels import AnimatedLamp
import pygame


class RegisterRoom(Room):
    def __init__(self):
        super().__init__(
            bg_path="assets/RegisterRoom.png",
            collision_path="assets/RegisterRoom_kolizje.png",
            npcs=None,
            teleport_zones={
                (255, 255, 0): ("MainRoom", "from_Register"),
            },
            entry_points={
                "default": (100, 100),
                "from_main": (1361, 550),
            }
        )

        self.interaction_point = {
            "position": (600, 500),
            "rect": pygame.Rect(0, 0, 40, 40),
            "image": pygame.image.load("assets/Sport.png"),
            "hint_text": "Naciśnij LSHIFT, aby zobaczyć dyscypliny sportowe"
        }
        self.interaction_point["rect"].center = self.interaction_point["position"]

        self.showing_image = False
        self.current_image = None
        self.setup_lamps()

    def setup_lamps(self):
        self.lamps = [
            AnimatedLamp(x=40, y=200, png_name="torch_big", animation_speed=250, scale=3),
            AnimatedLamp(x=1450, y=200, png_name="torch_big", animation_speed=250, scale=3),
            AnimatedLamp(x=1450, y=700, png_name="torch_big", animation_speed=250, scale=3),
            AnimatedLamp(x=1050, y=-20, png_name="torch_small", animation_speed=250, scale=3),
            AnimatedLamp(x=300, y=-20, png_name="torch_small", animation_speed=250, scale=3),
            AnimatedLamp(x=40, y=700, png_name="torch_big", animation_speed=250, scale=3),
        ]

    def update(self, game, dt):

        keys = pygame.key.get_pressed()

        # Sprawdź interakcję tylko, gdy obraz nie jest aktywny
        if not self.showing_image:
            inflated = self.interaction_point["rect"].inflate(100, 100)
            if game.player.rect.colliderect(inflated):
                game.interaction_hint = self.interaction_point["hint_text"]
                if keys[pygame.K_LSHIFT]:
                    self.showing_image = True
                    self.current_image = self.interaction_point["image"]
            else:
                if game.interaction_hint == self.interaction_point["hint_text"]:
                    game.interaction_hint = None
        else:
            # Wyjście z interakcji
            if keys[pygame.K_RETURN]:
                self.showing_image = False
                self.current_image = None
                game.interaction_hint = None

        # Aktualizacja animacji lamp
        for lamp in self.lamps:
            lamp.update()

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)

        # Rysuj lampy
        for lamp in self.lamps:
            lamp.draw(screen, camera_x, camera_y)

        # Rysuj interakcyjny obraz
        if self.showing_image and self.current_image:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((50, 50, 50, 100))
            screen.blit(overlay, (0, 0))

            image_rect = self.current_image.get_rect(center=screen.get_rect().center)
            screen.blit(self.current_image, image_rect)

            font = pygame.font.Font("assets/Czcionka.ttf", 36)
            text_surf = font.render("Naciśnij ENTER, aby wrócić", True, (0, 0, 0))
            screen.blit(text_surf, (screen.get_width() // 2 - text_surf.get_width() // 2, 30))

    def handle_interaction(self, game, key_pressed):
        if key_pressed == pygame.K_e and hasattr(self, 'player_near_coffee_machine') and self.player_near_coffee_machine:
            return self.coffee_machine.try_buy_coffee(game.player)
        return False

    def add_lamp(self, x, y, animation_speed=200):
        new_lamp = AnimatedLamp(x, y, animation_speed)
        self.lamps.append(new_lamp)
        return new_lamp

    def remove_lamp(self, index):
        if 0 <= index < len(self.lamps):
            del self.lamps[index]

    def move_lamp(self, index, new_x, new_y):
        if 0 <= index < len(self.lamps):
            self.lamps[index].set_position(new_x, new_y)

