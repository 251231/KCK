from Room import Room
from NPC import *

class PsychologistRoom(Room):
    def __init__(self):
        super().__init__(
                bg_path="assets/PsychologistRoom.png",
                collision_path="assets/PsychologistRoom_kolizje.png",
                npcs=[NPC(300, 400)],
                teleport_zones={
                    (255, 255, 0): ("MainRoom", "from_psychologist"),  # Żółty kolor -> MainRoom
                },
                entry_points={
                    "default": (100, 100),
                    "from_main": (137, 550),    # Gdzie gracz pojawia się przychodząc z MainRoom
                    
                }
            ),

    def update(self, game, delta_time):
        # np. minigra, sprawdzenie czegoś, zadanie
        pass