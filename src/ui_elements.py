# src/ui_elements.py

import pygame
from src.constants import (BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
                           BUTTON_DISABLED_COLOR, BUTTON_DISABLED_TEXT_COLOR,
                           FONT_NAME, BUTTON_FONT_SIZE)

class Button:
    """A simple clickable button class."""
    def __init__(self, x, y, width, height, text='',
                 color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR,
                 disabled_color=BUTTON_DISABLED_COLOR, disabled_text_color=BUTTON_DISABLED_TEXT_COLOR,
                 action=None, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.base_hover_color = hover_color
        self.base_text_color = text_color
        
        self.disabled_color = disabled_color
        self.disabled_text_color = disabled_text_color
        
        self.action = action
        self.is_hovered = False
        self.enabled = enabled

        try:
            self.font = pygame.font.SysFont(FONT_NAME, BUTTON_FONT_SIZE)
        except:
            self.font = pygame.font.Font(None, BUTTON_FONT_SIZE)

    def draw(self, screen):
        current_bg_color = self.base_color
        current_text_color = self.base_text_color

        if not self.enabled:
            current_bg_color = self.disabled_color
            current_text_color = self.disabled_text_color
        elif self.is_hovered:
            current_bg_color = self.base_hover_color
        
        pygame.draw.rect(screen, current_bg_color, self.rect, border_radius=5)

        if self.text != '':
            text_surface = self.font.render(self.text, True, current_text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """
        Handles mouse events. Updates hover state.
        If a click occurs on an enabled button, it executes the action and returns True.
        Returns True if a click was handled by this button, False otherwise.
        """
        if not self.enabled:
            self.is_hovered = False # Ensure hover is off if disabled
            return False # Event not handled

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False # MOUSEMOTION doesn't "consume" the click for other handlers
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered: # Left click on hovered button
                if self.action:
                    self.action() # Execute the button's action
                return True # Click was handled by this button
        
        return False # Event was not a click on this button

    def update_text(self, new_text):
        self.text = new_text

    def set_enabled(self, enabled_status):
        self.enabled = enabled_status
        if not self.enabled:
            self.is_hovered = False
