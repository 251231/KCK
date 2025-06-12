import pygame
import math
import random

# Stałe (zastąpienie config.py)
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class ArcheryGame:
    def __init__(self, player, screen):
        self.player = player
        self.screen = screen
        self.in_game = False
        self.game_state = "menu"  # menu, aiming, shooting, result
        
        # Czcionki
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Parametry gry
        self.arrows_left = 5
        self.score = 0
        self.current_bet = 10
        self.min_bet = 5
        self.max_bet = 100
        
        # Parametry łuku i strzały
        self.bow_x = 100
        self.bow_y = SCREEN_HEIGHT // 2
        self.arrow_start_x = self.bow_x + 50
        self.arrow_start_y = self.bow_y
        
        # Parametry celowania
        self.aim_angle = 0
        self.aim_power = 0
        self.charging_power = False
        self.power_direction = 1
        
        # Strzała w locie
        self.arrow_flying = False
        self.arrow_x = 0
        self.arrow_y = 0
        self.arrow_vel_x = 0
        self.arrow_vel_y = 0
        self.arrow_trail = []
        
        # Tarcza
        self.target_x = SCREEN_WIDTH - 200
        self.target_y = SCREEN_HEIGHT // 2
        self.target_radius = 80
        
        # Wyniki
        self.last_shot_score = 0
        self.shot_results = []
        
        # Animacje i efekty
        self.hit_effect_timer = 0
        self.hit_effect_pos = None
        self.wind_strength = 0
        self.wind_direction = 0
        
        # Interfejs - inicjalizuj buttony
        self.init_buttons()
        
        # Inicjalizuj wiatr
        self.generate_wind()
        
        # Stałe dla tła (optymalizacja - generuj raz)
        self.tree_positions = self.generate_tree_positions()

    def init_buttons(self):
        """Inicjalizuje przyciski interfejsu"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        self.play_button = pygame.Rect(center_x - 100, center_y + 50, 200, 50)
        self.quit_button = pygame.Rect(center_x - 100, center_y + 120, 200, 50)
        self.bet_up_button = pygame.Rect(center_x + 50, center_y - 50, 30, 30)
        self.bet_down_button = pygame.Rect(center_x - 80, center_y - 50, 30, 30)

    def generate_tree_positions(self):
        """Generuje pozycje drzew dla tła (optymalizacja)"""
        positions = []
        for i in range(0, SCREEN_WIDTH, 150):
            tree_x = i + random.randint(-20, 20)
            positions.append(tree_x)
        return positions

    def generate_wind(self):
        """Generuje losowy wiatr dla rundy"""
        self.wind_strength = random.uniform(0, 30)
        self.wind_direction = random.uniform(0, 2 * math.pi)

    def reset_game(self):
        """Resetuje grę do stanu początkowego"""
        self.in_game = True
        self.game_state = "menu"
        self.arrows_left = 5
        self.score = 0
        self.shot_results = []
        self.last_shot_score = 0
        
        # Aktualizuj maksymalny zakład
        self.max_bet = min(100, self.player.coins) if self.player.coins > 0 else 5
        self.current_bet = max(self.min_bet, min(self.current_bet, self.max_bet))
        
        self.generate_wind()

    def start_round(self):
        """Rozpoczyna rundę gry"""
        if self.player.coins < self.current_bet:
            return False
        
        self.player.coins -= self.current_bet
        self.game_state = "aiming"
        self.arrows_left = 5
        self.score = 0
        self.shot_results = []
        self.last_shot_score = 0
        self.generate_wind()
        return True

    def handle_event(self, event):
        """Obsługuje wydarzenia gry"""
        if self.game_state == "menu":
            self.handle_menu_event(event)
        elif self.game_state == "aiming":
            self.handle_aiming_event(event)
        elif self.game_state == "result":
            self.handle_result_event(event)

    def handle_menu_event(self, event):
        """Obsługuje wydarzenia w menu"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_button.collidepoint(event.pos):
                self.start_round()
            elif self.quit_button.collidepoint(event.pos):
                self.in_game = False
            elif self.bet_up_button.collidepoint(event.pos):
                if self.current_bet < self.max_bet:
                    self.current_bet += 5
            elif self.bet_down_button.collidepoint(event.pos):
                if self.current_bet > self.min_bet:
                    self.current_bet -= 5

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.in_game = False
            elif event.key == pygame.K_SPACE:
                self.start_round()

    def handle_aiming_event(self, event):
        """Obsługuje wydarzenia podczas celowania"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.arrow_flying:
                self.charging_power = True
            elif event.key == pygame.K_ESCAPE:
                self.game_state = "menu"
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and self.charging_power:
                self.shoot_arrow()
                self.charging_power = False

    def handle_result_event(self, event):
        """Obsługuje wydarzenia w ekranie wyników"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game_state = "menu"
            elif event.key == pygame.K_ESCAPE:
                self.in_game = False

    def update(self):
        """Główna pętla aktualizacji gry"""
        if self.game_state == "aiming":
            self.update_aiming()
            self.update_arrow()
            
        # Aktualizuj efekty
        if self.hit_effect_timer > 0:
            self.hit_effect_timer -= 1

    def update_aiming(self):
        """Aktualizuje celowanie"""
        if not self.arrow_flying:
            # Celowanie myszą
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.arrow_start_x
            dy = mouse_y - self.arrow_start_y
            
            # Oblicz kąt z ograniczeniem
            angle = math.atan2(dy, dx)
            self.aim_angle = max(-math.pi/3, min(math.pi/3, angle))
            
            # Ładowanie siły
            if self.charging_power:
                self.aim_power += self.power_direction * 2.5
                if self.aim_power >= 100:
                    self.aim_power = 100
                    self.power_direction = -1
                elif self.aim_power <= 0:
                    self.aim_power = 0
                    self.power_direction = 1

    def shoot_arrow(self):
        """Wystrzeliwuje strzałę"""
        if self.arrows_left <= 0 or self.arrow_flying:
            return
            
        # Parametry strzału
        power_multiplier = self.aim_power / 100.0
        base_speed = 12 * power_multiplier
        
        # Prędkość początkowa
        self.arrow_vel_x = base_speed * math.cos(self.aim_angle)
        self.arrow_vel_y = base_speed * math.sin(self.aim_angle)
        
        # Wpływ wiatru
        wind_effect = self.wind_strength * 0.008
        self.arrow_vel_x += wind_effect * math.cos(self.wind_direction)
        self.arrow_vel_y += wind_effect * math.sin(self.wind_direction)
        
        # Pozycja początkowa strzały
        self.arrow_x = float(self.arrow_start_x)
        self.arrow_y = float(self.arrow_start_y)
        
        # Stan strzału
        self.arrow_flying = True
        self.arrow_trail = []
        self.arrows_left -= 1
        self.aim_power = 0

    def update_arrow(self):
        """Aktualizuje pozycję strzały w locie"""
        if not self.arrow_flying:
            return
            
        # Zapisz pozycję do śladu
        self.arrow_trail.append((self.arrow_x, self.arrow_y))
        if len(self.arrow_trail) > 8:  # Zmniejszono dla wydajności
            self.arrow_trail.pop(0)
            
        # Aktualizuj pozycję
        self.arrow_x += self.arrow_vel_x
        self.arrow_y += self.arrow_vel_y
        
        # Grawitacja i opór powietrza
        self.arrow_vel_y += 0.25
        self.arrow_vel_x *= 0.998
        self.arrow_vel_y *= 0.998
        
        # Sprawdź kolizję z tarczą
        distance_to_target = math.sqrt(
            (self.arrow_x - self.target_x)**2 + 
            (self.arrow_y - self.target_y)**2
        )
        
        if distance_to_target <= self.target_radius:
            self.hit_target(distance_to_target)
            
        # Sprawdź czy strzała wyleciała poza ekran
        elif (self.arrow_x > SCREEN_WIDTH + 50 or self.arrow_x < -50 or 
              self.arrow_y > SCREEN_HEIGHT + 50 or self.arrow_y < -50):
            self.miss_target()

    def hit_target(self, distance):
        """Obsługuje trafienie w tarczę"""
        self.arrow_flying = False
        
        # Oblicz punkty na podstawie odległości od środka
        if distance <= 15:
            points = 50  # Bullseye
        elif distance <= 30:
            points = 30  # Wewnętrzny krąg
        elif distance <= 50:
            points = 20  # Środkowy krąg
        elif distance <= 70:
            points = 10  # Zewnętrzny krąg
        else:
            points = 5   # Trafienie w tarczę
            
        self.last_shot_score = points
        self.score += points
        self.shot_results.append(points)
        
        # Efekt trafienia
        self.hit_effect_timer = 20
        self.hit_effect_pos = (int(self.arrow_x), int(self.arrow_y))
        
        # Sprawdź czy koniec gry
        if self.arrows_left <= 0:
            self.end_game()

    def miss_target(self):
        """Obsługuje chybienie"""
        self.arrow_flying = False
        self.last_shot_score = 0
        self.shot_results.append(0)
        
        if self.arrows_left <= 0:
            self.end_game()

    def end_game(self):
        """Kończy grę i oblicza nagrody"""
        self.game_state = "result"
        
        # Oblicz nagrody na podstawie wyniku
        if self.score >= 200:
            reward = self.current_bet * 4
        elif self.score >= 150:
            reward = self.current_bet * 3
        elif self.score >= 100:
            reward = self.current_bet * 2
        elif self.score >= 50:
            reward = int(self.current_bet * 1.5)
        else:
            reward = 0
            
        self.player.coins += reward

    def draw(self):
        """Rysuje grę"""
        self.screen.fill((34, 139, 34))  # Zielone tło
        
        # Rysuj tło
        self.draw_background()
        
        # Rysuj odpowiedni ekran
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "aiming":
            self.draw_game()
        elif self.game_state == "result":
            self.draw_results()

    def draw_background(self):
        """Rysuje tło średniowieczne (zoptymalizowane)"""
        # Niebo z gradientem (uproszczone)
        sky_height = SCREEN_HEIGHT // 2
        for y in range(0, sky_height, 5):  # Co 5 pikseli zamiast każdego
            color_intensity = int(135 + (y / sky_height) * 120)
            color = (color_intensity, color_intensity, 255)
            pygame.draw.rect(self.screen, color, (0, y, SCREEN_WIDTH, 5))
        
        # Ziemia
        ground_rect = pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
        pygame.draw.rect(self.screen, (101, 67, 33), ground_rect)
        
        # Drzewa (używaj predefiniowanych pozycji)
        for tree_x in self.tree_positions:
            tree_y = SCREEN_HEIGHT - 50
            # Pień
            trunk_rect = pygame.Rect(tree_x, tree_y - 80, 15, 80)
            pygame.draw.rect(self.screen, (101, 67, 33), trunk_rect)
            # Korona
            pygame.draw.circle(self.screen, (34, 139, 34), (tree_x + 7, tree_y - 80), 30)

    def draw_menu(self):
        """Rysuje menu gry"""
        # Tytuł
        title = self.font.render("⚔️ ŚREDNIOWIECZNE ŁUCZNICTWO ⚔️", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Opis gry
        desc_lines = [
            "Celuj myszą, trzymaj SPACJĘ aby naładować moc",
            "Traf w centrum tarczy aby zdobyć więcej punktów!",
            f"Masz {5} strzał w rundzie",
            f"💰 Twoje monety: {self.player.coins}"
        ]
        
        for i, line in enumerate(desc_lines):
            text = self.small_font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 200 + i * 30))
            self.screen.blit(text, text_rect)
        
        # Zakład
        bet_text = self.font.render(f"Zakład: {self.current_bet} monet", True, (255, 215, 0))
        bet_rect = bet_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(bet_text, bet_rect)
        
        # Przyciski zakładu
        pygame.draw.rect(self.screen, (0, 100, 0), self.bet_up_button)
        pygame.draw.rect(self.screen, (100, 0, 0), self.bet_down_button)
        pygame.draw.rect(self.screen, WHITE, self.bet_up_button, 2)
        pygame.draw.rect(self.screen, WHITE, self.bet_down_button, 2)
        
        up_text = self.small_font.render("+", True, WHITE)
        down_text = self.small_font.render("-", True, WHITE)
        up_rect = up_text.get_rect(center=self.bet_up_button.center)
        down_rect = down_text.get_rect(center=self.bet_down_button.center)
        self.screen.blit(up_text, up_rect)
        self.screen.blit(down_text, down_rect)
        
        # Główne przyciski
        pygame.draw.rect(self.screen, (0, 100, 0), self.play_button)
        pygame.draw.rect(self.screen, (100, 0, 0), self.quit_button)
        pygame.draw.rect(self.screen, WHITE, self.play_button, 2)
        pygame.draw.rect(self.screen, WHITE, self.quit_button, 2)
        
        play_text = self.font.render("GRAJ", True, WHITE)
        quit_text = self.font.render("WYJDŹ", True, WHITE)
        
        play_rect = play_text.get_rect(center=self.play_button.center)
        quit_rect = quit_text.get_rect(center=self.quit_button.center)
        self.screen.blit(play_text, play_rect)
        self.screen.blit(quit_text, quit_rect)

    def draw_game(self):
        """Rysuje grę w trakcie"""
        # Rysuj elementy gry
        self.draw_bow()
        self.draw_target()
        
        if self.arrow_flying:
            self.draw_arrow()
        
        self.draw_ui()
        self.draw_wind_indicator()
        
        # Rysuj efekt trafienia
        if self.hit_effect_timer > 0:
            self.draw_hit_effect()

    def draw_bow(self):
        """Rysuje łuk i celownik"""
        # Łuk
        bow_rect = pygame.Rect(self.bow_x - 20, self.bow_y - 40, 40, 80)
        pygame.draw.arc(self.screen, (101, 67, 33), bow_rect, -math.pi/2, math.pi/2, 8)
        
        # Cięciwa
        pygame.draw.line(self.screen, (139, 69, 19), 
                        (self.bow_x, self.bow_y - 35), 
                        (self.bow_x, self.bow_y + 35), 2)
        
        # Celownik
        if not self.arrow_flying:
            aim_length = 100 + self.aim_power
            aim_end_x = self.arrow_start_x + aim_length * math.cos(self.aim_angle)
            aim_end_y = self.arrow_start_y + aim_length * math.sin(self.aim_angle)
            
            # Linia celowania
            pygame.draw.line(self.screen, (255, 0, 0), 
                           (self.arrow_start_x, self.arrow_start_y),
                           (aim_end_x, aim_end_y), 2)
            
            # Wskaźnik siły
            if self.charging_power:
                power_color = (255, int(255 - self.aim_power * 2.55), 0)
                radius = int(5 + self.aim_power * 0.2)
                pygame.draw.circle(self.screen, power_color, 
                                 (self.arrow_start_x, self.arrow_start_y), radius)

    def draw_target(self):
        """Rysuje tarczę"""
        # Koncentryczne kręgi
        colors_and_radii = [
            ((255, 255, 255), 80),
            ((255, 0, 0), 64),
            ((255, 215, 0), 48),
            ((0, 255, 0), 32),
            ((0, 0, 255), 16)
        ]
        
        for color, radius in colors_and_radii:
            pygame.draw.circle(self.screen, color, (self.target_x, self.target_y), radius)
            pygame.draw.circle(self.screen, BLACK, (self.target_x, self.target_y), radius, 2)
        
        # Środkowy punkt
        pygame.draw.circle(self.screen, (255, 0, 0), (self.target_x, self.target_y), 5)

    def draw_arrow(self):
        """Rysuje strzałę w locie"""
        # Ślad strzały
        if len(self.arrow_trail) > 1:
            for i in range(1, len(self.arrow_trail)):
                thickness = max(1, i)
                start_pos = (int(self.arrow_trail[i-1][0]), int(self.arrow_trail[i-1][1]))
                end_pos = (int(self.arrow_trail[i][0]), int(self.arrow_trail[i][1]))
                pygame.draw.line(self.screen, (255, 255, 0), start_pos, end_pos, thickness)
        
        # Strzała
        arrow_angle = math.atan2(self.arrow_vel_y, self.arrow_vel_x)
        arrow_length = 20
        
        tip_x = self.arrow_x + arrow_length * math.cos(arrow_angle)
        tip_y = self.arrow_y + arrow_length * math.sin(arrow_angle)
        
        # Korpus strzały
        pygame.draw.line(self.screen, (139, 69, 19), 
                        (int(self.arrow_x), int(self.arrow_y)), 
                        (int(tip_x), int(tip_y)), 3)
        
        # Grot
        pygame.draw.circle(self.screen, (192, 192, 192), (int(tip_x), int(tip_y)), 4)

    def draw_ui(self):
        """Rysuje interfejs użytkownika"""
        # Pozostałe strzały
        arrows_text = self.font.render(f"🏹 Strzały: {self.arrows_left}", True, WHITE)
        self.screen.blit(arrows_text, (10, 10))
        
        # Wynik
        score_text = self.font.render(f"⭐ Wynik: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 50))
        
        # Ostatni strzał
        if self.last_shot_score > 0:
            last_shot_text = self.small_font.render(f"Ostatni strzał: +{self.last_shot_score}", True, (0, 255, 0))
            self.screen.blit(last_shot_text, (10, 90))
        
        # Wskaźnik mocy
        if not self.arrow_flying:
            power_bar_rect = pygame.Rect(10, SCREEN_HEIGHT - 60, 200, 20)
            pygame.draw.rect(self.screen, (60, 60, 60), power_bar_rect)
            
            if self.charging_power:
                power_width = int(200 * (self.aim_power / 100))
                power_color = (255, int(255 - self.aim_power * 2.55), 0)
                power_rect = pygame.Rect(10, SCREEN_HEIGHT - 60, power_width, 20)
                pygame.draw.rect(self.screen, power_color, power_rect)
            
            pygame.draw.rect(self.screen, WHITE, power_bar_rect, 2)
            power_text = self.small_font.render("Moc strzału", True, WHITE)
            self.screen.blit(power_text, (10, SCREEN_HEIGHT - 85))

    def draw_wind_indicator(self):
        """Rysuje wskaźnik wiatru"""
        wind_x = SCREEN_WIDTH - 120
        wind_y = 50
        
        # Tło wskaźnika
        wind_bg = pygame.Rect(wind_x - 60, wind_y - 20, 120, 40)
        pygame.draw.rect(self.screen, (0, 0, 0), wind_bg)
        pygame.draw.rect(self.screen, WHITE, wind_bg, 2)
        
        # Strzałka wiatru
        wind_end_x = wind_x + 25 * math.cos(self.wind_direction)
        wind_end_y = wind_y + 25 * math.sin(self.wind_direction)
        
        pygame.draw.line(self.screen, WHITE, (wind_x, wind_y), (wind_end_x, wind_end_y), 3)
        pygame.draw.circle(self.screen, WHITE, (int(wind_end_x), int(wind_end_y)), 4)
        
        # Siła wiatru
        wind_text = self.small_font.render(f"💨 {int(self.wind_strength)}", True, WHITE)
        self.screen.blit(wind_text, (wind_x - 50, wind_y + 15))

    def draw_hit_effect(self):
        """Rysuje efekt trafienia"""
        if self.hit_effect_pos:
            effect_radius = int(15 * (self.hit_effect_timer / 20))
            colors = [(255, 255, 0), (255, 215, 0), (255, 165, 0)]
            
            for i, color in enumerate(colors):
                radius = max(0, effect_radius - i * 3)
                if radius > 0:
                    pygame.draw.circle(self.screen, color, self.hit_effect_pos, radius)

    def draw_results(self):
        """Rysuje ekran wyników"""
        # Tło wyników
        result_bg = pygame.Rect(SCREEN_WIDTH//4, SCREEN_HEIGHT//4, 
                               SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        pygame.draw.rect(self.screen, (0, 0, 0), result_bg)
        pygame.draw.rect(self.screen, (255, 215, 0), result_bg, 3)
        
        # Tytuł
        title = self.font.render("🏆 WYNIKI 🏆", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 40))
        self.screen.blit(title, title_rect)
        
        # Szczegółowe wyniki
        y_offset = SCREEN_HEIGHT//4 + 100
        
        for i, shot_score in enumerate(self.shot_results):
            shot_text = self.small_font.render(f"Strzał {i+1}: {shot_score} pkt", True, WHITE)
            self.screen.blit(shot_text, (SCREEN_WIDTH//2 - 60, y_offset + i * 22))
        
        # Podsumowanie
        total_text = self.font.render(f"Łączny wynik: {self.score} pkt", True, (255, 215, 0))
        total_rect = total_text.get_rect(center=(SCREEN_WIDTH//2, y_offset + len(self.shot_results) * 22 + 30))
        self.screen.blit(total_text, total_rect)
        
        # Nagroda
        if self.score >= 100:
            reward_text = self.font.render("🎉 DOSKONALE! 🎉", True, (0, 255, 0))
        elif self.score >= 50:
            reward_text = self.font.render("👍 DOBRZE!", True, (255, 255, 0))
        else:
            reward_text = self.font.render("Spróbuj ponownie!", True, (255, 100, 100))
        
        reward_rect = reward_text.get_rect(center=(SCREEN_WIDTH//2, total_rect.centery + 40))
        self.screen.blit(reward_text, reward_rect)
        
        # Instrukcja
        instruction = self.small_font.render("Naciśnij SPACJĘ aby kontynuować", True, (200, 200, 200))
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + SCREEN_HEIGHT//2 - 30))
        self.screen.blit(instruction, instruction_rect)