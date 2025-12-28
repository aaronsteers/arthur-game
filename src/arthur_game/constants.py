"""Game constants including colors, screen dimensions, and paths."""

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 40
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPACE_BG = (10, 10, 30)  # Dark space background
RED = (220, 50, 50)
BLUE = (50, 150, 255)  # Bright blue for laser
CYAN = (0, 255, 255)  # Cyan for freeze
YELLOW = (255, 255, 0)  # Bright yellow for lasers
PURPLE = (200, 50, 255)  # Purple for sniper
ORANGE = (255, 100, 0)  # Orange for missiles
GRAY = (80, 80, 100)  # Space gray for path
LIGHT_GRAY = (40, 40, 60)  # Dark UI
NEON_GREEN = (0, 255, 100)
STEEL_BLUE = (70, 130, 180)

# Game path (enemies follow this) - scaled for 16:9
PATH = [
    (0, 300),
    (480, 300),
    (480, 520),
    (800, 520),
    (800, 180),
    (1280, 180)
]
