# src/board.py

import pygame
# Corrected: Absolute imports from the 'src' package
from src.constants import ROWS, COLS, SQUARE_SIZE, LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT_COLOR, RED, GREEN
from src.assets_manager import get_piece_image # This should now work if assets_manager loads correctly
import chess

class Board:
    """
    Represents the chessboard, handles drawing, selection,
    and manages the underlying python-chess board state.
    """

    def __init__(self):
        """Initializes the board state."""
        self.visual_board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.chess_board = chess.Board() # Standard initial position
        self.setup_visual_pieces() # Populate visual_board based on chess_board

        self.selected_square_coords = None
        self.valid_moves_coords = []

    def setup_visual_pieces(self):
        """Populates the visual_board based on the python-chess board's current state."""
        for r in range(ROWS):
            for c in range(COLS):
                sq_index = self._coords_to_chess_sq(r, c)
                piece = self.chess_board.piece_at(sq_index)
                if piece:
                    color_prefix = 'w' if piece.color == chess.WHITE else 'b'
                    piece_symbol = piece.symbol().upper()
                    self.visual_board[r][c] = color_prefix + piece_symbol
                else:
                    self.visual_board[r][c] = None

    def _coords_to_chess_sq(self, row, col):
        """Converts (row, col) from our visual board to a chess.Square index."""
        return chess.square(col, ROWS - 1 - row)

    def _chess_sq_to_coords(self, sq_index):
        """Converts a chess.Square index to (row, col) for our visual board."""
        if sq_index is None:
            return None
        col = chess.square_file(sq_index)
        row = ROWS - 1 - chess.square_rank(sq_index)
        return row, col

    def get_row_col_from_mouse(self, pos):
        """Converts mouse coordinates (x, y) to board row and column."""
        x, y = pos
        if 0 <= x < COLS * SQUARE_SIZE and 0 <= y < ROWS * SQUARE_SIZE:
            row = y // SQUARE_SIZE
            col = x // SQUARE_SIZE
            return row, col
        return None

    def select_square(self, row, col):
        """Handles logic when a square (row, col) is clicked."""
        clicked_chess_sq = self._coords_to_chess_sq(row, col)
        piece_at_clicked_sq = self.chess_board.piece_at(clicked_chess_sq)
        current_player_color = chess.WHITE if self.chess_board.turn else chess.BLACK

        if self.selected_square_coords is None: # No piece currently selected
            if piece_at_clicked_sq and piece_at_clicked_sq.color == current_player_color:
                self.selected_square_coords = (row, col)
                self._calculate_valid_moves(row, col)
                print(f"Selected: {piece_at_clicked_sq.symbol()} at ({row},{col}). Valid moves: {self.valid_moves_coords}")
            # else: print("Invalid initial selection or empty square.")
        else: # A piece IS currently selected
            if (row, col) in self.valid_moves_coords: # Clicked on a valid move
                print(f"Attempting to move from {self.selected_square_coords} to ({row},{col})")
                # self.move_piece(self.selected_square_coords, (row, col)) # Next step
                self.selected_square_coords = None
                self.valid_moves_coords = []
            elif piece_at_clicked_sq and piece_at_clicked_sq.color == current_player_color: # Clicked another of own pieces
                if (row, col) == self.selected_square_coords: # Clicked same piece
                    self.selected_square_coords = None
                    self.valid_moves_coords = []
                    # print("Deselected same square.")
                else: # Selected a different piece
                    self.selected_square_coords = (row, col)
                    self._calculate_valid_moves(row, col)
                    print(f"Selected different: {piece_at_clicked_sq.symbol()} at ({row},{col}). Valid moves: {self.valid_moves_coords}")
            else: # Clicked on an empty square (not a valid move) or opponent's piece
                self.selected_square_coords = None
                self.valid_moves_coords = []
                # print("Selection cleared or invalid target.")

    def _calculate_valid_moves(self, row, col):
        """Calculates and stores valid move destination coordinates for the piece at (row, col)."""
        self.valid_moves_coords = []
        if self.selected_square_coords is None: # Should not happen if called correctly
            return

        from_sq_chess = self._coords_to_chess_sq(row, col)
        if self.chess_board.piece_at(from_sq_chess) is None: # No piece at selected square
             print(f"Warning: _calculate_valid_moves called on empty square ({row},{col})")
             return

        for move in self.chess_board.legal_moves:
            if move.from_square == from_sq_chess:
                to_coords = self._chess_sq_to_coords(move.to_square)
                if to_coords:
                    self.valid_moves_coords.append(to_coords)

    def draw_squares(self, screen):
        """Draws the alternating light and dark squares of the board."""
        for r_idx in range(ROWS):
            for c_idx in range(COLS):
                color = LIGHT_SQUARE if (r_idx + c_idx) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(screen, color, (c_idx * SQUARE_SIZE, r_idx * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self, screen):
        """Draws the pieces onto the board based on the visual_board state."""
        for r_idx in range(ROWS):
            for c_idx in range(COLS):
                piece_notation = self.visual_board[r_idx][c_idx]
                if piece_notation is not None:
                    image = get_piece_image(piece_notation) # Fetches from LOADED_ASSETS
                    if image:
                        img_rect = image.get_rect(center=(c_idx * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                          r_idx * SQUARE_SIZE + SQUARE_SIZE // 2))
                        screen.blit(image, img_rect.topleft)
                    # else:
                        # print(f"Warning: Image for piece '{piece_notation}' not found/loaded.")


    def draw_highlights(self, screen):
        """Draws highlights for the selected square and valid moves."""
        if self.selected_square_coords is not None:
            r, c = self.selected_square_coords
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight_surface.fill(HIGHLIGHT_COLOR)
            screen.blit(highlight_surface, (c * SQUARE_SIZE, r * SQUARE_SIZE))

        valid_move_highlight_color = GREEN
        for r_idx, c_idx in self.valid_moves_coords:
            center_x = c_idx * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = r_idx * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(screen, valid_move_highlight_color, (center_x, center_y), SQUARE_SIZE // 6)

    def draw(self, screen):
        """Draws the entire board including squares, pieces, and highlights."""
        self.draw_squares(screen)
        self.draw_pieces(screen)
        self.draw_highlights(screen)
