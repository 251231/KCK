import pygame
import random
import math
from config import *

class DiceGame:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 54)
        self.bet_amount = 1
        self.max_bets = 3
        self.result = ""
        self.rolling = False
        
        # Próbujemy załadować obrazki kostek, jeśli nie ma to tworzymy prostokąty
        self.dice_imgs = []
        try:
            self.dice_imgs = [pygame.image.load(f"assets/dice{i}.png") for i in range(1, 7)]
            # Skalujemy obrazki do odpowiedniego rozmiaru
            self.dice_imgs = [pygame.transform.scale(img, (80, 80)) for img in self.dice_imgs]
        except:
            # Jeśli nie ma obrazków, używamy prostokątów z numerami
            self.dice_imgs = None
            
        self.dice1 = random.randint(1, 6)
        self.dice2 = random.randint(1, 6)
        self.display_dice1 = self.dice1
        self.display_dice2 = self.dice2
        
        self.choices = ["Mniej niż 7", "Więcej niż 7"] + [str(i) for i in range(2, 13)]
        self.selected_bets = []
        self.roll_start_time = 0
        self.animation_duration = 2000  # 2 sekundy animacji
        self.button_rects = []
        
        # Lepsze rozmiary przycisków i pozycjonowanie
        self.roll_button = pygame.Rect(SCREEN_WIDTH//2 - 70, 320, 140, 45)
        self.exit_button = pygame.Rect(SCREEN_WIDTH - 110, 10, 95, 35)
        self.bet_up_button = pygame.Rect(250, SCREEN_HEIGHT - 300, 35, 30)
        self.bet_down_button = pygame.Rect(290, SCREEN_HEIGHT - 300, 35, 30)
        self.in_game = True
        
        # Animacja kostek
        self.dice1_angle = 0
        self.dice2_angle = 0
        self.dice1_scale = 1.0
        self.dice2_scale = 1.0
        self.animation_time = 0
        self.last_dice_change = 0
        self.dice_change_interval = 100  # Zmiana co 100ms podczas animacji

    def draw(self):
        # Tło gry z gradientem
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            color_intensity = int(45 + (y / SCREEN_HEIGHT) * 25)
            pygame.draw.line(overlay, (color_intensity, color_intensity, color_intensity + 15), (0, y), (SCREEN_WIDTH, y))
        overlay.set_alpha(240)
        screen.blit(overlay, (0, 0))
        
        # Tytuł gry z cieniem - lepsze pozycjonowanie
        title_shadow = self.title_font.render("GRA W KOŚCI", True, (20, 20, 20))
        title = self.title_font.render("GRA W KOŚCI", True, (255, 215, 0))
        title_x = SCREEN_WIDTH//2 - title.get_width()//2
        screen.blit(title_shadow, (title_x + 2, 22))
        screen.blit(title, (title_x, 20))

        # Animacja kostek z lepszym pozycjonowaniem
        current_time = pygame.time.get_ticks()
        
        if self.rolling:
            self.animation_time = current_time - self.roll_start_time
            progress = min(self.animation_time / self.animation_duration, 1.0)
            
            # Zmiana oczek podczas animacji
            if current_time - self.last_dice_change > self.dice_change_interval and progress < 0.9:
                self.display_dice1 = random.randint(1, 6)
                self.display_dice2 = random.randint(1, 6)
                self.last_dice_change = current_time
            elif progress >= 0.9:
                # Pod koniec animacji pokaż prawdziwy wynik
                self.display_dice1 = self.dice1
                self.display_dice2 = self.dice2
            
            # Animacja obrotu i skalowania - bardziej delikatna
            rotation_speed = max(10 - progress * 8, 1)  # Zwalnianie obrotu
            self.dice1_angle += rotation_speed
            self.dice2_angle += rotation_speed * 1.3
            
            scale_factor = 1.0 + 0.2 * math.sin(progress * math.pi * 4) * (1 - progress)
            self.dice1_scale = scale_factor
            self.dice2_scale = scale_factor
        else:
            # Bardzo delikatne animacje gdy nie ma rzutu
            self.dice1_angle += 0.3
            self.dice2_angle += 0.2
            self.dice1_scale = 1.0 + 0.03 * math.sin(current_time * 0.001)
            self.dice2_scale = 1.0 + 0.03 * math.cos(current_time * 0.0015)

        # Rysuj kości z lepszym pozycjonowaniem
        dice_y = 120
        dice_spacing = 140
        dice_x = SCREEN_WIDTH // 2 - dice_spacing // 2
        
        if self.dice_imgs:
            # Animowane obrazki kostek
            dice1_img = pygame.transform.rotozoom(self.dice_imgs[self.display_dice1 - 1], self.dice1_angle, self.dice1_scale)
            dice2_img = pygame.transform.rotozoom(self.dice_imgs[self.display_dice2 - 1], self.dice2_angle, self.dice2_scale)
            
            dice1_rect = dice1_img.get_rect(center=(dice_x, dice_y + 40))
            dice2_rect = dice2_img.get_rect(center=(dice_x + dice_spacing, dice_y + 40))
            
            screen.blit(dice1_img, dice1_rect)
            screen.blit(dice2_img, dice2_rect)
        else:
            # Animowane prostokąty z numerami - lepsze rozmiary
            base_size = 80
            dice1_size = int(base_size * max(self.dice1_scale, 0.6))
            dice2_size = int(base_size * max(self.dice2_scale, 0.6))
            
            dice1_rect = pygame.Rect(dice_x - dice1_size//2, dice_y + 40 - dice1_size//2, dice1_size, dice1_size)
            dice2_rect = pygame.Rect(dice_x + dice_spacing - dice2_size//2, dice_y + 40 - dice2_size//2, dice2_size, dice2_size)
            
            # Cienie kostek - proporcjonalne
            shadow_offset = 3
            shadow1 = pygame.Rect(dice1_rect.x + shadow_offset, dice1_rect.y + shadow_offset, dice1_size, dice1_size)
            shadow2 = pygame.Rect(dice2_rect.x + shadow_offset, dice2_rect.y + shadow_offset, dice2_size, dice2_size)
            pygame.draw.rect(screen, (20, 20, 20), shadow1, border_radius=8)
            pygame.draw.rect(screen, (20, 20, 20), shadow2, border_radius=8)
            
            # Główne kostki z subtelnym obramowaniem
            pygame.draw.rect(screen, WHITE, dice1_rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, dice2_rect, border_radius=8)
            pygame.draw.rect(screen, (160, 160, 160), dice1_rect, 1, border_radius=8)
            pygame.draw.rect(screen, (160, 160, 160), dice2_rect, 1, border_radius=8)
            
            # Numery na kostkach - proporcjonalne do rozmiaru
            dice_font_size = max(int(36 * self.dice1_scale), 20)
            dice_font = pygame.font.Font(None, dice_font_size)
            dice1_text = dice_font.render(str(self.display_dice1), True, BLACK)
            dice2_text = dice_font.render(str(self.display_dice2), True, BLACK)
            
            dice1_text_rect = dice1_text.get_rect(center=dice1_rect.center)
            dice2_text_rect = dice2_text.get_rect(center=dice2_rect.center)
            
            screen.blit(dice1_text, dice1_text_rect)
            screen.blit(dice2_text, dice2_text_rect)

        # Suma kostek z efektem - lepsze pozycjonowanie
        total = self.display_dice1 + self.display_dice2
        total_text = self.large_font.render(f"Suma: {total}", True, (255, 215, 0))
        total_shadow = self.large_font.render(f"Suma: {total}", True, (40, 40, 40))
        total_rect = total_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(total_shadow, (total_rect.x + 2, total_rect.y + 2))
        screen.blit(total_text, total_rect)

        # Przycisk losowania z gradientem - elegancki bez grubego konturu
        color = (50, 180, 50) if not self.rolling and self.selected_bets else (80, 80, 80)
        end_color = (min(color[0] + 40, 255), min(color[1] + 40, 255), min(color[2] + 40, 255))
        self.draw_gradient_button(self.roll_button, color, end_color)
        pygame.draw.rect(screen, (max(color[0] - 20, 0), max(color[1] - 20, 0), max(color[2] - 20, 0)), self.roll_button, 1, border_radius=6)
        roll_text = self.font.render("LOSUJ KOŚCI", True, WHITE)
        roll_rect = roll_text.get_rect(center=self.roll_button.center)
        screen.blit(roll_text, roll_rect)

        # Kontrola stawki z lepszym designem - subtelne obramowanie
        bet_bg = pygame.Rect(40, SCREEN_HEIGHT - 320, 300, 50)
        pygame.draw.rect(screen, (35, 35, 55), bet_bg, border_radius=8)
        pygame.draw.rect(screen, (70, 70, 110), bet_bg, 1, border_radius=8)
        
        bet_text = self.font.render(f"Stawka: {self.bet_amount} monet", True, WHITE)
        screen.blit(bet_text, (55, SCREEN_HEIGHT - 310))
        
        # Przyciski stawki z gradientem - eleganckie bez grubych konturów
        self.draw_gradient_button(self.bet_up_button, (40, 130, 40), (80, 170, 80))
        self.draw_gradient_button(self.bet_down_button, (130, 40, 40), (170, 80, 80))
        pygame.draw.rect(screen, (20, 100, 20), self.bet_up_button, 1, border_radius=4)
        pygame.draw.rect(screen, (100, 20, 20), self.bet_down_button, 1, border_radius=4)
        
        up_text = self.font.render("+", True, WHITE)
        down_text = self.font.render("−", True, WHITE)
        up_rect = up_text.get_rect(center=self.bet_up_button.center)
        down_rect = down_text.get_rect(center=self.bet_down_button.center)
        screen.blit(up_text, up_rect)
        screen.blit(down_text, down_rect)

        # Opcje zakładów - dopasowane rozmiary bez brzydkich obrysów
        self.button_rects = []
        start_x = 40
        y1 = SCREEN_HEIGHT - 220  # Pierwszy rząd
        y2 = SCREEN_HEIGHT - 175  # Drugi rząd
        
        # Pierwszy rząd - opcje "mniej/więcej niż 7" - bez grubych obramowań
        for i, choice in enumerate(self.choices[:2]):
            rect = pygame.Rect(start_x + i * 170, y1, 160, 35)
            
            if choice in self.selected_bets:
                # Wybrane - złoty gradient z delikatnym cieniem
                self.draw_gradient_button(rect, (255, 215, 0), (255, 235, 50))
                pygame.draw.rect(screen, (200, 180, 0), rect, 1, border_radius=6)
                text_color = BLACK
            else:
                # Niewybrane - niebieski gradient z delikatnym cieniem
                self.draw_gradient_button(rect, (60, 120, 160), (80, 140, 180))
                pygame.draw.rect(screen, (40, 100, 140), rect, 1, border_radius=6)
                text_color = WHITE
            
            text = self.small_font.render(choice, True, text_color)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
            self.button_rects.append((rect, choice))

        # Drugi rząd - konkretne liczby - bez grubych obramowań
        for i, choice in enumerate(self.choices[2:]):
            x = start_x + (i % 11) * 65
            y = y2 if i < 11 else y2 + 40
            rect = pygame.Rect(x, y, 60, 35)
            
            if choice in self.selected_bets:
                # Wybrane - złoty gradient
                self.draw_gradient_button(rect, (255, 215, 0), (255, 235, 50))
                pygame.draw.rect(screen, (200, 180, 0), rect, 1, border_radius=6)
                text_color = BLACK
            else:
                # Niewybrane - niebieski gradient
                self.draw_gradient_button(rect, (60, 120, 160), (80, 140, 180))
                pygame.draw.rect(screen, (40, 100, 140), rect, 1, border_radius=6)
                text_color = WHITE
            
            text = self.font.render(choice, True, text_color)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
            self.button_rects.append((rect, choice))

        # Panel informacyjny - subtelne obramowanie
        info_bg = pygame.Rect(40, SCREEN_HEIGHT - 120, SCREEN_WIDTH - 80, 70)
        pygame.draw.rect(screen, (35, 35, 55), info_bg, border_radius=8)
        pygame.draw.rect(screen, (70, 70, 110), info_bg, 1, border_radius=8)

        # Informacje o zakładach
        selected_text = self.font.render(f"Wybrane zakłady ({len(self.selected_bets)}/{self.max_bets}):", True, WHITE)
        screen.blit(selected_text, (55, SCREEN_HEIGHT - 110))
        
        if self.selected_bets:
            bets_str = ", ".join(self.selected_bets)
            if len(bets_str) > 50:  # Skróć długie napisy
                bets_str = bets_str[:47] + "..."
            bets_text = self.small_font.render(bets_str, True, (255, 215, 0))
            screen.blit(bets_text, (55, SCREEN_HEIGHT - 90))

        # Koszt całkowity i monety gracza
        total_cost = self.bet_amount * len(self.selected_bets)
        cost_text = self.small_font.render(f"Koszt: {total_cost} | Twoje monety: {self.player.coins}", True, (150, 255, 150))
        screen.blit(cost_text, (55, SCREEN_HEIGHT - 65))

        # Wynik z efektem - lepsze pozycjonowanie
        if self.result:
            result_color = (255, 100, 100) if "Przegrana" in self.result else (100, 255, 100)
            result_shadow = self.font.render(self.result, True, (20, 20, 20))
            result_text = self.font.render(self.result, True, result_color)
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, 290))
            screen.blit(result_shadow, (result_rect.x + 1, result_rect.y + 1))
            screen.blit(result_text, result_rect)

        # Przycisk wyjścia - elegancki bez grubego konturu
        self.draw_gradient_button(self.exit_button, (130, 40, 40), (170, 80, 80))
        pygame.draw.rect(screen, (100, 20, 20), self.exit_button, 1, border_radius=6)
        exit_text = self.small_font.render("WYJŚCIE", True, WHITE)
        exit_rect = exit_text.get_rect(center=self.exit_button.center)
        screen.blit(exit_text, exit_rect)

        # Instrukcje w ładnym panelu - subtelne obramowanie
        instr_bg = pygame.Rect(SCREEN_WIDTH - 280, 50, 260, 100)
        pygame.draw.rect(screen, (35, 35, 55, 200), instr_bg, border_radius=8)
        pygame.draw.rect(screen, (70, 70, 110), instr_bg, 1, border_radius=8)
        
        instructions = [
            "• Kliknij opcje aby wybrać zakłady",
            "• Ustaw stawkę przyciskami +/−",
            "• Kliknij LOSUJ KOŚCI aby grać",
            "• ESC lub SPACE - szybkie akcje"
        ]
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH - 270, 65 + i * 22))

    def draw_gradient_button(self, rect, color1, color2):
        """Rysuje przycisk z gradientem"""
        for y in range(rect.height):
            blend = y / rect.height
            r = int(color1[0] * (1 - blend) + color2[0] * blend)
            g = int(color1[1] * (1 - blend) + color2[1] * blend)
            b = int(color1[2] * (1 - blend) + color2[2] * blend)
            pygame.draw.line(screen, (r, g, b), 
                           (rect.x, rect.y + y), 
                           (rect.x + rect.width, rect.y + y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Przycisk wyjścia
            if self.exit_button.collidepoint(event.pos):
                self.in_game = False
                return
                
            # Przycisk losowania
            if self.roll_button.collidepoint(event.pos):
                self.roll_dice()
                return
                
            # Przyciski stawki
            if self.bet_up_button.collidepoint(event.pos):
                self.bet_amount += 1
                return
            if self.bet_down_button.collidepoint(event.pos) and self.bet_amount > 1:
                self.bet_amount -= 1
                return
                
            # Opcje zakładów
            for rect, choice in self.button_rects:
                if rect.collidepoint(event.pos):
                    if choice in self.selected_bets:
                        self.selected_bets.remove(choice)
                    elif len(self.selected_bets) < self.max_bets:
                        self.selected_bets.append(choice)
                    return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.in_game = False
            elif event.key == pygame.K_UP:
                self.bet_amount += 1
            elif event.key == pygame.K_DOWN and self.bet_amount > 1:
                self.bet_amount -= 1
            elif event.key == pygame.K_SPACE:
                self.roll_dice()
                
        # Obsługa animacji losowania
        elif event.type == pygame.USEREVENT + 1 and self.rolling:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            self.resolve_bet()

    def roll_dice(self):
        if not self.selected_bets or self.rolling:
            if not self.selected_bets:
                self.result = "Najpierw wybierz zakłady!"
            return

        total_bet = self.bet_amount * len(self.selected_bets)
        if self.player.coins < total_bet:
            self.result = "Za mało monet!"
            return

        self.player.coins -= total_bet
        self.rolling = True
        self.result = "Losowanie..."
        self.roll_start_time = pygame.time.get_ticks()
        self.last_dice_change = self.roll_start_time
        pygame.time.set_timer(pygame.USEREVENT + 1, self.animation_duration)

        # Ustaw finalne wartości kostek
        self.dice1 = random.randint(1, 6)
        self.dice2 = random.randint(1, 6)

    def resolve_bet(self):
        total = self.dice1 + self.dice2
        wins = []
        
        # Sprawdź które zakłady wygrały
        for bet in self.selected_bets:
            if bet == "Mniej niż 7" and total < 7:
                wins.append(bet)
            elif bet == "Więcej niż 7" and total > 7:
                wins.append(bet)
            elif bet == str(total):
                wins.append(bet)

        if wins:
            # Różne wypłaty dla różnych typów zakładów
            winnings = 0
            for win_bet in wins:
                if win_bet in ["Mniej niż 7", "Więcej niż 7"]:
                    winnings += self.bet_amount * 2  # 2:1 dla zakładów mniej/więcej
                else:
                    winnings += self.bet_amount * 6  # 6:1 dla konkretnej liczby
            
            self.player.coins += winnings
            self.result = f"Suma: {total} - Wygrana! +{winnings} monet"
        else:
            self.result = f"Suma: {total} - Przegrana!"

        self.selected_bets = []
        self.rolling = False
        self.player.save_data()

    def reset_game(self):
        """Reset gry do stanu początkowego"""
        self.dice1 = random.randint(1, 6)
        self.dice2 = random.randint(1, 6)
        self.display_dice1 = self.dice1
        self.display_dice2 = self.dice2
        self.selected_bets = []
        self.result = ""
        self.rolling = False
        self.bet_amount = 1
        self.in_game = True