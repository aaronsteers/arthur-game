"""LaserTower class - basic tower type with rotating cannon."""

import pygame
import math
from .base import Tower
from ..constants import WHITE, BLACK, BLUE, YELLOW


class LaserTower(Tower):
    """Laser tower with bipedal mech and rotating cannon."""

    name = "Laser"
    tower_type = "basic"
    color = BLUE
    base_range = 120
    base_damage = 20
    base_fire_rate = 30
    cost = 50
    projectile_color = YELLOW

    def draw(self, screen):
        """Draw the laser tower with bipedal mech design."""
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

        # Laser mech - bipedal with rotating cannon
        y_pos = self.y + bob_offset
        # Legs
        leg_width = 6
        pygame.draw.rect(screen, base_color,
                       (int(self.x - 12), int(y_pos + 8), leg_width, 12))
        pygame.draw.rect(screen, base_color,
                       (int(self.x + 6), int(y_pos + 8), leg_width, 12))
        # Body (rounded cartoon style)
        body_size = self.size + (self.level * 2)
        pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), body_size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), body_size, 2)
        # Rotating cannon with level-based multiple barrels
        cannon_length = 15 + self.level * 3
        end_x = self.x + math.cos(self.target_angle) * cannon_length
        end_y = y_pos + math.sin(self.target_angle) * cannon_length
        self.draw_barrel_lines(screen, self.x, y_pos, end_x, end_y, YELLOW, 4)
        # Muzzle flash when shooting
        if self.shoot_flash > 0:
            flash_x = end_x + math.cos(self.target_angle) * 8
            flash_y = end_y + math.sin(self.target_angle) * 8
            pygame.draw.circle(screen, WHITE, (int(flash_x), int(flash_y)), 8)
            pygame.draw.circle(screen, YELLOW, (int(flash_x), int(flash_y)), 5)
        # Cartoon eyes
        eye_size = 3
        pygame.draw.circle(screen, WHITE, (int(self.x - 5), int(y_pos - 3)), eye_size)
        pygame.draw.circle(screen, BLACK, (int(self.x - 5), int(y_pos - 3)), eye_size - 1)
        pygame.draw.circle(screen, WHITE, (int(self.x + 5), int(y_pos - 3)), eye_size)
        pygame.draw.circle(screen, BLACK, (int(self.x + 5), int(y_pos - 3)), eye_size - 1)

        # Draw level indicator
        if self.level > 1:
            star_text = "★" * self.level
            font = pygame.font.Font(None, 16)
            level_surf = font.render(star_text, True, YELLOW)
            screen.blit(level_surf, (int(self.x - 12), int(self.y + 22)))
