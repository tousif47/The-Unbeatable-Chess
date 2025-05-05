# src/constants.py

import pygame
import os

# Screen dimensions
WIDTH, HEIGHT = 800, 800

# Board dimensions
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors (RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Chessboard colors (Example: Brown tones)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)

# Highlight color for selected square (e.g., a translucent yellow or green)
HIGHLIGHT_COLOR = (100, 255, 100, 150) # RGBA - Added alpha for transparency

# --- Piece Representation ---
# 'w' = white, 'b' = black
# 'P','R','N','B','Q','K'
# Example: 'wP', 'bN'
# None = empty square

# --- Asset Loading ---
ASSET_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets')
IMAGE_PATH = os.path.join(ASSET_PATH, 'images', 'pieces')

PIECE_IMAGES = {
    'wP': 'wP.png', 'wR': 'wR.png', 'wN': 'wN.png', 'wB': 'wB.png', 'wQ': 'wQ.png', 'wK': 'wK.png',
    'bP': 'bP.png', 'bR': 'bR.png', 'bN': 'bN.png', 'bB': 'bB.png', 'bQ': 'bQ.png', 'bK': 'bK.png'
}