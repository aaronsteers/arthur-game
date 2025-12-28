"""QuantumTower class - advanced tower with quantum disruption capabilities."""

import pygame
import math
from .base import Tower
from ..constants import WHITE, YELLOW


class QuantumTower(Tower):
    """Quantum tower with floating golden sphere and rotating rings."""

    name = "Quantum"
    tower_type = "quantum"
    color = (255, 215, 0)  # Gold
    base_range = 150
    base_damage = 80
    base_fire_rate = 100
    cost = 750
    projectile_color = (255, 235, 100)

    def draw(self, screen):
        """Draw the quantum tower with floating sphere and rings."""
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

        # Quantum disruptor - floating golden sphere with rings
        y_pos = self.y + bob_offset * 1.5  # More dramatic floating
        # Quantum rings (rotating) - golden
        body_size = self.size + (self.level * 3)
        for i in range(3):
            ring_angle = self.animation_frame * 0.05 + i * math.pi / 3
            ring_radius = body_size + 8 + i * 4
            # Draw ring as ellipse for 3D effect
            for angle_step in range(0, 360, 30):
                angle = math.radians(angle_step)
                x1 = self.x + ring_radius * math.cos(angle) * math.cos(ring_angle)
                y1 = y_pos + ring_radius * math.sin(angle) * 0.3
                pygame.draw.circle(screen, (200, 150, 0), (int(x1), int(y1)), 2)
        # Core sphere (cartoon style with golden appearance)
        pygame.draw.circle(screen, (200, 150, 0), (int(self.x), int(y_pos)), body_size + 3)
        pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), body_size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), body_size, 2)
        # Quantum laser beam when shooting (level-based)
        if self.shoot_flash > 0:
            beam_length = self.range
            beam_end_x = self.x + math.cos(self.target_angle) * beam_length
            beam_end_y = y_pos + math.sin(self.target_angle) * beam_length
            # Draw golden quantum beam with multiple lines for higher levels
            if self.level == 1:
                for width in range(8, 0, -2):
                    beam_color = (255, 215 - width * 10, width * 10)
                    pygame.draw.line(screen, beam_color, (self.x, y_pos),
                                   (beam_end_x, beam_end_y), width)
            elif self.level == 2:
                # Double beam
                for width in range(6, 0, -2):
                    beam_color = (255, 215 - width * 10, width * 10)
                    offset = 3
                    perp_x = -math.sin(self.target_angle) * offset
                    perp_y = math.cos(self.target_angle) * offset
                    pygame.draw.line(screen, beam_color,
                                   (self.x + perp_x, y_pos + perp_y),
                                   (beam_end_x + perp_x, beam_end_y + perp_y), width)
                    pygame.draw.line(screen, beam_color,
                                   (self.x - perp_x, y_pos - perp_y),
                                   (beam_end_x - perp_x, beam_end_y - perp_y), width)
            else:  # level 3
                # Triple beam
                for width in range(6, 0, -2):
                    beam_color = (255, 215 - width * 10, width * 10)
                    offset = 4
                    perp_x = -math.sin(self.target_angle) * offset
                    perp_y = math.cos(self.target_angle) * offset
                    # Center beam
                    pygame.draw.line(screen, beam_color, (self.x, y_pos),
                                   (beam_end_x, beam_end_y), width)
                    # Side beams
                    pygame.draw.line(screen, beam_color,
                                   (self.x + perp_x, y_pos + perp_y),
                                   (beam_end_x + perp_x, beam_end_y + perp_y), width)
                    pygame.draw.line(screen, beam_color,
                                   (self.x - perp_x, y_pos - perp_y),
                                   (beam_end_x - perp_x, beam_end_y - perp_y), width)
        # Glowing core (golden)
        core_pulse = abs(math.sin(self.animation_frame * 0.1))
        core_size = int(8 * (0.5 + core_pulse * 0.5))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), core_size)
        pygame.draw.circle(screen, (255, 235, 100), (int(self.x), int(y_pos)), core_size - 2)

        # Draw level indicator
        if self.level > 1:
            star_text = "★" * self.level
            font = pygame.font.Font(None, 16)
            level_surf = font.render(star_text, True, YELLOW)
            screen.blit(level_surf, (int(self.x - 12), int(self.y + 22)))
