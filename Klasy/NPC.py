from config import *
import textwrap
import os
import openai

def draw_text_with_background(surface, text, font, text_color, bg_color, pos, padding=10):
    # Renderuj tekst
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=pos)
    
    # Stwórz tło
        bg_rect = text_rect.inflate(padding * 2, padding * 2)
        pygame.draw.rect(surface, bg_color, bg_rect, border_radius=5)
    
    # Opcjonalnie dodaj ramkę
        pygame.draw.rect(surface, (100, 100, 100), bg_rect, 2, border_radius=5)
    
    # Narysuj tekst na wierzchu
        surface.blit(text_surface, text_rect)
        
def get_ai_response(user_input):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # lub "gpt-4" jeśli masz dostęp
            messages=[
                {"role": "system", "content": "Jesteś pomocnym NPC w grze. Odpowiadaj krótko i w sposób odpowiedni dla uniwersyteckiej gry."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Przepraszam, nie mogę teraz odpowiedzieć. Błąd: {str(e)}"

class AIChatWindow:
    def __init__(self):
        self.active = False
        self.user_input = ""
        self.input_active = False
        self.conversation_history = [("ai", "Witaj studencie! W czym mogę pomóc?")]

        self.scroll_offset = 0
        self.typing_cursor = 0
        self.cursor_timer = 0
        
        # Ładowanie tła - pełnoekranowe
        try:
            self.background = pygame.image.load("assets/terapeuta_sredniowieczny.png")
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background = None
            print("Nie można załadować pliku terapeuta_sredniowieczny.png")
        
        # Pozycje i rozmiary elementów - pasek na dole ekranu
        self.chat_panel_height = 200
        self.input_height = 50
        
        # Panel czatu na dole ekranu
        self.chat_panel = pygame.Rect(0, SCREEN_HEIGHT - self.chat_panel_height, 
                                     SCREEN_WIDTH, self.chat_panel_height)
        
        # Obszar na historię rozmowy
        self.chat_area = pygame.Rect(20, SCREEN_HEIGHT - self.chat_panel_height + 10, 
                                    SCREEN_WIDTH - 40, self.chat_panel_height - self.input_height - 20)
        
        # Pole wprowadzania tekstu
        self.input_rect = pygame.Rect(20, SCREEN_HEIGHT - self.input_height - 10, 
                                     SCREEN_WIDTH - 140, self.input_height - 10)
        
        # Przycisk wysyłania
        self.send_button = pygame.Rect(SCREEN_WIDTH - 110, SCREEN_HEIGHT - self.input_height - 10, 
                                      80, self.input_height - 10)
        
        # Przycisk zamknięcia (prawy górny róg)
        self.exit_button = pygame.Rect(SCREEN_WIDTH - 50, 20, 40, 40)
        
        # Kolory z przezroczystością
        self.colors = {
            'panel_bg': (20, 20, 30, 220),  # Ciemne tło z przezroczystością
            'input_bg': (40, 40, 50, 200),
            'input_active': (60, 60, 70, 200),
            'button_bg': (70, 130, 180, 200),
            'button_hover': (100, 150, 200, 200),
            'exit_button': (220, 20, 60, 200),
            'exit_hover': (255, 50, 50, 200),
            'text_color': (255, 255, 255),
            'user_text': (150, 200, 255),
            'ai_text': (255, 200, 150),
            'border': (100, 100, 120)
        }
        
    def wrap_text(self, text, max_width):
        """Zawija tekst do określonej szerokości"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
            
        return lines
    
    def open_chat(self):
        """Otwiera okno czatu - zatrzymuje grę"""
        self.active = True
        self.input_active = True
        
    def close_chat(self):
        """Zamyka okno czatu - wznawia grę"""
        self.active = False
        self.input_active = False
        
    def send_message(self):
        """Wysyła wiadomość do AI"""
        if self.user_input.strip():
            # Dodaj wiadomość użytkownika do historii
            self.conversation_history.append(("user", self.user_input.strip()))
            
            try:
                # Pobierz odpowiedź AI
                ai_response = get_ai_response(self.user_input.strip())
                self.conversation_history.append(("ai", ai_response))
            except Exception as e:
                self.conversation_history.append(("ai", f"Przepraszam, wystąpił błąd: {str(e)}"))
            
            # Wyczyść pole input
            self.user_input = ""
            
            # Przewiń na dół
            self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Przewija czat na dół"""
        total_height = sum(len(self.wrap_text(msg[1], self.chat_area.width - 60)) * 25 + 35 
                          for msg in self.conversation_history)
        if total_height > self.chat_area.height:
            self.scroll_offset = total_height - self.chat_area.height
        else:
            self.scroll_offset = 0
    
    def handle_event(self, event):
        """Obsługuje zdarzenia w oknie czatu"""
        if not self.active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close_chat()
                return True
            elif self.input_active:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.send_message()
                elif event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                else:
                    if len(self.user_input) < 500:  # Limit długości
                        if event.unicode and ord(event.unicode) >= 32:  # Tylko drukowalne znaki
                            self.user_input += event.unicode
                        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Kliknięcie przycisku wyjścia
            if self.exit_button.collidepoint(mouse_pos):
                self.close_chat()
                return True
            
            # Kliknięcie przycisku wysyłania
            elif self.send_button.collidepoint(mouse_pos):
                self.send_message()
                return True
                
            # Kliknięcie w pole input
            elif self.input_rect.collidepoint(mouse_pos):
                self.input_active = True
                return True
                
            # Kliknięcie w obszar czatu
            elif self.chat_area.collidepoint(mouse_pos):
                self.input_active = False
                return True
                
        elif event.type == pygame.MOUSEWHEEL:
            # Przewijanie czatu
            if self.chat_area.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset = max(0, self.scroll_offset - event.y * 30)
                return True
                
        return True  # Zwracamy True żeby zatrzymać przetwarzanie innych zdarzeń gry
    
    def update(self):
        """Aktualizuje animacje"""
        if self.active:
            # Animacja kursora
            self.cursor_timer += 1
            if self.cursor_timer >= 30:  # Miganie co pół sekundy
                self.cursor_timer = 0
    
    def draw_transparent_surface(self, surface, color_with_alpha, rect):
        """Rysuje przezroczyste tło"""
        temp_surface = pygame.Surface((rect.width, rect.height))
        temp_surface.set_alpha(color_with_alpha[3])
        temp_surface.fill(color_with_alpha[:3])
        surface.blit(temp_surface, rect)

    
    
    def draw(self):
        """Rysuje interfejs czatu na pełnym ekranie"""
        if not self.active:
            return
            
        # Rysuj tło na pełnym ekranie
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((50, 50, 60))  # Zapasowe tło
        
        # Panel czatu na dole
        self.draw_transparent_surface(screen, self.colors['panel_bg'], self.chat_panel)
        pygame.draw.rect(screen, self.colors['border'], self.chat_panel, 2)
        
        # Obszar historii czatu
        pygame.draw.rect(screen, (10, 10, 20, 150), self.chat_area)
        pygame.draw.rect(screen, self.colors['border'], self.chat_area, 1)
        
        # Rysuj historię konwersacji
        y_offset = self.chat_area.y + 10 - self.scroll_offset
        line_height = 25
        
        for sender, message in self.conversation_history:
            if y_offset > self.chat_area.bottom:
                break
                
            if y_offset + 60 > self.chat_area.y:  # Rysuj tylko widoczne wiadomości
                # Kolor tekstu w zależności od nadawcy
                text_color = self.colors['user_text'] if sender == "user" else self.colors['ai_text']
                prefix = "Ty: " if sender == "user" else "Ojciec Mateusz: "
                
                # Zawijanie tekstu wiadomości
                wrapped_lines = self.wrap_text(message, self.chat_area.width - 60)
                
                # Rysuj prefiks
                if y_offset >= self.chat_area.y and y_offset < self.chat_area.bottom:
                    prefix_surface = font.render(prefix, True, text_color)
                    screen.blit(prefix_surface, (self.chat_area.x + 10, y_offset))
                y_offset += line_height
                
                # Rysuj zawiniętą wiadomość
                for line in wrapped_lines:
                    if y_offset >= self.chat_area.y and y_offset < self.chat_area.bottom:
                        line_surface = font.render(line, True, self.colors['text_color'])
                        screen.blit(line_surface, (self.chat_area.x + 30, y_offset))
                    y_offset += line_height
                    
                y_offset += 10  # Odstęp między wiadomościami
            else:
                # Oblicz wysokość wiadomości bez rysowania
                wrapped_lines = self.wrap_text(message, self.chat_area.width - 60)
                y_offset += line_height * (len(wrapped_lines) + 1) + 10
        
        # Pole wprowadzania tekstu
        mouse_pos = pygame.mouse.get_pos()
        input_color = self.colors['input_active'] if self.input_active else self.colors['input_bg']
        self.draw_transparent_surface(screen, input_color, self.input_rect)
        pygame.draw.rect(screen, self.colors['border'], self.input_rect, 2)
        
        # Tekst w polu input
        if self.user_input or self.input_active:
            display_text = self.user_input
            
            # Dodaj kursor jeśli pole jest aktywne
            if self.input_active and self.cursor_timer < 15:
                display_text += "|"
                
            # Ograniczenie wyświetlanego tekstu do szerokości pola
            text_width = font.size(display_text)[0]
            while text_width > self.input_rect.width - 20 and len(display_text) > 1:
                display_text = display_text[1:]
                text_width = font.size(display_text)[0]
                
            input_surface = font.render(display_text, True, self.colors['text_color'])
            screen.blit(input_surface, (self.input_rect.x + 10, self.input_rect.y + 12))
        else:
            # Placeholder text
            placeholder = font.render("Napisz coś do terapeuty...", True, (128, 128, 128))
            screen.blit(placeholder, (self.input_rect.x + 10, self.input_rect.y + 12))
        
        # Przycisk wysyłania
        send_color = self.colors['button_hover'] if self.send_button.collidepoint(mouse_pos) else self.colors['button_bg']
        self.draw_transparent_surface(screen, send_color, self.send_button)
        pygame.draw.rect(screen, self.colors['border'], self.send_button, 2)
        
        send_text = font.render("Wyślij", True, self.colors['text_color'])
        send_rect = send_text.get_rect(center=self.send_button.center)
        screen.blit(send_text, send_rect)
        
        # Przycisk zamknięcia (prawy górny róg)
        exit_color = self.colors['exit_hover'] if self.exit_button.collidepoint(mouse_pos) else self.colors['exit_button']
        self.draw_transparent_surface(screen, exit_color, self.exit_button)
        pygame.draw.rect(screen, self.colors['border'], self.exit_button, 2)
        
        # X na przycisku wyjścia
        x_text = font.render("Exit", True, self.colors['text_color'])
        x_rect = x_text.get_rect(center=self.exit_button.center)
        screen.blit(x_text, x_rect)
        
        # Instrukcja na górze ekranu
        draw_text_with_background(screen, "Naciśnij Exit w prawym górnym rogu aby wrócić do gry",
                         font, (255, 255, 255), (50, 50, 50, 180), (SCREEN_WIDTH // 2, 30))
        
        # Tło dla instrukcji
        
        

class NPC:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.chat_window = AIChatWindow()

    def draw(self, camera_x, camera_y):
        # Rysuj NPC tylko jeśli czat nie jest aktywny
        # if not self.chat_window.active:
        #     pygame.draw.rect(screen, YELLOW, (self.rect.x - camera_x, self.rect.y - camera_y, 40, 40))
        
        # Zawsze rysuj okno czatu jeśli jest aktywne (przejmuje cały ekran)
        if self.chat_window.active:
            self.chat_window.draw()
    
    def update(self):
        """Aktualizuje NPC i okno czatu"""
        self.chat_window.update()
    
    def handle_interaction(self):
        """Obsługuje interakcję z NPC (otwiera czat)"""
        self.chat_window.open_chat()
    
    def handle_event(self, event):
        """Przekazuje zdarzenia do okna czatu"""
        return self.chat_window.handle_event(event)
    
    def is_chat_active(self):
        """Sprawdza czy czat jest aktywny (do zatrzymania gry)"""
        return self.chat_window.active
    def draw_chat_only(self):
   
        if self.chat_window.active:
            self.chat_window.draw()

    