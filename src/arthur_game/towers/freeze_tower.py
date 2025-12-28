"""FreezeTower class - slows enemies with freeze rays."""

import pygame
import math
from .base import Tower
from ..constants import WHITE, CYAN, YELLOW


class FreezeTower(Tower):
    """Freeze tower with hexagonal design and freeze emitters."""

    name = "Freeze"
    tower_type = "freeze"
    color = CYAN
    base_range = 100
    base_damage = 5
    base_fire_rate = 45
    cost = 75
    projectile_color = CYAN

    def draw(self, screen):
        """Draw the freeze tower with hexagonal mech design."""
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

        # Freeze mech - hexagonal with freeze emitters
        y_pos = self.y + bob_offset
        # Base
        pygame.draw.circle(screen, base_color, (int(self.x), int(y_pos + 8)), 10)
        # Body - hexagon (cartoon style with rounded edges)
        body_size = self.size + (self.level * 2)
        pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), body_size + 2)
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            px = self.x + body_size * math.cos(angle)
            py = y_pos + body_size * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)
        # Freeze emitters (3 crystals with glow)
        for i in range(3):
            angle = i * (2 * math.pi / 3)
            crystal_x = self.x + (body_size + 8) * math.cos(angle)
            crystal_y = y_pos + (body_size + 8) * math.sin(angle)
            # Glow effect
            if self.shoot_flash > 0:
                pygame.draw.circle(screen, WHITE, (int(crystal_x), int(crystal_y)), 7)
            pygame.draw.circle(screen, CYAN, (int(crystal_x), int(crystal_y)), 5)
            pygame.draw.circle(screen, WHITE, (int(crystal_x), int(crystal_y)), 2)
        # Cartoon face
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), 4)

        # Draw level indicator
        if self.level > 1:
            star_text = "★" * self.level
            font = pygame.font.Font(None, 16)
            level_surf = font.render(star_text, True, YELLOW)
            screen.blit(level_surf, (int(self.x - 12), int(self.y + 22)))
