# src/ui_elements.py

import pygame
from src.constants import BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, FONT_NAME, BUTTON_FONT_SIZE

class Button:
    """A simple clickable button class."""
    def __init__(self, x, y, width, height, text='', color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action # A function to call when clicked
        self.is_hovered = False

        try:
            self.font = pygame.font.SysFont(FONT_NAME, BUTTON_FONT_SIZE)
        except:
            self.font = pygame.font.Font(None, BUTTON_FONT_SIZE)


    def draw(self, screen):
        """Draws the button on the screen."""
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=5)

        if self.text != '':
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Handles mouse events for hover and click."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered: # Left click
                if self.action:
                    self.action() # Execute the button's action
                return True # Indicate the button was clicked
        return False

    def update_text(self, new_text):
        """Updates the button's text."""
        self.text = new_text
