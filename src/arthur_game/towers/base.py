"""Base Tower class with common functionality for all tower types."""

import pygame
import math
from ..constants import WHITE, BLACK, GRAY, YELLOW
from ..projectile import Projectile


class Tower:
    """Base tower class with common functionality."""

    # Subclasses should override these
    name = "Tower"
    tower_type = "basic"
    color = WHITE
    base_range = 100
    base_damage = 10
    base_fire_rate = 30
    cost = 50
    projectile_color = YELLOW

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 1
        self.target_angle = 0
        self.update_stats()
        self.cooldown = 0
        self.size = 22
        self.animation_frame = 0
        self.shoot_flash = 0

    def update_stats(self):
        """Update tower stats based on current level."""
        level_multiplier = 1 + (self.level - 1) * 0.5
        self.range = self.base_range * level_multiplier
        self.damage = self.base_damage * level_multiplier
        self.fire_rate = self.base_fire_rate

    def get_upgrade_cost(self):
        """Calculate the cost to upgrade this tower."""
        if self.level >= 3:
            return None
        return int(self.cost * (1.5 ** self.level))

    def upgrade(self):
        """Upgrade the tower to the next level."""
        if self.level < 3:
            self.level += 1
            self.update_stats()
            return True
        return False

    def find_target(self, enemies):
        """Find the first enemy within range."""
        for enemy in enemies:
            dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if dist <= self.range:
                return enemy
        return None

    def shoot(self, target):
        """Create and return a projectile aimed at the target. Returns None if on cooldown."""
        if self.cooldown <= 0:
            # Reset cooldown
            self.cooldown = self.fire_rate

            # Calculate angle to target (for rotating turrets)
            dx = target.x - self.x
            dy = target.y - self.y
            self.target_angle = math.atan2(dy, dx)

            self.shoot_flash = 8
            return Projectile(
                self.x, self.y, target, self.damage,
                self.projectile_color, tower_level=self.level, tower_type=self.tower_type
            )
        return None

    def update(self):
        """Update tower cooldown and animation."""
        if self.cooldown > 0:
            self.cooldown -= 1
        self.animation_frame += 1
        if self.shoot_flash > 0:
            self.shoot_flash -= 1

    def draw_barrel_lines(self, screen, start_x, start_y, end_x, end_y, color, base_width=4):
        """Draw multiple parallel lines for barrel based on tower level."""
        if self.level == 1:
            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), base_width)
        elif self.level == 2:
            angle = self.target_angle
            offset = 2
            perp_x = -math.sin(angle) * offset
            perp_y = math.cos(angle) * offset

            pygame.draw.line(screen, color,
                           (start_x + perp_x, start_y + perp_y),
                           (end_x + perp_x, end_y + perp_y), base_width)
            pygame.draw.line(screen, color,
                           (start_x - perp_x, start_y - perp_y),
                           (end_x - perp_x, end_y - perp_y), base_width)
        else:  # level == 3
            angle = self.target_angle
            offset = 3
            perp_x = -math.sin(angle) * offset
            perp_y = math.cos(angle) * offset

            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), base_width)
            pygame.draw.line(screen, color,
                           (start_x + perp_x, start_y + perp_y),
                           (end_x + perp_x, end_y + perp_y), base_width)
            pygame.draw.line(screen, color,
                           (start_x - perp_x, start_y - perp_y),
                           (end_x - perp_x, end_y - perp_y), base_width)

    def draw(self, screen):
        """Draw the tower. Override in subclasses for unique visuals."""
        # Base animation
        bob_offset = math.sin(self.animation_frame * 0.1) * 2
        y_pos = self.y + bob_offset
        base_color = GRAY

        # Simple circle representation (override in subclasses)
        pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), self.size, 2)

        # Draw level indicator
        if self.level > 1:
            star_text = "★" * self.level
            font = pygame.font.Font(None, 16)
            level_surf = font.render(star_text, True, YELLOW)
            screen.blit(level_surf, (int(self.x - 12), int(self.y + 22)))
