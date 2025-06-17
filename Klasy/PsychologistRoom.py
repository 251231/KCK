from Room import Room
from NPC import *
from AnimatedModels import AnimatedLamp
class PsychologistRoom(Room):
    def __init__(self):
        super().__init__(
                npcs=[NPC(900, 500)],
                bg_path="assets/PsychologistRoom.png",
                collision_path="assets/PsychologistRoom_kolizje.png",
                
                teleport_zones={
                    (255, 255, 0): ("MainRoom", "from_psychologist"),  # Żółty kolor -> MainRoom
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
            AnimatedLamp(x=1210, y=415, png_name="candle_blue_1", animation_speed=124, scale=3),
            AnimatedLamp(x=1210, y=590, png_name="candle_blue_1", animation_speed=253, scale=3),
            AnimatedLamp(x=1150, y=590, png_name="candle_blue_1", animation_speed=312, scale=3),
            AnimatedLamp(x=1150, y=0, png_name="torch_small_blue", animation_speed=175, scale=3),
            AnimatedLamp(x=371, y=0, png_name="torch_small_blue", animation_speed=200, scale=3),
            AnimatedLamp(x=1450, y=200, png_name="torch_big_blue", animation_speed=200, scale=3),
            AnimatedLamp(x=1450, y=700, png_name="torch_big_blue", animation_speed=200, scale=3),
            
             
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