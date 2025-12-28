"""IonTower class - continuous beam weapon with fast fire rate."""

import pygame
import math
from .base import Tower
from ..constants import WHITE, YELLOW


class IonTower(Tower):
    """Ion tower with crystal design and continuous beam."""

    name = "Ion Beam"
    tower_type = "ion"
    color = (0, 255, 200)  # Teal
    base_range = 180
    base_damage = 60
    base_fire_rate = 20  # Fast continuous beam
    cost = 500
    projectile_color = (100, 255, 200)

    def draw(self, screen):
        """Draw the ion tower with crystal design."""
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

        # Ion beam - sleek crystal tower with beam emitter
        y_pos = self.y + bob_offset * 0.7
        # Crystal base
        points = [
            (int(self.x), int(y_pos + 15)),
            (int(self.x - 12), int(y_pos + 5)),
            (int(self.x + 12), int(y_pos + 5))
        ]
        pygame.draw.polygon(screen, base_color, points)
        # Main crystal body (cartoon style)
        body_size = self.size + (self.level * 2)
        # Draw as diamond shape
        diamond_points = [
            (int(self.x), int(y_pos - body_size)),
            (int(self.x - body_size * 0.7), int(y_pos)),
            (int(self.x), int(y_pos + body_size)),
            (int(self.x + body_size * 0.7), int(y_pos))
        ]
        pygame.draw.polygon(screen, self.color, diamond_points)
        pygame.draw.polygon(screen, WHITE, diamond_points, 2)
        # Ion beam emitter at top
        tip_x = self.x
        tip_y = y_pos - body_size
        pygame.draw.circle(screen, WHITE, (int(tip_x), int(tip_y)), 6)
        pygame.draw.circle(screen, self.color, (int(tip_x), int(tip_y)), 4)
        # Continuous beam effect when shooting (level-based width)
        if self.shoot_flash > 0:
            beam_length = self.range
            beam_end_x = self.x + math.cos(self.target_angle) * beam_length
            beam_end_y = y_pos + math.sin(self.target_angle) * beam_length
            # Draw beam with multiple lines for higher levels
            if self.level == 1:
                for width in range(8, 0, -2):
                    beam_color = (100 + width * 15, 255, 200)
                    pygame.draw.line(screen, beam_color, (tip_x, tip_y),
                                   (beam_end_x, beam_end_y), width)
            elif self.level == 2:
                # Double beam
                for width in range(6, 0, -2):
                    beam_color = (100 + width * 15, 255, 200)
                    offset = 3
                    perp_x = -math.sin(self.target_angle) * offset
                    perp_y = math.cos(self.target_angle) * offset
                    pygame.draw.line(screen, beam_color,
                                   (tip_x + perp_x, tip_y + perp_y),
                                   (beam_end_x + perp_x, beam_end_y + perp_y), width)
                    pygame.draw.line(screen, beam_color,
                                   (tip_x - perp_x, tip_y - perp_y),
                                   (beam_end_x - perp_x, beam_end_y - perp_y), width)
            else:  # level 3
                # Triple beam
                for width in range(6, 0, -2):
                    beam_color = (100 + width * 15, 255, 200)
                    offset = 4
                    perp_x = -math.sin(self.target_angle) * offset
                    perp_y = math.cos(self.target_angle) * offset
                    # Center beam
                    pygame.draw.line(screen, beam_color, (tip_x, tip_y),
                                   (beam_end_x, beam_end_y), width)
                    # Side beams
                    pygame.draw.line(screen, beam_color,
                                   (tip_x + perp_x, tip_y + perp_y),
                                   (beam_end_x + perp_x, beam_end_y + perp_y), width)
                    pygame.draw.line(screen, beam_color,
                                   (tip_x - perp_x, tip_y - perp_y),
                                   (beam_end_x - perp_x, beam_end_y - perp_y), width)
        # Energy pulses
        pulse = (self.animation_frame % 30) / 30.0
        pulse_size = int(body_size * (0.5 + pulse * 0.5))
        pygame.draw.circle(screen, (*self.color, 100), (int(self.x), int(y_pos)), pulse_size)

        # Draw level indicator
        if self.level > 1:
            star_text = "★" * self.level
            font = pygame.font.Font(None, 16)
            level_surf = font.render(star_text, True, YELLOW)
            screen.blit(level_surf, (int(self.x - 12), int(self.y + 22)))
