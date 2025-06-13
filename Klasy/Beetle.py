import pygame
import random
import math
import time
from config import *

class Beetle:
    def __init__(self, x, y, color, name, base_speed, lane_y):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = lane_y  # Stała pozycja Y (tor)
        self.target_y = lane_y  # Docelowa pozycja Y
        self.color = color
        self.name = name
        self.base_speed = base_speed  # Bazowa prędkość (wpływa na kursy)
        self.lane_y = lane_y
        self.distance_traveled = 0
        self.is_boosted = False  # Czy został "podkarmiony"
        self.boost_timer = 0
        self.wobble_offset = 0  # Efekt kołysania się
        self.animation_time = 0
        self.speed_variation = random.uniform(0.8, 1.2)  # Indywidualna zmienność prędkości
        
        # Statystyki do wyświetlania
        self.wins = random.randint(0, 50)  # Symulowane poprzednie wygrane
        self.races = random.randint(self.wins, 100)  # Symulowane poprzednie wyścigi
        
    def reset_position(self):
        """Resetuje pozycję żuka na start"""
        self.x = self.start_x
        self.y = self.lane_y
        self.target_y = self.lane_y
        self.distance_traveled = 0
        self.wobble_offset = 0
        self.animation_time = 0
        self.speed_variation = random.uniform(0.8, 1.2)
        
    def update(self, delta_time):
        """Aktualizuje pozycję żuka"""
        self.animation_time += delta_time * 3
        
        # Stały ruch do przodu z losowymi wahaniami
        base_move = self.base_speed * delta_time * 100 * self.speed_variation
        
        # Bonus za "podkarmienie"
        boost_factor = 1.5 if self.is_boosted else 1.0
        
        # Losowe wahania prędkości
        random_factor = random.uniform(0.8, 1.2)
        
        movement = base_move * random_factor * boost_factor
        self.x += movement
        self.distance_traveled += movement
        
        # Małe zbaczanie z toru (kołysanie się)
        if random.random() < 0.05:  # 5% szansy na zboczenie
            self.target_y = self.lane_y + random.uniform(-10, 10)
        
        # Płynne przejście do docelowej pozycji Y
        if abs(self.y - self.target_y) > 1:
            self.y += (self.target_y - self.y) * delta_time * 5
        
        # Efekt kołysania podczas ruchu
        self.wobble_offset = math.sin(self.animation_time) * 3
        
        # Zmniejsz timer boosta
        if self.is_boosted:
            self.boost_timer -= delta_time
            if self.boost_timer <= 0:
                self.is_boosted = False
    
    def apply_boost(self):
        """Aplikuje boost (podkarmienie żuka)"""
        self.is_boosted = True
        self.boost_timer = 5.0  # 5 sekund boosta
        self.speed_variation = random.uniform(1.1, 1.5)  # Zwiększ prędkość
    
    def draw(self, surface, offset_x=0):
        """Rysuje żuka"""
        draw_x = int(self.x + offset_x)
        draw_y = int(self.y + self.wobble_offset)
        
        # Efekt świecenia dla boosted żuka
        if self.is_boosted:
            glow_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
            glow_surface.fill((0, 0, 0, 0))
            pygame.draw.circle(glow_surface, (*self.color, 100), (15, 15), 15)
            surface.blit(glow_surface, (draw_x - 15, draw_y - 15))
        
        # Ciało żuka (owalna podstawa)
        pygame.draw.ellipse(surface, self.color, (draw_x - 10, draw_y - 8, 20, 16))
        
        # Głowa
        head_color = tuple(max(0, c - 30) for c in self.color)  # Ciemniejszy odcień
        pygame.draw.circle(surface, head_color, (draw_x - 12, draw_y), 5)
        
        # Oczy
        pygame.draw.circle(surface, (255, 255, 255), (draw_x - 14, draw_y - 2), 2)
        pygame.draw.circle(surface, (255, 255, 255), (draw_x - 14, draw_y + 2), 2)
        pygame.draw.circle(surface, (0, 0, 0), (draw_x - 13, draw_y - 2), 1)
        pygame.draw.circle(surface, (0, 0, 0), (draw_x - 13, draw_y + 2), 1)
        
        # Nóżki (animowane)
        leg_offset = math.sin(self.animation_time * 3) * 3
        for i in range(3):
            leg_y = draw_y - 4 + i * 4
            # Lewa strona
            pygame.draw.line(surface, head_color, 
                           (draw_x - 8, leg_y), 
                           (draw_x - 14 + leg_offset, leg_y + 4), 2)
            # Prawa strona  
            pygame.draw.line(surface, head_color,
                           (draw_x + 8, leg_y),
                           (draw_x + 14 - leg_offset, leg_y + 4), 2)
        
        # Czułki
        antenna_sway = math.sin(self.animation_time * 2) * 2
        pygame.draw.line(surface, head_color,
                        (draw_x - 12, draw_y - 4),
                        (draw_x - 18 + antenna_sway, draw_y - 10), 2)
        pygame.draw.line(surface, head_color,
                        (draw_x - 12, draw_y - 4),
                        (draw_x - 16 + antenna_sway, draw_y - 10), 2)
        
        # Kółeczka na końcach czułek
        pygame.draw.circle(surface, (255, 200, 0), 
                         (int(draw_x - 18 + antenna_sway), draw_y - 10), 2)
        pygame.draw.circle(surface, (255, 200, 0),
                         (int(draw_x - 16 + antenna_sway), draw_y - 10), 2)


class BeetleRaceGame:
    def __init__(self, player):
        self.player = player
        self.in_game = False
        self.screen = pygame.display.get_surface()
        
        # Czcionki
        try:
            self.font_large = pygame.font.Font("assets/Czcionka.ttf", 32)
            self.font_medium = pygame.font.Font("assets/Czcionka.ttf", 24)
            self.font_small = pygame.font.Font("assets/Czcionka.ttf", 18)
        except:
            self.font_large = pygame.font.Font(None, 32)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
        
        # Stan gry
        self.game_state = "betting"  # betting, racing, finished
        self.selected_beetle = 0
        self.bet_amount = 10
        self.min_bet = 5
        self.max_bet = min(100, self.player.coins // 2) if self.player.coins >= 10 else 0
        
        # Wyścig
        self.race_start_x = SCREEN_WIDTH * 0.1  # 10% szerokości ekranu
        self.race_finish_x = SCREEN_WIDTH * 0.9  # 90% szerokości ekranu
        self.race_distance = self.race_finish_x - self.race_start_x
        self.winner = None
        self.race_timer = 0
        self.race_duration = 0
        
        # UI
        self.betting_panel_rect = pygame.Rect(
            SCREEN_WIDTH * 0.05,  # 5% od lewej
            SCREEN_HEIGHT * 0.05,  # 5% od góry
            SCREEN_WIDTH * 0.9,    # 90% szerokości
            SCREEN_HEIGHT * 0.45   # 35% wysokości
        )
        
        self.track_rect = pygame.Rect(
            SCREEN_WIDTH * 0.05,   # 5% od lewej
            SCREEN_HEIGHT * 0.35,  # 35% od góry
            SCREEN_WIDTH * 0.9,    # 90% szerokości
            SCREEN_HEIGHT * 0.5    # 50% wysokości
        )
        
        # Żuki
        self.beetles = []
        self.init_beetles()
        
        # Animacje
        self.celebration_timer = 0
        self.fireworks = []
        
        # Dźwięki wyścigu (symulowane przez text)
        self.race_announcements = []
        self.announcement_timer = 0
        
    def init_beetles(self):
        """Inicjalizuje żuki z różnymi charakterystykami"""
        beetle_data = [
            {"name": "Błyskawica", "color": (255, 50, 50), "speed": 1.4, "odds": 2.2},
            {"name": "Żółtek", "color": (255, 255, 50), "speed": 1.2, "odds": 2.5},
            {"name": "Zieleń", "color": (50, 255, 50), "speed": 1.0, "odds": 3.0},
            {"name": "Błękitny", "color": (50, 150, 255), "speed": 0.9, "odds": 3.5},
            {"name": "Purpura", "color": (200, 50, 255), "speed": 0.8, "odds": 4.0},
        ]
        
        self.beetles = []
        lane_height = self.track_rect.height / len(beetle_data)
        
        for i, data in enumerate(beetle_data):
            lane_y = self.track_rect.y + (i + 0.5) * lane_height
            beetle = Beetle(
                x=self.race_start_x,
                y=lane_y,
                color=data["color"],
                name=data["name"],
                base_speed=data["speed"],
                lane_y=lane_y
            )
            # Dodaj kursy
            beetle.odds = data["odds"]
            self.beetles.append(beetle)
    
    def reset_game(self):
        """Resetuje grę do stanu początkowego"""
        self.in_game = True
        self.game_state = "betting"
        self.selected_beetle = 0
        self.bet_amount = max(self.min_bet, min(50, self.player.coins // 10))
        self.max_bet = min(100, self.player.coins // 2) if self.player.coins >= 10 else 0
        self.winner = None
        self.race_timer = 0
        self.celebration_timer = 0
        self.fireworks = []
        self.race_announcements = []
        
        # Reset pozycji żuków
        for beetle in self.beetles:
            beetle.reset_position()
    
    def handle_event(self, event):
        """Obsługuje wydarzenia"""
        if not self.in_game:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.in_game = False
                return
                
            if self.game_state == "betting":
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_beetle = (self.selected_beetle - 1) % len(self.beetles)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_beetle = (self.selected_beetle + 1) % len(self.beetles)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.bet_amount = max(self.min_bet, self.bet_amount - 5)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.bet_amount = min(self.max_bet, self.bet_amount + 5)
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.start_race()
                elif event.key == pygame.K_b and self.player.coins >= 20:  # Boost za dodatkowe 20 monet
                    if self.bet_amount + 20 <= self.player.coins:
                        self.beetles[self.selected_beetle].apply_boost()
                        self.player.coins -= 20
                        
            elif self.game_state == "finished":
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.reset_game()
    
    def start_race(self):
        """Rozpoczyna wyścig"""
        if self.player.coins < self.bet_amount:
            return
            
        self.player.coins -= self.bet_amount
        self.game_state = "racing"
        self.race_timer = 0
        self.winner = None
        self.in_game = True
        # Dodaj ogłoszenia wyścigu
        self.race_announcements = [
            "Żuki na pozycjach startowych!",
            "3... 2... 1... START!",
            "Wyścig się rozpoczął!",
        ]
        self.announcement_timer = 0
    
    def update(self, delta_time):
        """Aktualizuje stan gry"""
        if not self.in_game:
            return
            
        if self.game_state == "racing":
            self.race_timer += delta_time
            
            # Aktualizuj żuki
            for beetle in self.beetles:
                beetle.update(delta_time)
            
            # Sprawdź czy ktoś dotarł do mety
            for beetle in self.beetles:
                if beetle.x >= self.race_finish_x and not self.winner:
                    self.winner = beetle
                    self.game_state = "finished"
                    self.race_duration = self.race_timer
                    self.process_winnings()
                    self.celebration_timer = 3.0  # 3 sekundy celebracji
                    self.create_fireworks()
                    break
            
            # Aktualizuj ogłoszenia
            self.announcement_timer += delta_time
            if self.announcement_timer > 1.0 and self.race_announcements:
                self.race_announcements.pop(0)
                self.announcement_timer = 0
        
        elif self.game_state == "finished":
            if self.celebration_timer > 0:
                self.celebration_timer -= delta_time
                self.update_fireworks(delta_time)
    
    def process_winnings(self):
        """Przetwarza wygrane"""
        if self.beetles[self.selected_beetle] == self.winner:
            winnings = int(self.bet_amount * self.winner.odds)
            self.player.coins += winnings
            # Zamiast todo item — komunikat
            self.race_announcements.append(f"Wygrałeś {winnings} monet!")
        else:
            self.race_announcements.append(f"Przegrałeś {self.bet_amount} monet")
        
    def create_fireworks(self):
        """Tworzy efekt fajerwerków"""
        for _ in range(20):
            self.fireworks.append({
                'x': random.randint(int(SCREEN_WIDTH * 0.1), int(SCREEN_WIDTH * 0.9)),
                'y': random.randint(int(SCREEN_HEIGHT * 0.1), int(SCREEN_HEIGHT * 0.4)),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-3, -1),
                'color': random.choice([(255, 100, 100), (100, 255, 100), (100, 100, 255), 
                                      (255, 255, 100), (255, 100, 255), (100, 255, 255)]),
                'life': 1.0,
                'size': random.randint(2, 5)
            })
    
    def update_fireworks(self, delta_time):
        """Aktualizuje fajerwerki"""
        for firework in self.fireworks[:]:
            firework['x'] += firework['vx']
            firework['y'] += firework['vy']
            firework['vy'] += 0.1  # Grawitacja
            firework['life'] -= delta_time * 2
            
            if firework['life'] <= 0:
                self.fireworks.remove(firework)
    
    def draw(self):
        """Rysuje grę"""
        if not self.in_game:
            return
            
        self.screen.fill((20, 40, 20))  # Ciemnozielone tło
        
        if self.game_state == "betting":
            self.draw_betting_interface()
        elif self.game_state == "racing":
            self.draw_race()
        elif self.game_state == "finished":
            self.draw_race()
            self.draw_results()
            self.draw_fireworks()
    
    def draw_betting_interface(self):
        """Rysuje interfejs obstawiania"""
        # Tło panelu
        pygame.draw.rect(self.screen, (40, 60, 40), self.betting_panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 150, 100), self.betting_panel_rect, 3, border_radius=15)
        
        # Tytuł
        title = self.font_large.render(" WYŚCIG ŻUKÓW - OBSTAWIANIE ", True, (255, 255, 100))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, self.betting_panel_rect.y + 30))
        self.screen.blit(title, title_rect)
        
        # Informacje o grze
        info_y = self.betting_panel_rect.y + 60
        info_lines = [
            "Wybierz żuka (Strzałki Góra-Dół), ustaw zakład (Strzałki Prawo-Lewo), potwierdź (SPACJA)",
            f"Twoje monety: {self.player.coins} | Zakład: {self.bet_amount}",
            "Naciśnij 'B' aby podkarmić wybranego żuka (+20 monet, większa szansa)",
            "Naciśnij ESC aby wyjść z wyścigu",
        ]
        
        for i, line in enumerate(info_lines):
            color = (255, 255, 255) if i != 1 else (100, 255, 100)
            text = self.font_small.render(line, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, info_y + i * 25))
            self.screen.blit(text, text_rect)
        
        # Lista żuków
        beetle_y_start = info_y + 120
        beetle_list_height = min(150, SCREEN_HEIGHT * 0.4)  # Maksymalna wysokość listy
        row_height = beetle_list_height / len(self.beetles)
        
        for i, beetle in enumerate(self.beetles):
            y = beetle_y_start + i * row_height
            
            # Podświetl wybranego żuka
            if i == self.selected_beetle:
                highlight_rect = pygame.Rect(
                    self.betting_panel_rect.x + 10,
                    y - row_height/2 + 5,
                    self.betting_panel_rect.width - 20,
                    row_height - 10
                )
                pygame.draw.rect(self.screen, (80, 120, 80), highlight_rect, border_radius=5)
            
            # Nazwa i statistyki żuka
            win_rate = (beetle.wins / beetle.races * 100) if beetle.races > 0 else 0
            beetle_info = f"{beetle.name} | Kurs: {beetle.odds:.1f}x | Wygrane: {beetle.wins}/{beetle.races} ({win_rate:.0f}%)"
            
            color = (255, 255, 100) if i == self.selected_beetle else (200, 200, 200)
            if beetle.is_boosted:
                color = (255, 255, 0)  # Złoty dla podboosted
                beetle_info += "BOOST!"
            
            text = self.font_small.render(beetle_info, True, color)
            self.screen.blit(text, (self.betting_panel_rect.x + 20, y - 10))
            
            # Mały podgląd żuka
            preview_x = self.betting_panel_rect.right - 40
            pygame.draw.ellipse(self.screen, beetle.color, (preview_x - 10, y - 8, 20, 16))
        
        # Potencjalna wygrana
        potential_win = int(self.bet_amount * self.beetles[self.selected_beetle].odds)
        win_info = self.font_medium.render(f"Potencjalna wygrana: {potential_win} monet", True, (100, 255, 100))
        win_rect = win_info.get_rect(center=(SCREEN_WIDTH // 2, self.betting_panel_rect.bottom - 30))
        self.screen.blit(win_info, win_rect)
    
    def draw_race(self):
        """Rysuje wyścig"""
        # Tło toru
        pygame.draw.rect(self.screen, (60, 40, 20), self.track_rect, border_radius=10)
        pygame.draw.rect(self.screen, (150, 100, 50), self.track_rect, 3, border_radius=10)
        
        # Linia startu
        start_line = pygame.Rect(self.race_start_x - 5, self.track_rect.y, 10, self.track_rect.height)
        pygame.draw.rect(self.screen, (255, 255, 255), start_line)
        start_text = self.font_small.render("START", True, (255, 255, 255))
        self.screen.blit(start_text, (self.race_start_x - 25, self.track_rect.y - 25))
        
        # Linia mety
        finish_line = pygame.Rect(self.race_finish_x - 5, self.track_rect.y, 10, self.track_rect.height)
        pygame.draw.rect(self.screen, (255, 0, 0), finish_line)
        finish_text = self.font_small.render("META", True, (255, 0, 0))
        self.screen.blit(finish_text, (self.race_finish_x - 20, self.track_rect.y - 25))
        
        # Tory (linie oddzielające)
        lane_height = self.track_rect.height / len(self.beetles)
        for i in range(1, len(self.beetles)):
            y = self.track_rect.y + i * lane_height
            pygame.draw.line(self.screen, (100, 70, 30), 
                           (self.track_rect.x, y), (self.track_rect.right, y), 1)
        
        # Żuki
        for i, beetle in enumerate(self.beetles):
            beetle.draw(self.screen)
            
            # Numer żuka
            #number_text = self.font_small.render(str(i + 1), True, (255, 255, 255))
            #self.screen.blit(number_text, (beetle.x - 20, beetle.y - 10))
            
            # Podświetl obstawiany żuk
            #if i == self.selected_beetle:
            #    highlight_rect = pygame.Rect(beetle.x - 15, beetle.y - 15, 30, 30)
            #    pygame.draw.rect(self.screen, (255, 255, 0), highlight_rect, 2)
        
        # Informacje o wyścigu
        info_y = 20
        if self.game_state == "racing":
            race_info = [
                f"Czas wyścigu: {self.race_timer:.1f}s",
                f"Obstawiony żuk: {self.beetles[self.selected_beetle].name}",
                f"Zakład: {self.bet_amount} monet"
            ]
        else:
            race_info = [
                f"Wyścig zakończony w: {self.race_duration:.1f}s",
                f"Zwycięzca: {self.winner.name if self.winner else 'Brak'}",
                f"Twój żuk: {self.beetles[self.selected_beetle].name}"
            ]
        
        for i, info in enumerate(race_info):
            text = self.font_small.render(info, True, (255, 255, 255))
            self.screen.blit(text, (20, info_y + i * 20))
        
        # Pasek postępu wyścigu
        if self.game_state == "racing":
            progress_width = SCREEN_WIDTH * 0.8
            progress_height = 10
            progress_x = SCREEN_WIDTH * 0.1
            progress_y = SCREEN_HEIGHT * 0.9
            
            # Tło paska
            pygame.draw.rect(self.screen, (100, 100, 100), 
                           (progress_x, progress_y, progress_width, progress_height))
            
            # Najbardziej zaawansowany żuk
            max_progress = max(b.x for b in self.beetles)
            current_progress = min(1.0, (max_progress - self.race_start_x) / self.race_distance)
            
            # Wypełnienie paska
            pygame.draw.rect(self.screen, (0, 200, 0), 
                           (progress_x, progress_y, progress_width * current_progress, progress_height))
            
            # Etykieta
            progress_text = self.font_small.render(f"Postęp wyścigu: {current_progress*100:.1f}%", True, (255, 255, 255))
            self.screen.blit(progress_text, (progress_x, progress_y - 20))
        
        # Ogłoszenia wyścigu
        if self.race_announcements:
            announcement = self.font_medium.render(self.race_announcements[0], True, (255, 255, 100))
            announcement_rect = announcement.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.85))
            
            # Tło ogłoszenia
            bg_rect = announcement_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, (0, 0, 0, 150), bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 100), bg_rect, 2, border_radius=10)
            
            self.screen.blit(announcement, announcement_rect)
    
    def draw_results(self):
        """Rysuje wyniki wyścigu"""
        if not self.winner:
            return
            
        # Panel wyników
        result_rect = pygame.Rect(
            SCREEN_WIDTH * 0.2, 
            SCREEN_HEIGHT * 0.2, 
            SCREEN_WIDTH * 0.6, 
            SCREEN_HEIGHT * 0.3
        )
        pygame.draw.rect(self.screen, (40, 40, 80), result_rect, border_radius=15)
        pygame.draw.rect(self.screen, (150, 150, 255), result_rect, 3, border_radius=15)
        
        # Sprawdź czy gracz wygrał
        player_won = self.beetles[self.selected_beetle] == self.winner
        
        if player_won:
            result_title = " GRATULACJE! "
            result_color = (100, 255, 100)
            winnings = int(self.bet_amount * self.winner.odds)
            result_text = f"Wygrałeś {winnings} monet!"
        else:
            result_title = " Przegrana"
            result_color = (255, 100, 100)
            result_text = f"Straciłeś {self.bet_amount} monet"
        
        # Tytuł wyniku
        title = self.font_large.render(result_title, True, result_color)
        title_rect = title.get_rect(center=(result_rect.centerx, result_rect.y + 50))
        self.screen.blit(title, title_rect)
        
        # Zwycięzca
        winner_text = self.font_medium.render(f"Zwycięzca: {self.winner.name}", True, (255, 255, 255))
        winner_rect = winner_text.get_rect(center=(result_rect.centerx, result_rect.y + 100))
        self.screen.blit(winner_text, winner_rect)
        
        # Wynik finansowy
        money_text = self.font_medium.render(result_text, True, result_color)
        money_rect = money_text.get_rect(center=(result_rect.centerx, result_rect.y + 140))
        self.screen.blit(money_text, money_rect)
        
        # Instrukcja kontynuacji
        continue_text = self.font_small.render("Naciśnij SPACJĘ aby zagrać ponownie", True, (200, 200, 200))
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.9))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_fireworks(self):
        """Rysuje fajerwerki"""
        for firework in self.fireworks:
            alpha = int(255 * firework['life'])
            color = firework['color']
            
            # Użyj pygame.gfxdraw jeśli dostępne, inaczej zwykłe koło
            try:
                import pygame.gfxdraw
                pygame.gfxdraw.filled_circle(
                    self.screen, 
                    int(firework['x']), 
                    int(firework['y']), 
                    firework['size'], 
                    color
                )
            except:
                pygame.draw.circle(
                    self.screen, 
                    color, 
                    (int(firework['x']), int(firework['y'])), 
                    firework['size']
                )