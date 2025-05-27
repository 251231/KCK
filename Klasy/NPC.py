from config import *


def get_ai_response(user_input):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # lub "gpt-4" jeśli masz dostęp
        messages=[
            {"role": "system", "content": "Jesteś pomocnym NPC w grze."},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()


class NPC:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)

    def draw(self, camera_x, camera_y):
        pygame.draw.rect(screen, YELLOW, (self.rect.x - camera_x, self.rect.y - camera_y, 40, 40))