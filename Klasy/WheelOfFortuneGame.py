import pygame
import random
import math
import json
import os
from datetime import datetime, date
from config import *

class WheelOfFortuneGame:
    def __init__(self, player):
        self.player = player
        
        # Upewnij się, że folder DataBase istnieje
        os.makedirs("DataBase", exist_ok=True)
        
        # Inicjalizacja czcionek
        self._init_fonts()
        
        # Stan gry
        self.result = ""
        self.game_state = "waiting"  # waiting, spinning, finished
        self.in_game = True
        
        # Sprawdź czy gracz może dziś grać
        self.can_play_today = self._check_daily_availability()
        
        # Pozycje i rozmiary elementów
        self._init_positions()
        
        # Koło fortuny
        self._init_wheel()
        
        # Animacje
        self._init_animation()
        
        # Kolory
        self._init_colors()

    def _init_fonts(self):
        """Inicjalizuje wszystkie czcionki"""
        self.fonts = {
            'small': pygame.font.Font('assets/Czcionka.ttf', 24),
            'normal': pygame.font.Font('assets/Czcionka.ttf', 32),
            'large': pygame.font.Font('assets/Czcionka.ttf', 42),
            'title': pygame.font.Font('assets/Czcionka.ttf', 56)
        }

    def _init_positions(self):
        """Inicjalizuje pozycje elementów interfejsu"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 - 50
        
        # Koło fortuny
        self.wheel_center = (center_x, center_y)
        self.wheel_radius = 180
        
        # Przyciski
        self.buttons = {
            'spin': pygame.Rect(center_x - 100, center_y + 220, 200, 50),
            'exit': pygame.Rect(SCREEN_WIDTH - 120, 10, 110, 40)
        }
        
        # Wskazówka (strzałka)
        self.pointer_pos = (center_x, center_y - self.wheel_radius - 10)

    def _init_wheel(self):
        """Inicjalizuje koło fortuny z nagrodami"""
        # Nagrody - różne wartości monet
        self.prizes = [
            {"coins": 10, "color": (255, 100, 100), "name": "10 monet"},
            {"coins": 25, "color": (100, 255, 100), "name": "25 monet"},
            {"coins": 5, "color": (255, 255, 100), "name": "5 monet"},
            {"coins": 50, "color": (100, 100, 255), "name": "50 monet"},
            {"coins": 15, "color": (255, 150, 255), "name": "15 monet"},
            {"coins": 100, "color": (255, 215, 0), "name": "JACKPOT!"},
            {"coins": 20, "color": (150, 255, 150), "name": "20 monet"},
            {"coins": 1, "color": (200, 200, 200), "name": "1 moneta"}
        ]
        
        self.num_segments = len(self.prizes)
        self.segment_angle = 360 / self.num_segments

    def _init_animation(self):
        """Inicjalizuje parametry animacji"""
        self.animation = {
            'spinning': False,
            'angle': 0,
            'spin_speed': 0,
            'spin_duration': 0,
            'spin_start_time': 0,
            'final_angle': 0,
            'selected_prize': None
        }

    def _init_colors(self):
        """Inicjalizuje paletę kolorów"""
        self.colors = {
            'bg_start': (25, 25, 50),
            'bg_end': (60, 60, 120),
            'bg_accent': (100, 100, 200),
            'gold': (255, 215, 0),
            'gold_light': (255, 235, 100),
            'gold_dark': (218, 165, 32),
            'green': (76, 175, 80),
            'green_light': (129, 199, 132),
            'green_dark': (56, 142, 60),
            'red': (244, 67, 54),
            'red_light': (239, 154, 154),
            'red_dark': (198, 40, 40),
            'panel_bg': (40, 40, 80),
            'panel_bg_light': (60, 60, 100),
            'panel_border': (100, 100, 180),
            'panel_border_bright': (150, 150, 255),
            'text_white': (255, 255, 255),
            'text_light': (240, 240, 240),
            'text_dark': (40, 40, 40),
            'shadow': (0, 0, 0),
            'wheel_border': (220, 220, 220),
            'wheel_center': (200, 200, 200),
            'glow': (255, 255, 100)
        }

    def _check_daily_availability(self):
        """Sprawdza czy gracz może dziś grać"""
        today = date.today().isoformat()
        
        # Ścieżka do pliku z zapisanymi datami gier
        save_file = os.path.join("DataBase", f"wheel_plays_{self.player.name}.json")
        
        if os.path.exists(save_file):
            try:
                with open(save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    last_play_date = data.get("last_play_date", "")
                    print(f"Ostatnia gra: {last_play_date}, Dziś: {today}")
                    return last_play_date != today
            except Exception as e:
                print(f"Błąd podczas odczytu daty gry: {e}")
                return True
        
        return True

    def _save_daily_play(self):
        """Zapisuje dzisiejszą datę jako dzień gry"""
        today = date.today().isoformat()
        now = datetime.now()
        
        save_file = os.path.join("DataBase", f"wheel_plays_{self.player.name}.json")
        
        data = {"last_play_date": today}
        
        try:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd przy zapisywaniu daty gry: {e}")

    def _get_total_plays(self):
        """Pobiera całkowitą liczbę gier gracza"""
        save_file = os.path.join("DataBase", f"wheel_plays_{self.player.name}.json")
        
        if os.path.exists(save_file):
            try:
                with open(save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("total_plays", 0)
            except:
                return 0
        return 0

    def draw(self):
        """Główna funkcja rysowania"""
        self._draw_background()
        self._draw_title()
        
        if self.can_play_today:
            self._draw_wheel()
            self._draw_pointer()
            self._draw_instructions()
        elif self.in_game:
            self._draw_already_played_message()

        
        self._draw_buttons()
        self._draw_player_info()
        
        if self.result:
            self._draw_result()

    def _draw_background(self):
        """Rysuje ulepszone tło z gradientem i wzorami"""
        # Główny gradient
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            color_r = int(self.colors['bg_start'][0] + (self.colors['bg_end'][0] - self.colors['bg_start'][0]) * progress)
            color_g = int(self.colors['bg_start'][1] + (self.colors['bg_end'][1] - self.colors['bg_start'][1]) * progress)
            color_b = int(self.colors['bg_start'][2] + (self.colors['bg_end'][2] - self.colors['bg_start'][2]) * progress)
            
            pygame.draw.line(screen, (color_r, color_g, color_b), (0, y), (SCREEN_WIDTH, y))
        
        # Delikatne wzory w tle
        current_time = pygame.time.get_ticks()
        for i in range(0, SCREEN_WIDTH, 100):
            for j in range(0, SCREEN_HEIGHT, 100):
                alpha = int(20 + 10 * math.sin(current_time * 0.001 + i * 0.01 + j * 0.01))
                size = int(30 + 10 * math.cos(current_time * 0.002 + i * 0.005))
                if size > 0:
                    glow_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (*self.colors['bg_accent'], alpha), (size, size), size)
                    screen.blit(glow_surface, (i - size, j - size))

    def _draw_title(self):
        """Rysuje tytuł gry"""
        title_text = "KOŁO FORTUNY"
        
        title_shadow = self.fonts['title'].render(title_text, True, self.colors['shadow'])
        title = self.fonts['title'].render(title_text, True, self.colors['gold'])
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        
        screen.blit(title_shadow, (title_x + 2, 22))
        screen.blit(title, (title_x, 20))

    def _draw_wheel(self):
        """Rysuje koło fortuny"""
        center_x, center_y = self.wheel_center
        
        if self.animation['spinning']:
            current_time = pygame.time.get_ticks()
            self._update_spin_animation(current_time)
        
        # Rysuj segmenty koła
        for i, prize in enumerate(self.prizes):
            start_angle = math.radians(i * self.segment_angle + self.animation['angle'])
            end_angle = math.radians((i + 1) * self.segment_angle + self.animation['angle'])
            
            self._draw_wheel_segment(center_x, center_y, start_angle, end_angle, prize, i)
        
        # Rysuj obramowanie koła
        pygame.draw.circle(screen, self.colors['wheel_border'], 
                        (center_x, center_y), self.wheel_radius + 3, 3)

    def _draw_wheel_segment(self, center_x, center_y, start_angle, end_angle, prize, segment_index):
        """Rysuje pojedynczy segment koła"""
        mid_angle = (start_angle + end_angle) / 2
        
        # Tworzenie punktów segmentu
        points = [(center_x, center_y)]
        
        # Dodaj punkty na obwodzie
        num_points = max(8, int(abs(end_angle - start_angle) * 180 / math.pi))
        for i in range(num_points + 1):
            angle = start_angle + (end_angle - start_angle) * i / num_points
            x = center_x + self.wheel_radius * math.cos(angle)
            y = center_y + self.wheel_radius * math.sin(angle)
            points.append((x, y))
        
        # Rysuj segment
        pygame.draw.polygon(screen, prize["color"], points)
        pygame.draw.polygon(screen, self.colors['wheel_border'], points, 2)
        
        # Rysuj tekst nagrody - zawsze widoczny
        text_radius = self.wheel_radius * 0.65
        text_x = center_x + text_radius * math.cos(mid_angle)
        text_y = center_y + text_radius * math.sin(mid_angle)
        
        # Tekst z cieniem dla lepszej czytelności
        text_str = str(prize["coins"])
        text_shadow = self.fonts['normal'].render(text_str, True, (0, 0, 0))
        text_main = self.fonts['normal'].render(text_str, True, (255, 255, 255))
        
        text_rect = text_main.get_rect(center=(text_x, text_y))
        shadow_rect = text_shadow.get_rect(center=(text_x + 1, text_y + 1))
        
        screen.blit(text_shadow, shadow_rect)
        screen.blit(text_main, text_rect)


    def _draw_pointer(self):
        """Rysuje elegancką strzałkę wskazującą na górę koła"""
        center_x, center_y = self.wheel_center
        pointer_length = 25
        
        # Pozycja wskazówki (dokładnie na górze koła)
        pointer_x = center_x
        pointer_y = center_y - self.wheel_radius - pointer_length
        
        # Efekt trzęsienia pod koniec kręcenia
        if (self.animation['spinning'] and 
            pygame.time.get_ticks() > self.animation['spin_start_time'] + self.animation['spin_duration'] - 500):
            shake = random.randint(-2, 2)
            pointer_x += shake
        
        # Rysuj trójkątną strzałkę wskazującą w dół (na koło)
        pointer_points = [
            (pointer_x, pointer_y + pointer_length),  # Wierzchołek strzałki (wskazujący na koło)
            (pointer_x - 18, pointer_y - 5),          # Lewy róg podstawy
            (pointer_x + 18, pointer_y - 5)           # Prawy róg podstawy
        ]
        
        # Cień strzałki
        shadow_points = [(x + 2, y + 2) for x, y in pointer_points]
        pygame.draw.polygon(screen, self.colors['shadow'], shadow_points)
        
        # Główna strzałka
        pygame.draw.polygon(screen, self.colors['gold'], pointer_points)
        
        # Obramowanie
        pygame.draw.polygon(screen, self.colors['gold_dark'], pointer_points, 3)
        
        # Środkowy punkt mocowania
        pygame.draw.circle(screen, self.colors['gold_dark'], (pointer_x, pointer_y + pointer_length), 8)
        pygame.draw.circle(screen, self.colors['gold'], (pointer_x, pointer_y + pointer_length), 6)



    def _draw_instructions(self):
        """Rysuje panel instrukcji"""
        instr_rect = pygame.Rect(50, SCREEN_HEIGHT - 160, 300, 140)
        self._draw_panel(instr_rect)
        
        title = self.fonts['normal'].render("INSTRUKCJE", True, self.colors['gold'])
        screen.blit(title, (60, SCREEN_HEIGHT - 150))
        
        instructions = [
            "Kliknij KRĘĆ KOŁEM",
            "Można grać raz dziennie",
            "Nagrody: 1-100 monet",
            "Szczęśliwego kręcenia!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.fonts['small'].render(instruction, True, self.colors['text_white'])
            screen.blit(text, (60, SCREEN_HEIGHT - 115 + i * 22))

    def _draw_already_played_message(self):
        """Rysuje komunikat o już zagranej grze dzisiaj"""
        # Główny panel komunikatu
        message_rect = pygame.Rect(SCREEN_WIDTH//2 - 350, SCREEN_HEIGHT//2 - 200, 700, 400)
        self._draw_panel(message_rect)
        
        # Ikona zegara - większa i bardziej widoczna
        clock_center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100)
        pygame.draw.circle(screen, self.colors['gold'], clock_center, 40, 4)
        pygame.draw.line(screen, self.colors['gold'], clock_center, 
                        (clock_center[0] + 20, clock_center[1] - 15), 4)
        pygame.draw.line(screen, self.colors['gold'], clock_center, 
                        (clock_center[0] + 8, clock_center[1] - 25), 4)
        
        # Główny tytuł
        title = self.fonts['large'].render("Już dziś grałeś!", True, self.colors['gold'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
        screen.blit(title, title_rect)
        
        # Podtytuł
        subtitle = self.fonts['normal'].render("Wróć jutro po nową nagrodę!", True, self.colors['text_white'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
        screen.blit(subtitle, subtitle_rect)
        
        # Informacja o ograniczeniu
        info = self.fonts['small'].render("Każdy gracz może kręcić kołem tylko raz dziennie", True, self.colors['text_white'])
        info_rect = info.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(info, info_rect)
        
        # Informacja o następnej grze
        next_play_text = "Następna gra będzie dostępna jutro"
        next_play = self.fonts['small'].render(next_play_text, True, (180, 180, 180))
        next_play_rect = next_play.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        screen.blit(next_play, next_play_rect)
        
        # Dodatkowa informacja o statystykach
        total_plays = self._get_total_plays()
        if total_plays > 0:
            stats_text = f"Łączna liczba twoich gier: {total_plays}"
            stats = self.fonts['small'].render(stats_text, True, self.colors['gold'])
            stats_rect = stats.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 110))
            screen.blit(stats, stats_rect)
        
        # Informacja o dacie ostatniej gry
        last_play_info = self._get_last_play_info()
        if last_play_info:
            last_play_text = f"Ostatnia gra: {last_play_info}"
            last_play = self.fonts['small'].render(last_play_text, True, (150, 150, 150))
            last_play_rect = last_play.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 140))
            screen.blit(last_play, last_play_rect)

    def _get_last_play_info(self):
        """Pobiera informację o ostatniej grze"""
        save_file = os.path.join("DataBase", f"wheel_plays_{self.player.name}.json")
        
        if os.path.exists(save_file):
            try:
                with open(save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    date_str = data.get("last_play_date", "")
                    time_str = data.get("last_play_time", "")
                    if date_str and time_str:
                        return f"{date_str} o {time_str}"
                    elif date_str:
                        return date_str
            except:
                pass
        return None

    def _draw_player_info(self):
        """Rysuje informacje o graczu"""
        info_rect = pygame.Rect(SCREEN_WIDTH - 250, 80, 240, 120)
        self._draw_panel(info_rect)
        
        # Nazwa gracza
        player_text = self.fonts['normal'].render(f"Gracz: {self.player.name}", True, self.colors['gold'])
        screen.blit(player_text, (info_rect.x + 10, info_rect.y + 10))
        
        # Monety
        coins_text = self.fonts['normal'].render(f"Monety: {self.player.coins}", True, self.colors['text_white'])
        screen.blit(coins_text, (info_rect.x + 10, info_rect.y + 40))
        
        # Status gry dzisiaj
        if self.can_play_today:
            status_text = "Możesz dziś grać!"
            status_color = self.colors['green']
        else:
            status_text = "Już grałeś dziś"
            status_color = self.colors['red']
        
        status = self.fonts['small'].render(status_text, True, status_color)
        screen.blit(status, (info_rect.x + 10, info_rect.y + 70))
        
        # Łączna liczba gier
        total_plays = self._get_total_plays()
        total_text = self.fonts['small'].render(f"Łącznie gier: {total_plays}", True, self.colors['text_white'])
        screen.blit(total_text, (info_rect.x + 10, info_rect.y + 90))

    def _draw_buttons(self):
        """Rysuje przyciski"""
        # Przycisk kręcenia
        if self.can_play_today and self.game_state in ["waiting", "finished"]:
            button_text = "KRĘĆ KOŁEM"
            can_spin = self.game_state == "waiting" or self.game_state == "finished"
            
            if can_spin:
                self._draw_gradient_button(self.buttons['spin'], self.colors['green'], self.colors['green_light'])
                text_color = self.colors['text_white']
            else:
                self._draw_gradient_button(self.buttons['spin'], (80, 80, 80), (120, 120, 120))
                text_color = (150, 150, 150)
            
            spin_text = self.fonts['normal'].render(button_text, True, text_color)
            spin_rect = spin_text.get_rect(center=self.buttons['spin'].center)
            screen.blit(spin_text, spin_rect)
        elif not self.can_play_today:
            # Przycisk nieaktywny gdy już grał dziś
            self._draw_gradient_button(self.buttons['spin'], (60, 60, 60), (90, 90, 90))
            spin_text = self.fonts['normal'].render("JUTRO", True, (120, 120, 120))
            spin_rect = spin_text.get_rect(center=self.buttons['spin'].center)
            screen.blit(spin_text, spin_rect)
        
        # Przycisk wyjścia
        self._draw_gradient_button(self.buttons['exit'], self.colors['red'], self.colors['red_light'])
        exit_text = self.fonts['small'].render("WYJŚCIE", True, self.colors['text_white'])
        exit_rect = exit_text.get_rect(center=self.buttons['exit'].center)
        screen.blit(exit_text, exit_rect)

    def _draw_result(self):
        """Rysuje panel z wynikiem niżej na ekranie"""
        result_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 + 280, 500, 80)  # Przesunięte niżej
        
        # Różne kolory w zależności od wygranej
        if "JACKPOT" in self.result:
            self._draw_gradient_button(result_rect, self.colors['gold'], (255, 235, 100))
            text_color = self.colors['text_dark']
        else:
            self._draw_gradient_button(result_rect, self.colors['green'], self.colors['green_light'])
            text_color = self.colors['text_white']
        
        result_text = self.fonts['large'].render(self.result, True, text_color)
        text_rect = result_text.get_rect(center=result_rect.center)
        screen.blit(result_text, text_rect)

    def _draw_panel(self, rect):
        """Rysuje panel z tłem"""
        pygame.draw.rect(screen, self.colors['panel_bg'], rect, border_radius=8)
        pygame.draw.rect(screen, self.colors['panel_border'], rect, 2, border_radius=8)

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

    def _update_spin_animation(self, current_time):
        """Animacja obrotu z precyzyjnym zatrzymaniem"""
        elapsed = current_time - self.animation['spin_start_time']
        duration = self.animation['spin_duration']

        if elapsed < duration:
            # Ease-out dla płynnego zwalniania
            t = elapsed / duration
            eased = 1 - (1 - t) ** 3
            self.animation['angle'] = eased * self.animation['final_angle']
            
            # Lekkie drganie na końcu
            if t > 0.85:
                bounce_intensity = (1 - t) * 3
                bounce = math.sin((t - 0.85) * 40) * bounce_intensity
                self.animation['angle'] += bounce
        else:
            self.animation['spinning'] = False
            self.animation['angle'] = self.animation['final_angle']
            self._finish_spin()


    def _finish_spin(self):
        """Określa nagrodę z precyzyjnym wskazaniem"""
        # Kąt gdzie wskazuje pointer (góra = -π/2 radianów = 270°)
        pointer_direction = -math.pi / 2
        
        # Normalizuj kąt koła do zakresu 0-2π
        wheel_angle = math.radians(self.animation['angle']) % (2 * math.pi)
        
        # Oblicz rzeczywisty kąt segmentu względem pointera
        relative_angle = (pointer_direction - wheel_angle) % (2 * math.pi)
        
        # Przelicz na stopnie dla łatwiejszego debugowania
        relative_degrees = math.degrees(relative_angle)
        
        # Znajdź segment
        segment_index = int(relative_degrees / self.segment_angle) % self.num_segments
        selected_prize = self.prizes[segment_index]
        
        # Dodaj monety
        self.player.coins += selected_prize["coins"]
        self._save_daily_play()
        
        # Ustaw komunikat
        if selected_prize["coins"] == 100:
            self.result = f"JACKPOT! +{selected_prize['coins']} monet!"
        elif selected_prize["coins"] >= 50:
            self.result = f"SUPER! +{selected_prize['coins']} monet!"
        else:
            self.result = f"Wygrana: +{selected_prize['coins']} monet!"
        
        self.game_state = "finished"
        
        if hasattr(self.player, 'save_data'):
            self.player.save_data()
        

    def handle_event(self, event):
        """Obsługuje wydarzenia"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.in_game = False

    def _handle_mouse_click(self, pos):
        """Obsługuje kliknięcia myszy"""
        if self.buttons['exit'].collidepoint(pos):
            self.in_game = False
            return
        
        if (self.can_play_today and 
            self.buttons['spin'].collidepoint(pos) and 
            self.game_state == "waiting" and 
            not self.animation['spinning']):
            self.start_spin()

    def start_spin(self):
        """Rozpoczyna obrót z precyzyjnym targetowaniem"""
        self.game_state = "spinning"
        self.result = ""

        # Wybierz losowy segment
        target_segment = random.randint(0, self.num_segments - 1)
        self.animation['selected_prize'] = self.prizes[target_segment]

        # Oblicz kąt środka segmentu
        segment_center_degrees = target_segment * self.segment_angle + self.segment_angle / 2
        
        # Pointer wskazuje na górę (-90°), więc oblicz ile trzeba obrócić koło
        # żeby środek segmentu znalazł się pod pointerem
        target_angle = (270 - segment_center_degrees) % 360
        
        # Dodaj pełne obroty dla efektu wizualnego
        full_rotations = random.randint(8, 12)
        self.animation['final_angle'] = target_angle + 360 * full_rotations

        self.animation['spinning'] = True
        self.animation['spin_start_time'] = pygame.time.get_ticks()
        self.animation['spin_duration'] = 4000 + random.randint(0, 1000)


    def reset_game(self):
        """Resetuje grę"""
        self.can_play_today = self._check_daily_availability()
        self.game_state = "waiting"
        self.result = ""
        self.animation['spinning'] = False
        self.animation['angle'] = 0
        self.in_game = True  # ważne – gracz wchodzi w grę nawet jeśli już grał
