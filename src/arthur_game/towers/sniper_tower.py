"""SniperTower class - long range, high damage, slow fire rate."""

import pygame
import math
from .base import Tower
from ..constants import WHITE, PURPLE, YELLOW


class SniperTower(Tower):
    """Sniper tower with tall design and long barrel."""

    name = "Sniper"
    tower_type = "sniper"
    color = PURPLE
    base_range = 200
    base_damage = 80
    base_fire_rate = 120
    cost = 100
    projectile_color = PURPLE

    def draw(self, screen):
        """Draw the sniper tower with tall mech design."""
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

        # Sniper mech - tall with long barrel
        y_pos = self.y + bob_offset * 0.5  # Less bob for stability
        # Legs (tripod)
        for i in range(3):
            angle = i * (2 * math.pi / 3)
            leg_x = self.x + 10 * math.cos(angle)
            leg_y = self.y + 10 * math.sin(angle)
            pygame.draw.line(screen, base_color,
                           (self.x, y_pos + 5), (leg_x, leg_y + 15), 4)
        # Body - tall cylinder (cartoon style)
        body_size = self.size + (self.level * 2)
        pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), body_size + 2)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), body_size + 2, 2)
        pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), body_size)
        # Long rotating barrel with level-based multiple barrels
        barrel_length = 25 + self.level * 5
        end_x = self.x + math.cos(self.target_angle) * barrel_length
        end_y = y_pos + math.sin(self.target_angle) * barrel_length
        self.draw_barrel_lines(screen, self.x, y_pos, end_x, end_y, PURPLE, 4)
        # Add white highlight on main line
        pygame.draw.line(screen, WHITE, (self.x, y_pos), (end_x - 2, end_y - 2), 1)
        # Muzzle flash
        if self.shoot_flash > 0:
            flash_x = end_x + math.cos(self.target_angle) * 12
            flash_y = end_y + math.sin(self.target_angle) * 12
            pygame.draw.circle(screen, WHITE, (int(flash_x), int(flash_y)), 10)
            pygame.draw.circle(screen, PURPLE, (int(flash_x), int(flash_y)), 6)
        # Scope (cartoon eye)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), 6)
        pygame.draw.circle(screen, (220, 50, 50), (int(self.x), int(y_pos)), 3)

        # Draw level indicator
        if self.level > 1:
            star_text = "★" * self.level
            font = pygame.font.Font(None, 16)
            level_surf = font.render(star_text, True, YELLOW)
            screen.blit(level_surf, (int(self.x - 12), int(self.y + 22)))
