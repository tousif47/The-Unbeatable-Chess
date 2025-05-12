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
except NameError: 
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path: sys.path.insert(0, project_root)
    if current_dir not in sys.path: sys.path.insert(0, current_dir)

from src.constants import WIDTH, HEIGHT
from src.board import Board
import src.assets_manager # Import the module

def run_game():
    # --- Initialization ---
    pygame.init() # Initializes all Pygame modules, including mixer by default
    print("Pygame initialized.")

    # --- Screen Setup ---
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Unbeatable Chess")
    print(f"Screen setup complete: {WIDTH}x{HEIGHT}")

    # --- Load Assets ---
    src.assets_manager.load_images() # Load after display mode is set
    src.assets_manager.load_sounds() # Load sounds after mixer is initialized
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
        mouse_pos = pygame.mouse.get_pos() 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 

            board.handle_button_events(event) 

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    board.handle_click(mouse_pos) 
        
        board.draw(screen) 
        pygame.display.flip()
        clock.tick(60) 

    print("Exiting game loop. Quitting Pygame.")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    run_game()
