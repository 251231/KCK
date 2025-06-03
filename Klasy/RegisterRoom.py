from Room import Room
from NPC import *

class RegisterRoom(Room):
    def __init__(self):
        super().__init__(
                bg_path="assets/RegisterRoom.png",
                collision_path="assets/RegisterRoom_kolizje.png",
                npcs=[NPC(300, 400)],
                teleport_zones={
                    (255, 255, 0): ("MainRoom", "from_Register"),  
                },
                entry_points={
                    "default": (100, 100),
                    "from_main": (1361, 550),    # Gdzie gracz pojawia się przychodząc z MainRoom
                    
                }
            ),

    def update(self, game, delta_time):
        # np. minigra, sprawdzenie czegoś, zadanie
        pass

