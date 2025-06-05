from user_path import register_user, authenticate_user
from config import *

# Inicjalizacja pygame i czcionki
pygame.mouse.set_visible(True)


# Załaduj czcionkę (spróbuj kilka opcji)
def load_custom_font():
    """Próbuje załadować fajną czcionkę, fallback na domyślną"""
    font_paths = [          # Jeśli masz własną czcionkę
        "assets/Czcionka.ttf",
    ]
    
    for font_path in font_paths:
        try:
            return pygame.font.Font(font_path, 24)
        except Exception as e:
            print(f"Nie udało się załadować czcionki: {font_path}, błąd: {e}")
            continue

    # Fallback na domyślną czcionkę pygame
    return pygame.font.SysFont(None, 24)
    
   

# Stwórz różne style kursorów
custom_font = load_custom_font()
def set_cursor_style(cursor_type):
    """Ustawia odpowiedni styl kursora"""
    if cursor_type == "hand":
        # Kursor wskazujący (na przyciskach)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif cursor_type == "text":
        # Kursor tekstowy (w polach input)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        # Domyślny kursor (normalny)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

def check_hover_effects(mouse_pos, *rects):
    """Sprawdza czy mysz jest nad którymś z prostokątów"""
    for rect in rects:
        if rect.collidepoint(mouse_pos):
            return True
    return False

# Załaduj i przygotuj obrazek tła
def load_and_scale_background(image_path, screen_size):
    """Ładuje obrazek i skaluje go do rozmiaru ekranu"""
    try:
        background = pygame.image.load(image_path)
        return pygame.transform.scale(background, screen_size)
    except pygame.error:
        print(f"Nie można załadować obrazka: {image_path}")
        return None

def create_background_surface(screen_size, background_image=None):
    """Tworzy powierzchnię tła - z obrazkiem lub gradientem"""
    bg_surface = pygame.Surface(screen_size)
    
    if background_image:
        bg_surface.blit(background_image, (0, 0))
        # Dodaj przezroczyste nakładkę dla lepszej czytelności
        overlay = pygame.Surface(screen_size)
        overlay.set_alpha(100)  # Przezroczystość 0-255
        overlay.fill((0, 0, 0))
        bg_surface.blit(overlay, (0, 0))
    else:
        # Gradient jako fallback
        for y in range(screen_size[1]):
            color_value = int(20 + (y / screen_size[1]) * 30)
            pygame.draw.line(bg_surface, (color_value, color_value, color_value), (0, y), (screen_size[0], y))
    
    return bg_surface

def ekran_rejestracji(background_image=None):
    message = ''
    login_text = ''
    password_text = ''
    login_active = False
    password_active = False

    while True:
        screen_width, screen_height = screen.get_size()
        
        # Skaluj tło do aktualnego rozmiaru ekranu
        if background_image:
            scaled_bg = pygame.transform.scale(background_image, (screen_width, screen_height))
            bg_surface = create_background_surface((screen_width, screen_height), scaled_bg)
        else:
            bg_surface = create_background_surface((screen_width, screen_height))
        
        screen.blit(bg_surface, (0, 0))

        # Dynamiczne pozycjonowanie
        box_width, box_height = 300, 50
        center_x = screen_width // 2 - box_width // 2
        login_box = pygame.Rect(center_x, 300, box_width, box_height)
        password_box = pygame.Rect(center_x, 380, box_width, box_height)
        register_button = pygame.Rect(center_x, 470, box_width, box_height)
        back_button = pygame.Rect(center_x, 550, box_width, box_height)

        # Sprawdź hover effects i ustaw odpowiedni kursor
        mouse_pos = pygame.mouse.get_pos()
        if check_hover_effects(mouse_pos, register_button, back_button):
            set_cursor_style("hand")
        elif check_hover_effects(mouse_pos, login_box, password_box):
            set_cursor_style("text")
        else:
            set_cursor_style("normal")

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
                    return None

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

        # UI z półprzezroczystymi tłami + hover effects
        # Tło dla pól input
        input_bg = pygame.Surface((box_width, box_height))
        input_bg.set_alpha(180)
        input_bg.fill((40, 40, 40))
        
        screen.blit(input_bg, login_box)
        screen.blit(input_bg, password_box)
        
        # Podświetl aktywne pole
        if login_active:
            pygame.draw.rect(screen, pygame.Color('yellow'), login_box, 3)
        else:
            pygame.draw.rect(screen, pygame.Color('lightskyblue3'), login_box, 2)
            
        if password_active:
            pygame.draw.rect(screen, pygame.Color('yellow'), password_box, 3)
        else:
            pygame.draw.rect(screen, pygame.Color('lightskyblue3'), password_box, 2)
        
        screen.blit(custom_font.render("Login:", True, YELLOW), (login_box.x, login_box.y - 30))
        screen.blit(custom_font.render("Hasło:", True, YELLOW), (password_box.x, password_box.y - 30))
        screen.blit(custom_font.render(login_text, True, WHITE), (login_box.x + 5, login_box.y + 10))
        screen.blit(custom_font.render('*' * len(password_text), True, WHITE), (password_box.x + 5, password_box.y + 10))

        # Przyciski z efektami hover
        button_bg = pygame.Surface((box_width, box_height))
        button_bg.set_alpha(200)
        
        # Przycisk rejestracji z hover effect
        if register_button.collidepoint(mouse_pos):
            button_bg.fill((0, 120, 255))  # Jaśniejszy niebieski
            pygame.draw.rect(screen, pygame.Color("cyan"), register_button, 3)
        else:
            button_bg.fill((0, 100, 200))
            pygame.draw.rect(screen, pygame.Color("blue"), register_button, 2)
        
        screen.blit(button_bg, register_button)
        screen.blit(custom_font.render("ZAREJESTRUJ", True, WHITE), (register_button.x + 75, register_button.y + 10))

        # Przycisk wstecz z hover effect
        if back_button.collidepoint(mouse_pos):
            button_bg.fill((150, 150, 150))  # Jaśniejszy szary
            pygame.draw.rect(screen, pygame.Color("white"), back_button, 3)
        else:
            button_bg.fill((100, 100, 100))
            pygame.draw.rect(screen, pygame.Color("gray"), back_button, 2)
            
        screen.blit(button_bg, back_button)
        screen.blit(custom_font.render("WSTECZ", True, WHITE), (back_button.x + 100, back_button.y + 10))

        if message:
            # Tło dla komunikatu
            text_surface = custom_font.render(message, True, RED if "istnieje" in message or "dane" in message else GREEN)
            msg_bg = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10))
            msg_bg.set_alpha(180)
            msg_bg.fill((0, 0, 0))
            screen.blit(msg_bg, (login_box.x - 10, login_box.y - 70))
            screen.blit(text_surface, (login_box.x, login_box.y - 60))

        pygame.display.flip()

def ekran_logowania(background_image=None):
    login_text = ''
    password_text = ''
    login_active = False
    password_active = False
    message = ''

    while True:
        screen_width, screen_height = screen.get_size()
        
        # Skaluj tło do aktualnego rozmiaru ekranu
        if background_image:
            scaled_bg = pygame.transform.scale(background_image, (screen_width, screen_height))
            bg_surface = create_background_surface((screen_width, screen_height), scaled_bg)
        else:
            bg_surface = create_background_surface((screen_width, screen_height))
        
        screen.blit(bg_surface, (0, 0))

        # Dynamiczne pozycjonowanie
        box_width, box_height = 300, 50
        center_x = screen_width // 2 - box_width // 2
        login_box = pygame.Rect(center_x, 300, box_width, box_height)
        password_box = pygame.Rect(center_x, 380, box_width, box_height)
        login_button = pygame.Rect(center_x, 470, box_width, box_height)
        back_button = pygame.Rect(center_x, 550, box_width, box_height)

        # Sprawdź hover effects i ustaw odpowiedni kursor
        mouse_pos = pygame.mouse.get_pos()
        if check_hover_effects(mouse_pos, login_button, back_button):
            set_cursor_style("hand")
        elif check_hover_effects(mouse_pos, login_box, password_box):
            set_cursor_style("text")
        else:
            set_cursor_style("normal")

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
                    return None

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

        # UI z półprzezroczystymi tłami + hover effects
        input_bg = pygame.Surface((box_width, box_height))
        input_bg.set_alpha(180)
        input_bg.fill((40, 40, 40))
        
        screen.blit(input_bg, login_box)
        screen.blit(input_bg, password_box)
        
        # Podświetl aktywne pole
        if login_active:
            pygame.draw.rect(screen, pygame.Color('yellow'), login_box, 3)
        else:
            pygame.draw.rect(screen, pygame.Color('lightskyblue3'), login_box, 2)
            
        if password_active:
            pygame.draw.rect(screen, pygame.Color('yellow'), password_box, 3)
        else:
            pygame.draw.rect(screen, pygame.Color('lightskyblue3'), password_box, 2)
        
        screen.blit(custom_font.render("Login:", True, YELLOW), (login_box.x, login_box.y - 30))
        screen.blit(custom_font.render("Hasło:", True, YELLOW), (password_box.x, password_box.y - 30))
        screen.blit(custom_font.render(login_text, True, WHITE), (login_box.x + 5, login_box.y + 10))
        screen.blit(custom_font.render('*' * len(password_text), True, WHITE), (password_box.x + 5, password_box.y + 10))

        # Przyciski z efektami hover
        button_bg = pygame.Surface((box_width, box_height))
        button_bg.set_alpha(200)
        
        # Przycisk logowania z hover effect
        if login_button.collidepoint(mouse_pos):
            button_bg.fill((0, 200, 0))  # Jaśniejszy zielony
            pygame.draw.rect(screen, pygame.Color("lime"), login_button, 3)
        else:
            button_bg.fill((0, 150, 0))
            pygame.draw.rect(screen, pygame.Color("green"), login_button, 2)
            
        screen.blit(button_bg, login_button)
        screen.blit(custom_font.render("ZALOGUJ", True, WHITE), (login_button.x + 100, login_button.y + 10))

        # Przycisk wstecz z hover effect
        if back_button.collidepoint(mouse_pos):
            button_bg.fill((150, 150, 150))  # Jaśniejszy szary
            pygame.draw.rect(screen, pygame.Color("white"), back_button, 3)
        else:
            button_bg.fill((100, 100, 100))
            pygame.draw.rect(screen, pygame.Color("gray"), back_button, 2)
            
        screen.blit(button_bg, back_button)
        screen.blit(custom_font.render("WSTECZ", True, WHITE), (back_button.x + 100, back_button.y + 10))

        if message:
            text_surface = custom_font.render(message, True, RED)
            msg_bg = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10))
            msg_bg.set_alpha(180)
            msg_bg.fill((0, 0, 0))
            screen.blit(msg_bg, (login_box.x - 10, login_box.y - 70))
            screen.blit(text_surface, (login_box.x, login_box.y - 60))

        pygame.display.flip()

def menu_logowania(background_path="background.png"):
    # Załaduj obrazek tła
    background_image = None
    try:
        background_image = pygame.image.load(background_path)
        print(f"Załadowano tło: {background_path}")
    except pygame.error:
        print(f"Nie można załadować tła: {background_path}, używam gradientu")

    while True:
        screen_width, screen_height = screen.get_size()
        
        # Skaluj tło do aktualnego rozmiaru ekranu
        if background_image:
            scaled_bg = pygame.transform.scale(background_image, (screen_width, screen_height))
            bg_surface = create_background_surface((screen_width, screen_height), scaled_bg)
        else:
            bg_surface = create_background_surface((screen_width, screen_height))
        
        screen.blit(bg_surface, (0, 0))

        center_x = screen_width // 2 - 150
        login_btn = pygame.Rect(center_x, 400, 300, 60)
        register_btn = pygame.Rect(center_x, 480, 300, 60)

        # Sprawdź hover effects i ustaw odpowiedni kursor
        mouse_pos = pygame.mouse.get_pos()
        if check_hover_effects(mouse_pos, login_btn, register_btn):
            set_cursor_style("hand")
        else:
            set_cursor_style("normal")

        # Tytuł z tłem
        title_text = custom_font.render("Witamy w Królestwie!", True, YELLOW)
        title_bg = pygame.Surface((title_text.get_width() + 40, title_text.get_height() + 20))
        title_bg.set_alpha(150)
        title_bg.fill((0, 0, 0))
        screen.blit(title_bg, (center_x + 25, 290))
        screen.blit(title_text, (center_x + 45, 300))

        # Przyciski z półprzezroczystymi tłami + hover effects
        button_bg = pygame.Surface((300, 60))
        button_bg.set_alpha(200)
        
        # Przycisk logowania z hover effect
        if login_btn.collidepoint(mouse_pos):
            button_bg.fill((0, 200, 0))  # Jaśniejszy zielony
            pygame.draw.rect(screen, pygame.Color("lime"), login_btn, 4)
        else:
            button_bg.fill((0, 150, 0))
            pygame.draw.rect(screen, pygame.Color("green"), login_btn, 3)
            
        screen.blit(button_bg, login_btn)
        screen.blit(custom_font.render("ZALOGUJ SIĘ", True, WHITE), (login_btn.x + 85, login_btn.y + 15))

        # Przycisk rejestracji z hover effect
        if register_btn.collidepoint(mouse_pos):
            button_bg.fill((0, 120, 255))  # Jaśniejszy niebieski
            pygame.draw.rect(screen, pygame.Color("cyan"), register_btn, 4)
        else:
            button_bg.fill((0, 100, 200))
            pygame.draw.rect(screen, pygame.Color("blue"), register_btn, 3)
            
        screen.blit(button_bg, register_btn)
        screen.blit(custom_font.render("DOŁĄCZ DO NAS", True, WHITE), (register_btn.x + 70, register_btn.y + 15))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if login_btn.collidepoint(event.pos):
                    user = ekran_logowania(background_image)
                    if user:
                        return user
                elif register_btn.collidepoint(event.pos):
                    user = ekran_rejestracji(background_image)
                    if user:
                        return user

        pygame.display.flip()