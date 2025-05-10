# src/main.py

import pygame
import sys
import os

# --- Path Setup ---
try:
    if __package__ is None or __package__ == '':
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        if project_root not in sys.path: sys.path.insert(0, project_root)
        if current_dir not in sys.path: sys.path.insert(0, current_dir)
except NameError: # Fallback for older Pythons or unusual execution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path: sys.path.insert(0, project_root)
    if current_dir not in sys.path: sys.path.insert(0, current_dir)

from src.constants import WIDTH, HEIGHT # These are now TOTAL_WIDTH, TOTAL_HEIGHT effectively
from src.board import Board
import src.assets_manager

def run_game():
    pygame.init()
    print("Pygame initialized.")

    # Use WIDTH and HEIGHT from constants (which now include side panel)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Unbeatable Chess")
    print(f"Screen setup complete: {WIDTH}x{HEIGHT}")

    src.assets_manager.load_images() # Load after display mode is set
    print("Asset loading explicitly called.")

    try:
        board = Board()
        print("Board object created.")
    except Exception as e:
        print(f"Error creating Board object: {e}")
        pygame.quit()
        sys.exit()

    clock = pygame.time.Clock()
    running = True
    print("Starting game loop...")
    while running:
        mouse_pos = pygame.mouse.get_pos() # Get mouse position for hover effects

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False # Exit signal from Board's Exit button will also trigger this

            # Pass events to board's buttons for hover effects
            board.handle_button_events(event) # For main UI buttons

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    board.handle_click(mouse_pos) # Centralized click handling in Board

        # --- Game Logic (already handled by board interactions) ---

        # --- Drawing ---
        board.draw(screen) # Board's draw method now handles all game elements
        pygame.display.flip()

        # --- Frame Rate Control ---
        clock.tick(60) # Aim for 60 FPS

    print("Exiting game loop. Quitting Pygame.")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    run_game()
