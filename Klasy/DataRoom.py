from Room import Room
from NPC import *
from AnimatedModels import AnimatedLamp
class DataRoom(Room):
    def __init__(self):
        super().__init__(
                bg_path="assets/DataRoom.png",
                collision_path="assets/DataRoom_kolizje.png",
                npcs=None,
                teleport_zones={
                    (255, 255, 0): ("MainRoom", "from_data"),  
                },
                entry_points={
                    "default": (100, 100),
                    "from_main": (137, 550),    # Gdzie gracz pojawia się przychodząc z MainRoom
                    
                }
            ),
        self.setup_lamps()

    def setup_lamps(self):
        """Konfiguruje pozycje lamp - łatwe do edycji"""
        self.lamps = [
            AnimatedLamp(x=1350, y=100, png_name="candelabrum_tall", animation_speed=250, scale=3),
            AnimatedLamp(x=1350, y=750, png_name="candelabrum_tall", animation_speed=178, scale=3),
            
             
        ]   

    def update(self, game, dt):
        """Aktualizuje pokój, lampy i automat z kawą"""
        # Aktualizuj animacje lamp
        for lamp in self.lamps:
            lamp.update()
    def handle_interaction(self, game, key_pressed):
        """Obsługuje interakcje w pokoju"""
        if key_pressed == pygame.K_e and self.player_near_coffee_machine:
            # Gracz próbuje kupić kawę
            success = self.coffee_machine.try_buy_coffee(game.player)
            return success
        return False
    
    def draw(self, surface, camera_x, camera_y):
        """Rysuje pokój, lampy i automat z kawą"""
        # Rysuj podstawowy pokój
        super().draw(surface, camera_x, camera_y)
        
        # Rysuj lampy na górze
        for lamp in self.lamps:
            lamp.draw(surface, camera_x, camera_y)
    def add_lamp(self, x, y, animation_speed=200):
        """Dodaje nową lampę w określonej pozycji"""
        new_lamp = AnimatedLamp(x, y, animation_speed)
        self.lamps.append(new_lamp)
        return new_lamp
    
    def remove_lamp(self, index):
        """Usuwa lampę o określonym indeksie"""
        if 0 <= index < len(self.lamps):
            del self.lamps[index]
    
    def move_lamp(self, index, new_x, new_y):
        """Przesuwa lampę o określonym indeksie"""
        if 0 <= index < len(self.lamps):
            self.lamps[index].set_position(new_x, new_y)

