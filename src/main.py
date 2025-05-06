# src/main.py

import pygame
import sys
import os

# --- Path Setup ---
try:
    if __package__ is None or __package__ == '':
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        if current_dir not in sys.path:
             sys.path.insert(0, current_dir)
except NameError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if current_dir not in sys.path:
         sys.path.insert(0, current_dir)

# Now, absolute imports from 'src' should work reliably
from src.constants import WIDTH, HEIGHT
from src.board import Board
import src.assets_manager # Import the module

def run_game():
    """Initializes Pygame, sets up the screen, loads assets, and runs the main game loop."""
    # --- Initialization ---
    pygame.init()
    print("Pygame initialized.")

    # --- Screen Setup ---
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Unbeatable Chess")
    print("Screen setup complete.")

    # --- Load Assets ---
    # CRITICAL: Load images AFTER the display has been set up.
    src.assets_manager.load_images()
    print("Asset loading explicitly called.")

    # --- Create Board Object ---
    try:
        board = Board() # Board init will use get_piece_image, which now relies on LOADED_ASSETS
        print("Board object created.")
    except Exception as e:
        print(f"Error creating Board object: {e}")
        pygame.quit()
        sys.exit()

    # --- Clock for controlling frame rate ---
    clock = pygame.time.Clock()

    # --- Game Loop ---
    running = True
    print("Starting game loop...")
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    mouse_pos = event.pos
                    board_coords = board.get_row_col_from_mouse(mouse_pos)
                    if board_coords:
                        row, col = board_coords
                        board.select_square(row, col)
                    # else: print("Clicked outside board.")

        # --- Drawing ---
        board.draw(screen)

        # --- Update Display ---
        pygame.display.flip()

        # --- Frame Rate Control ---
        clock.tick(60)

    # --- Quit ---
    print("Exiting game loop. Quitting Pygame.")
    pygame.quit()
    sys.exit()

# --- Main Execution Guard ---
if __name__ == '__main__':
    run_game()
