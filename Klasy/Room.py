import pygame

from Klasy.config import BLUE, SCREEN_HEIGHT, SCREEN_WIDTH

class Room:
    def __init__(self, background_path, collision_path, npcs=None, objects=None):
        bg = pygame.image.load(background_path).convert()
        col = pygame.image.load(collision_path).convert()

        self.map_background = pygame.transform.scale(bg, (bg.get_width() * 2, bg.get_height() * 2))
        self.collision_map = pygame.transform.scale(col, (col.get_width() * 2, col.get_height() * 2))

        self.npcs = npcs or []
        self.objects = objects or []

    def draw(self, surface, camera_x, camera_y):
        surface.blit(self.map_background, (0, 0), pygame.Rect(camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT))
        for obj in self.objects:
            pygame.draw.rect(surface, BLUE, pygame.Rect(obj.x - camera_x, obj.y - camera_y, obj.width, obj.height))
        for npc in self.npcs:
            npc.draw(camera_x, camera_y)
