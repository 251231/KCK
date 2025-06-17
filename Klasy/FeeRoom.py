from Room import Room
from NPC import *
import pygame
from config import *
from AnimatedModels import AnimatedLamp
import math

class FeeRoom(Room):
    def __init__(self):
        super().__init__(
            bg_path="assets/FeeRoom.png",
            collision_path="assets/FeeRoom_kolizje.png",
            npcs=None,
            teleport_zones={
                (255, 255, 0): ("MainRoom", "from_fee"),  
            },
            entry_points={
                "default": (100, 100),
                "from_main": (1345, 600),    # Gdzie gracz pojawia się przychodząc z MainRoom
            }
        )
        self.fees = [
            {"name": "2 ECTS", "cost": 10},
            {"name": "Akademik", "cost": 50},
            {"name": "Legitymacja", "cost": 20}
        ]
        self.fee_buttons = []
        self.selected_fee_index = -1  # Która opłata jest aktualnie wybrana

        # Strefa wyboru opłat - przesunięta niżej w pokoju
        self.fee_zone = pygame.Rect(600, 600, 100, 100)  # Większa strefa
        self.fee_interface_active = False
        self.fee_message = ""
        self.fee_message_timer = 0
        self.fees_paid = set()  # Zestaw opłaconych opłat
        
        # Kolory i fonty - elegantsza paleta
        self.primary_color = (30, 30, 60)      # Ciemny granat
        self.secondary_color = (70, 130, 180)   # Steel blue
        self.accent_color = (255, 215, 0)       # Złoty
        self.success_color = (46, 204, 113)     # Emerald green
        self.error_color = (231, 76, 60)        # Alizarin red
        self.text_color = (248, 249, 250)       # Off white
        
        # Animacje
        self.animation_time = 0
        self.button_hover_effects = {}
        
        # Przyciski interfejsu
        self.confirm_button = None
        self.cancel_button = None
        self.current_player = None  # Referencja do gracza
        self.setup_lamps()
    
    def init_interface_buttons(self):
        """Inicjalizuje przyciski interfejsu z eleganckim układem"""
        interface_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 200, 500, 400)
        
        # Przycisk potwierdzenia - tylko gdy coś wybrano
        self.confirm_button = pygame.Rect(
            interface_rect.x + 80, 
            interface_rect.y + 320, 
            150, 50
        )
        
        # Przycisk anulowania
        self.cancel_button = pygame.Rect(
            interface_rect.x + 270, 
            interface_rect.y + 320, 
            150, 50
        )
        
        # Przyciski opłat
        self.fee_buttons = []
        interface_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 200, 500, 400)

        for i, fee in enumerate(self.fees):
            button_rect = pygame.Rect(
                interface_rect.x + 50,
                interface_rect.y + 80 + i * 70,
                400,
                60
            )
            self.fee_buttons.append((button_rect, fee, i))
            # Inicjalizuj efekty hover dla każdego przycisku
            self.button_hover_effects[i] = {"hover": False, "press_time": 0}

    def handle_fee_interaction(self, player):
        """Obsługuje interakcję ze strefą wyboru opłat"""
        if not self.fee_interface_active:
            self.fee_interface_active = True
            self.fee_message = ""
            self.fee_message_timer = 0
            self.current_player = player
            self.selected_fee_index = -1
            self.animation_time = 0
            self.init_interface_buttons()

    def handle_fee_event(self, event, player):
        """Obsługuje wydarzenia w interfejsie wyboru opłat"""
        if not self.fee_interface_active:
            return False
            
        # Obsługa myszy
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Kliknięcie na przycisk opłaty
            for button_rect, fee, index in self.fee_buttons:
                if button_rect.collidepoint(event.pos):
                    self.selected_fee_index = index
                    self.button_hover_effects[index]["press_time"] = pygame.time.get_ticks()
                    return True
            
            # Kliknięcie na przycisk potwierdzenia
            if self.confirm_button and self.confirm_button.collidepoint(event.pos) and self.selected_fee_index >= 0:
                self.try_pay_selected_fee(player)
                return True
                
            # Kliknięcie na przycisk anulowania
            if self.cancel_button and self.cancel_button.collidepoint(event.pos):
                self.close_fee_interface()
                return True

        # Obsługa hover myszy
        if event.type == pygame.MOUSEMOTION:
            for button_rect, fee, index in self.fee_buttons:
                was_hover = self.button_hover_effects[index]["hover"]
                is_hover = button_rect.collidepoint(event.pos)
                self.button_hover_effects[index]["hover"] = is_hover
                
                # Efekt dźwiękowy przy pierwszym hover (jeśli masz system audio)
                if is_hover and not was_hover:
                    pass  # Tutaj możesz dodać dźwięk hover
                    
        # Obsługa klawiatury
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close_fee_interface()
                return True
            elif event.key == pygame.K_RETURN and self.selected_fee_index >= 0:
                self.try_pay_selected_fee(player)
                return True
            elif event.key == pygame.K_UP:
                self.selected_fee_index = max(0, self.selected_fee_index - 1) if self.selected_fee_index > 0 else len(self.fees) - 1
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_fee_index = (self.selected_fee_index + 1) % len(self.fees) if self.selected_fee_index >= 0 else 0
                return True
                
        return False
    
    def try_pay_selected_fee(self, player):
        """Próbuje opłacić wybraną opłatę"""
        if self.selected_fee_index < 0 or self.selected_fee_index >= len(self.fees):
            return
            
        fee = self.fees[self.selected_fee_index]
        fee_id = f"{fee['name']}_{fee['cost']}"
        
        # Sprawdź czy opłata już została opłacona
        if fee_id in self.fees_paid:
            self.show_message(f"{fee['name']} już została opłacona!", "warning")
            return
        
        # Sprawdź czy gracz ma wystarczająco monet
        if player.coins >= fee["cost"]:
            player.coins -= fee["cost"]
            self.fees_paid.add(fee_id)
            self.show_message(f"Opłacono {fee['name']} za {fee['cost']} monet!", "success")
            
            # Animacja sukcesu
            self.button_hover_effects[self.selected_fee_index]["press_time"] = pygame.time.get_ticks()
            
            # Auto-zamknij interfejs po opłaceniu (opcjonalne)
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000)
        else:
            needed = fee["cost"] - player.coins
            self.show_message(f"Brak {needed} monet! Potrzebujesz {fee['cost']}, masz {player.coins}", "error")

    def close_fee_interface(self):
        """Zamyka interfejs wyboru opłat z animacją"""
        self.fee_interface_active = False
        self.fee_message = ""
        self.fee_message_timer = 0
        self.current_player = None
        self.selected_fee_index = -1
    
    def show_message(self, message, message_type):
        """Pokazuje wiadomość z odpowiednim czasem wyświetlania"""
        self.fee_message = message
        self.fee_message_timer = 4.0 if message_type == "error" else 3.0

    def update(self, game, delta_time):
        """Aktualizuje stan pokoju"""
        # Aktualizuj timer wiadomości
        if self.fee_message_timer > 0:
            self.fee_message_timer -= delta_time
            if self.fee_message_timer <= 0:
                self.fee_message = ""
        
        # Aktualizuj czas animacji
        self.animation_time += delta_time
        
        # Aktualizuj lampy
        for lamp in self.lamps:
            lamp.update()
    
    def draw(self, screen, camera_x, camera_y):
        """Rysuje pokój wraz z interfejsem wyboru opłat"""
        # Rysuj podstawowy pokój
        super().draw(screen, camera_x, camera_y)
        
        # Rysuj strefę wyboru opłat z elegancką animacją
        self.draw_fee_zone(screen, camera_x, camera_y)
        
        # Rysuj interfejs wyboru jeśli jest aktywny
        if self.fee_interface_active:
            self.draw_fee_interface(screen)
        
        # Rysuj lampy na górze
        for lamp in self.lamps:
            lamp.draw(screen, camera_x, camera_y)

    def draw_fee_zone(self, screen, camera_x, camera_y):
        """Rysuje elegancką strefę opłat"""
        fee_zone_screen = pygame.Rect(
            self.fee_zone.x - camera_x,
            self.fee_zone.y - camera_y,
            self.fee_zone.width,
            self.fee_zone.height
        )
        
        # Sprawdź czy strefa jest widoczna na ekranie
        if (fee_zone_screen.x > -self.fee_zone.width and fee_zone_screen.x < SCREEN_WIDTH and
            fee_zone_screen.y > -self.fee_zone.height and fee_zone_screen.y < SCREEN_HEIGHT):
            
            # Animacja pulsowania
            pulse = (math.sin(self.animation_time * 3) + 1) / 2
            glow_intensity = int(100 + pulse * 155)
            
            # Gradient glow effect
            for i in range(5):
                alpha = int((5-i) * 30)
                glow_surface = pygame.Surface((fee_zone_screen.width + i*8, fee_zone_screen.height + i*8))
                glow_surface.set_alpha(alpha)
                glow_surface.fill(self.accent_color)
                glow_pos = (fee_zone_screen.x - i*4, fee_zone_screen.y - i*4)
                screen.blit(glow_surface, glow_pos)
            
            # Główna strefa z gradientem
            zone_surface = pygame.Surface((fee_zone_screen.width, fee_zone_screen.height))
            for y in range(fee_zone_screen.height):
                progress = y / fee_zone_screen.height
                r = int(self.primary_color[0] + progress * (self.secondary_color[0] - self.primary_color[0]))
                g = int(self.primary_color[1] + progress * (self.secondary_color[1] - self.primary_color[1]))
                b = int(self.primary_color[2] + progress * (self.secondary_color[2] - self.primary_color[2]))
                pygame.draw.line(zone_surface, (r, g, b), (0, y), (fee_zone_screen.width, y))
            
            screen.blit(zone_surface, fee_zone_screen.topleft)
            
            # Elegancka ramka
            pygame.draw.rect(screen, self.accent_color, fee_zone_screen, 4)
            pygame.draw.rect(screen, self.text_color, fee_zone_screen, 2)
            
            # Ikona opłat w centrum
            center_x, center_y = fee_zone_screen.center
            
            # Animowane kółko
            circle_radius = 30 + int(pulse * 5)
            pygame.draw.circle(screen, self.accent_color, (center_x, center_y), circle_radius)
            pygame.draw.circle(screen, self.primary_color, (center_x, center_y), circle_radius - 5)
            
            # Symbol pieniędzy
            money_text = font.render("$", True, self.accent_color)
            money_rect = money_text.get_rect(center=(center_x, center_y))
            screen.blit(money_text, money_rect)
            
            # Tekst "OPŁATY" pod strefą
            fee_text = font.render("OPŁATY", True, self.accent_color)
            text_rect = fee_text.get_rect(center=(center_x, fee_zone_screen.bottom + 20))
            screen.blit(fee_text, text_rect)

    def draw_fee_interface(self, screen):
        """Rysuje elegancki interfejs wyboru opłat"""
        # Animowane półprzezroczyste tło
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        alpha = int(150 + 20 * math.sin(self.animation_time * 2))
        overlay.set_alpha(alpha)
        overlay.fill(self.primary_color)
        screen.blit(overlay, (0, 0))
        
        # Główne okno interfejsu
        interface_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 250, 600, 500)
        
        # Gradient tła okna
        bg_surface = pygame.Surface((interface_rect.width, interface_rect.height))
        for y in range(interface_rect.height):
            progress = y / interface_rect.height
            r = int(self.primary_color[0] + progress * 30)
            g = int(self.primary_color[1] + progress * 40)
            b = int(self.primary_color[2] + progress * 60)
            pygame.draw.line(bg_surface, (r, g, b), (0, y), (interface_rect.width, y))
        
        screen.blit(bg_surface, interface_rect.topleft)
        
        # Elegancka ramka okna z podwójną linią
        pygame.draw.rect(screen, self.accent_color, interface_rect, 4)
        pygame.draw.rect(screen, self.text_color, interface_rect, 2)
        
        # Animowany tytuł
        title_scale = 1 + 0.1 * math.sin(self.animation_time * 4)
        title_font = pygame.font.Font(None, int(36 * title_scale))
        title_text = title_font.render("OPŁATY STUDENCKIE", True, self.accent_color)
        title_rect = title_text.get_rect(center=(interface_rect.centerx, interface_rect.y + 40))
        screen.blit(title_text, title_rect)
        
        # Status gracza
        if self.current_player:
            coins_text = font.render(f"Dostępne monety: {self.current_player.coins}", True, self.text_color)
            coins_rect = coins_text.get_rect(center=(interface_rect.centerx, interface_rect.y + 65))
            screen.blit(coins_text, coins_rect)
        
        # Przyciski opłat z eleganckimi efektami
        self.draw_fee_buttons(screen, interface_rect)
        
        # Przyciski kontrolne
        self.draw_control_buttons(screen)
        

        
        # Wiadomość zwrotna
        self.draw_feedback_message(screen, interface_rect)

    def draw_fee_buttons(self, screen, interface_rect):
        """Rysuje przyciski opłat z zaawansowanymi efektami"""
        mouse_pos = pygame.mouse.get_pos()
        
        for button_rect, fee, index in self.fee_buttons:
            is_selected = (index == self.selected_fee_index)
            is_hovered = self.button_hover_effects[index]["hover"]
            is_paid = f"{fee['name']}_{fee['cost']}" in self.fees_paid
            press_time = self.button_hover_effects[index]["press_time"]
            
            # Animacja przycisku
            button_scale = 1.0
            if is_hovered:
                button_scale = 1.05
            if is_selected:
                button_scale = 1.08
            
            # Efekt naciśnięcia
            press_effect = 0
            if press_time > 0 and pygame.time.get_ticks() - press_time < 200:
                press_effect = math.sin((pygame.time.get_ticks() - press_time) / 200 * math.pi) * 5
            
            # Skalowany prostokąt przycisku
            scaled_width = int(button_rect.width * button_scale)
            scaled_height = int(button_rect.height * button_scale)
            scaled_rect = pygame.Rect(
                button_rect.centerx - scaled_width // 2,
                button_rect.centery - scaled_height // 2 + press_effect,
                scaled_width,
                scaled_height
            )
            
            # Kolor tła przycisku
            if is_paid:
                bg_color = self.success_color
                border_color = (0, 255, 0)
            elif is_selected:
                bg_color = self.secondary_color
                border_color = self.accent_color
            elif is_hovered:
                bg_color = tuple(min(255, c + 30) for c in self.primary_color)
                border_color = self.text_color
            else:
                bg_color = self.primary_color
                border_color = self.secondary_color
            
            # Efekt świecenia dla wybranego przycisku
            if is_selected or is_hovered:
                glow_surface = pygame.Surface((scaled_rect.width + 20, scaled_rect.height + 10))
                glow_surface.set_alpha(80)
                glow_surface.fill(border_color)
                screen.blit(glow_surface, (scaled_rect.x - 10, scaled_rect.y - 5))
            
            # Tło przycisku z gradientem
            button_surface = pygame.Surface((scaled_rect.width, scaled_rect.height))
            for y in range(scaled_rect.height):
                progress = y / scaled_rect.height
                r = int(bg_color[0] * (1 - progress * 0.3))
                g = int(bg_color[1] * (1 - progress * 0.3))
                b = int(bg_color[2] * (1 - progress * 0.3))
                pygame.draw.line(button_surface, (r, g, b), (0, y), (scaled_rect.width, y))
            
            screen.blit(button_surface, scaled_rect.topleft)
            
            # Ramka przycisku
            pygame.draw.rect(screen, border_color, scaled_rect, 3)
            if is_selected:
                pygame.draw.rect(screen, self.accent_color, scaled_rect, 1)
            
            # Ikona i tekst
            icon_text = font.render(fee.get("icon", "$"), True, self.text_color)
            icon_x = scaled_rect.x + 15
            icon_y = scaled_rect.centery - icon_text.get_height() // 2
            screen.blit(icon_text, (icon_x, icon_y))
            
            # Nazwa opłaty
            name_text = font.render(fee["name"], True, self.text_color)
            name_x = icon_x + icon_text.get_width() + 10
            name_y = scaled_rect.centery - 24
            screen.blit(name_text, (name_x, name_y))
            
            # Koszt
            cost_color = self.success_color if is_paid else self.accent_color
            cost_text = font.render(f"{fee['cost']} monet", True, cost_color)
            cost_x = name_x
            cost_y = scaled_rect.centery
            screen.blit(cost_text, (cost_x, cost_y))
            
            # Status opłaty
            if is_paid:
                status_text = font.render("OPŁACONE", True, self.success_color)
                status_rect = status_text.get_rect(right=scaled_rect.right - 10, centery=scaled_rect.centery)
                screen.blit(status_text, status_rect)

    def draw_control_buttons(self, screen):
        """Rysuje przyciski kontrolne z efektami hover"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Przycisk potwierdzenia
        if self.selected_fee_index >= 0:
            confirm_hovered = self.confirm_button.collidepoint(mouse_pos)
            confirm_color = tuple(min(255, c + 40) for c in self.success_color) if confirm_hovered else self.success_color
            
            # Gradient tła
            confirm_surface = pygame.Surface((self.confirm_button.width, self.confirm_button.height))
            for y in range(self.confirm_button.height):
                progress = y / self.confirm_button.height
                r = int(confirm_color[0] * (1 - progress * 0.2))
                g = int(confirm_color[1] * (1 - progress * 0.2))
                b = int(confirm_color[2] * (1 - progress * 0.2))
                pygame.draw.line(confirm_surface, (r, g, b), (0, y), (self.confirm_button.width, y))
            
            screen.blit(confirm_surface, self.confirm_button.topleft)
            pygame.draw.rect(screen, self.text_color, self.confirm_button, 3)
            
            confirm_text = font.render("OPŁAĆ", True, self.text_color)
            confirm_text_rect = confirm_text.get_rect(center=self.confirm_button.center)
            screen.blit(confirm_text, confirm_text_rect)
        
        # Przycisk anulowania
        cancel_hovered = self.cancel_button.collidepoint(mouse_pos)
        cancel_color = tuple(min(255, c + 40) for c in self.error_color) if cancel_hovered else self.error_color
        
        # Gradient tła
        cancel_surface = pygame.Surface((self.cancel_button.width, self.cancel_button.height))
        for y in range(self.cancel_button.height):
            progress = y / self.cancel_button.height
            r = int(cancel_color[0] * (1 - progress * 0.2))
            g = int(cancel_color[1] * (1 - progress * 0.2))
            b = int(cancel_color[2] * (1 - progress * 0.2))
            pygame.draw.line(cancel_surface, (r, g, b), (0, y), (self.cancel_button.width, y))
        
        screen.blit(cancel_surface, self.cancel_button.topleft)
        pygame.draw.rect(screen, self.text_color, self.cancel_button, 3)
        
        cancel_text = font.render("ANULUJ", True, self.text_color)
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_button.center)
        screen.blit(cancel_text, cancel_text_rect)

    def draw_feedback_message(self, screen, interface_rect):
        """Rysuje wiadomość zwrotną z animacją"""
        if self.fee_message:
            # Określ kolor na podstawie typu wiadomości
            if "Opłacono" in self.fee_message:
                message_color = self.success_color
                bg_alpha = 120
            elif "Brak" in self.fee_message:
                message_color = self.error_color
                bg_alpha = 120
            else:
                message_color = self.accent_color
                bg_alpha = 100
            
            # Animacja pojawiania się
            fade_progress = min(1.0, (4.0 - self.fee_message_timer) / 0.5)
            alpha = int(bg_alpha * fade_progress)
            
            message_bg = pygame.Rect(interface_rect.x + 20, interface_rect.bottom - 60,  # Changed from -120 to -100
                         interface_rect.width - 40, 35)
            
            # Tło wiadomości z animacją
            bg_surface = pygame.Surface((message_bg.width, message_bg.height))
            bg_surface.set_alpha(alpha)
            for y in range(message_bg.height):
                progress = y / message_bg.height
                r = int(message_color[0] * 0.3 * (1 - progress * 0.5))
                g = int(message_color[1] * 0.3 * (1 - progress * 0.5))
                b = int(message_color[2] * 0.3 * (1 - progress * 0.5))
                pygame.draw.line(bg_surface, (r, g, b), (0, y), (message_bg.width, y))
            
            screen.blit(bg_surface, message_bg.topleft)
            pygame.draw.rect(screen, message_color, message_bg, 2)
            
            # Tekst wiadomości
            message_text = font.render(self.fee_message, True, message_color)
            message_rect = message_text.get_rect(center=message_bg.center)
            screen.blit(message_text, message_rect)

    def check_fee_interaction(self, player):
        """Sprawdza czy gracz może wejść w interakcję ze strefą wyboru opłat"""
        return player.rect.colliderect(self.fee_zone.inflate(50, 50))
    
    def setup_lamps(self):
        """Konfiguruje pozycje lamp - łatwe do edycji"""
        self.lamps = [
            AnimatedLamp(x=40, y=300, png_name="torch_big", animation_speed=250, scale=3),
            AnimatedLamp(x=1450, y=300, png_name="torch_big", animation_speed=250, scale=3),
            AnimatedLamp(x=1450, y=800, png_name="torch_big", animation_speed=250, scale=3),
            AnimatedLamp(x=1050, y=15, png_name="torch_small", animation_speed=250, scale=3),
            AnimatedLamp(x=300, y=15, png_name="torch_small", animation_speed=250, scale=3),
            AnimatedLamp(x=40, y=800, png_name="torch_big", animation_speed=250, scale=3),
        ]   

    def handle_interaction(self, game, key_pressed):
        """Obsługuje interakcje w pokoju"""
        if key_pressed == pygame.K_e and self.check_fee_interaction(game.player):
            self.handle_fee_interaction(game.player)
            return True
        return False
    
    def add_lamp(self, x, y, animation_speed=200):
        """Dodaje nową lampę w określonej pozycji"""
        new_lamp = AnimatedLamp(x, y, animation_speed)
        self.lamps.append(new_lamp)
        return new_lamp
    
    def remove_lamp(self, index):
        """Usuwa lampę o określonym indeksie"""
        if 0 <= index < len(self.lamps):
            del self.lamps[index]
    
    def move_lamp(self, index, new_x, new_y):
        """Przesuwa lampę o określonym indeksie"""
        if 0 <= index < len(self.lamps):
            self.lamps[index].set_position(new_x, new_y)