from config import *

class InstructionScreen:
    def __init__(self):
        # Kolory ceglowe
        self.BRICK_RED = (139, 69, 19)
        self.BRICK_ORANGE = (160, 82, 45)
        self.LIGHT_BRICK = (205, 133, 63)
        self.DARK_BRICK = (101, 67, 33)
        
        # Zegar do kontroli FPS
        self.clock = pygame.time.Clock()
        
        # Instrukcje gry
        self.instructions = [
            "INSTRUKCJE GRY",
            "",
            "PORUSZANIE:",
            "WASD lub Strzałki - Ruch postaci",
            "SPACJA - Skok/Akcja",
            "SHIFT - Bieg",
            "",
            "PODSTAWOWE ZASADY:",
            "- Zbieraj przedmioty na mapie",
            "- Unikaj przeszkód i przeciwników",
            "- Znajdź wyjście z poziomu",
            "- Wykonuj zadania dziekanatu",
            "- Rozmawiaj z NPC aby otrzymać misje",
            "",
            "INTERFEJS:",
            "ESC - Menu pauzy",
            "TAB - Inwentarz",
            "M - Mapa",
            "",
            "Powodzenia w przygodzie!"
        ]
    
    def draw_pixel_border(self, surface, rect, color, thickness=4):
        """Rysuje pixelową ramkę"""
        # Górna i dolna linia
        for i in range(thickness):
            pygame.draw.rect(surface, color, (rect.x, rect.y + i, rect.width, 1))
            pygame.draw.rect(surface, color, (rect.x, rect.y + rect.height - 1 - i, rect.width, 1))
        
        # Lewa i prawa linia
        for i in range(thickness):
            pygame.draw.rect(surface, color, (rect.x + i, rect.y, 1, rect.height))
            pygame.draw.rect(surface, color, (rect.x + rect.width - 1 - i, rect.y, 1, rect.height))
    
    def draw_brick_pattern(self, surface):
        """Rysuje ceglowy wzór w tle"""
        brick_width = 80
        brick_height = 40
        
        for y in range(0, SCREEN_HEIGHT + brick_height, brick_height):
            for x in range(0, SCREEN_WIDTH + brick_width, brick_width):
                # Przesunięcie co drugi rząd dla efektu ceglanych bloków
                offset = (brick_width // 2) if (y // brick_height) % 2 else 0
                brick_x = x + offset
                
                # Różne odcienie cegły
                colors = [self.BRICK_RED, self.BRICK_ORANGE, self.LIGHT_BRICK]
                color_index = (x // brick_width + y // brick_height) % len(colors)
                color = colors[color_index]
                
                brick_rect = pygame.Rect(brick_x, y, brick_width - 3, brick_height - 3)
                if brick_rect.x < SCREEN_WIDTH and brick_rect.y < SCREEN_HEIGHT:
                    pygame.draw.rect(surface, color, brick_rect)
                    
                    # Ciemniejsza ramka cegły
                    self.draw_pixel_border(surface, brick_rect, self.DARK_BRICK, 1)
    
    def create_text_surface(self, text, font_obj, color):
        """Tworzy powierzchnię z tekstem"""
        return font_obj.render(text, True, color)
    
    def draw_blinking_text(self, surface, text, font_obj, color, pos, blink_speed=30):
        """Rysuje migający tekst"""
        if (pygame.time.get_ticks() // blink_speed) % 2:
            text_surface = self.create_text_surface(text, font_obj, color)
            text_rect = text_surface.get_rect(center=pos)
            surface.blit(text_surface, text_rect)
    
    def draw_title_with_shadow(self, surface, text, x, y, main_color, shadow_color):
        """Rysuje tytuł z cieniem dla efektu pixel art"""
        # Cień
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect(center=(x + 3, y + 3))
        surface.blit(shadow_surface, shadow_rect)
        
        # Główny tekst
        main_surface = font.render(text, True, main_color)
        main_rect = main_surface.get_rect(center=(x, y))
        surface.blit(main_surface, main_rect)
    
    def run(self):
        """Główna pętla ekranu instrukcji"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return True  # Przejdź dalej
                    elif event.key == pygame.K_ESCAPE:
                        return False  # Wróć do menu
            
            # Czyszczenie ekranu
            screen.fill(BLACK)
            
            # Rysowanie ceglowego tła
            self.draw_brick_pattern(screen)
            
            # Półprzezroczyste tło dla tekstu
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(120)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            # Tytuł gry z cieniem
            self.draw_title_with_shadow(screen, "GAMEDZIKANAT", 
                                      SCREEN_WIDTH // 2, 80, 
                                      YELLOW, self.DARK_BRICK)
            
            # Ramka wokół tytułu
            title_text = font.render("GAMEDZIKANAT", True, YELLOW)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
            border_rect = pygame.Rect(title_rect.x - 15, title_rect.y - 10, 
                                    title_rect.width + 30, title_rect.height + 20)
            self.draw_pixel_border(screen, border_rect, YELLOW, 3)
            
            # Główna ramka z instrukcjami
            content_rect = pygame.Rect(SCREEN_WIDTH // 4, 140, 
                                     SCREEN_WIDTH // 2, SCREEN_HEIGHT - 280)
            pygame.draw.rect(screen, self.BRICK_RED, content_rect)
            pygame.draw.rect(screen, BLACK, 
                           (content_rect.x + 10, content_rect.y + 10, 
                            content_rect.width - 20, content_rect.height - 20))
            self.draw_pixel_border(screen, content_rect, self.LIGHT_BRICK, 4)
            
            # Instrukcje
            y_offset = 170
            for instruction in self.instructions:
                if instruction == "INSTRUKCJE GRY":
                    color = self.LIGHT_BRICK
                    text_surface = font.render(instruction, True, color)
                elif instruction.startswith(("PORUSZANIE:", "PODSTAWOWE ZASADY:", "INTERFEJS:")):
                    color = self.BRICK_ORANGE
                    text_surface = font.render(instruction, True, color)
                elif instruction == "":
                    y_offset += 15
                    continue
                else:
                    color = WHITE
                    text_surface = font.render(instruction, True, color)
                
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                screen.blit(text_surface, text_rect)
                y_offset += 35
            
            # Migający tekst na dole
            self.draw_blinking_text(screen, "NACISNIJ ENTER ABY KONTYNUOWAC", 
                                  font, YELLOW, 
                                  (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            
            self.draw_blinking_text(screen, "ESC - POWROT DO MENU", 
                                  font, self.LIGHT_BRICK, 
                                  (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            
            # Ramka wokół całego ekranu
            screen_border = pygame.Rect(5, 5, SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)
            self.draw_pixel_border(screen, screen_border, self.LIGHT_BRICK, 6)
            
            # Dekoracyjne elementy w rogach
            corner_size = 30
            # Lewy górny róg
            pygame.draw.rect(screen, self.BRICK_ORANGE, (20, 20, corner_size, corner_size))
            self.draw_pixel_border(screen, pygame.Rect(20, 20, corner_size, corner_size), 
                                 self.DARK_BRICK, 2)
            
            # Prawy górny róg
            pygame.draw.rect(screen, self.BRICK_ORANGE, 
                           (SCREEN_WIDTH - 50, 20, corner_size, corner_size))
            self.draw_pixel_border(screen, 
                                 pygame.Rect(SCREEN_WIDTH - 50, 20, corner_size, corner_size), 
                                 self.DARK_BRICK, 2)
            
            # Lewy dolny róg
            pygame.draw.rect(screen, self.BRICK_ORANGE, 
                           (20, SCREEN_HEIGHT - 50, corner_size, corner_size))
            self.draw_pixel_border(screen, 
                                 pygame.Rect(20, SCREEN_HEIGHT - 50, corner_size, corner_size), 
                                 self.DARK_BRICK, 2)
            
            # Prawy dolny róg
            pygame.draw.rect(screen, self.BRICK_ORANGE, 
                           (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, corner_size, corner_size))
            self.draw_pixel_border(screen, 
                                 pygame.Rect(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, corner_size, corner_size), 
                                 self.DARK_BRICK, 2)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return False