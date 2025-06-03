from Room import Room
from NPC import *

class DataRoom(Room):
    def __init__(self):
        super().__init__(
                bg_path="assets/DataRoom.png",
                collision_path="assets/DataRoom_kolizje.png",
                npcs=[NPC(300, 400)],
                teleport_zones={
                    (255, 255, 0): ("MainRoom", "from_data"),  
                },
                entry_points={
                    "default": (100, 100),
                    "from_main": (137, 550),    # Gdzie gracz pojawia się przychodząc z MainRoom
                    
                }
            ),

    def update(self, game, delta_time):
        # np. minigra, sprawdzenie czegoś, zadanie
        pass

