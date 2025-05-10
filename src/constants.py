# src/constants.py

import pygame
import os

# --- Main Dimensions ---
BOARD_WIDTH, BOARD_HEIGHT = 800, 800  # Chessboard area
SIDE_PANEL_WIDTH = 250               # Width for the new side panel
# INFO_PANEL_HEIGHT = 50             # REMOVED - Integrating status into side panel

# Total window dimensions
WIDTH = BOARD_WIDTH + SIDE_PANEL_WIDTH
HEIGHT = BOARD_HEIGHT                # Window height is now just the board height

# Board dimensions (for calculations within the board area)
ROWS, COLS = 8, 8
SQUARE_SIZE = BOARD_WIDTH // COLS # Squares are based on BOARD_WIDTH

# Colors (RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0) # For background fill if needed outside board/panel
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (100, 255, 100, 150) # RGBA for selected square

SIDE_PANEL_BG_COLOR = (50, 50, 50) 
TEXT_COLOR = (230, 230, 230)
GAME_OVER_BG_COLOR = (40, 40, 40, 220) 

BUTTON_COLOR = (70, 70, 90)
BUTTON_HOVER_COLOR = (100, 100, 120)
BUTTON_TEXT_COLOR = (220, 220, 220)
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

# --- Asset Loading ---
ASSET_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets')
IMAGE_PATH = os.path.join(ASSET_PATH, 'images', 'pieces')

PIECE_IMAGES = {
    'wP': 'wP.png', 'wR': 'wR.png', 'wN': 'wN.png', 'wB': 'wB.png', 'wQ': 'wQ.png', 'wK': 'wK.png',
    'bP': 'bP.png', 'bR': 'bR.png', 'bN': 'bN.png', 'bB': 'bB.png', 'bQ': 'bQ.png', 'bK': 'bK.png'
}
