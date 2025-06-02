from Room import Room
from NPC import NPC

class MainRoom(Room):
    def __init__(self):
        super().__init__(
            background_path="assets/Glowna_mapa.png",
            collision_path="assets/Glowna_mapa_kolizje.png",
            npcs=[NPC(800, 600)],
            objects=[]
        )

