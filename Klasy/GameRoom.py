from Room import Room
from NPC import *


class GameRoom(Room):
    def __init__(self):
        super().__init__(
            bg_path="assets/GameRoom.png",
            collision_path="assets/GameRoom_kolizje.png",
            npcs=[NPC(300, 400)],
            teleport_zones={
                (255, 255, 0): ("MainRoom", "from_game"),  
            },
            entry_points={
                "default": (100, 100),
                "from_main": (786, 1555)
            }
        )

    def update(self, game, delta_time):
        # np. minigra, sprawdzenie czegoś, zadanie
        pass