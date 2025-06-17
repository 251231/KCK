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
        self.interaction_points = [
            {
                "position": (838, 316),
                "rect": pygame.Rect(0, 0, 40, 40),
                "image": pygame.image.load("assets/Data.png"),
                "hint_text": "Naciśnij LSHIFT, aby zobaczyć swoje dane"
            },
            {
                "position": (838, 613),
                "rect": pygame.Rect(0, 0, 40, 40),
                "image": pygame.image.load("assets/Grades.png"),
                "hint_text": "Naciśnij LSHIFT, aby zobaczyć swoje oceny"
            }
        ]

        for point in self.interaction_points:
            point["rect"].center = point["position"]

        self.showing_chart = False
        self.current_image = None
        self.active_hint = None  

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
        keys = pygame.key.get_pressed()

        # Jeśli NIE pokazujemy obrazka — sprawdzamy czy gracz jest blisko któregoś punktu
        if not self.showing_chart:
            self.active_hint = None
            for i, point in enumerate(self.interaction_points):
                inflated = point["rect"].inflate(100, 100)
                if game.player.rect.colliderect(inflated):
                    game.interaction_hint = point["hint_text"]
                    self.active_hint = i
                    if keys[pygame.K_LSHIFT]:
                        self.showing_chart = True
                        self.current_image = point["image"]
                    break
            else:
                # Nie ma aktywnego hinta
                if game.interaction_hint and "obejrzeć wykres" in game.interaction_hint:
                    game.interaction_hint = None
        else:
            # Jeśli obrazek jest otwarty — ENTER zamyka
            if keys[pygame.K_RETURN]:
                self.showing_chart = False
                self.current_image = None
                game.interaction_hint = None
                self.active_hint = None

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
        

        if self.showing_chart and self.current_image:
            # Ciemna półprzezroczysta nakładka
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((50, 50, 50, 100))  # szary z alpha 100/255
            screen.blit(overlay, (0, 0))

            # Obrazek
            image_rect = self.current_image.get_rect(center=screen.get_rect().center)
            screen.blit(self.current_image, image_rect)

            # Tekst instrukcji
            font = pygame.font.Font("assets/Czcionka.ttf", 36)
            text_surf = font.render("Naciśnij ENTER, aby wrócić", True, (0, 0, 0))
            screen.blit(text_surf, (screen.get_width() // 2 - text_surf.get_width() // 2, 30))
        
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


    
       
    

