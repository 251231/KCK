from Room import Room
from NPC import NPC
from AnimatedLamp import AnimatedLamp

class MainRoom(Room):
    def __init__(self):
        super().__init__(
                bg_path="assets/Glowna_mapa.png",
                collision_path="assets/Glowna_mapa_kolizje.png",
                npcs=[NPC(800, 600)],
                teleport_zones={
                    (128, 0, 128): ("GameRoom", "from_main"),  # Fioletowy kolor -> GameRoom
                    (255, 0, 0): ("RegisterRoom", "from_main"),     # Czerwony kolor -> Library
                    (0,0,255):("FeeRoom","from_main"), 
                    (255,0,255):("DataRoom","from_main"),
                },
                entry_points={
                    "default": (400, 400),
                    "from_game": (805, 220),    # Gdzie gracz pojawia się wracając z GameRoom
                    "from_register":(211,538),
                    "from_fee":(211,1330),
                    "from_data":(1420,575)
                }
            )
        
        # Konfiguracja lamp - łatwo edytowalne pozycje
        self.setup_lamps()
    
    def setup_lamps(self):
        """Konfiguruje pozycje lamp - łatwe do edycji"""
        self.lamps = [
            # Dodaj lub usuń lampy tutaj, zmieniając pozycje (x, y) i opcjonalnie prędkość animacji
            AnimatedLamp(x=570, y=50, animation_speed=250, scale=3), 
            AnimatedLamp(x=1050, y=50, animation_speed=250, scale=3), # Pierwsza lampa
              # Trzecia lampa
            # AnimatedLamp(x=900, y=300, animation_speed=180),  # Możesz dodać więcej
        ]
    
    def update(self, game, dt):
        """Aktualizuje pokój i wszystkie lampy"""
    # Aktualizuj animacje lamp
        for lamp in self.lamps:
            lamp.update()
    
    def draw(self, surface, camera_x, camera_y):
        """Rysuje pokój i wszystkie lampy"""
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