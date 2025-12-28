"""TeslaTower class - chains lightning between enemies."""

import pygame
import math
import random
from .base import Tower
from ..constants import WHITE, YELLOW


class TeslaTower(Tower):
    """Tesla tower with sphere design and orbiting satellites."""

    name = "Tesla"
    tower_type = "tesla"
    color = (0, 200, 255)  # Electric blue
    base_range = 130
    base_damage = 30
    base_fire_rate = 50
    cost = 200
    projectile_color = (100, 200, 255)

    def draw(self, screen):
        """Draw the tesla tower with sphere and satellite design."""
        # Draw range circle (semi-transparent)
        range_surface = pygame.Surface((int(self.range * 2), int(self.range * 2)), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (*self.color, 30),
                          (int(self.range), int(self.range)), int(self.range))
        screen.blit(range_surface, (int(self.x - self.range), int(self.y - self.range)))

        base_color = (self.color[0]//2, self.color[1]//2, self.color[2]//2)
        level_glow = (255, 255, 100) if self.level == 3 else (200, 200, 200) if self.level == 2 else None

        # Idle bob animation (subtle up-down movement)
        bob_offset = math.sin(self.animation_frame * 0.1) * 2

        # Draw level 3 glow
        if level_glow:
            glow_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*level_glow, 40),
                             (self.size * 2, self.size * 2), self.size * 2)
            screen.blit(glow_surface, (int(self.x - self.size * 2), int(self.y + bob_offset - self.size * 2)))

        # Tesla mech - sphere with lightning coils (satellites increase with level)
        y_pos = self.y + bob_offset
        # Base platform
        pygame.draw.circle(screen, base_color, (int(self.x), int(y_pos + 10)), 12)
        # Main sphere (cartoon style) - grows with level
        body_size = self.size + (self.level * 3)
        pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), body_size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), body_size, 2)
        # Tesla coils (satellites) - number increases with level
        # Level 1: 3 satellites, Level 2: 5 satellites, Level 3: 7 satellites
        num_satellites = 3 + (self.level - 1) * 2
        satellite_size = 4 + self.level  # Satellites also grow with level

        # Smooth rotation using time-based angle (prevents jitter)
        rotation_speed = 0.02  # Slower, smoother rotation
        rotation_offset = self.animation_frame * rotation_speed

        for i in range(num_satellites):
            # Evenly distribute satellites around the circle
            base_angle = (i * 2 * math.pi / num_satellites)
            angle = base_angle + rotation_offset
            coil_x = self.x + body_size * 1.3 * math.cos(angle)
            coil_y = y_pos + body_size * 1.3 * math.sin(angle)
            pygame.draw.circle(screen, (255, 255, 0), (int(coil_x), int(coil_y)), satellite_size)
            pygame.draw.circle(screen, self.color, (int(coil_x), int(coil_y)), satellite_size - 2)
        # Electric arc when shooting
        if self.shoot_flash > 0:
            arc_count = 3 + self.level  # More arcs at higher levels
            for i in range(arc_count):
                offset_x = random.randint(-15, 15)
                offset_y = random.randint(-15, 15)
                pygame.draw.line(screen, WHITE, (self.x, y_pos),
                               (self.x + offset_x, y_pos + offset_y), 2)
        # Core (glowing center) - grows with level
        core_size = 8 + self.level
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), core_size)
        pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), core_size - 3)

        # Draw level indicator
        if self.level > 1:
            star_text = "★" * self.level
            font = pygame.font.Font(None, 16)
            level_surf = font.render(star_text, True, YELLOW)
            screen.blit(level_surf, (int(self.x - 12), int(self.y + 22)))
