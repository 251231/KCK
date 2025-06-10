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
        self.fee_input_active = False
        self.fee_message = ""
        self.fee_message_timer = 0
        self.total_burned_coins = 0  # Łączna liczba spalonych monet
        
        # Kolory i fonty
        self.input_color = pygame.Color('dodgerblue2')
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')

    def handle_fee_interaction(self, player):
        """Obsługuje interakcję ze strefą wpłat"""
        if not self.fee_interface_active:
            self.fee_interface_active = True
            self.fee_input = ""
            self.fee_message = ""
            self.fee_message_timer = 0
    
    def handle_fee_event(self, event, player):
        """Obsługuje wydarzenia w interfejsie wpłat"""
        if not self.fee_interface_active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.fee_interface_active = False
                self.fee_input = ""
                return True
            elif event.key == pygame.K_RETURN:
                self.process_fee_payment(player)
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.fee_input = self.fee_input[:-1]
                return True
            else:
                # Akceptuj tylko cyfry
                if event.unicode.isdigit():
                    self.fee_input += event.unicode
                return True
        return False
    
    def process_fee_payment(self, player):
        """Przetwarza wpłatę monet"""
        if not self.fee_input:
            self.fee_message = "Wprowadź kwotę!"
            self.fee_message_timer = 3.0
            return
        
        try:
            amount = int(self.fee_input)
            
            if amount <= 0:
                self.fee_message = "Kwota musi być większa od zera!"
                self.fee_message_timer = 3.0
                return
            
            if amount > player.coins:
                self.fee_message = f"Nie masz wystarczająco monet! Masz: {player.coins}"
                self.fee_message_timer = 3.0
                return
            
            # Wykonaj wpłatę (burnowanie monet)
            player.coins -= amount
            self.total_burned_coins += amount
            player.save_data()  # Zapisz dane gracza
            
            self.fee_message = f"Wpłacono {amount} monet!"
            self.fee_message_timer = 3.0
            self.fee_input = ""
            
        except ValueError:
            self.fee_message = "Nieprawidłowa kwota!"
            self.fee_message_timer = 3.0

    def update(self, game, delta_time):
        """Aktualizuje stan pokoju"""
        # Aktualizuj timer wiadomości
        if self.fee_message_timer > 0:
            self.fee_message_timer -= delta_time
            if self.fee_message_timer <= 0:
                self.fee_message = ""

    def draw(self, screen, camera_x, camera_y):
        """Rysuje pokój wraz z interfejsem wpłat"""
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
            
            # Rysuj strefę wpłat
            pygame.draw.rect(screen, (255, 215, 0), fee_zone_screen)  # Złoty kolor
            pygame.draw.rect(screen, (255, 140, 0), fee_zone_screen, 3)  # Ciemniejsza ramka
            
            # Ikona monety
            pygame.draw.circle(screen, (255, 255, 0), fee_zone_screen.center, 25)
            pygame.draw.circle(screen, (255, 140, 0), fee_zone_screen.center, 25, 3)
            
            # Tekst "OPŁATY"
            fee_text = font.render("OPŁATY", True, (139, 69, 19))
            text_rect = fee_text.get_rect(center=(fee_zone_screen.centerx, fee_zone_screen.bottom + 15))
            screen.blit(fee_text, text_rect)
            
        
        # Rysuj interfejs wpłat jeśli jest aktywny
        if self.fee_interface_active:
            self.draw_fee_interface(screen)

    def draw_fee_interface(self, screen):
        """Rysuje interfejs wpłacania monet"""
        # Tło interfejsu
        interface_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(screen, (50, 50, 50), interface_rect)
        pygame.draw.rect(screen, (255, 255, 255), interface_rect, 3)
        
        # Tytuł
        title_text = font.render("WPŁATA MONET", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(interface_rect.centerx, interface_rect.y + 30))
        screen.blit(title_text, title_rect)
        
        # Informacja o aktualnej liczbie monet
        from Game import Game  # Import tutaj żeby uniknąć circular import
        player = pygame.key.get_pressed()  # Hack - potrzebujemy dostępu do gracza
        
        # Pole input
        input_rect = pygame.Rect(interface_rect.x + 50, interface_rect.y + 100, 300, 40)
        color = self.color_active if self.fee_input_active else self.color_inactive
        pygame.draw.rect(screen, color, input_rect, 2)
        
        # Tekst w polu input
        input_text = font.render(self.fee_input, True, (255, 255, 255))
        screen.blit(input_text, (input_rect.x + 5, input_rect.y + 10))
        
        # Etykieta
        label_text = font.render("Kwota do wpłaty:", True, (255, 255, 255))
        screen.blit(label_text, (input_rect.x, input_rect.y - 25))
        
        # Instrukcje
        instruction1 = font.render("ENTER - Potwierdź wpłatę", True, (200, 200, 200))
        instruction2 = font.render("ESC - Anuluj", True, (200, 200, 200))
        screen.blit(instruction1, (interface_rect.x + 20, interface_rect.y + 180))
        screen.blit(instruction2, (interface_rect.x + 20, interface_rect.y + 210))
        
        # Ostrzeżenie
        warning_text = font.render("UWAGA: Monet nie można odzyskać!", True, (255, 100, 100))
        warning_rect = warning_text.get_rect(center=(interface_rect.centerx, interface_rect.y + 250))
        screen.blit(warning_text, warning_rect)
        
        # Wiadomość zwrotna
        if self.fee_message:
            message_color = (100, 255, 100) if "Wpłacono" in self.fee_message else (255, 100, 100)
            message_text = font.render(self.fee_message, True, message_color)
            message_rect = message_text.get_rect(center=(interface_rect.centerx, interface_rect.y + 270))
            screen.blit(message_text, message_rect)

    def check_fee_interaction(self, player):
        """Sprawdza czy gracz może wejść w interakcję ze strefą wpłat"""
        return player.rect.colliderect(self.fee_zone.inflate(50, 50))