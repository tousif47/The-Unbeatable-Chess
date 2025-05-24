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
HIGHLIGHT_COLOR = (100, 255, 100, 150) # For selected square
CHECK_HIGHLIGHT_COLOR = (255, 50, 50, 150) # RGBA for king in check (translucent red)

SIDE_PANEL_BG_COLOR = (50, 50, 50)
TEXT_COLOR = (230, 230, 230) 
OVERLAY_TEXT_COLOR = (240, 240, 240) 
GAME_OVER_BG_COLOR = (40, 40, 40, 220)
TEXT_OVERLAY_BG_COLOR = (30, 30, 30, 230) 

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
OVERLAY_TITLE_FONT_SIZE = 36
OVERLAY_BODY_FONT_SIZE = 18
OVERLAY_LINE_SPACING = 5 

# --- Game Modes & AI ---
MODE_PVP = "Player vs Player"
MODE_PVA = "Player vs AI"

AI_DIFFICULTIES = ["Easiest", "Easy", "Medium", "Hard", "Unbeatable"]
STOCKFISH_SKILL_LEVELS = {
    "Easiest": 0, "Easy": 3, "Medium": 7, "Hard": 12, "Unbeatable": 20
}
DEFAULT_GAME_MODE = MODE_PVP
DEFAULT_AI_DIFFICULTY = AI_DIFFICULTIES[0] # Easiest

# --- Animation Settings ---
ANIMATION_SPEED = 30

# --- Asset Loading ---
ASSET_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets')
IMAGE_PATH = os.path.join(ASSET_PATH, 'images', 'pieces')
SOUND_PATH = os.path.join(ASSET_PATH, 'sounds')
TEXT_FILE_PATH = ASSET_PATH 

# --- Text File Names ---
RULES_FILENAME = "rules.txt"
ABOUT_FILENAME = "about.txt"

# --- Overlay Types ---
OVERLAY_NONE = 0
OVERLAY_RULES = 1
OVERLAY_ABOUT = 2
# OVERLAY_RESTART_CONFIRM (Handled by show_restart_confirmation flag)

PIECE_IMAGES = {
    'wP': 'wP.png', 'wR': 'wR.png', 'wN': 'wN.png', 'wB': 'wB.png', 'wQ': 'wQ.png', 'wK': 'wK.png',
    'bP': 'bP.png', 'bR': 'bR.png', 'bN': 'bN.png', 'bB': 'bB.png', 'bQ': 'bQ.png', 'bK': 'bK.png'
}

SOUND_FILES = {
    'button_click': 'buttons.wav',
    'piece_select': 'select.wav',
    'piece_deselect': 'deselect.wav',
    'piece_move': 'move.wav',
    # Consider adding 'check.wav', 'game_over.wav' later
}

# --- Stockfish Engine Path ---
STOCKFISH_EXECUTABLE_NAME = "stockfish-windows-x86-64-avx2.exe"
STOCKFISH_PATH = os.path.join(os.path.dirname(__file__), '..', 'engine', STOCKFISH_EXECUTABLE_NAME)

if not os.path.exists(STOCKFISH_PATH):
    print(f"WARNING: Stockfish executable not found at {STOCKFISH_PATH}")
