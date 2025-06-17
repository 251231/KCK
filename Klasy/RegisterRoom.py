from Room import Room
from NPC import *

import pygame  # pamiętaj, żeby zaimportować pygame, jeśli nie jest jeszcze

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

        # Jeden punkt interakcji z pozycją, obrazkiem i tekstem hintu
        self.interaction_point = {
            "position": (600, 500),  # ustaw właściwe współrzędne punktu
            "rect": pygame.Rect(0, 0, 40, 40),
            "image": pygame.image.load("assets/Sport.png"),  # ścieżka do obrazka
            "hint_text": "Naciśnij LSHIFT, aby zobaczyć dyscypliny sportowe"
        }
        self.interaction_point["rect"].center = self.interaction_point["position"]

        self.showing_image = False
        self.current_image = None

    def update(self, game, delta_time):
        keys = pygame.key.get_pressed()

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
            if keys[pygame.K_RETURN]:
                self.showing_image = False
                self.current_image = None
                game.interaction_hint = None

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)
        if self.showing_image and self.current_image:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((50, 50, 50, 100))  # szary z alpha 100/255
            screen.blit(overlay, (0, 0))

            # Rysujemy obrazek na środku ekranu
            image_rect = self.current_image.get_rect(center=screen.get_rect().center)
            screen.blit(self.current_image, image_rect)

            # Instrukcja do wyjścia
            font = pygame.font.Font("assets/Czcionka.ttf", 36)
            text_surf = font.render("Naciśnij ENTER, aby wrócić", True, (0, 0, 0))
            screen.blit(text_surf, (screen.get_width() // 2 - text_surf.get_width() // 2, 30))
        
            
