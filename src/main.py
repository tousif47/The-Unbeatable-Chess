# src/main.py

import pygame
import sys
import os

# Import constants and the Board class
try:
    from .constants import WIDTH, HEIGHT
    from .board import Board

except ImportError:
    # Adjust path if running directly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from src.constants import WIDTH, HEIGHT
    from src.board import Board

def run_game():
    # --- Initialization ---
    pygame.init()

    # --- Screen Setup ---
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Unbeatable Chess")

    # --- Create Board Object ---
    board = Board()

    # --- Clock for controlling frame rate (optional but good practice) ---
    clock = pygame.time.Clock()

    # --- Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check for mouse button click
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Get mouse position (x, y)
                mouse_pos = event.pos

                # Convert mouse position to board coordinates (row, col)
                board_coords = board.get_row_col_from_mouse(mouse_pos)

                if board_coords: # Check if the click was within the board
                    row, col = board_coords

                    # Call the board's selection logic
                    board.select_square(row, col)
                else:
                    # Clicked outside the board, maybe deselect? (Optional)
                    # board.select_square(None, None) # Or handle UI clicks
                    print("Clicked outside board.")


        # --- Drawing ---
        # The board object handles all drawing
        board.draw(screen)

        # --- Update Display ---
        pygame.display.flip()

        # --- Frame Rate Control ---
        clock.tick(60) # Limit game to 60 frames per second

    # --- Quit ---
    pygame.quit()
    sys.exit()

# --- Main Execution ---
if __name__ == '__main__':
    run_game()