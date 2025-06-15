import pygame
from config import *

class CoffeeMachine:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 120
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Właściwości automatu
        self.coffee_price = 25
        self.speed_boost = 1.5  # Mnożnik prędkości
        self.boost_duration = 60000  # CZAS
        
        # Animacja automatu
        self.animation_timer = 0
        self.animation_speed = 500  # Zmiana co 500ms
        self.light_on = True
        
        # Interface
        self.show_interface = False
        self.interface_timer = 0
        self.message = ""
        self.message_timer = 0
        
        # Kolory
        self.machine_color = (60, 40, 20)  # Brązowy
        self.light_color_on = (255, 255, 0)  # Żółty
        self.light_color_off = (100, 100, 0)  # Ciemny żółty
        self.button_color = (200, 50, 50)  # Czerwony
        self.screen_color = (0, 100, 0)  # Zielony
        
    def update(self, dt):
        """Aktualizuje animację automatu"""
        self.animation_timer += dt * 1000  # Konwertuj na milisekundy
        
        if self.animation_timer >= self.animation_speed:
            self.light_on = not self.light_on
            self.animation_timer = 0
            
        # Aktualizuj timer wiadomości
        if self.message_timer > 0:
            self.message_timer -= dt * 1000
            if self.message_timer <= 0:
                self.message = ""
                
        # Aktualizuj timer interfejsu
        if self.show_interface:
            self.interface_timer += dt * 1000
            if self.interface_timer > 3000:  # Ukryj po 3 sekundach
                self.show_interface = False
                self.interface_timer = 0
    
    def draw(self, surface, camera_x, camera_y):
        """Rysuje automat z kawą"""
        # Pozycja na ekranie
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Główny korpus automatu
        pygame.draw.rect(surface, self.machine_color, 
                        (screen_x, screen_y, self.width, self.height))
        
        # Ramka
        pygame.draw.rect(surface, BLACK, 
                        (screen_x, screen_y, self.width, self.height), 3)
        
        # Ekran automatu
        screen_rect = (screen_x + 10, screen_y + 20, self.width - 20, 30)
        pygame.draw.rect(surface, self.screen_color, screen_rect)
        pygame.draw.rect(surface, BLACK, screen_rect, 2)
        
        # Tekst na ekranie
        font = pygame.font.Font(None, 24)
        text = font.render("KAWA 25$", True, WHITE)
        text_rect = text.get_rect(center=(screen_x + self.width//2, screen_y + 35))
        surface.blit(text, text_rect)
        
        # Przycisk
        button_rect = (screen_x + 20, screen_y + 60, self.width - 40, 25)
        pygame.draw.rect(surface, self.button_color, button_rect)
        pygame.draw.rect(surface, BLACK, button_rect, 2)
        
        button_text = font.render("KUP", True, WHITE)
        button_text_rect = button_text.get_rect(center=(screen_x + self.width//2, screen_y + 72))
        surface.blit(button_text, button_text_rect)
        
        # Światełko (animowane)
        light_color = self.light_color_on if self.light_on else self.light_color_off
        pygame.draw.circle(surface, light_color, 
                          (screen_x + self.width - 15, screen_y + 15), 5)
        
        # Slot na kawę
        slot_rect = (screen_x + 25, screen_y + 95, self.width - 50, 15)
        pygame.draw.rect(surface, BLACK, slot_rect)
        
        # Rysuj interface jeśli aktywny
        if self.show_interface:
            self.draw_interface(surface, screen_x, screen_y)
            
        # Rysuj wiadomość jeśli jest
        if self.message:
            self.draw_message(surface, screen_x, screen_y)
    
    def draw_interface(self, surface, screen_x, screen_y):
        """Rysuje interface interakcji"""
        # Tło interfejsu
        interface_rect = (screen_x - 50, screen_y - 60, self.width + 100, 50)
        pygame.draw.rect(surface, (0, 0, 0, 180), interface_rect)
        pygame.draw.rect(surface, WHITE, interface_rect, 2)
        
        # Tekst instrukcji
        font = pygame.font.Font(None, 28)
        instruction_text = font.render("Naciśnij SPACE aby kupić kawę", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(screen_x + self.width//2, screen_y - 35))
        surface.blit(instruction_text, instruction_rect)
    
    def draw_message(self, surface, screen_x, screen_y):
        """Rysuje wiadomość nad automatem"""
        font = pygame.font.Font(None, 32)
        
        # Kolor tekstu zależny od typu wiadomości
        color = RED if "brak" in self.message.lower() else GREEN
        
        message_text = font.render(self.message, True, color)
        message_rect = message_text.get_rect(center=(screen_x + self.width//2, screen_y - 20))
        
        # Tło dla lepszej czytelności
        bg_rect = message_rect.inflate(20, 10)
        pygame.draw.rect(surface, BLACK, bg_rect)
        pygame.draw.rect(surface, color, bg_rect, 2)
        
        surface.blit(message_text, message_rect)
    
    def is_player_near(self, player_x, player_y, interaction_distance=50):
        """Sprawdza czy gracz jest blisko automatu"""
        player_center_x = player_x + player_size // 2
        player_center_y = player_y + player_size // 2
        machine_center_x = self.x + self.width // 2
        machine_center_y = self.y + self.height // 2
        
        distance = ((player_center_x - machine_center_x) ** 2 + 
                   (player_center_y - machine_center_y) ** 2) ** 0.5
        
        return distance <= interaction_distance
    
    def show_interaction_prompt(self):
        """Pokazuje prompt interakcji"""
        self.show_interface = True
        self.interface_timer = 0
    
    def hide_interaction_prompt(self):
        """Ukrywa prompt interakcji"""
        self.show_interface = False
        self.interface_timer = 0
    
    def try_buy_coffee(self, player):
        """Próbuje kupić kawę dla gracza"""
        if player.coins >= self.coffee_price:
            # Gracz ma wystarczające monety
            player.coins -= self.coffee_price
            player.save_data()  # Zapisz dane gracza
            
            # Zwiększ prędkość gracza
            if not hasattr(player, 'original_speed'):
                player.original_speed = player.player_speed
            
            player.player_speed = player.original_speed * self.speed_boost
            
            # Ustaw timer na boost
            if not hasattr(player, 'speed_boost_timer'):
                player.speed_boost_timer = 0
            player.speed_boost_timer = self.boost_duration
            
            # Pokaż wiadomość sukcesu
            self.message = f"Kupiłeś kawę! Prędkość zwiększona!"
            self.message_timer = 3000
            
            return True
        else:
            # Gracz nie ma wystarczających monet
            needed = self.coffee_price - player.coins
            self.message = f"Brak monet! Potrzebujesz {needed} więcej"
            self.message_timer = 3000
            
            return False
    
    def update_player_speed_boost(self, player, dt):
        """Aktualizuje boost prędkości gracza"""
        if hasattr(player, 'speed_boost_timer') and player.speed_boost_timer > 0:
            player.speed_boost_timer -= dt * 1000
            
            if player.speed_boost_timer <= 0:
                # Boost się skończył, przywróć normalną prędkość
                if hasattr(player, 'original_speed'):
                    player.player_speed = player.original_speed
                
                # Pokaż wiadomość o końcu boostu
                self.message = "Efekt kawy się skończył"
                self.message_timer = 2000