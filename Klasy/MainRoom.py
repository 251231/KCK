from config import *
from Room import Room
from NPC import NPC
from pygame.locals import *

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
            ),


    
    
    
        

    
        
        
    
            

