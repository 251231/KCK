from config import *


class StartScreen:
    def __init__(self):
        self.background = pygame.image.load("assets/tlo2.png").convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        play_button_width = SCREEN_WIDTH * 0.3
        play_button_height = SCREEN_HEIGHT * 0.07
        play_button_x = (SCREEN_WIDTH - play_button_width) // 2
        play_button_y = SCREEN_HEIGHT * 0.6

        quit_button_width = SCREEN_WIDTH * 0.3
        quit_button_height = SCREEN_HEIGHT * 0.07
        quit_button_x = (SCREEN_WIDTH - quit_button_width) // 2
        quit_button_y = SCREEN_HEIGHT * 0.7

        self.play_button = pygame.Rect(play_button_x, play_button_y, play_button_width, play_button_height)

        self.quit_button = pygame.Rect(quit_button_x, quit_button_y, quit_button_width, quit_button_height)

        


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