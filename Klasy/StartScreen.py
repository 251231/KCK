from config import *


class StartScreen:
    def __init__(self):
        self.background = pygame.image.load("../assets/tlo2.png").convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.play_button = pygame.Rect(580, 500, 400, 55)
        self.quit_button = pygame.Rect(480, 580, 400, 55)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_button.collidepoint(event.pos):
                        return "play"
                    if self.quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

            screen.blit(self.background, (0, 0))

            mouse_pos = pygame.mouse.get_pos()
            if self.play_button.collidepoint(mouse_pos) or self.quit_button.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            pygame.display.flip()