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
import src.assets_manager

AI_MOVE_EVENT = pygame.USEREVENT + 1

def run_game():
    pygame.init()
    print("Pygame initialized.")

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Unbeatable Chess")
    print(f"Screen setup complete: {WIDTH}x{HEIGHT}")

    src.assets_manager.load_images() 
    src.assets_manager.load_sounds()
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

            # Pass MOUSEMOTION to buttons for hover effects.
            # Button click actions are now initiated from board.handle_button_events
            # if it returns True for a MOUSEBUTTONDOWN event.
            button_was_clicked_and_actioned = board.handle_button_events(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    if not button_was_clicked_and_actioned: # If no main UI button handled the click
                        if not board.is_animating: 
                            # board.handle_click_on_board_or_dialog will check confirmation dialog first, then board
                            board.handle_click_on_board_or_dialog(mouse_pos) 
            
            if event.type == AI_MOVE_EVENT: 
                if not board.is_animating: 
                    board._trigger_ai_move()
        
        board.update() 
        board.draw(screen) 
        pygame.display.flip()
        clock.tick(60) 

    board.close_engine() 
    print("Exiting game loop. Quitting Pygame.")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    run_game()
