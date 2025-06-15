from config import *
from Room import Room
from NPC import NPC
from CoffeeMachine import CoffeeMachine

from pygame.locals import *

from AnimatedLamp import AnimatedLamp


class MainRoom(Room):
    def __init__(self):
        super().__init__(
                bg_path="assets/Glowna_mapa.png",
                collision_path="assets/Glowna_mapa_kolizje.png",
                npcs=None,
                teleport_zones={
                    (128, 0, 128): ("GameRoom", "from_main"),  # Fioletowy kolor -> GameRoom
                    (255, 0, 0): ("RegisterRoom", "from_main"),     # Czerwony kolor -> Library
                    (0,0,255):("FeeRoom","from_main"), 
                    (255,0,255):("DataRoom","from_main"),
                    (255,255,0):("PsychologistRoom","from_main"),
                    (0, 255, 0): ("Authors", "from_main"),  # Zielony kolor -> pokaż obraz
                },
                entry_points={
                    "default": (400, 400),
                    "from_game": (805, 220),    # Gdzie gracz pojawia się wracając z GameRoom
                    "from_register":(211,538),
                    "from_fee":(211,1330),
                    "from_data":(1420,575),
                    "from_psychologist":(1420,1362)
                }

            )
        
        # Konfiguracja lamp - łatwo edytowalne pozycje
        self.setup_lamps()
        
        # Dodaj automat z kawą w lewym górnym rogu, bliżej środka
        self.setup_coffee_machine()
        
        # Flaga do śledzenia czy gracz był blisko automatu
        self.player_near_coffee_machine = False
    
    def setup_lamps(self):
        """Konfiguruje pozycje lamp - łatwe do edycji"""
        self.lamps = [
            # Dodaj lub usuń lampy tutaj, zmieniając pozycje (x, y) i opcjonalnie prędkość animacji
            AnimatedLamp(x=570, y=50, animation_speed=250, scale=3), 
            AnimatedLamp(x=1050, y=50, animation_speed=250, scale=3), # Pierwsza lampa
              # Trzecia lampa
            # AnimatedLamp(x=900, y=300, animation_speed=180),  # Możesz dodać więcej
        ]
    
    def setup_coffee_machine(self):
        """Konfiguruje automat z kawą"""
        # Umieść automat w lewym górnym rogu, bliżej środka dla lepszej dostępności
        # Zmieniono z (1400, 100) na (300, 150) - lewy górny róg, bliżej środka
        self.coffee_machine = CoffeeMachine(x=300, y=150)
    
    def update(self, game, dt):
        """Aktualizuje pokój, lampy i automat z kawą"""
        # Aktualizuj animacje lamp
        for lamp in self.lamps:
            lamp.update()
            
        # Aktualizuj automat z kawą
        self.coffee_machine.update(dt)
        
        # Sprawdź czy gracz jest blisko automatu
        player = game.player
        is_near = self.coffee_machine.is_player_near(player.rect.x, player.rect.y)
        
        if is_near and not self.player_near_coffee_machine:
            # Gracz zbliżył się do automatu
            self.coffee_machine.show_interaction_prompt()
            self.player_near_coffee_machine = True
        elif not is_near and self.player_near_coffee_machine:
            # Gracz oddalił się od automatu
            self.coffee_machine.hide_interaction_prompt()
            self.player_near_coffee_machine = False
            
        # Aktualizuj boost prędkości gracza
        self.coffee_machine.update_player_speed_boost(player, dt)
    
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
            
        # Rysuj automat z kawą
        self.coffee_machine.draw(surface, camera_x, camera_y)
    
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
            
    def move_coffee_machine(self, new_x, new_y):
        """Przesuwa automat z kawą"""
        self.coffee_machine.x = new_x
        self.coffee_machine.y = new_y
        self.coffee_machine.rect.x = new_x
        self.coffee_machine.rect.y = new_y
    
    def get_coffee_machine_info(self):
        """Zwraca informacje o automacie (do debugowania)"""
        return {
            "position": (self.coffee_machine.x, self.coffee_machine.y),
            "price": self.coffee_machine.coffee_price,
            "speed_boost": self.coffee_machine.speed_boost,
            "boost_duration": self.coffee_machine.boost_duration / 1000,  # w sekundach
            "player_near": self.player_near_coffee_machine
        }