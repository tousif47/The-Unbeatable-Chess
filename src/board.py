# src/board.py

import pygame
import sys
from src.constants import (ROWS, COLS, SQUARE_SIZE, BOARD_WIDTH, BOARD_HEIGHT, SIDE_PANEL_WIDTH,
                           WIDTH, HEIGHT,
                           LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT_COLOR, GREEN, BLACK,
                           SIDE_PANEL_BG_COLOR, TEXT_COLOR, GAME_OVER_BG_COLOR,
                           BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
                           BUTTON_DISABLED_COLOR, BUTTON_DISABLED_TEXT_COLOR,
                           BUTTON_WARN_COLOR, BUTTON_WARN_HOVER_COLOR,
                           FONT_NAME, STATUS_FONT_SIZE, GAME_OVER_FONT_SIZE, CONFIRM_MSG_FONT_SIZE,
                           MODE_PVP, MODE_PVA, AI_DIFFICULTIES, DEFAULT_GAME_MODE, DEFAULT_AI_DIFFICULTY)
from src.assets_manager import get_piece_image, play_sound
from src.ui_elements import Button
import chess

class Board:
    def __init__(self):
        self.chess_board = chess.Board()
        self.visual_board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self._sync_visual_board()

        self.selected_square_coords = None
        self.valid_moves_coords = []

        self.game_over = False
        self.game_over_message = ""
        self.status_message = ""

        self.game_mode = DEFAULT_GAME_MODE
        self.ai_difficulty_index = AI_DIFFICULTIES.index(DEFAULT_AI_DIFFICULTY)
        self.current_ai_difficulty = AI_DIFFICULTIES[self.ai_difficulty_index]

        try:
            if not pygame.font.get_init(): pygame.font.init()
            self.status_font = pygame.font.SysFont(FONT_NAME, STATUS_FONT_SIZE)
            self.game_over_font = pygame.font.SysFont(FONT_NAME, GAME_OVER_FONT_SIZE)
            self.confirm_font = pygame.font.SysFont(FONT_NAME, CONFIRM_MSG_FONT_SIZE)
        except Exception as e:
            print(f"Error initializing fonts: {e}. Using default font.")
            self.status_font = pygame.font.Font(None, STATUS_FONT_SIZE)
            self.game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
            self.confirm_font = pygame.font.Font(None, CONFIRM_MSG_FONT_SIZE)

        self.buttons = []
        self._setup_buttons() 
        self.show_restart_confirmation = False
        self._update_status_message()

    def _setup_buttons(self):
        self.buttons = []
        panel_x = BOARD_WIDTH + 20
        button_width = SIDE_PANEL_WIDTH - 40
        button_height = 40
        spacing = 15
        current_y = 30 
        current_y += 30 

        self.restart_button = Button(panel_x, current_y, button_width, button_height,
                                     text="Restart Game", action=self._handle_restart_click)
        self.buttons.append(self.restart_button)
        current_y += button_height + spacing

        self.game_mode_button = Button(panel_x, current_y, button_width, button_height,
                                       text=f"Mode: {self.game_mode}", action=self._toggle_game_mode)
        self.buttons.append(self.game_mode_button)
        current_y += button_height + spacing

        self.ai_difficulty_button = Button(panel_x, current_y, button_width, button_height,
                                           text="AI Difficulty", 
                                           action=self._cycle_ai_difficulty)
        self.buttons.append(self.ai_difficulty_button)
        current_y += button_height + spacing
        
        self.exit_button = Button(panel_x, current_y, button_width, button_height,
                                  text="Exit Game", action=self._handle_exit_click)
        self.buttons.append(self.exit_button)
        self._update_ai_difficulty_button_state()

        confirm_btn_y = BOARD_HEIGHT // 2 + 20 
        self.confirm_yes_button = Button(BOARD_WIDTH // 2 - 110, confirm_btn_y, 100, 40, "Yes",
                                         color=BUTTON_WARN_COLOR, hover_color=BUTTON_WARN_HOVER_COLOR,
                                         text_color=BUTTON_TEXT_COLOR, action=self.restart_game)
        self.confirm_no_button = Button(BOARD_WIDTH // 2 + 10, confirm_btn_y, 100, 40, "No",
                                        color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                        text_color=BUTTON_TEXT_COLOR, action=self._cancel_restart_confirmation)

    def _toggle_game_mode(self):
        play_sound('button_click') 
        if self.game_mode == MODE_PVP:
            self.game_mode = MODE_PVA
        else:
            self.game_mode = MODE_PVP
        self.game_mode_button.update_text(f"Mode: {self.game_mode}")
        self._update_ai_difficulty_button_state()
        self.restart_game() 
        print(f"Game mode changed to: {self.game_mode}")

    def _cycle_ai_difficulty(self):
        if self.game_mode == MODE_PVA:
            play_sound('button_click') 
            self.ai_difficulty_index = (self.ai_difficulty_index + 1) % len(AI_DIFFICULTIES)
            self.current_ai_difficulty = AI_DIFFICULTIES[self.ai_difficulty_index]
            self.ai_difficulty_button.update_text(f"AI: {self.current_ai_difficulty}")
            print(f"AI difficulty changed to: {self.current_ai_difficulty}")

    def _update_ai_difficulty_button_state(self):
        if self.game_mode == MODE_PVA:
            self.ai_difficulty_button.set_enabled(True)
            self.ai_difficulty_button.update_text(f"AI: {self.current_ai_difficulty}")
        else:
            self.ai_difficulty_button.set_enabled(False)
            self.ai_difficulty_button.update_text("AI Difficulty (PvP)")

    def _handle_restart_click(self):
        play_sound('button_click') 
        if not self.game_over and self.chess_board.move_stack:
            self.show_restart_confirmation = True
        else:
            self.restart_game()

    def _handle_exit_click(self):
        play_sound('button_click') 
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _cancel_restart_confirmation(self):
        play_sound('button_click') 
        self.show_restart_confirmation = False

    def restart_game(self):
        self.chess_board.reset()
        self._sync_visual_board()
        self.selected_square_coords = None
        self.valid_moves_coords = []
        self.game_over = False
        self.game_over_message = ""
        self.show_restart_confirmation = False
        self._update_status_message()
        print("Game restarted.")

    def _sync_visual_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                sq_index = self._coords_to_chess_sq(r, c)
                piece = self.chess_board.piece_at(sq_index)
                self.visual_board[r][c] = (f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().upper()}"
                                           if piece else None)

    def _coords_to_chess_sq(self, row, col):
        return chess.square(col, ROWS - 1 - row)

    def _chess_sq_to_coords(self, sq_index):
        if sq_index is None: return None
        return ROWS - 1 - chess.square_rank(sq_index), chess.square_file(sq_index)

    def get_row_col_from_mouse(self, pos):
        x, y = pos
        if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
            row = y // SQUARE_SIZE
            col = x // SQUARE_SIZE
            return row, col
        return None

    def handle_click(self, pos):
        if self.show_restart_confirmation:
            if self.confirm_yes_button.rect.collidepoint(pos):
                if self.confirm_yes_button.action: 
                    play_sound('button_click') 
                    self.confirm_yes_button.action()
                return
            if self.confirm_no_button.rect.collidepoint(pos):
                if self.confirm_no_button.action: 
                    self.confirm_no_button.action() # Sound is in _cancel_restart_confirmation
                return
            # If click is on confirmation dialog but not on its buttons, do nothing
            # to prevent clicks "through" the dialog.
            return

        for button in self.buttons:
            if button.rect.collidepoint(pos):
                if button.enabled and button.action: 
                    # Specific button sounds are handled in their respective action methods
                    # (e.g., _handle_restart_click, _toggle_game_mode)
                    button.action()
                elif not button.enabled:
                    print(f"Button '{button.text}' is disabled.")
                return

        board_coords = self.get_row_col_from_mouse(pos)
        if board_coords:
            self.select_square(*board_coords)

    def select_square(self, row, col):
        if self.game_over: return
        if self.game_mode == MODE_PVA and self.chess_board.turn == chess.BLACK: 
            return

        clicked_chess_sq = self._coords_to_chess_sq(row, col)
        piece_at_clicked_sq = self.chess_board.piece_at(clicked_chess_sq)
        current_player_color = chess.WHITE if self.chess_board.turn else chess.BLACK
        
        previously_selected = self.selected_square_coords is not None

        if self.selected_square_coords is None: 
            if piece_at_clicked_sq and piece_at_clicked_sq.color == current_player_color:
                self.selected_square_coords = (row, col)
                self._calculate_valid_moves(row, col)
                play_sound('piece_select')
        else: 
            from_r, from_c = self.selected_square_coords
            if (row, col) in self.valid_moves_coords: 
                self.move_piece((from_r, from_c), (row, col)) 
            elif piece_at_clicked_sq and piece_at_clicked_sq.color == current_player_color: 
                if (row, col) == self.selected_square_coords: 
                    self.selected_square_coords = None
                    self.valid_moves_coords = []
                    play_sound('piece_deselect')
                else: 
                    self.selected_square_coords = (row, col)
                    self._calculate_valid_moves(row, col)
                    play_sound('piece_select') 
            else: 
                self.selected_square_coords = None
                self.valid_moves_coords = []
                if previously_selected: 
                    play_sound('piece_deselect')


    def _calculate_valid_moves(self, row, col):
        self.valid_moves_coords = []
        if self.selected_square_coords is None: return
        from_sq_chess = self._coords_to_chess_sq(row, col)
        if self.chess_board.piece_at(from_sq_chess) is None: return
        for move in self.chess_board.legal_moves:
            if move.from_square == from_sq_chess:
                to_coords = self._chess_sq_to_coords(move.to_square)
                if to_coords: self.valid_moves_coords.append(to_coords)

    def move_piece(self, from_coords, to_coords):
        if self.game_over: return
        from_sq_chess = self._coords_to_chess_sq(*from_coords)
        to_sq_chess = self._coords_to_chess_sq(*to_coords)
        piece = self.chess_board.piece_at(from_sq_chess)
        promo = chess.QUEEN if piece and piece.piece_type == chess.PAWN and \
                               ((piece.color == chess.WHITE and to_coords[0] == 0) or \
                                (piece.color == chess.BLACK and to_coords[0] == 7)) else None
        move = chess.Move(from_sq_chess, to_sq_chess, promotion=promo)

        if move in self.chess_board.legal_moves:
            self.chess_board.push(move)
            play_sound('piece_move') 
            self._sync_visual_board()
            self._update_status_message() 
            self._check_game_over()      

            if not self.game_over and self.game_mode == MODE_PVA and self.chess_board.turn == chess.BLACK: 
                print("AI's turn - (AI move logic to be implemented here)")
        
        self.selected_square_coords = None
        self.valid_moves_coords = []

    def _update_status_message(self):
        if self.game_over: 
            self.status_message = "" 
            return
        
        player_turn_text = ""
        if self.game_mode == MODE_PVP:
            player_turn_text = "White's Turn" if self.chess_board.turn == chess.WHITE else "Black's Turn"
        elif self.game_mode == MODE_PVA:
            player_turn_text = "Your Turn (White)" if self.chess_board.turn == chess.WHITE else "AI's Turn (Black)"
        
        self.status_message = f"{player_turn_text}{' - CHECK!' if self.chess_board.is_check() else ''}"

    def _check_game_over(self):
        outcome = self.chess_board.outcome()
        if outcome:
            self.game_over = True
            if outcome.termination == chess.Termination.CHECKMATE:
                winner_color = "White" if outcome.winner == chess.WHITE else "Black"
                if self.game_mode == MODE_PVA:
                    winner_display = "You Win!" if outcome.winner == chess.WHITE else "AI Wins!"
                    self.game_over_message = f"CHECKMATE! {winner_display}"
                else:
                    self.game_over_message = f"CHECKMATE! {winner_color} wins."
            elif outcome.termination == chess.Termination.STALEMATE:
                self.game_over_message = "STALEMATE! Draw."
            elif outcome.termination == chess.Termination.INSUFFICIENT_MATERIAL:
                self.game_over_message = "DRAW! Insufficient Material."
            elif outcome.termination == chess.Termination.SEVENTYFIVE_MOVES:
                self.game_over_message = "DRAW! 75-move rule."
            elif outcome.termination == chess.Termination.FIVEFOLD_REPETITION:
                self.game_over_message = "DRAW! Fivefold repetition."
            else: 
                self.game_over_message = "GAME OVER! Draw."
            self.status_message = "" 

    # --- Drawing Methods ---
    def draw_board_area(self, screen):
        for r_idx in range(ROWS):
            for c_idx in range(COLS):
                color = LIGHT_SQUARE if (r_idx + c_idx) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(screen, color, (c_idx * SQUARE_SIZE, r_idx * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        for r_idx in range(ROWS):
            for c_idx in range(COLS):
                piece_notation = self.visual_board[r_idx][c_idx]
                if piece_notation:
                    image = get_piece_image(piece_notation)
                    if image:
                        img_rect = image.get_rect(center=(c_idx * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                          r_idx * SQUARE_SIZE + SQUARE_SIZE // 2))
                        screen.blit(image, img_rect.topleft)
        
        if self.selected_square_coords:
            r, c = self.selected_square_coords
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight_surface.fill(HIGHLIGHT_COLOR)
            screen.blit(highlight_surface, (c * SQUARE_SIZE, r * SQUARE_SIZE))

        for r_idx, c_idx in self.valid_moves_coords:
            center_x = c_idx * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = r_idx * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(screen, GREEN, (center_x, center_y), SQUARE_SIZE // 6)

    def draw_side_panel(self, screen):
        panel_rect = pygame.Rect(BOARD_WIDTH, 0, SIDE_PANEL_WIDTH, HEIGHT)
        pygame.draw.rect(screen, SIDE_PANEL_BG_COLOR, panel_rect)

        if not self.game_over:
            self._update_status_message() 

        if self.status_message: 
             text_surface = self.status_font.render(self.status_message, True, TEXT_COLOR)
             status_text_y_center = 30 
             text_rect = text_surface.get_rect(center=(BOARD_WIDTH + SIDE_PANEL_WIDTH // 2, status_text_y_center))
             screen.blit(text_surface, text_rect)
        
        for button in self.buttons:
            button.draw(screen)

    def draw_game_over_display(self, screen):
        if self.game_over and self.game_over_message:
            overlay_rect = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT)
            overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
            overlay_surface.fill(GAME_OVER_BG_COLOR)
            text_surface = self.game_over_font.render(self.game_over_message, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(overlay_rect.width // 2, overlay_rect.height // 2))
            overlay_surface.blit(text_surface, text_rect)
            screen.blit(overlay_surface, overlay_rect.topleft)

    def draw_restart_confirmation_dialog(self, screen):
        if self.show_restart_confirmation:
            overlay_rect = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT)
            overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
            overlay_surface.fill(GAME_OVER_BG_COLOR) 

            msg = "Restart game?"
            msg_surface = self.confirm_font.render(msg, True, TEXT_COLOR)
            msg_rect = msg_surface.get_rect(center=(overlay_rect.width // 2, overlay_rect.height // 2 - 40))
            overlay_surface.blit(msg_surface, msg_rect)
            
            yes_btn_rect_local = pygame.Rect(overlay_rect.width // 2 - 110, overlay_rect.height // 2 + 20, 100, 40)
            yes_hover = self.confirm_yes_button.rect.collidepoint(pygame.mouse.get_pos())
            yes_color = self.confirm_yes_button.base_hover_color if yes_hover else self.confirm_yes_button.base_color
            pygame.draw.rect(overlay_surface, yes_color, yes_btn_rect_local, border_radius=5)
            # Use base_text_color from the Button object for rendering text
            yes_text = self.confirm_font.render("Yes", True, self.confirm_yes_button.base_text_color) 
            overlay_surface.blit(yes_text, yes_text.get_rect(center=yes_btn_rect_local.center))
            
            no_btn_rect_local = pygame.Rect(overlay_rect.width // 2 + 10, overlay_rect.height // 2 + 20, 100, 40)
            no_hover = self.confirm_no_button.rect.collidepoint(pygame.mouse.get_pos())
            no_color = self.confirm_no_button.base_hover_color if no_hover else self.confirm_no_button.base_color
            pygame.draw.rect(overlay_surface, no_color, no_btn_rect_local, border_radius=5)
            # Use base_text_color from the Button object for rendering text
            no_text = self.confirm_font.render("No", True, self.confirm_no_button.base_text_color) 
            overlay_surface.blit(no_text, no_text.get_rect(center=no_btn_rect_local.center))
            
            screen.blit(overlay_surface, overlay_rect.topleft)

    def draw(self, screen):
        screen.fill(SIDE_PANEL_BG_COLOR) 
        self.draw_board_area(screen)     
        self.draw_side_panel(screen)     
        self.draw_game_over_display(screen) 
        self.draw_restart_confirmation_dialog(screen)

    def handle_button_events(self, event):
        for button in self.buttons:
            button.handle_event(event)
