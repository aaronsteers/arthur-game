"""MissileTower class - fires explosive missiles at enemies."""

import pygame
import math
from .base import Tower
from ..constants import WHITE, BLACK, GRAY, ORANGE, YELLOW


class MissileTower(Tower):
    """Missile tower with tank-like design and missile pods."""

    name = "Missile"
    tower_type = "missile"
    color = ORANGE
    base_range = 140
    base_damage = 40
    base_fire_rate = 90
    cost = 125
    projectile_color = ORANGE

    def draw(self, screen):
        """Draw the missile tower with tank-like mech design."""
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

        # Missile mech - square tank-like with missile pods
        y_pos = self.y + bob_offset * 0.3  # Minimal bob for heavy tank
        # Treads (cartoon style)
        pygame.draw.rect(screen, base_color,
                       (int(self.x - 20), int(y_pos + 6), 40, 14), border_radius=5)
        pygame.draw.rect(screen, GRAY, (int(self.x - 18), int(y_pos + 8), 36, 10), border_radius=3)
        # Body - rounded square (cartoon style)
        body_size = self.size + (self.level * 3)
        pygame.draw.rect(screen, self.color,
                       (int(self.x - body_size), int(y_pos - body_size),
                        body_size * 2, body_size * 2), border_radius=5)
        pygame.draw.rect(screen, WHITE,
                       (int(self.x - body_size), int(y_pos - body_size),
                        body_size * 2, body_size * 2), 2, border_radius=5)
        # Missile pods with glow
        pod_count = 2 + self.level
        for i in range(pod_count):
            pod_x = self.x - body_size + 8 + i * 10
            pygame.draw.rect(screen, ORANGE,
                           (int(pod_x), int(y_pos - body_size - 10), 7, 10), border_radius=2)
            if self.shoot_flash > 0:
                pygame.draw.circle(screen, WHITE, (int(pod_x + 3), int(y_pos - body_size - 12)), 6)
                pygame.draw.circle(screen, ORANGE, (int(pod_x + 3), int(y_pos - body_size - 12)), 3)
        # Targeting laser (cartoon eye)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(y_pos)), 6)
        pygame.draw.circle(screen, (220, 50, 50), (int(self.x), int(y_pos)), 4)

        # Draw level indicator
        if self.level > 1:
            star_text = "★" * self.level
            font = pygame.font.Font(None, 16)
            level_surf = font.render(star_text, True, YELLOW)
            screen.blit(level_surf, (int(self.x - 12), int(self.y + 22)))
