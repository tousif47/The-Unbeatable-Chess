# src/assets_manager.py

import pygame
import os
from src.constants import PIECE_IMAGES, IMAGE_PATH, SQUARE_SIZE, SOUND_FILES, SOUND_PATH

# Dictionary to hold the loaded and scaled images
LOADED_ASSETS = {}
# Dictionary to hold the loaded sound objects
LOADED_SOUNDS = {}

def load_images():
    """
    Loads all piece images from the assets folder, scales them,
    and stores them in the LOADED_ASSETS dictionary.
    This function MUST be called after pygame.display.set_mode() has been called.
    """
    print(f"Attempting to load images from: {IMAGE_PATH}")
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
            image = pygame.image.load(path).convert_alpha()
            scaled_image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            LOADED_ASSETS[piece] = scaled_image
        except pygame.error as e:
            print(f"Pygame error loading image {filename}: {e}")
            LOADED_ASSETS[piece] = None
        except Exception as e:
            print(f"Unexpected error loading image {filename}: {e}")
            LOADED_ASSETS[piece] = None
    
    successfully_loaded_count = sum(1 for img in LOADED_ASSETS.values() if img is not None)
    print(f"Image loading complete. Successfully loaded {successfully_loaded_count}/{len(PIECE_IMAGES)} images.")
    if successfully_loaded_count < len(PIECE_IMAGES):
        print("WARNING: Not all piece images were loaded.")

def get_piece_image(piece_notation):
    """Returns the pre-loaded pygame.Surface for the given piece notation."""
    return LOADED_ASSETS.get(piece_notation, None)

def load_sounds():
    """
    Loads all sound effects from the assets folder.
    This function should be called after pygame.mixer.init().
    """
    print(f"Attempting to load sounds from: {SOUND_PATH}")
    if not os.path.exists(SOUND_PATH):
        print(f"ERROR: Sound path does not exist: {SOUND_PATH}")
        return

    # Ensure the mixer is initialized with good defaults
    # Pygame's pygame.init() usually calls pygame.mixer.init()
    # but explicit call can configure parameters if needed.
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("Pygame mixer initialized by assets_manager.")
        except pygame.error as e:
            print(f"Error initializing pygame.mixer: {e}. Sounds may not play.")
            return # Cannot load sounds if mixer fails

    for sound_name, filename in SOUND_FILES.items():
        try:
            path = os.path.join(SOUND_PATH, filename)
            if not os.path.exists(path):
                print(f"ERROR: Sound file not found: {path} for sound '{sound_name}'")
                LOADED_SOUNDS[sound_name] = None
                continue
            sound = pygame.mixer.Sound(path)
            LOADED_SOUNDS[sound_name] = sound
            # print(f"Loaded sound: {filename} as '{sound_name}'")
        except pygame.error as e:
            print(f"Pygame error loading sound {filename}: {e}")
            LOADED_SOUNDS[sound_name] = None
        except Exception as e:
            print(f"Unexpected error loading sound {filename}: {e}")
            LOADED_SOUNDS[sound_name] = None

    successfully_loaded_count = sum(1 for snd in LOADED_SOUNDS.values() if snd is not None)
    print(f"Sound loading complete. Successfully loaded {successfully_loaded_count}/{len(SOUND_FILES)} sounds.")
    if successfully_loaded_count < len(SOUND_FILES):
        print("WARNING: Not all sound files were loaded.")


def play_sound(sound_name):
    """Plays the pre-loaded sound effect for the given sound name."""
    if not pygame.mixer.get_init():
        # print("Mixer not initialized. Cannot play sound.") # Avoid spamming console
        return

    sound = LOADED_SOUNDS.get(sound_name)
    if sound:
        try:
            sound.play()
        except pygame.error as e:
            print(f"Error playing sound '{sound_name}': {e}")
    # else:
        # print(f"Sound '{sound_name}' not found or not loaded.")
