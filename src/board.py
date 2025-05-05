# src/board.py

import pygame
import chess

from .constants import ROWS, COLS, SQUARE_SIZE, LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT_COLOR
from .assets_manager import get_piece_image

class Board:
    """
    Represents the chessboard, handles drawing, selection,
    and manages the underlying python-chess board state.
    """

    def __init__(self):
        """Initializes the board state."""

        # --- Visual Representation ---
        # 2D list holding piece notations ('wP', 'bN', None) for drawing
        self.visual_board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.setup_visual_pieces() # Populate visual_board

        # --- Logical Representation (python-chess) ---
        # Create an instance of the python-chess board
        self.chess_board = chess.Board() # Starts in the standard initial position

        # --- Selection State ---
        self.selected_square = None # Stores the (row, col) of the selected square, or None
        self.valid_moves = []       # List to store valid move destinations for the selected piece (as (row, col))

        # --- Game State ---
        self.turn = 'w' # Start with white's turn ('w' or 'b')

    def setup_visual_pieces(self):
        """Populates the visual_board with piece notations for drawing."""

        # Standard chess starting position
        self.visual_board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]

        # We don't need to manually set up self.chess_board,
        # as chess.Board() initializes to the standard starting position.
        # We just need to ensure visual_board matches initially.

    def get_row_col_from_mouse(self, pos):
        """Converts mouse coordinates (x, y) to board row and column."""
        x, y = pos

        # Ensure coordinates are within the board boundaries
        if 0 <= x < COLS * SQUARE_SIZE and 0 <= y < ROWS * SQUARE_SIZE:
            row = y // SQUARE_SIZE
            col = x // SQUARE_SIZE
            return row, col
        
        return None # Return None if click is outside the board

    def select_square(self, row, col):
        """Handles logic when a square (row, col) is clicked."""
        clicked_piece_notation = self.visual_board[row][col]

        # --- Case 1: No piece currently selected ---
        if self.selected_square is None:
            # Check if the clicked square has a piece and if it's the current player's turn

            if clicked_piece_notation is not None and clicked_piece_notation[0] == self.turn:
                self.selected_square = (row, col)

                # Calculate valid moves for this piece (we'll implement this next)
                # self.valid_moves = self._calculate_valid_moves(row, col)
                print(f"Selected piece: {clicked_piece_notation} at ({row}, {col})") # Debug

            else:
                # Clicked on empty square or opponent's piece when nothing was selected
                self.selected_square = None
                self.valid_moves = []

                print("Selection cleared or invalid initial selection.") # Debug

        # --- Case 2: A piece IS currently selected ---
        else:
            # We'll add move logic here later. For now, clicking anywhere else
            # will either select a *different* piece of the player's color
            # or simply deselect the current piece.

            # If the newly clicked square has a piece of the current player's color
            if clicked_piece_notation is not None and clicked_piece_notation[0] == self.turn:

                 # If it's the *same* square, deselect
                if (row, col) == self.selected_square:
                    self.selected_square = None
                    self.valid_moves = []

                    print("Deselected same square.") # Debug
                else:
                    # Select the new piece instead
                    self.selected_square = (row, col)

                    # self.valid_moves = self._calculate_valid_moves(row, col) # Calculate new moves
                    print(f"Selected different piece: {clicked_piece_notation} at ({row}, {col})") # Debug
            else:
                # Clicked on an empty square or an opponent's piece while having a selection.
                # For now, this just deselects. Later, this will check if it's a valid move.
                self.selected_square = None
                self.valid_moves = []

                print("Selection cleared.") # Debug


    # --- Drawing Methods ---
    def draw_squares(self, screen):
        """Draws the alternating light and dark squares of the board."""

        for r in range(ROWS):
            for c in range(COLS):
                color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(screen, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self, screen):
        """Draws the pieces onto the board based on the visual_board state."""

        for r in range(ROWS):
            for c in range(COLS):
                piece = self.visual_board[r][c]
                if piece is not None:
                    image = get_piece_image(piece)
                    if image:
                        # Center the piece image within the square (optional, adjust as needed)
                        img_rect = image.get_rect(center=(c * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                          r * SQUARE_SIZE + SQUARE_SIZE // 2))
                        screen.blit(image, img_rect.topleft)

    def draw_highlights(self, screen):
        """Draws highlights for the selected square and valid moves."""

        # Highlight selected square
        if self.selected_square is not None:
            row, col = self.selected_square

            # Create a temporary surface for transparency
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

            # Fill with the highlight color (including alpha)
            highlight_surface.fill(HIGHLIGHT_COLOR)
            
            # Blit this temporary surface onto the main screen
            screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Highlight valid moves (add later when self.valid_moves is populated)
        # for move_row, move_col in self.valid_moves:
        #     pygame.draw.circle(screen, RED,
        #                        (move_col * SQUARE_SIZE + SQUARE_SIZE // 2, move_row * SQUARE_SIZE + SQUARE_SIZE // 2),
        #                        SQUARE_SIZE // 6) # Draw small circles for valid moves

    def draw(self, screen):
        """Draws the entire board including squares, pieces, and highlights."""
        self.draw_squares(screen)
        self.draw_pieces(screen)
        self.draw_highlights(screen) # Draw highlights on top

    # --- Add functions later for: ---
    # - _calculate_valid_moves(row, col) using self.chess_board
    # - move_piece(from_sq, to_sq) updating both visual_board and chess_board