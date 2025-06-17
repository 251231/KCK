import pygame
import random
import math
from config import *

class CupsGame:
    def __init__(self, player):
        self.player = player
        
        # Inicjalizacja czcionek
        self._init_fonts()
        
        # Stan gry
        self.bet_amount = 1
        self.max_bet = min(100, getattr(self.player, 'coins', 100))  # Zwiększony maksymalny zakład
        self.result = ""
        self.game_state = "betting"  # betting, shuffling, reveal, finished
        self.in_game = True
        
        # Pozycje i rozmiary elementów
        self._init_positions()
        
        # Stan gry
        self.ball_position = random.randint(0, 2)
        self.selected_cup = -1
        self.show_ball = False
        
        # Grafiki (cache)
        self._load_graphics()
        
        # Animacje
        self._init_animation()
        
        # Kolory (cache)
        self._init_colors()

    def _init_fonts(self):
        """Inicjalizuje wszystkie czcionki"""
        self.fonts = {
            'small': pygame.font.Font('assets/Czcionka.ttf', 22),
            'normal': pygame.font.Font('assets/Czcionka.ttf', 28),
            'large': pygame.font.Font('assets/Czcionka.ttf', 36),
            'title': pygame.font.Font('assets/Czcionka.ttf', 48)
        }

    def _init_positions(self):
        """Inicjalizuje pozycje elementów interfejsu"""
        center_x = SCREEN_WIDTH // 2
        
        # Pozycje kubków - większe kubki, więcej miejsca
        self.cup_positions = [
            (center_x - 180, 180),
            (center_x, 180),
            (center_x + 180, 180)
        ]
        self.cup_size = (140, 160)  # Zwiększone z (100, 120)
        
        # Przyciski - przesunięte wyżej, żeby nie zasłaniały tekstu
        self.buttons = {
            'bet_up': pygame.Rect(50, SCREEN_HEIGHT - 260, 40, 35),        # Przesunięte wyżej
            'bet_down': pygame.Rect(95, SCREEN_HEIGHT - 260, 40, 35),      # Przesunięte wyżej
            'bet_up_big': pygame.Rect(140, SCREEN_HEIGHT - 260, 60, 35),    # Przesunięte wyżej
            'bet_down_big': pygame.Rect(205, SCREEN_HEIGHT - 260, 60, 35),  # Przesunięte wyżej
            'play': pygame.Rect(center_x - 120, 380, 240, 50),               # Przesunięty niżej
            'exit': pygame.Rect(SCREEN_WIDTH - 120, 10, 110, 40)
        }
        
        # Obszary kubków do kliknięcia - większe
        self.cup_rects = [
            pygame.Rect(pos[0] - 70, pos[1], 140, 160) 
            for pos in self.cup_positions
        ]

    def _load_graphics(self):
        """Ładuje i cache'uje grafiki"""
        self.graphics = {'cup': None, 'ball': None, 'background': None}
        
        try:
            # Ładowanie kubka i piłki
            cup_img = pygame.image.load('assets/medieval_cup.png').convert_alpha()
            ball_img = pygame.image.load('assets/golden_ball.png').convert_alpha()
            
            self.graphics['cup'] = pygame.transform.scale(cup_img, (140, 160))  # Większe kubki
            self.graphics['ball'] = pygame.transform.scale(ball_img, (25, 25))  # Nieco większa piłka
            
            print("Kubek i piłka wczytane pomyślnie!")
            
        except pygame.error as e:
            print(f"Nie można wczytać kubka/piłki: {e}")
            print("Używam domyślnych rysunków")

        # Ładowanie tła
        try:
            # Spróbuj wczytać własne tło
            background_img = pygame.image.load('assets/kubki.png').convert()
            # Przeskaluj tło do rozmiaru ekranu
            self.graphics['background'] = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print("Własne tło PNG wczytane pomyślnie!")
            
        except pygame.error as e:
            print(f"Nie można wczytać tła PNG: {e}")
            print("Używam domyślnego gradientu")
            self.graphics['background'] = None

    def _init_animation(self):
        """Inicjalizuje parametry animacji"""
        self.animation = {
            'shuffling': False,
            'progress': 0,
            'duration': 3000,
            'start_time': 0,
            'cup_offsets': [0, 0, 0],
            'cup_scales': [1.0, 1.0, 1.0],
            'revealing': False,
            'reveal_progress': 0,
            'reveal_duration': 1000,
            'reveal_start_time': 0,
            'cup_lifts': [0, 0, 0]  # Wysokość podniesienia kubków
        }

    def _init_colors(self):
        """Inicjalizuje paletę kolorów"""
        self.colors = {
            'bg_start': (45, 45, 60),
            'bg_end': (70, 70, 85),
            'gold': (255, 215, 0),
            'gold_light': (255, 235, 50),
            'blue': (60, 120, 160),
            'blue_light': (80, 140, 180),
            'green': (50, 180, 50),
            'green_light': (80, 210, 80),
            'red': (180, 50, 50),
            'red_light': (210, 80, 80),
            'panel_bg': (35, 35, 55),
            'panel_border': (70, 70, 110),
            'text_white': (255, 255, 255),
            'text_dark': (50, 50, 50),
            'shadow': (20, 20, 20),
            'cup_brown': (139, 69, 19),
            'cup_highlight': (255, 255, 0, 100)
        }

    def draw(self):
        """Główna funkcja rysowania"""
        self._draw_background()
        self._draw_title()
        self._draw_cups_and_ball()
        self._draw_betting_panel()
        self._draw_instructions()
        self._draw_buttons()
        
        if self.result:
            self._draw_result()

    def _draw_background(self):
        """Rysuje tło - PNG lub gradient"""
        if self.graphics['background']:
            # Używaj własnego tła PNG
            screen.blit(self.graphics['background'], (0, 0))
        else:
            # Fallback - gradient jak wcześniej
            for y in range(SCREEN_HEIGHT):
                color_intensity_start = self.colors['bg_start'][0] + int((y / SCREEN_HEIGHT) * 25)
                color_intensity_green = self.colors['bg_start'][1] + int((y / SCREEN_HEIGHT) * 25)
                color_intensity_blue = self.colors['bg_start'][2] + int((y / SCREEN_HEIGHT) * 25)
                color = (color_intensity_start, color_intensity_green, color_intensity_blue)
                pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

    def _draw_title(self):
        """Rysuje tytuł gry"""
        title_text = "KUBKI SZCZĘŚCIA"
        
        title_shadow = self.fonts['title'].render(title_text, True, self.colors['shadow'])
        title = self.fonts['title'].render(title_text, True, self.colors['gold'])
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        
        screen.blit(title_shadow, (title_x + 2, 22))
        screen.blit(title, (title_x, 20))

    def _draw_cups_and_ball(self):
        """Rysuje kubki i piłkę"""
        current_time = pygame.time.get_ticks()
        
        if self.animation['shuffling']:
            self._update_shuffle_animation(current_time)
        elif self.animation['revealing']:
            self._update_reveal_animation(current_time)
        else:
            for i in range(3):
                self.animation['cup_scales'][i] = 1.0 + 0.03 * math.sin(current_time * 0.002 + i)
        
        # Rysuj piłkę pod kubkiem gdy powinna być widoczna
        if self.show_ball and not self.animation['shuffling']:
            self._draw_ball()
        
        # Rysuj kubki
        for i in range(3):
            self._draw_single_cup(i)

    def _draw_ball(self):
        """Rysuje piłkę pod kubkiem"""
        ball_x = self.cup_positions[self.ball_position][0]
        ball_y = self.cup_positions[self.ball_position][1] + 120 - self.animation['cup_lifts'][self.ball_position]
        
        if self.graphics['ball']:
            ball_rect = self.graphics['ball'].get_rect(center=(ball_x, ball_y))
            screen.blit(self.graphics['ball'], ball_rect)
        else:
            # Fallback - większa piłka
            pygame.draw.circle(screen, (255, 223, 0), (ball_x, ball_y), 12)
            pygame.draw.circle(screen, (255, 255, 150), (ball_x - 3, ball_y - 3), 10)
            pygame.draw.circle(screen, (255, 255, 255), (ball_x - 4, ball_y - 4), 4)

    def _draw_single_cup(self, cup_index):
        """Rysuje pojedynczy kubek"""
        base_x, base_y = self.cup_positions[cup_index]
        cup_x = base_x + self.animation['cup_offsets'][cup_index]
        cup_y = base_y - self.animation['cup_lifts'][cup_index]  # Odsłanianie
        
        self.cup_rects[cup_index] = pygame.Rect(cup_x - 70, cup_y, 140, 160)
        
        if self.graphics['cup']:
            self._draw_cup_with_graphics(cup_index, cup_x, cup_y)
        else:
            self._draw_cup_fallback(cup_index, cup_x, cup_y)
        
        self._draw_cup_number(cup_index, cup_x, cup_y)

    def _draw_cup_with_graphics(self, cup_index, cup_x, cup_y):
        """Rysuje kubek używając grafik"""
        scale = self.animation['cup_scales'][cup_index]
        scaled_cup = pygame.transform.scale(self.graphics['cup'], 
                                          (int(140 * scale), int(160 * scale)))
        cup_rect = scaled_cup.get_rect(center=(cup_x, cup_y + 80))
        
        if self.game_state == "finished" and cup_index == self.selected_cup:
            tinted_cup = scaled_cup.copy()
            if cup_index == self.ball_position:
                tinted_cup.fill((255, 255, 0, 100), special_flags=pygame.BLEND_ADD)
            else:
                tinted_cup.fill((255, 100, 100, 100), special_flags=pygame.BLEND_ADD)
            screen.blit(tinted_cup, cup_rect)
        else:
            screen.blit(scaled_cup, cup_rect)

    def _draw_cup_fallback(self, cup_index, cup_x, cup_y):
        """Rysuje kubek bez grafik"""
        scale = self.animation['cup_scales'][cup_index]
        base_width = int(105 * scale)  # Większy kubek
        base_height = int(130 * scale)
        
        if self.game_state == "finished" and cup_index == self.selected_cup:
            cup_color = self.colors['gold'] if cup_index == self.ball_position else self.colors['red']
        else:
            cup_color = self.colors['cup_brown']
        
        # Korpus kubka
        cup_points = [
            (cup_x - base_width//2, cup_y + base_height),
            (cup_x + base_width//2, cup_y + base_height),
            (cup_x + (base_width//2 - 8), cup_y + 20),
            (cup_x - (base_width//2 - 8), cup_y + 20)
        ]
        pygame.draw.polygon(screen, cup_color, cup_points)
        
        # Górna krawędź
        rim_width = base_width - 15
        rim_rect = pygame.Rect(cup_x - rim_width//2, cup_y + 15, rim_width, 25)
        pygame.draw.ellipse(screen, cup_color, rim_rect)

    def _draw_cup_number(self, cup_index, cup_x, cup_y):
        """Rysuje numer kubka"""
        number_text = str(cup_index + 1)
        number = self.fonts['normal'].render(number_text, True, self.colors['text_white'])
        screen.blit(number, (cup_x - number.get_width()//2, cup_y + 140))

    def _update_shuffle_animation(self, current_time):
        """Aktualizuje animację tasowania"""
        elapsed = current_time - self.animation['start_time']
        self.animation['progress'] = min(elapsed / self.animation['duration'], 1.0)
        
        for i in range(3):
            wave_offset = math.sin((elapsed * 0.01) + i * 2) * 50
            scale_offset = 1.0 + 0.2 * math.sin((elapsed * 0.015) + i * 1.5)
            
            self.animation['cup_offsets'][i] = wave_offset
            self.animation['cup_scales'][i] = scale_offset
        
        if self.animation['progress'] >= 1.0:
            self.animation['shuffling'] = False
            self.animation['cup_offsets'] = [0, 0, 0]
            self.animation['cup_scales'] = [1.0, 1.0, 1.0]
            self.game_state = "reveal"
            self.result = "Wybierz kubek, pod którym jest złota kula!"

    def _update_reveal_animation(self, current_time):
        """Aktualizuje animację odsłaniania"""
        elapsed = current_time - self.animation['reveal_start_time']
        self.animation['reveal_progress'] = min(elapsed / self.animation['reveal_duration'], 1.0)
        
        # Odsłanianie wybranego kubka
        if self.selected_cup >= 0:
            lift_height = 50 * self.animation['reveal_progress']
            self.animation['cup_lifts'][self.selected_cup] = lift_height
        
        if self.animation['reveal_progress'] >= 1.0:
            self.animation['revealing'] = False
            self.show_ball = True
            self._finish_reveal()

    def _finish_reveal(self):
        """Kończy odsłanianie i pokazuje wynik"""
        self.game_state = "finished"
        
        if self.selected_cup == self.ball_position:
            winnings = self.bet_amount * 3
            self.player.coins += winnings
            self.result = f"Wygrana! +{winnings} monet"
        else:
            self.result = f"Przegrana! Kula była pod kubkiem {self.ball_position + 1}"
        
        if hasattr(self.player, 'save_data'):
            self.player.save_data()

    def _draw_betting_panel(self):
        """Rysuje panel zakładów - większy i z lepszym rozmieszczeniem"""
        panel_rect = pygame.Rect(40, SCREEN_HEIGHT - 400, 520, 220) 
        self._draw_panel(panel_rect)
        
        y_start = SCREEN_HEIGHT - 390
        
        title = self.fonts['normal'].render("ZAKŁAD", True, self.colors['gold'])
        screen.blit(title, (55, y_start))
        
        # Większe odstępy między tekstami
        texts = [
            (f"Stawka: {self.bet_amount} monet", self.colors['text_white'], 30),
            (f"Potencjalna wygrana: {self.bet_amount * 3} monet", self.colors['green'], 50),
            (f"Twoje monety: {getattr(self.player, 'coins', 0)}", self.colors['text_white'], 70)
        ]
        
        for text, color, offset in texts:
            rendered = self.fonts['small'].render(text, True, color)
            screen.blit(rendered, (55, y_start + offset))
        
        # Przyciski stawki - przesunięte tak, żeby nie zasłaniały tekstu
        self._draw_gradient_button(self.buttons['bet_up'], self.colors['green'], self.colors['green_light'])
        self._draw_gradient_button(self.buttons['bet_down'], self.colors['red'], self.colors['red_light'])
        self._draw_gradient_button(self.buttons['bet_up_big'], self.colors['blue'], self.colors['blue_light'])
        self._draw_gradient_button(self.buttons['bet_down_big'], self.colors['red'], self.colors['red_light'])
        
        # Teksty na przyciskach
        up_text = self.fonts['large'].render("+", True, self.colors['text_white'])
        down_text = self.fonts['large'].render("−", True, self.colors['text_white'])
        up_big_text = self.fonts['small'].render("+5", True, self.colors['text_white'])
        down_big_text = self.fonts['small'].render("−5", True, self.colors['text_white'])
        
        up_rect = up_text.get_rect(center=self.buttons['bet_up'].center)
        down_rect = down_text.get_rect(center=self.buttons['bet_down'].center)
        up_big_rect = up_big_text.get_rect(center=self.buttons['bet_up_big'].center)
        down_big_rect = down_big_text.get_rect(center=self.buttons['bet_down_big'].center)
        
        screen.blit(up_text, up_rect)
        screen.blit(down_text, down_rect)
        screen.blit(up_big_text, up_big_rect)
        screen.blit(down_big_text, down_big_rect)

    def _draw_instructions(self):
        """Rysuje panel instrukcji - większy"""
        instr_rect = pygame.Rect(SCREEN_WIDTH - 370, 80, 360, 220)  # Większy panel
        self._draw_panel(instr_rect)
        
        title = self.fonts['normal'].render("INSTRUKCJE", True, self.colors['gold'])
        screen.blit(title, (SCREEN_WIDTH - 290, 95))
        
        instructions = self._get_instructions()
        
        for i, instruction in enumerate(instructions):
            if instruction:
                text = self.fonts['small'].render(instruction, True, self.colors['text_white'])
                screen.blit(text, (SCREEN_WIDTH - 330, 120 + i * 22))  # Większe odstępy

    def _get_instructions(self):
        """Zwraca uproszczone instrukcje"""
        if self.game_state == "betting":
            return [
                "• Ustaw stawkę przyciskami",
                "  (+/−, +5/−5)",
                "• Kliknij ROZPOCZNIJ GRĘ",
                "• Wybierz kubek z kulą",
                "• Wygrana = stawka × 3",
                "",
                "Powodzenia!"
            ]
        elif self.game_state == "shuffling":
            return [
                "• Kubki są tasowane...",
                "• Śledź położenie kuli!",
                "• Za chwilę będziesz",
                "  mógł wybrać kubek",
                "",
                "Skoncentruj się!"
            ]
        else:
            return [
                "• Kliknij kubek z kulą",
                "• Jeden z trzech",
                "  zawiera złotą kulę",
                "",
                "Powodzenia!"
            ]

    def _draw_buttons(self):
        """Rysuje przyciski główne"""
        if self.game_state in ["betting", "finished"]:
            button_text = "ROZPOCZNIJ GRĘ" if self.game_state == "betting" else "ZAGRAJ PONOWNIE"
            can_play = (getattr(self.player, 'coins', 0) >= self.bet_amount 
                       if self.game_state == "betting" else True)
            
            if can_play:
                self._draw_gradient_button(self.buttons['play'], self.colors['green'], self.colors['green_light'])
            else:
                self._draw_gradient_button(self.buttons['play'], (80, 80, 80), (120, 120, 120))
            
            text_color = self.colors['text_white'] if can_play else (150, 150, 150)
            play_text = self.fonts['small'].render(button_text, True, text_color)
            play_rect = play_text.get_rect(center=self.buttons['play'].center)
            screen.blit(play_text, play_rect)
        
        # Przycisk wyjścia
        self._draw_gradient_button(self.buttons['exit'], self.colors['red'], self.colors['red_light'])
        exit_text = self.fonts['small'].render("WYJŚCIE", True, self.colors['text_white'])
        exit_rect = exit_text.get_rect(center=self.buttons['exit'].center)
        screen.blit(exit_text, exit_rect)

    def _draw_result(self):
        """Rysuje panel z wynikiem"""
        result_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, 330, 600, 50)
        
        if "Wygrana" in self.result:
            bg_color = self.colors['green']
            light_color = self.colors['green_light']
        else:
            bg_color = self.colors['red'] 
            light_color = self.colors['red_light']
        
        self._draw_gradient_rect(result_rect, bg_color, light_color)
        
        result_text = self.fonts['normal'].render(self.result, True, self.colors['text_white'])
        text_rect = result_text.get_rect(center=result_rect.center)
        screen.blit(result_text, text_rect)

    def _draw_panel(self, rect):
        """Rysuje panel"""
        pygame.draw.rect(screen, self.colors['panel_bg'], rect, border_radius=8)
        pygame.draw.rect(screen, self.colors['panel_border'], rect, 1, border_radius=8)

    def _draw_gradient_button(self, rect, color1, color2):
        """Rysuje przycisk z gradientem"""
        for y in range(rect.height):
            blend = y / rect.height
            r = int(color1[0] * (1 - blend) + color2[0] * blend)
            g = int(color1[1] * (1 - blend) + color2[1] * blend)
            b = int(color1[2] * (1 - blend) + color2[2] * blend)
            pygame.draw.line(screen, (r, g, b), 
                           (rect.x, rect.y + y), 
                           (rect.x + rect.width, rect.y + y))

    def _draw_gradient_rect(self, rect, color1, color2):
        """Rysuje prostokąt z gradientem"""
        for y in range(rect.height):
            blend = y / rect.height
            r = int(color1[0] * (1 - blend) + color2[0] * blend)
            g = int(color1[1] * (1 - blend) + color2[1] * blend)
            b = int(color1[2] * (1 - blend) + color2[2] * blend)
            pygame.draw.line(screen, (r, g, b), 
                           (rect.x, rect.y + y), 
                           (rect.x + rect.width, rect.y + y))

    def handle_event(self, event):
        """Obsługuje wydarzenia - tylko myszka"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos)

    def _handle_mouse_click(self, pos):
        """Obsługuje kliknięcia myszy"""
        if self.buttons['exit'].collidepoint(pos):
            self.in_game = False
            return
        
        if self.game_state == "betting":
            self._handle_betting_click(pos)
        elif self.game_state == "finished":
            if self.buttons['play'].collidepoint(pos):
                self.reset_game()
        elif self.game_state == "reveal":
            for i, cup_rect in enumerate(self.cup_rects):
                if cup_rect.collidepoint(pos):
                    self.selected_cup = i
                    self.start_reveal_animation()
                    break

    def _handle_betting_click(self, pos):
        """Obsługuje kliknięcia w stanie betting"""
        if self.buttons['bet_up'].collidepoint(pos) and self.bet_amount < self.max_bet:
            self.bet_amount += 1
        elif self.buttons['bet_down'].collidepoint(pos) and self.bet_amount > 1:
            self.bet_amount -= 1
        elif self.buttons['bet_up_big'].collidepoint(pos) and self.bet_amount <= self.max_bet - 5:
            self.bet_amount += 5
        elif self.buttons['bet_down_big'].collidepoint(pos) and self.bet_amount > 5:
            self.bet_amount -= 5
        elif self.buttons['play'].collidepoint(pos):
            if getattr(self.player, 'coins', 0) >= self.bet_amount:
                self.start_game()
            else:
                self.result = "Za mało monet!"

    def start_game(self):
        """Rozpoczyna nową grę"""
        self.player.coins -= self.bet_amount
        self.ball_position = random.randint(0, 2)
        self.game_state = "shuffling"
        self.animation['shuffling'] = True
        self.animation['start_time'] = pygame.time.get_ticks()
        self.show_ball = True
        self.selected_cup = -1
        self.result = ""

    def start_reveal_animation(self):
        """Rozpoczyna animację odsłaniania"""
        self.animation['revealing'] = True
        self.animation['reveal_start_time'] = pygame.time.get_ticks()
        self.animation['reveal_progress'] = 0

    def reset_game(self):
        """Resetuje grę"""
        self.game_state = "betting"
        self.selected_cup = -1
        self.show_ball = False
        self.animation['shuffling'] = False
        self.animation['revealing'] = False
        self.animation['cup_offsets'] = [0, 0, 0]
        self.animation['cup_lifts'] = [0, 0, 0]
        self.result = ""
        self.max_bet = min(100, getattr(self.player, 'coins', 0))
        if self.bet_amount > self.max_bet:
            self.bet_amount = max(1, self.max_bet)
        self.in_game = True