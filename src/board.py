# src/board.py

import pygame
import sys
import math 
import time 
import os 
from src.constants import (ROWS, COLS, SQUARE_SIZE, BOARD_WIDTH, BOARD_HEIGHT, SIDE_PANEL_WIDTH,
                           WIDTH, HEIGHT,
                           LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT_COLOR, GREEN, BLACK,
                           SIDE_PANEL_BG_COLOR, TEXT_COLOR, OVERLAY_TEXT_COLOR, GAME_OVER_BG_COLOR, TEXT_OVERLAY_BG_COLOR,
                           BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
                           BUTTON_DISABLED_COLOR, BUTTON_DISABLED_TEXT_COLOR,
                           BUTTON_WARN_COLOR, BUTTON_WARN_HOVER_COLOR,
                           FONT_NAME, STATUS_FONT_SIZE, BUTTON_FONT_SIZE, GAME_OVER_FONT_SIZE, CONFIRM_MSG_FONT_SIZE,
                           OVERLAY_TITLE_FONT_SIZE, OVERLAY_BODY_FONT_SIZE, OVERLAY_LINE_SPACING,
                           MODE_PVP, MODE_PVA, AI_DIFFICULTIES, STOCKFISH_SKILL_LEVELS,
                           DEFAULT_GAME_MODE, DEFAULT_AI_DIFFICULTY,
                           ANIMATION_SPEED, STOCKFISH_PATH,
                           RULES_FILENAME, ABOUT_FILENAME, TEXT_FILE_PATH, 
                           OVERLAY_NONE, OVERLAY_RULES, OVERLAY_ABOUT, OVERLAY_RESTART_CONFIRM) 
from src.assets_manager import get_piece_image, play_sound
from src.ui_elements import Button
import chess
import chess.engine

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

        self.is_animating = False
        self.animating_piece_surface = None
        self.anim_start_pixel_pos = None
        self.anim_end_pixel_pos = None
        self.anim_current_pixel_pos = None
        self.anim_piece_to_draw_after_anim = None
        self.anim_target_coords = None
        self.pending_move = None

        self.stockfish_engine = None
        self._init_stockfish_engine() # Call to the method

        try:
            if not pygame.font.get_init(): pygame.font.init()
            self.status_font = pygame.font.SysFont(FONT_NAME, STATUS_FONT_SIZE)
            self.game_over_font = pygame.font.SysFont(FONT_NAME, GAME_OVER_FONT_SIZE)
            self.confirm_font = pygame.font.SysFont(FONT_NAME, CONFIRM_MSG_FONT_SIZE)
            self.overlay_title_font = pygame.font.SysFont(FONT_NAME, OVERLAY_TITLE_FONT_SIZE, bold=True)
            self.overlay_body_font = pygame.font.SysFont(FONT_NAME, OVERLAY_BODY_FONT_SIZE)
        except Exception as e:
            print(f"Error initializing fonts: {e}. Using default font.")
            self.status_font = pygame.font.Font(None, STATUS_FONT_SIZE)
            self.game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
            self.confirm_font = pygame.font.Font(None, CONFIRM_MSG_FONT_SIZE)
            self.overlay_title_font = pygame.font.Font(None, OVERLAY_TITLE_FONT_SIZE)
            self.overlay_body_font = pygame.font.Font(None, OVERLAY_BODY_FONT_SIZE)

        self.buttons = []
        self.active_overlay_type = OVERLAY_NONE 
        self.overlay_title_text = ""
        self.overlay_body_paragraphs = []
        self.overlay_close_button = None 

        self._setup_buttons() 
        self.show_restart_confirmation = False 
        self._update_status_message()

    # ADD THIS METHOD BACK
    def _init_stockfish_engine(self):
        """Initializes the Stockfish engine if the path is valid."""
        if STOCKFISH_PATH and os.path.exists(STOCKFISH_PATH):
            try:
                self.stockfish_engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
                print(f"Stockfish engine initialized successfully from: {STOCKFISH_PATH}")
                # Set initial skill level based on current_ai_difficulty
                skill = STOCKFISH_SKILL_LEVELS.get(self.current_ai_difficulty, STOCKFISH_SKILL_LEVELS["Medium"]) # Fallback
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

        self.ai_difficulty_button = Button(panel_x, current_y, button_width, button_height,
                                           text="AI Difficulty", action=self._cycle_ai_difficulty)
        self.buttons.append(self.ai_difficulty_button)
        current_y += button_height + spacing

        self.rules_button = Button(panel_x, current_y, button_width, button_height,
                                   text="Game Rules", action=self._show_rules_overlay)
        self.buttons.append(self.rules_button)
        current_y += button_height + spacing
        
        self.about_button = Button(panel_x, current_y, button_width, button_height,
                                   text="About Game", action=self._show_about_overlay)
        self.buttons.append(self.about_button)

        exit_button_y = HEIGHT - button_height - 30 
        self.exit_button = Button(panel_x, exit_button_y, button_width, button_height,
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
        
        self.overlay_close_button = Button(0, 0, 100, 30, "Close", action=self._close_text_overlay)


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
            print(f"Error: Text file not found: {filename}")
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
        self._update_status_message()
        print("Game restarted.")
        if self.game_mode == MODE_PVA and self.chess_board.turn == chess.BLACK and not self.is_animating and not self.game_over:
            pygame.time.set_timer(pygame.USEREVENT + 1, 500) 

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
        if self.is_animating: return False

        if self.active_overlay_type in [OVERLAY_RULES, OVERLAY_ABOUT]:
            # Check if overlay_close_button has screen_rect, otherwise use its default rect
            # This assumes overlay_close_button.rect is updated to screen coords when drawn
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
        if self.game_over or self.is_animating: return
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

    def move_piece(self, from_coords, to_coords, is_ai_move=False): 
        if self.game_over or self.is_animating: return

        from_r, from_c = from_coords
        to_r, to_c = to_coords
        from_sq_chess = self._coords_to_chess_sq(from_r, from_c)
        to_sq_chess = self._coords_to_chess_sq(to_r, to_c)
        
        piece_to_animate_chess = self.chess_board.piece_at(from_sq_chess)
        if not piece_to_animate_chess: return 

        color_prefix = 'w' if piece_to_animate_chess.color == chess.WHITE else 'b'
        symbol = piece_to_animate_chess.symbol().upper()
        self.anim_piece_to_draw_after_anim = color_prefix + symbol

        promo = chess.QUEEN if piece_to_animate_chess.piece_type == chess.PAWN and \
                               ((piece_to_animate_chess.color == chess.WHITE and to_r == 0) or \
                                (piece_to_animate_chess.color == chess.BLACK and to_r == 7)) else None
        
        move = chess.Move(from_sq_chess, to_sq_chess, promotion=promo)

        self.is_animating = True
        self.animating_piece_surface = get_piece_image(self.visual_board[from_r][from_c])
        self.anim_start_pixel_pos = (from_c * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                     from_r * SQUARE_SIZE + SQUARE_SIZE // 2)
        self.anim_end_pixel_pos = (to_c * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                   to_r * SQUARE_SIZE + SQUARE_SIZE // 2)
        self.anim_current_pixel_pos = list(self.anim_start_pixel_pos)
        self.anim_original_start_coords = (from_r, from_c)
        self.anim_target_coords = (to_r, to_c)
        self.pending_move = move 
        play_sound('piece_move')
        
        self.selected_square_coords = None 
        self.valid_moves_coords = []
    def _trigger_ai_move(self):
        if self.game_over or self.is_animating or not self.stockfish_engine:
            self._update_status_message() 
            return
        if self.chess_board.turn == chess.BLACK: 
            print(f"AI ({self.current_ai_difficulty}) is thinking...")
            
            skill = STOCKFISH_SKILL_LEVELS.get(self.current_ai_difficulty, STOCKFISH_SKILL_LEVELS["Medium"]) 
            try:
                self.stockfish_engine.configure({"Skill Level": skill})
            except Exception as e: 
                print(f"Error configuring Stockfish for AI move: {e}")
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
                        self.move_piece(from_coords, to_coords, is_ai_move=True)
                else:
                    print("AI returned no move.")
                    self._update_status_message() 
            except chess.engine.EngineTerminatedError:
                print("Stockfish engine terminated unexpectedly during AI move.")
                self.stockfish_engine = None 
                self._update_status_message()
            except Exception as e:
                print(f"Error during AI move processing: {e}")
                self._update_status_message()
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

            if hasattr(self, 'pending_move') and self.pending_move:
                if self.pending_move in self.chess_board.legal_moves or self.chess_board.is_capture(self.pending_move): 
                    self.chess_board.push(self.pending_move)
                else: 
                    print(f"Warning: Pending move {self.pending_move.uci()} was not pushed. Current legal moves: {list(self.chess_board.legal_moves)}")
                self.pending_move = None 
            
            self._sync_visual_board() 
            self.animating_piece_surface = None
            self.anim_original_start_coords = None
            self.anim_target_coords = None
            
            self._update_status_message() 
            self._check_game_over()     

            if not self.game_over and self.game_mode == MODE_PVA and self.chess_board.turn == chess.BLACK:
                pygame.time.set_timer(pygame.USEREVENT + 1, 500) 
        else: 
            self.anim_current_pixel_pos[0] += (dx / distance) * ANIMATION_SPEED
            self.anim_current_pixel_pos[1] += (dy / distance) * ANIMATION_SPEED
    def _update_status_message(self):
        if self.game_over: 
            self.status_message = "" 
            return
        
        player_turn_text = ""
        if self.game_mode == MODE_PVP:
            player_turn_text = "White's Turn" if self.chess_board.turn == chess.WHITE else "Black's Turn"
        elif self.game_mode == MODE_PVA:
            if self.chess_board.turn == chess.BLACK and not self.is_animating and not self.game_over : 
                 player_turn_text = f"AI ({self.current_ai_difficulty}) is thinking..."
            else:
                player_turn_text = "Your Turn (White)" if self.chess_board.turn == chess.WHITE else "AI's Turn (Black)"
        
        self.status_message = f"{player_turn_text}{' - CHECK!' if self.chess_board.is_check() else ''}"
    def _check_game_over(self):
        if self.game_over: return 

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

    def draw_board_area(self, screen):
        for r_idx in range(ROWS):
            for c_idx in range(COLS):
                color = LIGHT_SQUARE if (r_idx + c_idx) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(screen, color, (c_idx * SQUARE_SIZE, r_idx * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        for r_idx in range(ROWS):
            for c_idx in range(COLS):
                if self.is_animating and self.anim_original_start_coords == (r_idx, c_idx):
                    continue 

                piece_notation = self.visual_board[r_idx][c_idx]
                if piece_notation:
                    image = get_piece_image(piece_notation)
                    if image:
                        img_rect = image.get_rect(center=(c_idx * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                          r_idx * SQUARE_SIZE + SQUARE_SIZE // 2))
                        screen.blit(image, img_rect.topleft)
        
        if not self.is_animating:
            if self.selected_square_coords:
                r, c = self.selected_square_coords
                highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                highlight_surface.fill(HIGHLIGHT_COLOR)
                screen.blit(highlight_surface, (c * SQUARE_SIZE, r * SQUARE_SIZE))

            for r_idx, c_idx in self.valid_moves_coords:
                center_x = c_idx * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = r_idx * SQUARE_SIZE + SQUARE_SIZE // 2
                pygame.draw.circle(screen, GREEN, (center_x, center_y), SQUARE_SIZE // 6)
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
        # Position close button on the overlay_surface
        self.overlay_close_button.rect.width = close_btn_width
        self.overlay_close_button.rect.height = close_btn_height
        self.overlay_close_button.rect.centerx = overlay_rect_on_screen.width // 2
        self.overlay_close_button.rect.bottom = overlay_rect_on_screen.height - 20
        
        # Store screen_rect for click detection
        self.overlay_close_button.screen_rect = pygame.Rect(
            self.overlay_close_button.rect.left + overlay_rect_on_screen.left,
            self.overlay_close_button.rect.top + overlay_rect_on_screen.top,
            close_btn_width, close_btn_height
        )
        self.overlay_close_button.draw(overlay_surface) # Draw on the local overlay surface
        screen.blit(overlay_surface, overlay_rect_on_screen.topleft)


    def update(self):
        if not self.game_over : 
            self._update_animation()

    def draw(self, screen):
        screen.fill(SIDE_PANEL_BG_COLOR) 
        self.draw_board_area(screen)     
        self.draw_animated_piece(screen) 
        self.draw_side_panel(screen)     
        
        # Draw overlays on top of game over, but game over on top of board
        self.draw_game_over_display(screen) 
        
        if self.active_overlay_type in [OVERLAY_RULES, OVERLAY_ABOUT]:
            self._draw_text_overlay(screen)
        elif self.show_restart_confirmation: 
             self.draw_restart_confirmation_dialog(screen)


    def handle_button_events(self, event):
        # This method is primarily for hover state updates for main buttons.
        # Click actions are now mostly handled by the Button class itself or specific logic in main.py.
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.handle_event(event) # Updates is_hovered for main buttons

            # Hover for overlay close button
            if self.active_overlay_type in [OVERLAY_RULES, OVERLAY_ABOUT] and self.overlay_close_button:
                if hasattr(self.overlay_close_button, 'screen_rect'):
                    self.overlay_close_button.is_hovered = self.overlay_close_button.screen_rect.collidepoint(event.pos)
                else: # Fallback if screen_rect not set (should be set during draw)
                    self.overlay_close_button.is_hovered = self.overlay_close_button.rect.collidepoint(event.pos)
            
            # Hover for restart confirmation buttons
            if self.show_restart_confirmation:
                self.confirm_yes_button.is_hovered = self.confirm_yes_button.rect.collidepoint(event.pos)
                self.confirm_no_button.is_hovered = self.confirm_no_button.rect.collidepoint(event.pos)
            return False # MOUSEMOTION doesn't "consume" a click in the context of main loop

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check main UI buttons first
            for button in self.buttons:
                # The Button's handle_event will call the action if clicked
                if button.handle_event(event): 
                    return True # Click was handled by a main UI button
            
            # If an overlay is active, its close button click is handled in handle_click_on_board_or_dialog
            # If restart confirmation is active, its buttons are handled in handle_click_on_board_or_dialog
            # This method now primarily signals if a main UI button was clicked.
            
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
