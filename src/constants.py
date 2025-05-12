# src/constants.py

import pygame
import os

# --- Main Dimensions ---
BOARD_WIDTH, BOARD_HEIGHT = 800, 800
SIDE_PANEL_WIDTH = 250

WIDTH = BOARD_WIDTH + SIDE_PANEL_WIDTH
HEIGHT = BOARD_HEIGHT

ROWS, COLS = 8, 8
SQUARE_SIZE = BOARD_WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (100, 255, 100, 150)

SIDE_PANEL_BG_COLOR = (50, 50, 50)
TEXT_COLOR = (230, 230, 230)
GAME_OVER_BG_COLOR = (40, 40, 40, 220)

BUTTON_COLOR = (70, 70, 90)
BUTTON_HOVER_COLOR = (100, 100, 120)
BUTTON_TEXT_COLOR = (220, 220, 220)
BUTTON_DISABLED_COLOR = (50, 50, 50)
BUTTON_DISABLED_TEXT_COLOR = (100, 100, 100)
BUTTON_WARN_COLOR = (180, 50, 50)
BUTTON_WARN_HOVER_COLOR = (210, 80, 80)

# --- Font Settings ---
pygame.font.init()
FONT_NAME = "arial"
try:
    if "arial" not in pygame.font.get_fonts():
        print("Arial font not found, using Pygame default font.")
        FONT_NAME = None
except Exception as e:
    print(f"Font initialization error: {e}. Using Pygame default font.")
    FONT_NAME = None

STATUS_FONT_SIZE = 22
BUTTON_FONT_SIZE = 20
GAME_OVER_FONT_SIZE = 48
CONFIRM_MSG_FONT_SIZE = 24

# --- Game Modes & AI ---
MODE_PVP = "Player vs Player"
MODE_PVA = "Player vs AI"
AI_DIFFICULTIES = ["Easy", "Medium", "Hard", "Unbeatable"]
DEFAULT_GAME_MODE = MODE_PVP
DEFAULT_AI_DIFFICULTY = AI_DIFFICULTIES[1] # Medium

# --- Asset Loading ---
ASSET_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets')
IMAGE_PATH = os.path.join(ASSET_PATH, 'images', 'pieces')
SOUND_PATH = os.path.join(ASSET_PATH, 'sounds') # Path to sounds folder

PIECE_IMAGES = {
    'wP': 'wP.png', 'wR': 'wR.png', 'wN': 'wN.png', 'wB': 'wB.png', 'wQ': 'wQ.png', 'wK': 'wK.png',
    'bP': 'bP.png', 'bR': 'bR.png', 'bN': 'bN.png', 'bB': 'bB.png', 'bQ': 'bQ.png', 'bK': 'bK.png'
}

# --- Sound Effect Files ---
# Using keys that describe the action
SOUND_FILES = {
    'button_click': 'buttons.wav',
    'piece_select': 'select.wav',
    'piece_deselect': 'deselect.wav', # Or use the same as select if you prefer
    'piece_move': 'move.wav',
    # Add more sounds later e.g. 'capture.wav', 'check.wav'
}
