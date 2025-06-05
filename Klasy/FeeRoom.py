from Room import Room
from NPC import *

class FeeRoom(Room):
    def __init__(self):
        super().__init__(
                bg_path="assets/FeeRoom.png",
                collision_path="assets/FeeRoom_kolizje.png",
                npcs=[NPC(300, 400)],
                teleport_zones={
                    (255, 255, 0): ("MainRoom", "from_fee"),  
                },
                entry_points={
                    "default": (100, 100),
                    "from_main": (1345, 600),    # Gdzie gracz pojawia się przychodząc z MainRoom
                    
                }
            ),

    def update(self, game, delta_time):
        # np. minigra, sprawdzenie czegoś, zadanie
        pass