# Room.py
import pygame
from config import *


class Room:
    def __init__(self, bg_path, collision_path, npcs=None, objects=None, teleport_zones=None, entry_points=None):
        original_bg = pygame.image.load(bg_path).convert()
        original_width, original_height = original_bg.get_size()
        self.map_background = pygame.transform.scale(original_bg, (original_width * 2, original_height * 2))

        collision_map = pygame.image.load(collision_path).convert()
        self.collision_map = pygame.transform.scale(collision_map, (original_width * 2, original_height * 2))

        self.npcs = npcs if npcs else []
        self.objects = objects if objects else []
        
        # Strefy teleportacji - kolory pikseli które aktywują przejście do innego pokoju
        # Format: {(R, G, B): ("nazwa_pokoju", "punkt_wejścia")}
        self.teleport_zones = teleport_zones if teleport_zones else {}
        
        # Punkty wejścia - gdzie gracz się pojawia po przejściu z innego pokoju
        # Format: {"nazwa_punktu": (x, y)}
        self.entry_points = entry_points if entry_points else {"default": (100, 100)}

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.map_background, (0, 0), area=pygame.Rect(camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT))

        for obj in self.objects:
            pygame.draw.rect(screen, BLUE, pygame.Rect(
                obj.x - camera_x, obj.y - camera_y, obj.width, obj.height))

        for npc in self.npcs:
            npc.draw(camera_x, camera_y)

    def check_collision(self, x, y):
        if x < 0 or y < 0 or x >= self.collision_map.get_width() or y >= self.collision_map.get_height():
            return True
        try:
            color = self.collision_map.get_at((int(x), int(y)))
            return color[:3] == (0, 0, 0)
        except:
            return True
        
    def get_pixel_color(self, x, y):
        if 0 <= x < self.collision_map.get_width() and 0 <= y < self.collision_map.get_height():
            return self.collision_map.get_at((int(x), int(y)))
        return None

    def check_teleport(self, player_x, player_y):
        """Sprawdza czy gracz stoi na strefie teleportacji"""
        pixel_color = self.get_pixel_color(player_x, player_y)
        if pixel_color:
            color = pixel_color[:3]
            if color in self.teleport_zones:
                return self.teleport_zones[color]
        return None
        