# src/assets_manager.py

import pygame
import os
# Corrected: Absolute import from the 'src' package
from src.constants import PIECE_IMAGES, IMAGE_PATH, SQUARE_SIZE

# Dictionary to hold the loaded and scaled images
# Initialize as empty; will be populated by load_images() when called
LOADED_ASSETS = {}

def load_images():
    """
    Loads all piece images from the assets folder, scales them,
    and stores them in the LOADED_ASSETS dictionary.
    This function MUST be called after pygame.display.set_mode() has been called.
    """
    print(f"Attempting to load images from: {IMAGE_PATH}") # Debug print
    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image path does not exist: {IMAGE_PATH}")
        return

    for piece, filename in PIECE_IMAGES.items():
        try:
            path = os.path.join(IMAGE_PATH, filename)
            if not os.path.exists(path):
                print(f"ERROR: Image file not found: {path} for piece {piece}")
                LOADED_ASSETS[piece] = None
                continue

            # Load the image
            image = pygame.image.load(path)
            # convert_alpha() is important for images with transparency (like PNGs)
            # and for performance. It requires the display to be initialized.
            image = image.convert_alpha()
            
            # Scale the image to fit the square size
            scaled_image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            LOADED_ASSETS[piece] = scaled_image
            # print(f"Loaded and scaled: {filename}")
        except pygame.error as e:
            print(f"Pygame error loading image {filename}: {e}")
            LOADED_ASSETS[piece] = None
        except Exception as e: # Catch any other unexpected errors
            print(f"Unexpected error loading image {filename}: {e}")
            LOADED_ASSETS[piece] = None
    
    # Count successfully loaded images for debugging
    successfully_loaded_count = sum(1 for img in LOADED_ASSETS.values() if img is not None)
    print(f"Assets loading complete. Successfully loaded {successfully_loaded_count}/{len(PIECE_IMAGES)} images.")
    if successfully_loaded_count < len(PIECE_IMAGES):
        print("WARNING: Not all piece images were loaded. Check paths and filenames in assets/images/pieces/ and constants.py")


def get_piece_image(piece_notation):
    """Returns the pre-loaded pygame.Surface for the given piece notation."""
    # This will now return images only if load_images() has been successfully called.
    return LOADED_ASSETS.get(piece_notation, None)

# DO NOT call load_images() here anymore. It will be called from main.py
# load_images() 
