from user_path import register_user, authenticate_user
from config import *

def ekran_rejestracji():
    message = ''
    login_text = ''
    password_text = ''
    login_active = False
    password_active = False

    while True:
        screen.fill((30, 30, 30))
        screen_width, screen_height = screen.get_size()

        # Dynamiczne pozycjonowanie
        box_width, box_height = 300, 50
        center_x = screen_width // 2 - box_width // 2
        login_box = pygame.Rect(center_x, 300, box_width, box_height)
        password_box = pygame.Rect(center_x, 380, box_width, box_height)
        register_button = pygame.Rect(center_x, 470, box_width, box_height)
        back_button = pygame.Rect(center_x, 550, box_width, box_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                login_active = login_box.collidepoint(event.pos)
                password_active = password_box.collidepoint(event.pos)

                if register_button.collidepoint(event.pos):
                    if not login_text or not password_text:
                        message = "Wprowadź dane!"
                    elif register_user(login_text, password_text):
                        message = "Rejestracja zakończona sukcesem!"
                        return login_text
                    else:
                        message = "Użytkownik już istnieje!"

                elif back_button.collidepoint(event.pos):
                    return None  # wróć do menu_logowania()

            elif event.type == pygame.KEYDOWN:
                if login_active:
                    if event.key == pygame.K_BACKSPACE:
                        login_text = login_text[:-1]
                    elif event.key != pygame.K_RETURN:
                        login_text += event.unicode
                    message = ''
                elif password_active:
                    if event.key == pygame.K_BACKSPACE:
                        password_text = password_text[:-1]
                    elif event.key != pygame.K_RETURN:
                        password_text += event.unicode
                    message = ''

                if event.key == pygame.K_RETURN:
                    if not login_text or not password_text:
                        message = "Wprowadź dane!"
                    elif register_user(login_text, password_text):
                        return login_text
                    else:
                        message = "Użytkownik już istnieje!"

        # UI
        pygame.draw.rect(screen, pygame.Color('lightskyblue3'), login_box, 2)
        pygame.draw.rect(screen, pygame.Color('lightskyblue3'), password_box, 2)
        screen.blit(font.render("Login:", True, YELLOW), (login_box.x, login_box.y - 30))
        screen.blit(font.render("Hasło:", True, YELLOW), (password_box.x, password_box.y - 30))
        screen.blit(font.render(login_text, True, WHITE), (login_box.x + 5, login_box.y + 10))
        screen.blit(font.render('*' * len(password_text), True, WHITE), (password_box.x + 5, password_box.y + 10))

        pygame.draw.rect(screen, pygame.Color("blue"), register_button)
        screen.blit(font.render("ZAREJESTRUJ", True, WHITE), (register_button.x + 75, register_button.y + 10))

        pygame.draw.rect(screen, pygame.Color("gray"), back_button)
        screen.blit(font.render("WSTECZ", True, WHITE), (back_button.x + 100, back_button.y + 10))

        if message:
            screen.blit(font.render(message, True, RED if "istnieje" in message or "dane" in message else GREEN), (login_box.x, login_box.y - 60))

        pygame.display.flip()

def ekran_logowania():
    login_text = ''
    password_text = ''
    login_active = False
    password_active = False
    message = ''

    while True:
        screen.fill((30, 30, 30))
        screen_width, screen_height = screen.get_size()

        # Dynamiczne pozycjonowanie
        box_width, box_height = 300, 50
        center_x = screen_width // 2 - box_width // 2
        login_box = pygame.Rect(center_x, 300, box_width, box_height)
        password_box = pygame.Rect(center_x, 380, box_width, box_height)
        login_button = pygame.Rect(center_x, 470, box_width, box_height)
        back_button = pygame.Rect(center_x, 550, box_width, box_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                login_active = login_box.collidepoint(event.pos)
                password_active = password_box.collidepoint(event.pos)

                if login_button.collidepoint(event.pos):
                    if authenticate_user(login_text, password_text):
                        return login_text
                    else:
                        message = "Nieprawidłowy login lub hasło!"

                elif back_button.collidepoint(event.pos):
                    return None  # wróć do menu_logowania()

            elif event.type == pygame.KEYDOWN:
                if login_active:
                    if event.key == pygame.K_BACKSPACE:
                        login_text = login_text[:-1]
                    elif event.key != pygame.K_RETURN:
                        login_text += event.unicode
                    message = ''
                elif password_active:
                    if event.key == pygame.K_BACKSPACE:
                        password_text = password_text[:-1]
                    elif event.key != pygame.K_RETURN:
                        password_text += event.unicode
                    message = ''

                if event.key == pygame.K_RETURN:
                    if authenticate_user(login_text, password_text):
                        return login_text
                    else:
                        message = "Nieprawidłowy login lub hasło!"

        # UI
        pygame.draw.rect(screen, pygame.Color('lightskyblue3'), login_box, 2)
        pygame.draw.rect(screen, pygame.Color('lightskyblue3'), password_box, 2)
        screen.blit(font.render("Login:", True, YELLOW), (login_box.x, login_box.y - 30))
        screen.blit(font.render("Hasło:", True, YELLOW), (password_box.x, password_box.y - 30))
        screen.blit(font.render(login_text, True, WHITE), (login_box.x + 5, login_box.y + 10))
        screen.blit(font.render('*' * len(password_text), True, WHITE), (password_box.x + 5, password_box.y + 10))

        pygame.draw.rect(screen, pygame.Color("green"), login_button)
        screen.blit(font.render("ZALOGUJ", True, BLACK), (login_button.x + 100, login_button.y + 10))

        pygame.draw.rect(screen, pygame.Color("gray"), back_button)
        screen.blit(font.render("WSTECZ", True, WHITE), (back_button.x + 100, back_button.y + 10))

        if message:
            screen.blit(font.render(message, True, RED), (login_box.x, login_box.y - 60))

        pygame.display.flip()

def menu_logowania():
    login_btn = pygame.Rect(600, 400, 300, 60)
    register_btn = pygame.Rect(600, 480, 300, 60)

    while True:
        screen.fill((20, 20, 20))

        screen_width, screen_height = screen.get_size()
        center_x = screen_width // 2 - 150

        login_btn = pygame.Rect(center_x, 400, 300, 60)
        register_btn = pygame.Rect(center_x, 480, 300, 60)

        title = font.render("Witamy!", True, YELLOW)
        screen.blit(title, (center_x + 75, 300))

        pygame.draw.rect(screen, pygame.Color("green"), login_btn)
        pygame.draw.rect(screen, pygame.Color("blue"), register_btn)

        screen.blit(font.render("ZALOGUJ", True, BLACK), (login_btn.x + 100, login_btn.y + 15))
        screen.blit(font.render("ZAREJESTRUJ", True, WHITE), (register_btn.x + 85, register_btn.y + 15))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if login_btn.collidepoint(event.pos):
                    user = ekran_logowania()
                    if user:
                        return user
                elif register_btn.collidepoint(event.pos):
                    user = ekran_rejestracji()
                    if user:
                        return user

        pygame.display.flip()