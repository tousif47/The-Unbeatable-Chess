# src/board.py

import pygame
import sys
import math 
import time 
import os 
from src.constants import (ROWS, COLS, SQUARE_SIZE, BOARD_WIDTH, BOARD_HEIGHT, SIDE_PANEL_WIDTH,
                           WIDTH, HEIGHT,
                           LIGHT_SQUARE, DARK_SQUARE, SELECTED_SQUARE_HIGHLIGHT_COLOR, 
                           VALID_MOVE_DOT_COLOR, 
                           BLACK, CHECK_HIGHLIGHT_COLOR, 
                           SIDE_PANEL_BG_COLOR, TEXT_COLOR, OVERLAY_TEXT_COLOR, GAME_OVER_BG_COLOR, TEXT_OVERLAY_BG_COLOR,
                           PROMOTION_OVERLAY_BG_COLOR, AI_CONFIRM_OVERLAY_BG_COLOR, 
                           BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
                           BUTTON_DISABLED_COLOR, BUTTON_DISABLED_TEXT_COLOR,
                           BUTTON_WARN_COLOR, BUTTON_WARN_HOVER_COLOR,
                           BUTTON_PLAY_COLOR, BUTTON_PLAY_HOVER_COLOR, 
                           FONT_NAME, STATUS_FONT_SIZE, BUTTON_FONT_SIZE, GAME_OVER_FONT_SIZE, CONFIRM_MSG_FONT_SIZE,
                           OVERLAY_TITLE_FONT_SIZE, OVERLAY_BODY_FONT_SIZE, OVERLAY_LINE_SPACING,
                           PROMOTION_CHOICE_FONT_SIZE, PROMOTION_BUTTON_WIDTH, PROMOTION_BUTTON_HEIGHT, 
                           MODE_PVP, MODE_PVA, AI_DIFFICULTIES, STOCKFISH_SKILL_LEVELS,
                           DEFAULT_GAME_MODE, DEFAULT_AI_DIFFICULTY, PLAYER_PLAYS_AS_WHITE,
                           ANIMATION_SPEED, STOCKFISH_PATH,
                           RULES_FILENAME, ABOUT_FILENAME, TEXT_FILE_PATH, 
                           OVERLAY_NONE, OVERLAY_RULES, OVERLAY_ABOUT, OVERLAY_AI_CONFIRM) 
from src.assets_manager import get_piece_image, play_sound
from src.ui_elements import Button
import chess
import chess.engine

AI_MOVE_EVENT = pygame.USEREVENT + 1


class Board:
    def __init__(self):
        # ... (most __init__ variables remain the same) ...
        self.chess_board = chess.Board()
        self.visual_board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self._sync_visual_board()

        self.selected_square_coords = None
        self.valid_moves_coords = []

        self.game_over = False
        self.game_over_message = ""
        self.status_message = ""
        self.king_in_check_coords = None 

        self.game_mode = DEFAULT_GAME_MODE
        self.ai_difficulty_index = AI_DIFFICULTIES.index(DEFAULT_AI_DIFFICULTY)
        self.current_ai_difficulty = AI_DIFFICULTIES[self.ai_difficulty_index]
        
        self.player_is_white = PLAYER_PLAYS_AS_WHITE 

        self.is_animating = False
        self.animating_piece_surface = None
        self.anim_start_pixel_pos = None
        self.anim_end_pixel_pos = None
        self.anim_current_pixel_pos = None
        self.anim_piece_to_draw_after_anim = None
        self.anim_target_coords = None
        self.pending_move = None

        self.is_awaiting_promotion = False
        self.promotion_square_coords = None
        self.promotion_pending_base_move_uci = None
        self.promotion_buttons = []
        self.promoting_pawn_color_is_white = True

        self.stockfish_engine = None
        self.ai_is_thinking = False 
        self._init_stockfish_engine() 

        try:
            # ... (font initializations) ...
            if not pygame.font.get_init(): pygame.font.init()
            self.status_font = pygame.font.SysFont(FONT_NAME, STATUS_FONT_SIZE)
            self.game_over_font = pygame.font.SysFont(FONT_NAME, GAME_OVER_FONT_SIZE)
            self.confirm_font = pygame.font.SysFont(FONT_NAME, CONFIRM_MSG_FONT_SIZE)
            self.overlay_title_font = pygame.font.SysFont(FONT_NAME, OVERLAY_TITLE_FONT_SIZE, bold=True)
            self.overlay_body_font = pygame.font.SysFont(FONT_NAME, OVERLAY_BODY_FONT_SIZE)
            self.promotion_font = pygame.font.SysFont(FONT_NAME, PROMOTION_CHOICE_FONT_SIZE, bold=True)
        except Exception as e:
            print(f"Error initializing fonts: {e}. Using default font.")
            self.status_font = pygame.font.Font(None, STATUS_FONT_SIZE)
            self.game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
            self.confirm_font = pygame.font.Font(None, CONFIRM_MSG_FONT_SIZE)
            self.overlay_title_font = pygame.font.Font(None, OVERLAY_TITLE_FONT_SIZE)
            self.overlay_body_font = pygame.font.Font(None, OVERLAY_BODY_FONT_SIZE)
            self.promotion_font = pygame.font.Font(None, PROMOTION_CHOICE_FONT_SIZE)


        self.buttons = []
        self.active_overlay_type = OVERLAY_NONE 
        self.overlay_title_text = "" 
        self.overlay_body_paragraphs = [] 
        self.overlay_close_button = None 
        self.ai_confirm_start_button = None 

        self._setup_buttons() 
        self.show_restart_confirmation = False 
        self._update_status_message()

    def _init_stockfish_engine(self):
        if STOCKFISH_PATH and os.path.exists(STOCKFISH_PATH):
            try:
                self.stockfish_engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
                print(f"Stockfish engine initialized successfully from: {STOCKFISH_PATH}")
                skill = STOCKFISH_SKILL_LEVELS.get(self.current_ai_difficulty, STOCKFISH_SKILL_LEVELS["Medium"]) 
                self.stockfish_engine.configure({"Skill Level": skill})
                print(f"Stockfish initial skill level set to: {skill} ({self.current_ai_difficulty})")
            except Exception as e:
                print(f"Error initializing Stockfish engine: {e}")
                self.stockfish_engine = None
        else:
            if STOCKFISH_PATH: 
                 print(f"Stockfish executable not found at configured path: {STOCKFISH_PATH}. AI will not be available.")
            else:
                 print("STOCKFISH_PATH not configured. AI will not be available.")
            self.stockfish_engine = None

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

        player_color_text = "Play as: White" if self.player_is_white else "Play as: Black"
        self.player_color_button = Button(panel_x, current_y, button_width, button_height,
                                           text=player_color_text, action=self._toggle_player_color)
        self.buttons.append(self.player_color_button)
        current_y += button_height + spacing
        
        self.ai_difficulty_button = Button(panel_x, current_y, button_width, button_height,
                                           text="AI Difficulty", action=self._cycle_ai_difficulty)
        self.buttons.append(self.ai_difficulty_button)
        current_y += button_height + spacing

        # ADDED _handle_undo_click as action
        self.undo_button = Button(panel_x, current_y, button_width, button_height,
                                  text="Undo", action=self._handle_undo_click)
        self.buttons.append(self.undo_button)
        
        exit_button_y = HEIGHT - button_height - 30 
        about_button_y = exit_button_y - button_height - spacing
        rules_button_y = about_button_y - button_height - spacing

        self.rules_button = Button(panel_x, rules_button_y, button_width, button_height,
                                   text="Game Rules", action=self._show_rules_overlay)
        self.buttons.append(self.rules_button)
        
        self.about_button = Button(panel_x, about_button_y, button_width, button_height,
                                   text="About Game", action=self._show_about_overlay)
        self.buttons.append(self.about_button)

        self.exit_button = Button(panel_x, exit_button_y, button_width, button_height,
                                  text="Exit Game", action=self._handle_exit_click)
        self.buttons.append(self.exit_button) 

        self._update_player_color_button_state() 
        self._update_ai_difficulty_button_state()
        self._update_undo_button_state() 

        confirm_btn_y = BOARD_HEIGHT // 2 + 20 
        self.confirm_yes_button = Button(BOARD_WIDTH // 2 - 110, confirm_btn_y, 100, 40, "Yes",
                                         color=BUTTON_WARN_COLOR, hover_color=BUTTON_WARN_HOVER_COLOR,
                                         text_color=BUTTON_TEXT_COLOR, action=self.restart_game)
        self.confirm_no_button = Button(BOARD_WIDTH // 2 + 10, confirm_btn_y, 100, 40, "No",
                                        color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                        text_color=BUTTON_TEXT_COLOR, action=self._cancel_restart_confirmation)
        
        self.overlay_close_button = Button(0, 0, 100, 30, "Close", action=self._close_text_overlay)
        
        self.promotion_buttons = [
            Button(0,0, PROMOTION_BUTTON_WIDTH, PROMOTION_BUTTON_HEIGHT, "Queen", action=lambda: self._handle_promotion_choice(chess.QUEEN)),
            Button(0,0, PROMOTION_BUTTON_WIDTH, PROMOTION_BUTTON_HEIGHT, "Rook", action=lambda: self._handle_promotion_choice(chess.ROOK)),
            Button(0,0, PROMOTION_BUTTON_WIDTH, PROMOTION_BUTTON_HEIGHT, "Bishop", action=lambda: self._handle_promotion_choice(chess.BISHOP)),
            Button(0,0, PROMOTION_BUTTON_WIDTH, PROMOTION_BUTTON_HEIGHT, "Knight", action=lambda: self._handle_promotion_choice(chess.KNIGHT)),
        ]

        self.ai_confirm_start_button = Button(
            BOARD_WIDTH // 2 - 75, BOARD_HEIGHT // 2 + 60, 150, 50, "Start Game",
            color=BUTTON_PLAY_COLOR, hover_color=BUTTON_PLAY_HOVER_COLOR,
            action=self._handle_ai_confirm_start_click
        )

    def _load_text_file_content(self, filename):
        title = "Error"
        paragraphs = ["Could not load content."]
        try:
            filepath = os.path.join(TEXT_FILE_PATH, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]
            if lines:
                title = lines[0]
                paragraphs = []
                current_paragraph = []
                for line in lines[1:]:
                    if not line: 
                        if current_paragraph:
                            paragraphs.append(" ".join(current_paragraph))
                            current_paragraph = []
                    else:
                        current_paragraph.append(line)
                if current_paragraph: 
                    paragraphs.append(" ".join(current_paragraph))
                if not paragraphs and len(lines) > 1: 
                    paragraphs.append("(No additional content)")
                elif not paragraphs and len(lines) == 1: 
                     paragraphs.append("(No additional content)")
        except FileNotFoundError:
            print(f"Error: Text file not found: {filepath}") 
            title = f"File Not Found: {filename}"
        except Exception as e:
            print(f"Error reading text file {filename}: {e}")
            title = f"Error Reading: {filename}"
        return title, paragraphs

    def _show_rules_overlay(self):
        play_sound('button_click')
        title, paragraphs = self._load_text_file_content(RULES_FILENAME)
        self.overlay_title_text = title
        self.overlay_body_paragraphs = paragraphs
        self.active_overlay_type = OVERLAY_RULES
        print("Showing Rules Overlay")

    def _show_about_overlay(self):
        play_sound('button_click')
        title, paragraphs = self._load_text_file_content(ABOUT_FILENAME)
        self.overlay_title_text = title
        self.overlay_body_paragraphs = paragraphs
        self.active_overlay_type = OVERLAY_ABOUT
        print("Showing About Overlay")

    def _close_text_overlay(self):
        play_sound('button_click') 
        self.active_overlay_type = OVERLAY_NONE
        self.overlay_title_text = ""
        self.overlay_body_paragraphs = []
        print("Text Overlay Closed")

    def _toggle_game_mode(self):
        play_sound('button_click') 
        if self.game_mode == MODE_PVP:
            self.game_mode = MODE_PVA
            if not self.stockfish_engine: 
                self._init_stockfish_engine()
        else: 
            self.game_mode = MODE_PVP
            pygame.time.set_timer(AI_MOVE_EVENT, 0) 
            self.ai_is_thinking = False 

        self.game_mode_button.update_text(f"Mode: {self.game_mode}")
        self._update_ai_difficulty_button_state()
        self._update_player_color_button_state() 
        self.restart_game() 
        print(f"Game mode changed to: {self.game_mode}")

    def _toggle_player_color(self):
        if self.game_mode == MODE_PVA: 
            play_sound('button_click')
            self.player_is_white = not self.player_is_white
            player_color_text = "Play as: White" if self.player_is_white else "Play as: Black"
            self.player_color_button.update_text(player_color_text)
            self.restart_game() 
            print(f"Player will now play as {'White' if self.player_is_white else 'Black'}")

    def _update_player_color_button_state(self):
        if hasattr(self, 'player_color_button'): 
            if self.game_mode == MODE_PVA:
                self.player_color_button.set_enabled(True)
                player_color_text = "Play as: White" if self.player_is_white else "Play as: Black"
                self.player_color_button.update_text(player_color_text)
            else:
                self.player_color_button.set_enabled(False)
                self.player_color_button.update_text("Play as (PvA)")


    def _cycle_ai_difficulty(self):
        if self.game_mode == MODE_PVA:
            play_sound('button_click') 
            self.ai_difficulty_index = (self.ai_difficulty_index + 1) % len(AI_DIFFICULTIES)
            self.current_ai_difficulty = AI_DIFFICULTIES[self.ai_difficulty_index]
            self.ai_difficulty_button.update_text(f"AI: {self.current_ai_difficulty}")
            
            if self.stockfish_engine: 
                skill = STOCKFISH_SKILL_LEVELS.get(self.current_ai_difficulty, STOCKFISH_SKILL_LEVELS["Medium"]) 
                try:
                    self.stockfish_engine.configure({"Skill Level": skill})
                    print(f"Stockfish skill level updated to: {skill} ({self.current_ai_difficulty})")
                except Exception as e:
                    print(f"Error configuring Stockfish skill level: {e}")
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
    
    def _handle_ai_confirm_start_click(self):
        play_sound('button_click')
        self.active_overlay_type = OVERLAY_NONE 
        self.ai_is_thinking = True
        self._update_status_message() 
        pygame.time.set_timer(AI_MOVE_EVENT, 100) 
        print("AI first move confirmed by player.")

    # --- ADDED UNDO LOGIC ---
    def _handle_undo_click(self):
        """Handles the undo move button click."""
        if self.is_animating or self.ai_is_thinking or self.is_awaiting_promotion or self.game_over:
            print("Cannot undo at this time.")
            return

        if self.chess_board.move_stack:
            play_sound('button_click') 
            
            moves_to_undo = 1
            if self.game_mode == MODE_PVA:
                ai_color = chess.BLACK if self.player_is_white else chess.WHITE
                human_player_color = chess.WHITE if self.player_is_white else chess.BLACK
                
                # If it's human's turn now, it means AI made the last move.
                # We want to undo both AI's move and player's preceding move.
                if self.chess_board.turn == human_player_color and len(self.chess_board.move_stack) >= 2:
                     moves_to_undo = 2
                # If it's AI's turn now, it means human made the last move. Undo 1.
                # (This is covered by moves_to_undo = 1 default)
            
            print(f"Attempting to undo {moves_to_undo} half-move(s).")
            for _ in range(moves_to_undo):
                if self.chess_board.move_stack:
                    self.chess_board.pop()
                else:
                    break 

            self._sync_visual_board()
            self.selected_square_coords = None
            self.valid_moves_coords = []
            self.king_in_check_coords = None
            self.game_over = False 
            self.game_over_message = ""
            self.ai_is_thinking = False 
            pygame.time.set_timer(AI_MOVE_EVENT, 0) 
            self._update_status_message() 
            self._check_game_over() # Re-check game over state (unlikely to be over after undo)
            self._update_undo_button_state() 
            print("Move(s) undone.")

            # If after undo, it's AI's turn, trigger AI move
            ai_color_after_undo = chess.BLACK if self.player_is_white else chess.WHITE
            if self.game_mode == MODE_PVA and self.chess_board.turn == ai_color_after_undo and \
               not self.is_animating and not self.game_over:
                self.ai_is_thinking = True
                self._update_status_message()
                pygame.time.set_timer(AI_MOVE_EVENT, 500)
        else:
            print("No moves to undo.")

    def _update_undo_button_state(self):
        """Enables or disables the undo button."""
        if hasattr(self, 'undo_button'): 
            can_undo = bool(self.chess_board.move_stack) and \
                       not self.is_animating and \
                       not self.ai_is_thinking and \
                       not self.is_awaiting_promotion and \
                       not self.game_over and \
                       self.active_overlay_type == OVERLAY_NONE and \
                       not self.show_restart_confirmation
            self.undo_button.set_enabled(can_undo)
    # --- END OF ADDED UNDO LOGIC ---


    def restart_game(self):
        self.chess_board.reset()
        self._sync_visual_board()
        self.selected_square_coords = None
        self.valid_moves_coords = []
        self.game_over = False
        self.game_over_message = ""
        self.show_restart_confirmation = False
        self.active_overlay_type = OVERLAY_NONE 
        self.is_animating = False 
        self.animating_piece_surface = None
        self.king_in_check_coords = None 
        self.ai_is_thinking = False 
        self.is_awaiting_promotion = False
        pygame.time.set_timer(AI_MOVE_EVENT, 0) 
        self._update_status_message()
        self._update_undo_button_state() 
        print("Game restarted.")

        ai_color_to_move_first = chess.WHITE 
        if self.game_mode == MODE_PVA and not self.player_is_white and self.chess_board.turn == ai_color_to_move_first:
            if not self.is_animating and not self.game_over:
                self.active_overlay_type = OVERLAY_AI_CONFIRM 
                self._update_status_message() 
        
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


    def handle_click_on_board_or_dialog(self, pos):
        if self.is_animating or (self.game_mode == MODE_PVA and self.ai_is_thinking and not self.active_overlay_type == OVERLAY_AI_CONFIRM): 
            return False 

        if self.active_overlay_type == OVERLAY_AI_CONFIRM:
            if self.ai_confirm_start_button and self.ai_confirm_start_button.rect.collidepoint(pos):
                if self.ai_confirm_start_button.action:
                    self.ai_confirm_start_button.action()
                return True 
            return True 

        if self.is_awaiting_promotion:
            for i, promo_button in enumerate(self.promotion_buttons):
                btn_rect_to_check = promo_button.screen_rect if hasattr(promo_button, 'screen_rect') else promo_button.rect
                if btn_rect_to_check.collidepoint(pos):
                    chosen_piece_type = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT][i]
                    self._handle_promotion_choice(chosen_piece_type)
                    return True 
            if pygame.Rect(0,0,BOARD_WIDTH, BOARD_HEIGHT).collidepoint(pos):
                 return True


        if self.active_overlay_type in [OVERLAY_RULES, OVERLAY_ABOUT]:
            close_button_rect = self.overlay_close_button.screen_rect if hasattr(self.overlay_close_button, 'screen_rect') else self.overlay_close_button.rect
            if self.overlay_close_button and close_button_rect.collidepoint(pos):
                if self.overlay_close_button.action:
                    self.overlay_close_button.action() 
                return True 
            return True 

        if self.show_restart_confirmation:
            if self.confirm_yes_button.rect.collidepoint(pos):
                if self.confirm_yes_button.action: play_sound('button_click'); self.confirm_yes_button.action()
                return True 
            if self.confirm_no_button.rect.collidepoint(pos):
                if self.confirm_no_button.action: self.confirm_no_button.action() 
                return True 
            return True 

        board_coords = self.get_row_col_from_mouse(pos)
        if board_coords:
            self.select_square(*board_coords)
            return True 
        return False 

    def select_square(self, row, col):
        if self.game_over or self.is_animating or self.ai_is_thinking or self.is_awaiting_promotion or self.active_overlay_type != OVERLAY_NONE: return
        
        human_player_chess_color = chess.WHITE if self.player_is_white else chess.BLACK
        if self.game_mode == MODE_PVA and self.chess_board.turn != human_player_chess_color:
            return 

        clicked_chess_sq = self._coords_to_chess_sq(row, col)
        piece_at_clicked_sq = self.chess_board.piece_at(clicked_chess_sq)
        current_player_color_on_board = self.chess_board.turn 
        
        previously_selected = self.selected_square_coords is not None

        if self.selected_square_coords is None: 
            if piece_at_clicked_sq and piece_at_clicked_sq.color == current_player_color_on_board:
                if self.game_mode == MODE_PVA and piece_at_clicked_sq.color != human_player_chess_color:
                    return
                self.selected_square_coords = (row, col)
                self._calculate_valid_moves(row, col)
                play_sound('piece_select')
        else: 
            from_r, from_c = self.selected_square_coords
            if (row, col) in self.valid_moves_coords: 
                self.move_piece((from_r, from_c), (row, col)) 
            elif piece_at_clicked_sq and piece_at_clicked_sq.color == current_player_color_on_board: 
                if self.game_mode == MODE_PVA and piece_at_clicked_sq.color != human_player_chess_color:
                    return 
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

    def move_piece(self, from_coords, to_coords, is_ai_move=False): 
        if self.game_over or self.is_animating: return

        from_r, from_c = from_coords
        to_r, to_c = to_coords
        from_sq_chess = self._coords_to_chess_sq(from_r, from_c)
        to_sq_chess = self._coords_to_chess_sq(to_r, to_c)
        
        piece_to_move = self.chess_board.piece_at(from_sq_chess)
        if not piece_to_move: return 

        is_player_promotion_opportunity = False
        is_human_turn_for_promo = (self.game_mode == MODE_PVP and piece_to_move.color == self.chess_board.turn) or \
                                  (self.game_mode == MODE_PVA and piece_to_move.color == (chess.WHITE if self.player_is_white else chess.BLACK))

        if not is_ai_move and is_human_turn_for_promo and piece_to_move.piece_type == chess.PAWN:
            if (piece_to_move.color == chess.WHITE and to_r == 0) or \
               (piece_to_move.color == chess.BLACK and to_r == 7):
                is_player_promotion_opportunity = True
        
        if is_player_promotion_opportunity:
            self.is_awaiting_promotion = True
            self.promotion_square_coords = to_coords 
            self.promotion_pending_base_move_uci = chess.Move(from_sq_chess, to_sq_chess).uci()[:4] 
            self.promoting_pawn_color_is_white = (piece_to_move.color == chess.WHITE)
            
            self.is_animating = True
            self.animating_piece_surface = get_piece_image(self.visual_board[from_r][from_c])
            self.anim_start_pixel_pos = (from_c * SQUARE_SIZE + SQUARE_SIZE // 2, from_r * SQUARE_SIZE + SQUARE_SIZE // 2)
            self.anim_end_pixel_pos = (to_c * SQUARE_SIZE + SQUARE_SIZE // 2, to_r * SQUARE_SIZE + SQUARE_SIZE // 2)
            self.anim_current_pixel_pos = list(self.anim_start_pixel_pos)
            self.anim_original_start_coords = (from_r, from_c)
            self.anim_target_coords = to_coords 
            play_sound('piece_move')
            self.selected_square_coords = None 
            self.valid_moves_coords = []
            return 

        if is_ai_move and hasattr(self, 'pending_move_for_ai') and self.pending_move_for_ai:
            move_to_push = self.pending_move_for_ai
            del self.pending_move_for_ai 
        else: 
            promo_piece_for_move = None
            if piece_to_move.piece_type == chess.PAWN:
                if (piece_to_move.color == chess.WHITE and to_r == 0) or \
                   (piece_to_move.color == chess.BLACK and to_r == 7):
                    promo_piece_for_move = chess.QUEEN 
            move_to_push = chess.Move(from_sq_chess, to_sq_chess, promotion=promo_piece_for_move)

        self.is_animating = True
        self.animating_piece_surface = get_piece_image(self.visual_board[from_r][from_c])
        self.anim_start_pixel_pos = (from_c * SQUARE_SIZE + SQUARE_SIZE // 2, from_r * SQUARE_SIZE + SQUARE_SIZE // 2)
        self.anim_end_pixel_pos = (to_c * SQUARE_SIZE + SQUARE_SIZE // 2, to_r * SQUARE_SIZE + SQUARE_SIZE // 2)
        self.anim_current_pixel_pos = list(self.anim_start_pixel_pos)
        self.anim_original_start_coords = (from_r, from_c)
        self.anim_target_coords = to_coords
        self.pending_move = move_to_push 
        play_sound('piece_move')
        
        self.selected_square_coords = None 
        self.valid_moves_coords = []
    def _handle_promotion_choice(self, chosen_piece_type):
        play_sound('button_click')
        if not self.is_awaiting_promotion or self.promotion_pending_base_move_uci is None:
            self.is_awaiting_promotion = False 
            return

        promotion_uci = self.promotion_pending_base_move_uci + chess.piece_symbol(chosen_piece_type).lower()
        promoted_move = chess.Move.from_uci(promotion_uci)

        if promoted_move in self.chess_board.legal_moves:
            self.chess_board.push(promoted_move)
            self._sync_visual_board() 
            self._update_status_message()
            self._check_game_over()
            self._update_undo_button_state() 
        else:
            print(f"Error: Chosen promotion move {promoted_move.uci()} is not legal.")
            self._sync_visual_board() 
        
        self.is_awaiting_promotion = False
        self.promotion_pending_base_move_uci = None
        self.promotion_square_coords = None
        
        ai_color = chess.BLACK if self.player_is_white else chess.WHITE
        if not self.game_over and self.game_mode == MODE_PVA and self.chess_board.turn == ai_color:
            self.ai_is_thinking = True
            self._update_status_message()
            pygame.time.set_timer(AI_MOVE_EVENT, 500)

    def _trigger_ai_move(self):
        if self.game_mode != MODE_PVA:
            self.ai_is_thinking = False 
            self._update_status_message() 
            return

        if self.game_over or self.is_animating or not self.stockfish_engine:
            self.ai_is_thinking = False 
            self._update_status_message() 
            return
        
        ai_color = chess.BLACK if self.player_is_white else chess.WHITE
        if self.chess_board.turn == ai_color: 
            print(f"AI ({self.current_ai_difficulty}) is actually processing move...")
            
            skill = STOCKFISH_SKILL_LEVELS.get(self.current_ai_difficulty, STOCKFISH_SKILL_LEVELS["Medium"]) 
            try:
                self.stockfish_engine.configure({"Skill Level": skill})
            except Exception as e: 
                print(f"Error configuring Stockfish for AI move: {e}")
                self.ai_is_thinking = False
                self._update_status_message() 
                return

            think_time = 0.1 if self.current_ai_difficulty == "Easiest" else \
                         0.3 if self.current_ai_difficulty == "Easy" else \
                         0.7 if self.current_ai_difficulty == "Medium" else \
                         1.5 if self.current_ai_difficulty == "Hard" else 2.5

            try:
                result = self.stockfish_engine.play(self.chess_board, chess.engine.Limit(time=think_time))
                ai_chess_move = result.move 
                
                if ai_chess_move:
                    print(f"AI plays: {ai_chess_move.uci()}")
                    from_coords = self._chess_sq_to_coords(ai_chess_move.from_square)
                    to_coords = self._chess_sq_to_coords(ai_chess_move.to_square)
                    
                    if from_coords and to_coords:
                        self.pending_move_for_ai = ai_chess_move 
                        self.move_piece(from_coords, to_coords, is_ai_move=True) 
                else: 
                    print("AI returned no move (unexpected).")
                    self.ai_is_thinking = False 
                    self._update_status_message() 
            except chess.engine.EngineTerminatedError:
                print("Stockfish engine terminated unexpectedly during AI move.")
                self.stockfish_engine = None 
                self.ai_is_thinking = False
                self._update_status_message()
            except Exception as e:
                print(f"Error during AI move processing: {e}")
                self.ai_is_thinking = False
                self._update_status_message()
        else: 
            self.ai_is_thinking = False

    def _update_animation(self):
        if not self.is_animating:
            return

        target_x, target_y = self.anim_end_pixel_pos
        current_x, current_y = self.anim_current_pixel_pos
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance < ANIMATION_SPEED: 
            self.anim_current_pixel_pos = list(self.anim_end_pixel_pos) 
            self.is_animating = False 

            if self.is_awaiting_promotion: 
                self._sync_visual_board() 
                self.animating_piece_surface = None 
                self.anim_original_start_coords = None
                self._update_status_message() 
                self._update_undo_button_state() 
                return 

            if hasattr(self, 'pending_move') and self.pending_move:
                move_to_execute = self.pending_move
                
                if move_to_execute in self.chess_board.legal_moves or self.chess_board.is_capture(move_to_execute): 
                    self.chess_board.push(move_to_execute)
                else: 
                    print(f"Warning: Pending move {move_to_execute.uci()} was not pushed. Current legal moves: {list(self.chess_board.legal_moves)}")
                self.pending_move = None
            
            self._sync_visual_board() 
            self.animating_piece_surface = None
            self.anim_original_start_coords = None
            self.anim_target_coords = None
            
            ai_color = chess.BLACK if self.player_is_white else chess.WHITE
            if self.game_mode == MODE_PVA and self.chess_board.turn != ai_color : 
                self.ai_is_thinking = False

            self._update_status_message() 
            self._check_game_over()     
            self._update_undo_button_state() 

            if not self.game_over and self.game_mode == MODE_PVA and self.chess_board.turn == ai_color:
                self.ai_is_thinking = True 
                self._update_status_message() 
                pygame.time.set_timer(AI_MOVE_EVENT, 500) 
        else: 
            self.anim_current_pixel_pos[0] += (dx / distance) * ANIMATION_SPEED
            self.anim_current_pixel_pos[1] += (dy / distance) * ANIMATION_SPEED
    def _update_status_message(self):
        self.king_in_check_coords = None 
        if self.game_over: 
            self.status_message = "" 
            return
        
        current_turn_color = self.chess_board.turn 
        player_turn_text = ""

        if self.is_awaiting_promotion:
            player_turn_text = "Choose promotion:"
        elif self.active_overlay_type == OVERLAY_AI_CONFIRM: 
            player_turn_text = "AI Prepares..." 
        elif self.game_mode == MODE_PVP:
            player_turn_text = "White's Turn" if current_turn_color == chess.WHITE else "Black's Turn"
        elif self.game_mode == MODE_PVA:
            human_player_chess_color = chess.WHITE if self.player_is_white else chess.BLACK
            ai_color = chess.BLACK if self.player_is_white else chess.WHITE

            if current_turn_color == ai_color and self.ai_is_thinking: 
                 player_turn_text = f"AI ({self.current_ai_difficulty}) is thinking..."
            elif current_turn_color == ai_color and not self.is_animating: 
                 player_turn_text = f"AI's Turn ({self.current_ai_difficulty})"
            elif current_turn_color == human_player_chess_color:
                player_turn_text = "Your Turn"
        
        self.status_message = player_turn_text
        if self.chess_board.is_check() and not self.is_awaiting_promotion and self.active_overlay_type != OVERLAY_AI_CONFIRM :
            if self.status_message:
                self.status_message += " - CHECK!"
            else: 
                self.status_message = "CHECK!"


        if self.chess_board.is_check(): 
            king_square = self.chess_board.king(self.chess_board.turn) 
            if king_square is not None:
                self.king_in_check_coords = self._chess_sq_to_coords(king_square)
    def _check_game_over(self):
        if self.game_over: return 

        outcome = self.chess_board.outcome()
        if outcome:
            self.game_over = True
            self.ai_is_thinking = False 
            self.king_in_check_coords = None 
            if outcome.termination == chess.Termination.CHECKMATE:
                actual_winner_color = outcome.winner 
                if self.game_mode == MODE_PVA:
                    human_player_chess_color = chess.WHITE if self.player_is_white else chess.BLACK
                    if actual_winner_color == human_player_chess_color:
                        self.game_over_message = "CHECKMATE! You Win!"
                    else:
                        self.game_over_message = "CHECKMATE! AI Wins!"
                else: 
                    winner_display = "White" if actual_winner_color == chess.WHITE else "Black"
                    self.game_over_message = f"CHECKMATE! {winner_display} wins."

            elif outcome.termination == chess.Termination.STALEMATE:
                self.game_over_message = "STALEMATE! Draw."
            elif outcome.termination == chess.Termination.INSUFFICIENT_MATERIAL:
                self.game_over_message = "DRAW! Insufficient Material."
            else: 
                self.game_over_message = "GAME OVER! Draw."
            self.status_message = "" 
            self._update_undo_button_state() 
    # --- Drawing Methods ---
    def draw_board_area(self, screen):
        for r_idx in range(ROWS):
            for c_idx in range(COLS):
                color = LIGHT_SQUARE if (r_idx + c_idx) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(screen, color, (c_idx * SQUARE_SIZE, r_idx * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        if self.king_in_check_coords and not self.game_over:
            r, c = self.king_in_check_coords
            check_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            check_surface.fill(CHECK_HIGHLIGHT_COLOR)
            screen.blit(check_surface, (c * SQUARE_SIZE, r * SQUARE_SIZE))

        for r_idx in range(ROWS):
            for c_idx in range(COLS):
                if self.is_awaiting_promotion and self.promotion_square_coords == (r_idx, c_idx):
                    continue
                if self.is_animating and self.anim_original_start_coords == (r_idx, c_idx):
                    continue 

                piece_notation = self.visual_board[r_idx][c_idx]
                if piece_notation:
                    image = get_piece_image(piece_notation)
                    if image:
                        img_rect = image.get_rect(center=(c_idx * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                          r_idx * SQUARE_SIZE + SQUARE_SIZE // 2))
                        screen.blit(image, img_rect.topleft)
        
        if not self.is_animating and not (self.game_mode == MODE_PVA and self.ai_is_thinking) and not self.is_awaiting_promotion and self.active_overlay_type == OVERLAY_NONE: 
            if self.selected_square_coords:
                r, c = self.selected_square_coords
                highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                highlight_surface.fill(SELECTED_SQUARE_HIGHLIGHT_COLOR) 
                screen.blit(highlight_surface, (c * SQUARE_SIZE, r * SQUARE_SIZE))

            for r_idx, c_idx in self.valid_moves_coords:
                center_x = c_idx * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = r_idx * SQUARE_SIZE + SQUARE_SIZE // 2
                pygame.draw.circle(screen, VALID_MOVE_DOT_COLOR, (center_x, center_y), SQUARE_SIZE // 6) 
    def draw_animated_piece(self, screen):
        if self.is_animating and self.animating_piece_surface and self.anim_current_pixel_pos:
            piece_width, piece_height = self.animating_piece_surface.get_size()
            draw_x = self.anim_current_pixel_pos[0] - piece_width // 2
            draw_y = self.anim_current_pixel_pos[1] - piece_height // 2
            screen.blit(self.animating_piece_surface, (draw_x, draw_y))

    def draw_side_panel(self, screen):
        panel_rect = pygame.Rect(BOARD_WIDTH, 0, SIDE_PANEL_WIDTH, HEIGHT)
        pygame.draw.rect(screen, SIDE_PANEL_BG_COLOR, panel_rect)

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
            yes_text = self.confirm_font.render("Yes", True, self.confirm_yes_button.base_text_color) 
            overlay_surface.blit(yes_text, yes_text.get_rect(center=yes_btn_rect_local.center))
            
            no_btn_rect_local = pygame.Rect(overlay_rect.width // 2 + 10, overlay_rect.height // 2 + 20, 100, 40)
            no_hover = self.confirm_no_button.rect.collidepoint(pygame.mouse.get_pos())
            no_color = self.confirm_no_button.base_hover_color if no_hover else self.confirm_no_button.base_color
            pygame.draw.rect(overlay_surface, no_color, no_btn_rect_local, border_radius=5)
            no_text = self.confirm_font.render("No", True, self.confirm_no_button.base_text_color) 
            overlay_surface.blit(no_text, no_text.get_rect(center=no_btn_rect_local.center))
            
            screen.blit(overlay_surface, overlay_rect.topleft)


    def _draw_text_overlay(self, screen):
        if self.active_overlay_type not in [OVERLAY_RULES, OVERLAY_ABOUT]:
            return

        overlay_margin = 40
        overlay_rect_on_screen = pygame.Rect(overlay_margin, overlay_margin, 
                                   BOARD_WIDTH - 2 * overlay_margin, 
                                   BOARD_HEIGHT - 2 * overlay_margin)
        
        overlay_surface = pygame.Surface((overlay_rect_on_screen.width, overlay_rect_on_screen.height), pygame.SRCALPHA)
        overlay_surface.fill(TEXT_OVERLAY_BG_COLOR)

        title_surface = self.overlay_title_font.render(self.overlay_title_text, True, OVERLAY_TEXT_COLOR)
        title_rect = title_surface.get_rect(centerx=overlay_rect_on_screen.width // 2, top=20)
        overlay_surface.blit(title_surface, title_rect)

        current_y = title_rect.bottom + 30
        max_text_width = overlay_rect_on_screen.width - 40 

        for paragraph_text in self.overlay_body_paragraphs:
            words = paragraph_text.split(' ')
            line = ""
            for word in words:
                test_line = line + word + " "
                if self.overlay_body_font.size(test_line)[0] < max_text_width:
                    line = test_line
                else: 
                    body_surface = self.overlay_body_font.render(line.strip(), True, OVERLAY_TEXT_COLOR)
                    body_rect = body_surface.get_rect(left=20, top=current_y)
                    overlay_surface.blit(body_surface, body_rect)
                    current_y += self.overlay_body_font.get_linesize() + OVERLAY_LINE_SPACING
                    line = word + " "
            if line:
                body_surface = self.overlay_body_font.render(line.strip(), True, OVERLAY_TEXT_COLOR)
                body_rect = body_surface.get_rect(left=20, top=current_y)
                overlay_surface.blit(body_surface, body_rect)
                current_y += self.overlay_body_font.get_linesize() + OVERLAY_LINE_SPACING
            current_y += self.overlay_body_font.get_linesize() 

        close_btn_width = 100
        close_btn_height = 30
        
        self.overlay_close_button.rect.width = close_btn_width
        self.overlay_close_button.rect.height = close_btn_height
        self.overlay_close_button.rect.centerx = overlay_rect_on_screen.width // 2
        self.overlay_close_button.rect.bottom = overlay_rect_on_screen.height - 20
        
        self.overlay_close_button.screen_rect = pygame.Rect(
            self.overlay_close_button.rect.left + overlay_rect_on_screen.left,
            self.overlay_close_button.rect.top + overlay_rect_on_screen.top,
            close_btn_width, close_btn_height
        )
        self.overlay_close_button.draw(overlay_surface) 
        
        screen.blit(overlay_surface, overlay_rect_on_screen.topleft)

    def _draw_promotion_choice_overlay(self, screen):
        if not self.is_awaiting_promotion:
            return

        overlay_rect = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT) 
        overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
        overlay_surface.fill(PROMOTION_OVERLAY_BG_COLOR)

        prompt_text = "Promote pawn to:"
        prompt_surface = self.promotion_font.render(prompt_text, True, OVERLAY_TEXT_COLOR)
        prompt_rect = prompt_surface.get_rect(centerx=overlay_rect.width // 2, y=overlay_rect.height // 2 - 100)
        overlay_surface.blit(prompt_surface, prompt_rect)

        button_start_x = overlay_rect.width // 2 - (len(self.promotion_buttons) * (PROMOTION_BUTTON_WIDTH + 10) - 10) // 2
        button_y = overlay_rect.height // 2 - PROMOTION_BUTTON_HEIGHT // 2

        for i, button in enumerate(self.promotion_buttons):
            button.rect.x = button_start_x + i * (PROMOTION_BUTTON_WIDTH + 10)
            button.rect.y = button_y
            button.rect.width = PROMOTION_BUTTON_WIDTH 
            button.rect.height = PROMOTION_BUTTON_HEIGHT
            
            button.screen_rect = pygame.Rect(button.rect.x, button.rect.y, button.rect.width, button.rect.height)
            
            button.draw(overlay_surface) 

        screen.blit(overlay_surface, overlay_rect.topleft)

    def _draw_ai_first_move_confirmation_overlay(self, screen):
        if self.active_overlay_type != OVERLAY_AI_CONFIRM:
            return

        overlay_rect = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT)
        overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
        overlay_surface.fill(AI_CONFIRM_OVERLAY_BG_COLOR)

        line1_text = "AI will play as White."
        line2_text = f"Difficulty: {self.current_ai_difficulty}"
        line3_text = "Ready to start?"

        line1_surf = self.overlay_title_font.render(line1_text, True, OVERLAY_TEXT_COLOR)
        line2_surf = self.overlay_body_font.render(line2_text, True, OVERLAY_TEXT_COLOR)
        line3_surf = self.overlay_body_font.render(line3_text, True, OVERLAY_TEXT_COLOR)

        line1_rect = line1_surf.get_rect(centerx=overlay_rect.width // 2, y=overlay_rect.height // 2 - 80)
        line2_rect = line2_surf.get_rect(centerx=overlay_rect.width // 2, top=line1_rect.bottom + 10)
        line3_rect = line3_surf.get_rect(centerx=overlay_rect.width // 2, top=line2_rect.bottom + 20)

        overlay_surface.blit(line1_surf, line1_rect)
        overlay_surface.blit(line2_surf, line2_rect)
        overlay_surface.blit(line3_surf, line3_rect)

        self.ai_confirm_start_button.rect.centerx = overlay_rect.width // 2
        self.ai_confirm_start_button.rect.bottom = overlay_rect.height - 50 
        self.ai_confirm_start_button.screen_rect = pygame.Rect(
            self.ai_confirm_start_button.rect.x, 
            self.ai_confirm_start_button.rect.y, 
            self.ai_confirm_start_button.rect.width, 
            self.ai_confirm_start_button.rect.height
        )
        self.ai_confirm_start_button.draw(overlay_surface)

        screen.blit(overlay_surface, overlay_rect.topleft)


    def update(self):
        if not self.game_over : 
            self._update_animation()
            if self.game_mode == MODE_PVA and self.ai_is_thinking and self.active_overlay_type == OVERLAY_NONE:
                self._update_status_message()


    def draw(self, screen):
        screen.fill(SIDE_PANEL_BG_COLOR) 
        self.draw_board_area(screen)     
        self.draw_animated_piece(screen) 
        self.draw_side_panel(screen)     
        
        self.draw_game_over_display(screen) 
        
        if self.active_overlay_type == OVERLAY_AI_CONFIRM: # Draw AI confirm on top of game over if both active
            self._draw_ai_first_move_confirmation_overlay(screen)
        elif self.active_overlay_type in [OVERLAY_RULES, OVERLAY_ABOUT]:
            self._draw_text_overlay(screen)
        elif self.show_restart_confirmation: 
             self.draw_restart_confirmation_dialog(screen)
        elif self.is_awaiting_promotion: 
            self._draw_promotion_choice_overlay(screen)


    def handle_button_events(self, event):
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.handle_event(event) 
            if self.active_overlay_type in [OVERLAY_RULES, OVERLAY_ABOUT] and self.overlay_close_button:
                btn_rect = self.overlay_close_button.screen_rect if hasattr(self.overlay_close_button, 'screen_rect') else self.overlay_close_button.rect
                self.overlay_close_button.is_hovered = btn_rect.collidepoint(event.pos)
            if self.show_restart_confirmation:
                self.confirm_yes_button.is_hovered = self.confirm_yes_button.rect.collidepoint(event.pos)
                self.confirm_no_button.is_hovered = self.confirm_no_button.rect.collidepoint(event.pos)
            if self.is_awaiting_promotion:
                for promo_btn in self.promotion_buttons:
                    promo_btn_screen_rect = promo_btn.screen_rect if hasattr(promo_btn, 'screen_rect') else promo_btn.rect
                    promo_btn.is_hovered = promo_btn_screen_rect.collidepoint(event.pos)
            if self.active_overlay_type == OVERLAY_AI_CONFIRM and self.ai_confirm_start_button:
                self.ai_confirm_start_button.is_hovered = self.ai_confirm_start_button.rect.collidepoint(event.pos)
            return False 
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.handle_event(event): 
                    return True 
        return False 

    def close_engine(self):
        if self.stockfish_engine:
            try:
                print("Quitting Stockfish engine...")
                self.stockfish_engine.quit()
                print("Stockfish engine quit successfully.")
            except Exception as e:
                print(f"Error quitting Stockfish engine: {e}")
            finally: 
                self.stockfish_engine = None
