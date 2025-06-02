import math
import pygame
import sys
import json
import os
import openai




openai.api_key = "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"
GRAY = (128,128,128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

player_speed = 7
player_size = 40
pygame.init()
pygame.display.set_caption("GameDziekanat")
font = pygame.font.SysFont('Arial', 24)
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))