"""PlasmaTower class - massive plasma cannon with splash damage."""

import pygame
import math
from .base import Tower
from ..constants import WHITE, YELLOW


class PlasmaTower(Tower):
    """Plasma tower with massive cannon design."""

    name = "Plasma"
    tower_type = "plasma"
    color = (0, 200, 0)  # Dark green
    base_range = 160
    base_damage = 150
    base_fire_rate = 150
    cost = 350
    projectile_color = (100, 255, 100)

    def draw(self, screen):
        """Draw the plasma tower with massive cannon design."""
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

        # Plasma cannon - massive gun with huge barrel
        y_pos = self.y + bob_offset * 0.4  # Heavy weapon, less bob
        # Heavy base (4 legs)
        for i in range(4):
            angle = i * math.pi / 2
            leg_x = self.x + 15 * math.cos(angle)
            leg_y = self.y + 15 * math.sin(angle)
            pygame.draw.line(screen, base_color, (self.x, y_pos + 5),
                           (leg_x, leg_y + 12), 5)
        # Body - large cylinder (cartoon style)
        body_size = self.size + (self.level * 3)
        pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), body_size + 4)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), body_size + 4, 3)
        pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), body_size)
        # Massive plasma cannon with level-based multiple barrels
        cannon_length = 30 + self.level * 5
        end_x = self.x + math.cos(self.target_angle) * cannon_length
        end_y = y_pos + math.sin(self.target_angle) * cannon_length
        # Draw thick green plasma cannon
        self.draw_barrel_lines(screen, self.x, y_pos, end_x, end_y, (0, 150, 0), 8)
        # Muzzle glow when shooting (green plasma)
        if self.shoot_flash > 0:
            flash_size = 15 + self.shoot_flash
            flash_x = end_x + math.cos(self.target_angle) * 10
            flash_y = end_y + math.sin(self.target_angle) * 10
            pygame.draw.circle(screen, WHITE, (int(flash_x), int(flash_y)), flash_size)
            pygame.draw.circle(screen, (0, 255, 0), (int(flash_x), int(flash_y)), flash_size - 3)
            pygame.draw.circle(screen, (100, 255, 100), (int(flash_x), int(flash_y)), flash_size - 6)

        # Draw level indicator
        if self.level > 1:
            star_text = "★" * self.level
            font = pygame.font.Font(None, 16)
            level_surf = font.render(star_text, True, YELLOW)
            screen.blit(level_surf, (int(self.x - 12), int(self.y + 22)))
