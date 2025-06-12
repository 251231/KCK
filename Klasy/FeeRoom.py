from Room import Room
from NPC import *
import pygame
from config import *

class FeeRoom(Room):
    def __init__(self):
        super().__init__(
            bg_path="assets/FeeRoom.png",
            collision_path="assets/FeeRoom_kolizje.png",
            npcs=[NPC(300, 400)],
            teleport_zones={
                (255, 255, 0): ("MainRoom", "from_fee"),  
            },
            entry_points={
                "default": (100, 100),
                "from_main": (1345, 600),    # Gdzie gracz pojawia się przychodząc z MainRoom
            }
        )
        
        # Strefa wpłat monet
        self.fee_zone = pygame.Rect(500, 300, 80, 80)
        self.fee_interface_active = False
        self.fee_input = ""
        self.fee_input_active = True  # Zawsze aktywne gdy interfejs jest otwarty
        self.fee_message = ""
        self.fee_message_timer = 0
        self.total_burned_coins = 0  # Łączna liczba spalonych monet
        
        # Kolory i fonty
        self.input_color = pygame.Color('dodgerblue2')
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        
        # Przyciski interfejsu
        self.confirm_button = None
        self.cancel_button = None
        self.current_player = None  # Referencja do gracza
        
    def init_interface_buttons(self):
        """Inicjalizuje przyciski interfejsu"""
        interface_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
        
        # Przycisk potwierdzenia
        self.confirm_button = pygame.Rect(
            interface_rect.x + 50, 
            interface_rect.y + 180, 
            120, 40
        )
        
        # Przycisk anulowania
        self.cancel_button = pygame.Rect(
            interface_rect.x + 230, 
            interface_rect.y + 180, 
            120, 40
        )

    def handle_fee_interaction(self, player):
        """Obsługuje interakcję ze strefą wypłat"""
        if not self.fee_interface_active:
            self.fee_interface_active = True
            self.fee_input = ""
            self.fee_message = ""
            self.fee_message_timer = 0
            self.current_player = player
            self.init_interface_buttons()
    
    def handle_fee_event(self, event, player):
        """Obsługuje wydarzenia w interfejsie wypłat"""
        if not self.fee_interface_active:
            return False
            
        # Obsługa myszy
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.confirm_button and self.confirm_button.collidepoint(event.pos):
                self.process_fee_payment(player)
                return True
            elif self.cancel_button and self.cancel_button.collidepoint(event.pos):
                self.close_fee_interface()
                return True
                
        # Obsługa klawiatury
        if event.type == pygame.KEYDOWN:
            # ESC zamyka interfejs (ale nie pauzuje gry)
            if event.key == pygame.K_ESCAPE:
                self.close_fee_interface()
                return True
            elif event.key == pygame.K_RETURN:
                self.process_fee_payment(player)
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.fee_input = self.fee_input[:-1]
                return True
            else:
                # Akceptuj tylko cyfry (maksymalnie 8 cyfr)
                if event.unicode.isdigit() and len(self.fee_input) < 8:
                    self.fee_input += event.unicode
                return True
        return False
    
    def close_fee_interface(self):
        """Zamyka interfejs wypłat"""
        self.fee_interface_active = False
        self.fee_input = ""
        self.fee_message = ""
        self.fee_message_timer = 0
        self.current_player = None
    
    def process_fee_payment(self, player):
        """Przetwarza wypłatę monet"""
        if not self.fee_input:
            self.show_message("Wprowadź kwotę!", "error")
            return
        
        try:
            amount = int(self.fee_input)
            
            if amount <= 0:
                self.show_message("Kwota musi być większa od zera!", "error")
                return
            
            if amount > player.coins:
                self.show_message(f"Nie masz wystarczająco monet! Masz: {player.coins}", "error")
                return
            
            # Wykonaj wypłatę (burnowanie monet)
            player.coins -= amount
            self.total_burned_coins += amount
            player.save_data()  # Zapisz dane gracza
            
            self.show_message(f"Wypłacono {amount} monet!", "success")
            self.fee_input = ""
            
        except ValueError:
            self.show_message("Nieprawidłowa kwota!", "error")
    
    def show_message(self, message, message_type):
        """Pokazuje wiadomość z odpowiednim czasem wyświetlania"""
        self.fee_message = message
        self.fee_message_timer = 3.0 if message_type == "error" else 2.0

    def update(self, game, delta_time):
        """Aktualizuje stan pokoju"""
        # Aktualizuj timer wiadomości
        if self.fee_message_timer > 0:
            self.fee_message_timer -= delta_time
            if self.fee_message_timer <= 0:
                self.fee_message = ""

    def draw(self, screen, camera_x, camera_y):
        """Rysuje pokój wraz z interfejsem wypłat"""
        # Rysuj podstawowy pokój
        super().draw(screen, camera_x, camera_y)
        
        # Rysuj strefę wpłat
        fee_zone_screen = pygame.Rect(
            self.fee_zone.x - camera_x,
            self.fee_zone.y - camera_y,
            self.fee_zone.width,
            self.fee_zone.height
        )
        
        # Sprawdź czy strefa jest widoczna na ekranie
        if (fee_zone_screen.x > -self.fee_zone.width and fee_zone_screen.x < SCREEN_WIDTH and
            fee_zone_screen.y > -self.fee_zone.height and fee_zone_screen.y < SCREEN_HEIGHT):
            
            # Rysuj strefę wpłat z animacją
            pulse = abs(pygame.time.get_ticks() % 2000 - 1000) / 1000.0
            glow_color = (255, int(215 + 40 * pulse), int(40 * pulse))
            
            # Efekt świecenia
            glow_surface = pygame.Surface((fee_zone_screen.width + 20, fee_zone_screen.height + 20))
            glow_surface.set_alpha(100)
            glow_surface.fill(glow_color)
            screen.blit(glow_surface, (fee_zone_screen.x - 10, fee_zone_screen.y - 10))
            
            # Główna strefa
            pygame.draw.rect(screen, (255, 215, 0), fee_zone_screen)  # Złoty kolor
            pygame.draw.rect(screen, (255, 140, 0), fee_zone_screen, 3)  # Ciemniejsza ramka
            
            # Ikona monety
            pygame.draw.circle(screen, (255, 255, 0), fee_zone_screen.center, 25)
            pygame.draw.circle(screen, (255, 140, 0), fee_zone_screen.center, 25, 3)
            
            # Symbol $ w środku
            dollar_text = font.render("$", True, (139, 69, 19))
            dollar_rect = dollar_text.get_rect(center=fee_zone_screen.center)
            screen.blit(dollar_text, dollar_rect)
            
            # Tekst "OPŁATY"
            fee_text = font.render("OPŁATY", True, (139, 69, 19))
            text_rect = fee_text.get_rect(center=(fee_zone_screen.centerx, fee_zone_screen.bottom + 15))
            screen.blit(fee_text, text_rect)
        
        # Rysuj interfejs wpłat jeśli jest aktywny
        if self.fee_interface_active:
            self.draw_fee_interface(screen)

    def draw_fee_interface(self, screen):
        """Rysuje interfejs wypłacania monet"""
        # Półprzezroczyste tło
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Główne okno interfejsu
        interface_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
        
        # Gradient tła
        bg_surface = pygame.Surface((interface_rect.width, interface_rect.height))
        for y in range(interface_rect.height):
            progress = y / interface_rect.height
            color_r = int(40 + progress * 20)
            color_g = int(50 + progress * 20)
            color_b = int(80 + progress * 20)
            pygame.draw.line(bg_surface, (color_r, color_g, color_b), (0, y), (interface_rect.width, y))
        
        screen.blit(bg_surface, interface_rect.topleft)
        
        # Ramka okna
        pygame.draw.rect(screen, (255, 215, 0), interface_rect, 4)
        pygame.draw.rect(screen, (139, 69, 19), interface_rect, 2)
        
        # Tytuł
        title_text = font.render("WYPŁATA MONET", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(interface_rect.centerx, interface_rect.y + 30))
        screen.blit(title_text, title_rect)
        
        # Informacja o aktualnej liczbie monet gracza
        if self.current_player:
            coins_info = font.render(f"Twoje monety: {self.current_player.coins}", True, (255, 255, 255))
            coins_rect = coins_info.get_rect(center=(interface_rect.centerx, interface_rect.y + 60))
            screen.blit(coins_info, coins_rect)
        
        # Etykieta pola input
        label_text = font.render("Kwota do wpłaty:", True, (255, 255, 255))
        screen.blit(label_text, (interface_rect.x + 50, interface_rect.y + 90))
        
        # Pole input
        input_rect = pygame.Rect(interface_rect.x + 50, interface_rect.y + 115, 300, 35)
        input_color = self.color_active if self.fee_input_active else self.color_inactive
        pygame.draw.rect(screen, (30, 30, 30), input_rect)
        pygame.draw.rect(screen, input_color, input_rect, 2)
        
        # Tekst w polu input
        display_text = self.fee_input if self.fee_input else "0"
        input_text = font.render(display_text, True, (255, 255, 255))
        text_rect = input_text.get_rect(centery=input_rect.centery, x=input_rect.x + 10)
        screen.blit(input_text, text_rect)
        
        # Kursor
        if self.fee_input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_rect.right + 2
            pygame.draw.line(screen, (255, 255, 255), 
                           (cursor_x, input_rect.y + 5), 
                           (cursor_x, input_rect.bottom - 5), 2)
        
        # Przyciski
        mouse_pos = pygame.mouse.get_pos()
        
        # Przycisk potwierdzenia
        confirm_hovered = self.confirm_button.collidepoint(mouse_pos)
        confirm_color = (100, 200, 100) if not confirm_hovered else (120, 255, 120)
        pygame.draw.rect(screen, confirm_color, self.confirm_button)
        pygame.draw.rect(screen, (255, 255, 255), self.confirm_button, 2)
        
        confirm_text = font.render("WPŁAĆ", True, (255, 255, 255))
        confirm_text_rect = confirm_text.get_rect(center=self.confirm_button.center)
        screen.blit(confirm_text, confirm_text_rect)
        
        # Przycisk anulowania
        cancel_hovered = self.cancel_button.collidepoint(mouse_pos)
        cancel_color = (200, 100, 100) if not cancel_hovered else (255, 120, 120)
        pygame.draw.rect(screen, cancel_color, self.cancel_button)
        pygame.draw.rect(screen, (255, 255, 255), self.cancel_button, 2)
        
        cancel_text = font.render("ANULUJ", True, (255, 255, 255))
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_button.center)
        screen.blit(cancel_text, cancel_text_rect)
        
        # Instrukcje
        instructions = [
            "ENTER - Potwierdź wpłatę",
            "ESC - Anuluj",
            "Cyfry - Wprowadź kwotę"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_text = pygame.font.Font(None, 20).render(instruction, True, (200, 200, 200))
            screen.blit(instruction_text, (interface_rect.x + 20, interface_rect.y + 240 + i * 15))
        
        # Ostrzeżenie
        warning_text = font.render("UWAGA: Monet nie można odzyskać!", True, (255, 100, 100))
        warning_rect = warning_text.get_rect(center=(interface_rect.centerx, interface_rect.bottom - 50))
        screen.blit(warning_text, warning_rect)
        
        # Statystyki (opcjonalnie)
        if self.total_burned_coins > 0:
            stats_text = pygame.font.Font(None, 18).render(
                f"Łącznie wypłacono: {self.total_burned_coins} monet", 
                True, (150, 150, 150)
            )
            stats_rect = stats_text.get_rect(center=(interface_rect.centerx, interface_rect.bottom - 30))
            screen.blit(stats_text, stats_rect)
        
        # Wiadomość zwrotna
        if self.fee_message:
            message_color = (100, 255, 100) if "Wpłacono" in self.fee_message else (255, 100, 100)
            message_bg = pygame.Rect(interface_rect.x + 20, interface_rect.bottom - 15, 
                                   interface_rect.width - 40, 25)
            pygame.draw.rect(screen, (0, 0, 0, 180), message_bg)
            pygame.draw.rect(screen, message_color, message_bg, 1)
            
            message_text = font.render(self.fee_message, True, message_color)
            message_rect = message_text.get_rect(center=message_bg.center)
            screen.blit(message_text, message_rect)

    def check_fee_interaction(self, player):
        """Sprawdza czy gracz może wejść w interakcję ze strefą wpłat"""
        return player.rect.colliderect(self.fee_zone.inflate(50, 50))