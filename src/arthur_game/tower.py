"""
Tower class for Arthur's Tower Defense game.

Defines all tower types and their properties, including damage, range, fire rate,
and visual rendering for each unique tower type.
"""

import pygame
import math
import random
from .constants import (
    WHITE, BLACK, BLUE, CYAN, YELLOW, PURPLE, ORANGE, GRAY,
    NEON_GREEN, STEEL_BLUE
)
from .projectile import Projectile


class Tower:
    """Represents a tower in the game with different types and upgrade levels."""

    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.type = tower_type
        self.level = 1  # Upgrade level (1, 2, or 3)
        self.target_angle = 0  # For rotating turret

        # Base stats for each tower type
        if tower_type == "basic":
            self.name = "Laser"
            self.color = BLUE
            self.base_range = 120
            self.base_damage = 20
            self.base_fire_rate = 30
            self.cost = 50
            self.projectile_color = YELLOW
        elif tower_type == "freeze":
            self.name = "Freeze"
            self.color = CYAN
            self.base_range = 100
            self.base_damage = 5
            self.base_fire_rate = 45
            self.cost = 75
            self.projectile_color = CYAN
        elif tower_type == "sniper":
            self.name = "Sniper"
            self.color = PURPLE
            self.base_range = 200
            self.base_damage = 80
            self.base_fire_rate = 120
            self.cost = 100
            self.projectile_color = PURPLE
        elif tower_type == "missile":
            self.name = "Missile"
            self.color = ORANGE
            self.base_range = 140
            self.base_damage = 40
            self.base_fire_rate = 90
            self.cost = 125
            self.projectile_color = ORANGE
        elif tower_type == "tesla":
            self.name = "Tesla"
            self.color = (0, 200, 255)  # Electric blue
            self.base_range = 130
            self.base_damage = 30
            self.base_fire_rate = 50
            self.cost = 200
            self.projectile_color = (100, 200, 255)
        elif tower_type == "plasma":
            self.name = "Plasma"
            self.color = (0, 200, 0)  # Dark green
            self.base_range = 160
            self.base_damage = 150
            self.base_fire_rate = 150
            self.cost = 350
            self.projectile_color = (100, 255, 100)
        elif tower_type == "ion":
            self.name = "Ion Beam"
            self.color = (0, 255, 200)  # Teal
            self.base_range = 180
            self.base_damage = 60
            self.base_fire_rate = 20  # Fast continuous beam
            self.cost = 500
            self.projectile_color = (100, 255, 200)
        elif tower_type == "quantum":
            self.name = "Quantum"
            self.color = (255, 215, 0)  # Gold
            self.base_range = 150
            self.base_damage = 80
            self.base_fire_rate = 100
            self.cost = 750
            self.projectile_color = (255, 235, 100)

        self.update_stats()
        self.cooldown = 0
        self.size = 22
        self.animation_frame = 0  # For idle animations
        self.shoot_flash = 0  # For muzzle flash effect

    def update_stats(self):
        """Apply level multipliers to base stats."""
        self.range = self.base_range * (1 + (self.level - 1) * 0.25)
        self.damage = self.base_damage * (1 + (self.level - 1) * 0.5)
        self.fire_rate = max(10, self.base_fire_rate - (self.level - 1) * 10)

    def get_upgrade_cost(self):
        """Calculate upgrade cost for the next level."""
        if self.level >= 3:
            return None  # Max level
        return int(self.cost * 0.6 * self.level)

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
        """Shoot a projectile at the target if cooldown allows."""
        if self.cooldown <= 0:
            self.cooldown = self.fire_rate
            self.shoot_flash = 10  # Flash for 10 frames
            # Calculate angle to target
            dx = target.x - self.x
            dy = target.y - self.y
            self.target_angle = math.atan2(dy, dx)
            return Projectile(self.x, self.y, target, self.damage, self.projectile_color, tower_level=self.level, tower_type=self.type)
        return None

    def update(self):
        """Update tower animation and cooldown states."""
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.shoot_flash > 0:
            self.shoot_flash -= 1
        self.animation_frame = (self.animation_frame + 1) % 60  # Cycle every second at 60 FPS

    def draw_barrel_lines(self, screen, start_x, start_y, end_x, end_y, color, base_width=4):
        """Draw multiple parallel lines for barrel based on tower level."""
        if self.level == 1:
            # Single line
            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), base_width)
        elif self.level == 2:
            # Double parallel lines
            angle = self.target_angle
            offset = 2  # Distance between lines
            perp_x = -math.sin(angle) * offset
            perp_y = math.cos(angle) * offset

            pygame.draw.line(screen, color,
                           (start_x + perp_x, start_y + perp_y),
                           (end_x + perp_x, end_y + perp_y), base_width)
            pygame.draw.line(screen, color,
                           (start_x - perp_x, start_y - perp_y),
                           (end_x - perp_x, end_y - perp_y), base_width)
        else:  # level == 3
            # Triple parallel lines
            angle = self.target_angle
            offset = 3  # Distance between lines
            perp_x = -math.sin(angle) * offset
            perp_y = math.cos(angle) * offset

            # Center line
            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), base_width)
            # Top line
            pygame.draw.line(screen, color,
                           (start_x + perp_x, start_y + perp_y),
                           (end_x + perp_x, end_y + perp_y), base_width)
            # Bottom line
            pygame.draw.line(screen, color,
                           (start_x - perp_x, start_y - perp_y),
                           (end_x - perp_x, end_y - perp_y), base_width)

    def draw(self, screen):
        """Draw the tower and its range indicator."""
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

        # Draw mech based on type
        if self.type == "basic":
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

        elif self.type == "freeze":
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

        elif self.type == "sniper":
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

        elif self.type == "missile":
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

        elif self.type == "tesla":
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
            for i in range(num_satellites):
                angle = (i * 2 * math.pi / num_satellites) + self.animation_frame * 0.05
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

        elif self.type == "plasma":
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

        elif self.type == "ion":
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

        elif self.type == "quantum":
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
