from user_path import register_user, authenticate_user
from config import *

# Inicjalizacja pygame i czcionki
pygame.mouse.set_visible(True)

# Średniowieczne kolory
MEDIEVAL_GOLD = (255, 215, 0)
MEDIEVAL_BROWN = (101, 67, 33)
MEDIEVAL_DARK_BROWN = (62, 39, 35)
MEDIEVAL_RED = (139, 69, 19)
MEDIEVAL_GREEN = (34, 139, 34)
MEDIEVAL_STONE = (128, 128, 128)
MEDIEVAL_DARK_STONE = (64, 64, 64)
PARCHMENT = (245, 245, 220)

# Załaduj czcionkę (spróbuj kilka opcji)
def load_custom_font():
    """Próbuje załadować fajną czcionkę, fallback na domyślną"""
    font_paths = [
        "assets/Czcionka.ttf",
    ]
    
    for font_path in font_paths:
        try:
            return pygame.font.Font(font_path, 24)
        except Exception as e:
            print(f"Nie udało się załadować czcionki: {font_path}, błąd: {e}")
            continue

    return pygame.font.SysFont('serif', 24)

# Stwórz różne rozmiary czcionek
custom_font = load_custom_font()
title_font = load_custom_font()
button_font = load_custom_font()

def set_cursor_style(cursor_type):
    """Ustawia odpowiedni styl kursora"""
    if cursor_type == "hand":
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif cursor_type == "text":
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

def check_hover_effects(mouse_pos, *rects):
    """Sprawdza czy mysz jest nad którymś z prostokątów"""
    for rect in rects:
        if rect.collidepoint(mouse_pos):
            return True
    return False

def draw_medieval_button(surface, rect, text, color, hover_color, mouse_pos, border_color=MEDIEVAL_GOLD):
    """Rysuje przycisk w stylu średniowiecznym z ramką i efektami"""
    is_hovered = rect.collidepoint(mouse_pos)
    
    # Główne tło przycisku
    button_color = hover_color if is_hovered else color
    
    # Gradient tła
    button_surface = pygame.Surface((rect.width, rect.height))
    for i in range(rect.height):
        shade = int(i / rect.height * 40)
        gradient_color = (
            max(0, button_color[0] - shade),
            max(0, button_color[1] - shade),
            max(0, button_color[2] - shade)
        )
        pygame.draw.line(button_surface, gradient_color, (0, i), (rect.width, i))
    
    surface.blit(button_surface, rect)
    
    # Ramka złota
    pygame.draw.rect(surface, border_color, rect, 3)
    
    # Wewnętrzna ramka
    inner_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, rect.height - 6)
    pygame.draw.rect(surface, MEDIEVAL_DARK_BROWN, inner_rect, 1)
    
    # Efekt 3D
    if is_hovered:
        # Podświetlenie góra-lewo
        pygame.draw.line(surface, (255, 255, 255, 100), (rect.x + 1, rect.y + 1), (rect.x + rect.width - 1, rect.y + 1), 2)
        pygame.draw.line(surface, (255, 255, 255, 100), (rect.x + 1, rect.y + 1), (rect.x + 1, rect.y + rect.height - 1), 2)
    
    # Tekst
    text_surface = button_font.render(text, True, PARCHMENT)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def draw_medieval_input_field(surface, rect, text, active, label, mouse_pos):
    """Rysuje pole input w stylu średniowiecznym"""
    # Tło pola
    field_color = PARCHMENT if active else (220, 220, 200)
    pygame.draw.rect(surface, field_color, rect)
    
    # Ramka
    border_color = MEDIEVAL_GOLD if active else MEDIEVAL_BROWN
    pygame.draw.rect(surface, border_color, rect, 3 if active else 2)
    
    # Wewnętrzna ramka
    inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
    pygame.draw.rect(surface, MEDIEVAL_DARK_BROWN, inner_rect, 1)
    
    # Label
    label_surface = custom_font.render(label, True, MEDIEVAL_GOLD)
    surface.blit(label_surface, (rect.x, rect.y - 35))
    
    # Tekst
    text_surface = custom_font.render(text, True, MEDIEVAL_DARK_BROWN)
    surface.blit(text_surface, (rect.x + 10, rect.y + 12))
    
    # Kursor migający
    if active:
        cursor_x = rect.x + 10 + text_surface.get_width() + 2
        pygame.draw.line(surface, MEDIEVAL_DARK_BROWN, (cursor_x, rect.y + 8), (cursor_x, rect.y + rect.height - 8), 2)

def create_medieval_background(screen_size, background_image=None):
    """Tworzy tło w stylu średniowiecznym"""
    bg_surface = pygame.Surface(screen_size)
    
    if background_image:
        bg_surface.blit(background_image, (0, 0))
        # Dodaj ciemną nakładkę
        overlay = pygame.Surface(screen_size)
        overlay.set_alpha(120)
        overlay.fill((40, 30, 20))
        bg_surface.blit(overlay, (0, 0))
    else:
        # Gradient w kolorach średniowiecznych
        for y in range(screen_size[1]):
            ratio = y / screen_size[1]
            r = int(40 + ratio * 20)
            g = int(30 + ratio * 15)
            b = int(20 + ratio * 10)
            pygame.draw.line(bg_surface, (r, g, b), (0, y), (screen_size[0], y))
        
        # Dodaj teksturę kamienia (proste linie)
        for i in range(0, screen_size[0], 100):
            for j in range(0, screen_size[1], 80):
                pygame.draw.rect(bg_surface, (r+10, g+8, b+5), (i, j, 95, 75), 1)
    
    return bg_surface

def show_message_box(surface, message, rect_area, message_type="info"):
    """Wyświetla komunikat w stylizowanym okienku"""
    colors = {
        "error": MEDIEVAL_RED,
        "success": MEDIEVAL_GREEN,
        "info": MEDIEVAL_STONE
    }
    
    text_surface = custom_font.render(message, True, PARCHMENT)
    padding = 20
    box_width = text_surface.get_width() + padding * 2
    box_height = text_surface.get_height() + padding
    
    box_x = rect_area.centerx - box_width // 2
    box_y = rect_area.y - box_height - 10
    
    # Tło komunikatu
    msg_bg = pygame.Surface((box_width, box_height))
    msg_bg.fill(colors.get(message_type, MEDIEVAL_STONE))
    surface.blit(msg_bg, (box_x, box_y))
    
    # Ramka złota
    pygame.draw.rect(surface, MEDIEVAL_GOLD, (box_x, box_y, box_width, box_height), 2)
    
    # Tekst
    surface.blit(text_surface, (box_x + padding, box_y + padding // 2))

def ekran_rejestracji(background_image=None):
    message = ''
    message_type = 'info'
    login_text = ''
    password_text = ''
    login_active = False
    password_active = False

    while True:
        screen_width, screen_height = screen.get_size()
        
        # Tło
        if background_image:
            scaled_bg = pygame.transform.scale(background_image, (screen_width, screen_height))
            bg_surface = create_medieval_background((screen_width, screen_height), scaled_bg)
        else:
            bg_surface = create_medieval_background((screen_width, screen_height))
        
        screen.blit(bg_surface, (0, 0))

        # Wyśrodkowane pozycjonowanie
        box_width, box_height = 350, 55
        center_x = screen_width // 2 - box_width // 2
        start_y = screen_height // 2 - 150
        
        login_box = pygame.Rect(center_x, start_y, box_width, box_height)
        password_box = pygame.Rect(center_x, start_y + 90, box_width, box_height)
        register_button = pygame.Rect(center_x, start_y + 180, box_width, 60)
        back_button = pygame.Rect(center_x, start_y + 260, box_width, 60)

        # Sprawdź hover effects
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
                        message = "Wypełnij wszystkie pola, szlachetny wojowniku!"
                        message_type = "error"
                    elif register_user(login_text, password_text):
                        message = "Pomyślnie dołączyłeś do naszego królestwa!"
                        message_type = "success"
                        pygame.time.wait(1500)
                        return login_text
                    else:
                        message = "Ten student już istnieje w naszych kronikach!"
                        message_type = "error"

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
                        message = "Wypełnij wszystkie pola, szlachetny wojowniku!"
                        message_type = "error"
                    elif register_user(login_text, password_text):
                        message = "Pomyślnie dołączyłeś do naszego królestwa!"
                        message_type = "success"
                        pygame.time.wait(1500)
                        return login_text
                    else:
                        message = "Ten student już istnieje w naszych kronikach!"
                        message_type = "error"

        # Tytuł
        title_text = title_font.render("KSIĘGA REJESTRACJI", True, MEDIEVAL_GOLD)
        title_rect = title_text.get_rect(center=(screen_width // 2, start_y - 80))
        
        # Tło tytułu
        title_bg = pygame.Surface((title_text.get_width() + 40, title_text.get_height() + 20))
        title_bg.fill(MEDIEVAL_DARK_BROWN)
        title_bg_rect = title_bg.get_rect(center=title_rect.center)
        screen.blit(title_bg, title_bg_rect)
        pygame.draw.rect(screen, MEDIEVAL_GOLD, title_bg_rect, 3)
        screen.blit(title_text, title_rect)

        # Pola input
        draw_medieval_input_field(screen, login_box, login_text, login_active, "Imię Student:", mouse_pos)
        draw_medieval_input_field(screen, password_box, '*' * len(password_text), password_active, "Hasło do Zamku:", mouse_pos)

        # Przyciski
        draw_medieval_button(screen, register_button, "WSTĄP DO KRÓLESTWA", 
                           MEDIEVAL_GREEN, (50, 180, 50), mouse_pos)
        draw_medieval_button(screen, back_button, "POWRÓT DO BRAMY", 
                           MEDIEVAL_STONE, (150, 150, 150), mouse_pos)

        # Komunikat
        if message:
            show_message_box(screen, message, login_box, message_type)

        pygame.display.flip()

def ekran_logowania(background_image=None):
    login_text = ''
    password_text = ''
    login_active = False
    password_active = False
    message = ''
    message_type = 'info'

    while True:
        screen_width, screen_height = screen.get_size()
        
        # Tło
        if background_image:
            scaled_bg = pygame.transform.scale(background_image, (screen_width, screen_height))
            bg_surface = create_medieval_background((screen_width, screen_height), scaled_bg)
        else:
            bg_surface = create_medieval_background((screen_width, screen_height))
        
        screen.blit(bg_surface, (0, 0))

        # Wyśrodkowane pozycjonowanie
        box_width, box_height = 350, 55
        center_x = screen_width // 2 - box_width // 2
        start_y = screen_height // 2 - 150
        
        login_box = pygame.Rect(center_x, start_y, box_width, box_height)
        password_box = pygame.Rect(center_x, start_y + 90, box_width, box_height)
        login_button = pygame.Rect(center_x, start_y + 180, box_width, 60)
        back_button = pygame.Rect(center_x, start_y + 260, box_width, 60)

        # Sprawdź hover effects
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
                        message = "Straż nie rozpoznaje tego rycerza!"
                        message_type = "error"

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
                        message = "Straż nie rozpoznaje tego rycerza!"
                        message_type = "error"

        # Tytuł
        title_text = title_font.render("BRAMA KRÓLESTWA", True, MEDIEVAL_GOLD)
        title_rect = title_text.get_rect(center=(screen_width // 2, start_y - 80))
        
        # Tło tytułu
        title_bg = pygame.Surface((title_text.get_width() + 40, title_text.get_height() + 20))
        title_bg.fill(MEDIEVAL_DARK_BROWN)
        title_bg_rect = title_bg.get_rect(center=title_rect.center)
        screen.blit(title_bg, title_bg_rect)
        pygame.draw.rect(screen, MEDIEVAL_GOLD, title_bg_rect, 3)
        screen.blit(title_text, title_rect)

        # Pola input
        draw_medieval_input_field(screen, login_box, login_text, login_active, "Imię Studenta:", mouse_pos)
        draw_medieval_input_field(screen, password_box, '*' * len(password_text), password_active, "Hasło do Zamku:", mouse_pos)

        # Przyciski
        draw_medieval_button(screen, login_button, "WEJDŹ DO ZAMKU", 
                           MEDIEVAL_GREEN, (50, 180, 50), mouse_pos)
        draw_medieval_button(screen, back_button, "POWRÓT DO BRAMY", 
                           MEDIEVAL_STONE, (150, 150, 150), mouse_pos)

        # Komunikat
        if message:
            show_message_box(screen, message, login_box, message_type)

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
        
        # Tło
        if background_image:
            scaled_bg = pygame.transform.scale(background_image, (screen_width, screen_height))
            bg_surface = create_medieval_background((screen_width, screen_height), scaled_bg)
        else:
            bg_surface = create_medieval_background((screen_width, screen_height))
        
        screen.blit(bg_surface, (0, 0))

        # Wyśrodkowane pozycjonowanie
        button_width, button_height = 300, 70
        center_x = screen_width // 2 - button_width // 2
        start_y = screen_height // 2 - 100
        
        login_btn = pygame.Rect(center_x, start_y, button_width, button_height)
        register_btn = pygame.Rect(center_x, start_y + 90, button_width, button_height)
        exit_btn = pygame.Rect(center_x, start_y + 180, button_width, button_height)

        # Sprawdź hover effects
        mouse_pos = pygame.mouse.get_pos()
        if check_hover_effects(mouse_pos, login_btn, register_btn, exit_btn):
            set_cursor_style("hand")
        else:
            set_cursor_style("normal")

        # Główny tytuł
        main_title = title_font.render("KRÓLESTWO GAMEDZIEKANAT", True, MEDIEVAL_GOLD)
        subtitle = custom_font.render("Wkrocz do świata przygód", True, PARCHMENT)
        
        title_rect = main_title.get_rect(center=(screen_width // 2, start_y - 120))
        subtitle_rect = subtitle.get_rect(center=(screen_width // 2, start_y - 80))
        
        # Tło tytułu
        title_bg_width = max(main_title.get_width(), subtitle.get_width()) + 60
        title_bg = pygame.Surface((title_bg_width, 80))
        title_bg.fill(MEDIEVAL_DARK_BROWN)
        title_bg_rect = title_bg.get_rect(center=(screen_width // 2, start_y - 100))
        screen.blit(title_bg, title_bg_rect)
        pygame.draw.rect(screen, MEDIEVAL_GOLD, title_bg_rect, 4)
        
        screen.blit(main_title, title_rect)
        screen.blit(subtitle, subtitle_rect)

        # Przyciski
        draw_medieval_button(screen, login_btn, "POWRÓT DO ZAMKU", 
                           MEDIEVAL_GREEN, (50, 180, 50), mouse_pos)
        draw_medieval_button(screen, register_btn, "DOŁĄCZ DO KRÓLESTWA", 
                           MEDIEVAL_BROWN, (130, 90, 50), mouse_pos)
        draw_medieval_button(screen, exit_btn, "OPUŚĆ KRÓLESTWO", 
                           MEDIEVAL_RED, (180, 90, 70), mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
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
                elif exit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()