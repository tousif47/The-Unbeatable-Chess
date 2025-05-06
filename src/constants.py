# src/constants.py

import pygame
import os # Import os to help with file paths

# Screen dimensions
WIDTH, HEIGHT = 800, 800

# Board dimensions
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors (RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0) # For valid move highlights
RED = (255, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (100, 255, 100, 150) # RGBA for selected square

# --- Piece Representation ---
# 'wP', 'bN', etc. None for empty.

# --- Asset Loading ---
# __file__ is the path to the current file (constants.py)
# os.path.dirname(__file__) is the directory of the current file (src/)
# os.path.join(..., '..', 'assets') goes one level up from src/ and then into assets/
ASSET_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets')
IMAGE_PATH = os.path.join(ASSET_PATH, 'images', 'pieces')

# Map piece notation to image filenames
PIECE_IMAGES = {
    'wP': 'wP.png', 'wR': 'wR.png', 'wN': 'wN.png', 'wB': 'wB.png', 'wQ': 'wQ.png', 'wK': 'wK.png',
    'bP': 'bP.png', 'bR': 'bR.png', 'bN': 'bN.png', 'bB': 'bB.png', 'bQ': 'bQ.png', 'bK': 'bK.png'
}

# Ensure this file has an __init__.py in the same directory (src/)
# if it's part of a package.