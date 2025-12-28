"""Enemy class for the tower defense game."""

import pygame
import math
from .constants import (
    PATH, RED, NEON_GREEN, CYAN, WHITE
)


class Enemy:
    """Represents an enemy robot that follows the path."""

    def __init__(self, health, speed, reward, color=RED, enemy_type="normal", shield=False):
        self.max_health = health
        self.health = health
        self.speed = speed
        self.reward = reward
        self.color = color
        self.enemy_type = enemy_type
        self.shield = shield  # Shield enemies take 50% less damage
        self.path_index = 0
        self.x = PATH[0][0]
        self.y = PATH[0][1]

        # Size based on type
        if enemy_type == "alien_king":
            self.radius = 60  # 5x larger than normal
        elif enemy_type == "boss":
            self.radius = 20
        elif enemy_type == "ufo":
            self.radius = 15
        elif enemy_type == "tank":
            self.radius = 16
        else:
            self.radius = 12

        self.slow_timer = 0
        self.animation_frame = 0  # For animations

        # Boss immunities (set in game.py for Alien King)
        self.immune_to_freeze = False
        self.immune_to_knockback = False

    def move(self):
        """Move enemy along the path. Returns True if reached the end."""
        self.animation_frame += 1

        if self.path_index >= len(PATH) - 1:
            return True  # Reached end

        # Apply slow effect
        current_speed = self.speed
        if self.slow_timer > 0:
            current_speed *= 0.5
            self.slow_timer -= 1

        target_x, target_y = PATH[self.path_index + 1]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < current_speed:
            self.path_index += 1
            if self.path_index >= len(PATH) - 1:
                return True
        else:
            self.x += (dx / distance) * current_speed
            self.y += (dy / distance) * current_speed

        return False

    def take_damage(self, damage):
        """Apply damage to enemy. Returns True if enemy dies."""
        # Shield enemies take reduced damage
        if self.shield:
            damage *= 0.5
        self.health -= damage
        return self.health <= 0

    def slow(self, duration):
        """Apply slow effect for given duration."""
        # Check immunity (bosses like Alien King are immune)
        if self.immune_to_freeze:
            return
        self.slow_timer = max(self.slow_timer, duration)

    def draw(self, screen):
        """Draw the enemy on screen with sci-fi alien designs."""
        # Animation helpers
        bob = math.sin(self.animation_frame * 0.1) * 2
        pulse = abs(math.sin(self.animation_frame * 0.05))

        # Draw shield effect first (behind enemy)
        if self.shield:
            shield_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            shield_alpha = int(60 + pulse * 40)
            pygame.draw.circle(shield_surface, (100, 200, 255, shield_alpha),
                             (self.radius * 1.5, self.radius * 1.5), int(self.radius * 1.3))
            screen.blit(shield_surface, (int(self.x - self.radius * 1.5), int(self.y - self.radius * 1.5)))

        # ALIEN KING: Massive boss with crown and tentacles
        if self.enemy_type == "alien_king":
            size = self.radius
            y = self.y + bob * 0.4

            # Massive pulsating body with dark aura
            body_size = int(size * (0.95 + pulse * 0.08))

            # Dark ominous aura
            aura_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            for i in range(5):
                aura_alpha = int(20 - i * 3 + pulse * 15)
                aura_radius = int(size * (1.2 + i * 0.15))
                pygame.draw.circle(aura_surface, (100, 0, 100, aura_alpha),
                                 (int(size * 1.5), int(size * 1.5)), aura_radius)
            screen.blit(aura_surface, (int(self.x - size * 1.5), int(y - size * 1.5)))

            # Main body with darker, more menacing colors
            body_color = (int(self.color[0] * 0.6), int(self.color[1] * 0.3), int(self.color[2] * 0.3))
            pygame.draw.circle(screen, body_color, (int(self.x), int(y)), body_size)

            # Multiple pulsing layers for depth
            for i in range(3):
                layer_alpha = int(100 + pulse * 50)
                layer_surf = pygame.Surface((body_size * 2 + 10, body_size * 2 + 10), pygame.SRCALPHA)
                layer_radius = body_size - i * 8
                pygame.draw.circle(layer_surf, (*self.color, layer_alpha),
                                 (body_size + 5, body_size + 5), layer_radius, 3)
                screen.blit(layer_surf, (int(self.x - body_size - 5), int(y - body_size - 5)))

            # Giant eye stalks (4 of them, more menacing)
            for i in range(4):
                angle = (i / 4) * math.pi * 2
                stalk_sway = math.sin(self.animation_frame * 0.1 + i) * 4
                stalk_len = size * 0.4
                stalk_x = self.x + math.cos(angle) * (size * 0.7)
                stalk_y = y - size * 0.5 + math.sin(angle) * (size * 0.3)

                # Stalk
                end_x = stalk_x + stalk_sway
                end_y = stalk_y - stalk_len
                pygame.draw.line(screen, body_color, (stalk_x, stalk_y), (end_x, end_y), 5)

                # Eye (glowing red)
                eye_glow = int(150 + pulse * 105)
                pygame.draw.circle(screen, (eye_glow, 0, 0), (int(end_x), int(end_y)), 8)
                pygame.draw.circle(screen, (255, 255, 0), (int(end_x), int(end_y)), 5)
                pygame.draw.circle(screen, (0, 0, 0), (int(end_x), int(end_y)), 2)

            # Massive golden crown with jewels
            crown_y = y - size - 15
            crown_color = (255, 215, 0)
            gem_color = (200, 0, 200)

            # Crown base (thicker)
            pygame.draw.rect(screen, crown_color, (int(self.x - size * 0.5), int(crown_y), size, 8), border_radius=2)
            pygame.draw.rect(screen, (200, 150, 0), (int(self.x - size * 0.5), int(crown_y), size, 8), 2, border_radius=2)

            # Crown points (5 large points)
            for i in range(5):
                point_x = self.x - size * 0.4 + i * (size * 0.2)
                points = [
                    (int(point_x - 6), int(crown_y)),
                    (int(point_x), int(crown_y - 20)),
                    (int(point_x + 6), int(crown_y))
                ]
                pygame.draw.polygon(screen, crown_color, points)
                pygame.draw.polygon(screen, (200, 150, 0), points, 2)

                # Jewel on each point
                jewel_pulse = int(150 + pulse * 105)
                pygame.draw.circle(screen, (jewel_pulse, 0, jewel_pulse),
                                 (int(point_x), int(crown_y - 15)), 4)

            # Many thick tentacles (12 tentacles for massive boss)
            for i in range(12):
                angle = (i / 12) * math.pi * 2
                wave = math.sin(self.animation_frame * 0.08 + i) * 6
                wave2 = math.cos(self.animation_frame * 0.1 + i * 0.5) * 5

                start_x = self.x + math.cos(angle) * (size * 0.8)
                start_y = y + math.sin(angle) * (size * 0.8)

                # Multi-segment tentacles
                for seg in range(4):
                    seg_len = size * 0.4
                    end_x = start_x + math.cos(angle) * seg_len + wave * (seg + 1)
                    end_y = start_y + seg_len + wave2 * (seg + 1)

                    thickness = 6 - seg
                    pygame.draw.line(screen, body_color, (start_x, start_y), (end_x, end_y), thickness)
                    start_x, start_y = end_x, end_y

            # Energy rings around the king
            for i in range(3):
                ring_angle = (self.animation_frame * 0.02 + i * 0.33) * math.pi * 2
                ring_radius = size * (0.9 + i * 0.15)
                ring_alpha = int(80 + pulse * 40)

                ring_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                # Draw rotating energy particles
                for j in range(8):
                    particle_angle = ring_angle + (j / 8) * math.pi * 2
                    px = size * 1.5 + math.cos(particle_angle) * ring_radius
                    py = size * 1.5 + math.sin(particle_angle) * ring_radius
                    pygame.draw.circle(ring_surf, (255, 215, 0, ring_alpha), (int(px), int(py)), 3)
                screen.blit(ring_surf, (int(self.x - size * 1.5), int(y - size * 1.5)))

        # UFO: Flying Saucer
        elif self.enemy_type == "ufo":
            size = self.radius
            y = self.y + bob * 1.2  # More pronounced floating

            # Rotation for spinning effect
            rotation = self.animation_frame * 0.05

            # Top dome (metallic)
            dome_points = []
            for i in range(10):
                angle = (i / 10) * math.pi
                radius = size * 0.7 * (0.95 + pulse * 0.05)
                px = self.x + math.cos(angle + math.pi) * radius
                py = y - size * 0.3 + math.sin(angle + math.pi) * radius * 0.5
                dome_points.append((int(px), int(py)))
            pygame.draw.polygon(screen, (150, 150, 180), dome_points)
            pygame.draw.polygon(screen, (100, 100, 150), dome_points, 2)

            # Cockpit window (large glowing dome window)
            cockpit_glow = int(100 + pulse * 155)
            pygame.draw.circle(screen, (cockpit_glow, cockpit_glow, 255),
                             (int(self.x), int(y - size * 0.3)), int(size * 0.3))
            pygame.draw.circle(screen, (200, 200, 255), (int(self.x), int(y - size * 0.3)), int(size * 0.3), 2)

            # Main saucer disk (wide ellipse)
            disk_points = []
            for i in range(16):
                angle = (i / 16) * math.pi * 2 + rotation
                radius_x = size * 1.3
                radius_y = size * 0.4
                px = self.x + math.cos(angle) * radius_x
                py = y + math.sin(angle) * radius_y
                disk_points.append((int(px), int(py)))
            pygame.draw.polygon(screen, self.color, disk_points)
            pygame.draw.polygon(screen, (self.color[0]//2, self.color[1]//2, self.color[2]//2), disk_points, 2)

            # Spinning lights around the rim
            for i in range(8):
                light_angle = rotation + (i / 8) * math.pi * 2
                light_x = self.x + math.cos(light_angle) * (size * 1.2)
                light_y = y + math.sin(light_angle) * (size * 0.35)

                # Alternating colors
                if i % 2 == 0:
                    light_color = (255, int(100 + pulse * 155), 100)
                else:
                    light_color = (100, int(100 + pulse * 155), 255)

                pygame.draw.circle(screen, light_color, (int(light_x), int(light_y)), 3)

                # Light beam glow
                if pulse > 0.7:
                    beam_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
                    beam_alpha = int((pulse - 0.7) * 300)
                    pygame.draw.circle(beam_surf, (*light_color, beam_alpha), (4, 4), 4)
                    screen.blit(beam_surf, (int(light_x - 4), int(light_y - 4)))

            # Tractor beam effect (underneath)
            beam_alpha = int(30 + pulse * 30)
            beam_surf = pygame.Surface((size * 2, size * 3), pygame.SRCALPHA)
            # Cone shape
            for i in range(10):
                beam_y = i * (size * 0.3)
                beam_width = int((i + 1) * (size * 0.15))
                pygame.draw.line(beam_surf, (100, 255, 100, beam_alpha),
                               (size, 0), (size - beam_width, beam_y), 2)
                pygame.draw.line(beam_surf, (100, 255, 100, beam_alpha),
                               (size, 0), (size + beam_width, beam_y), 2)
            screen.blit(beam_surf, (int(self.x - size), int(y)))

        # BOSS: Alien Battleship/Cruiser
        elif self.enemy_type == "boss":
            size = self.radius
            y = self.y + bob * 0.5

            # Main hull (wide rectangle)
            hull_w = size * 2.2
            hull_h = size * 1.6
            pygame.draw.rect(screen, self.color,
                           (int(self.x - hull_w/2), int(y - hull_h/2), hull_w, hull_h), border_radius=4)
            pygame.draw.rect(screen, RED,
                           (int(self.x - hull_w/2), int(y - hull_h/2), hull_w, hull_h), 2, border_radius=4)

            # Command bridge (top)
            bridge_w = size * 1.2
            bridge_h = size * 0.8
            pygame.draw.rect(screen, (self.color[0]//2, self.color[1]//2, self.color[2]//2),
                           (int(self.x - bridge_w/2), int(y - hull_h/2 - bridge_h), bridge_w, bridge_h), border_radius=3)

            # Windows/eyes (glowing)
            glow_color = (255, int(100 + pulse * 155), 100)
            pygame.draw.circle(screen, glow_color, (int(self.x - 8), int(y - hull_h/2 - bridge_h/2)), 4)
            pygame.draw.circle(screen, glow_color, (int(self.x + 8), int(y - hull_h/2 - bridge_h/2)), 4)

            # Weapon turrets (sides)
            pygame.draw.circle(screen, (150, 50, 50), (int(self.x - hull_w/2 - 3), int(y)), 4)
            pygame.draw.circle(screen, (150, 50, 50), (int(self.x + hull_w/2 + 3), int(y)), 4)

            # Reactor core (glowing center)
            core_size = int(4 + pulse * 3)
            pygame.draw.circle(screen, (255, 255, 100), (int(self.x), int(y)), core_size)

        # TANK: Armored Beetle Alien
        elif self.enemy_type == "tank":
            size = self.radius - 2
            y = self.y + bob * 0.3

            # Thick armored carapace (segmented)
            for i in range(3):
                segment_y = y - size + i * (size * 0.7)
                segment_w = size * 1.8 - i * 2
                pygame.draw.rect(screen, self.color,
                               (int(self.x - segment_w/2), int(segment_y), segment_w, size * 0.6), border_radius=2)
                pygame.draw.rect(screen, (self.color[0]//2, self.color[1]//2, self.color[2]//2),
                               (int(self.x - segment_w/2), int(segment_y), segment_w, size * 0.6), 2, border_radius=2)

            # Glowing vents (sides)
            vent_pulse = int(100 + pulse * 155)
            pygame.draw.circle(screen, (vent_pulse, vent_pulse, 255), (int(self.x - size), int(y)), 3)
            pygame.draw.circle(screen, (vent_pulse, vent_pulse, 255), (int(self.x + size), int(y)), 3)

            # Mechanical legs (6 legs, 3 per side)
            leg_color = (self.color[0]//3, self.color[1]//3, self.color[2]//3)
            for i in range(3):
                leg_y = y - size/2 + i * (size * 0.6)
                # Left legs
                pygame.draw.line(screen, leg_color, (self.x - size * 0.8, leg_y),
                               (self.x - size * 1.3, leg_y + 5), 2)
                # Right legs
                pygame.draw.line(screen, leg_color, (self.x + size * 0.8, leg_y),
                               (self.x + size * 1.3, leg_y + 5), 2)

        # SCOUT: Dart Ship (fast spacecraft)
        elif self.enemy_type == "scout":
            size = self.radius
            y = self.y + bob

            # Calculate movement direction for tilt
            if self.path_index < len(PATH) - 1:
                target_x, target_y = PATH[self.path_index + 1]
                angle = math.atan2(target_y - self.y, target_x - self.x)
            else:
                angle = 0

            # Ship body (sleek triangle)
            nose = (int(self.x + math.cos(angle) * size), int(y + math.sin(angle) * size))
            left_wing = (int(self.x + math.cos(angle + 2.5) * size), int(y + math.sin(angle + 2.5) * size))
            right_wing = (int(self.x + math.cos(angle - 2.5) * size), int(y + math.sin(angle - 2.5) * size))

            pygame.draw.polygon(screen, self.color, [nose, left_wing, right_wing])
            pygame.draw.polygon(screen, (255, 200, 0), [nose, left_wing, right_wing], 2)

            # Cockpit window (glowing)
            cockpit_x = self.x + math.cos(angle) * (size * 0.4)
            cockpit_y = y + math.sin(angle) * (size * 0.4)
            glow_val = int(150 + pulse * 105)
            pygame.draw.circle(screen, (glow_val, glow_val, 255), (int(cockpit_x), int(cockpit_y)), 3)

            # Engine trails (glowing lines behind)
            trail_start_x = self.x - math.cos(angle) * (size * 0.5)
            trail_start_y = y - math.sin(angle) * (size * 0.5)
            trail_end_x = trail_start_x - math.cos(angle) * (size * 0.8)
            trail_end_y = trail_start_y - math.sin(angle) * (size * 0.8)

            for i in range(2):
                offset_angle = angle + (math.pi/2 if i == 0 else -math.pi/2)
                offset_x = math.cos(offset_angle) * (size * 0.3)
                offset_y = math.sin(offset_angle) * (size * 0.3)
                trail_alpha = int(100 + pulse * 100)
                trail_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.line(trail_surf, (255, 200, 0, trail_alpha),
                               (size + offset_x, size + offset_y),
                               (size + offset_x - math.cos(angle) * size * 0.8,
                                size + offset_y - math.sin(angle) * size * 0.8), 2)
                screen.blit(trail_surf, (int(self.x - size), int(y - size)))

        # NORMAL with CROWN: Alien King
        elif self.enemy_type == "normal" and hasattr(self, 'is_king') and self.is_king:
            size = self.radius
            y = self.y + bob

            # Blob body
            pygame.draw.circle(screen, self.color, (int(self.x), int(y)), size)
            pygame.draw.circle(screen, (self.color[0]//2, self.color[1]//2, self.color[2]//2),
                             (int(self.x), int(y)), size, 2)

            # Eye stalks (animated)
            stalk_sway = math.sin(self.animation_frame * 0.15) * 2
            # Left eye
            pygame.draw.line(screen, self.color, (self.x - 5, y - size),
                           (self.x - 5 + stalk_sway, y - size - 6), 2)
            pygame.draw.circle(screen, NEON_GREEN, (int(self.x - 5 + stalk_sway), int(y - size - 6)), 3)
            pygame.draw.circle(screen, WHITE, (int(self.x - 5 + stalk_sway), int(y - size - 6)), 2)
            # Right eye
            pygame.draw.line(screen, self.color, (self.x + 5, y - size),
                           (self.x + 5 - stalk_sway, y - size - 6), 2)
            pygame.draw.circle(screen, NEON_GREEN, (int(self.x + 5 - stalk_sway), int(y - size - 6)), 3)
            pygame.draw.circle(screen, WHITE, (int(self.x + 5 - stalk_sway), int(y - size - 6)), 2)

            # Crown (golden)
            crown_y = y - size - 8
            crown_color = (255, 215, 0)
            # Crown base
            pygame.draw.rect(screen, crown_color, (int(self.x - 8), int(crown_y), 16, 3))
            # Crown points
            for i in range(3):
                point_x = self.x - 6 + i * 6
                points = [
                    (int(point_x - 2), int(crown_y)),
                    (int(point_x), int(crown_y - 5)),
                    (int(point_x + 2), int(crown_y))
                ]
                pygame.draw.polygon(screen, crown_color, points)

            # Tentacles (wavy)
            for i in range(4):
                angle = (i / 4) * math.pi * 2
                wave = math.sin(self.animation_frame * 0.1 + i) * 3
                start_x = self.x + math.cos(angle) * (size * 0.7)
                start_y = y + math.sin(angle) * (size * 0.7)
                end_x = start_x + math.cos(angle) * (size * 0.8) + wave
                end_y = start_y + math.sin(angle) * (size * 0.8) + size * 0.3
                pygame.draw.line(screen, self.color, (start_x, start_y), (end_x, end_y), 2)

        # NORMAL: Blob Alien (original design enhanced)
        elif self.enemy_type == "normal":
            size = self.radius
            y = self.y + bob

            # Blob body (pulsating)
            body_size = int(size * (0.95 + pulse * 0.05))
            pygame.draw.circle(screen, self.color, (int(self.x), int(y)), body_size)
            pygame.draw.circle(screen, (self.color[0]//2, self.color[1]//2, self.color[2]//2),
                             (int(self.x), int(y)), body_size, 2)

            # Eye stalks (animated)
            stalk_sway = math.sin(self.animation_frame * 0.15) * 2
            # Left eye
            pygame.draw.line(screen, self.color, (self.x - 5, y - size),
                           (self.x - 5 + stalk_sway, y - size - 6), 2)
            pygame.draw.circle(screen, NEON_GREEN, (int(self.x - 5 + stalk_sway), int(y - size - 6)), 3)
            pygame.draw.circle(screen, WHITE, (int(self.x - 5 + stalk_sway), int(y - size - 6)), 2)
            # Right eye
            pygame.draw.line(screen, self.color, (self.x + 5, y - size),
                           (self.x + 5 - stalk_sway, y - size - 6), 2)
            pygame.draw.circle(screen, NEON_GREEN, (int(self.x + 5 - stalk_sway), int(y - size - 6)), 3)
            pygame.draw.circle(screen, WHITE, (int(self.x + 5 - stalk_sway), int(y - size - 6)), 2)

            # Tentacles (wavy, dangling below)
            for i in range(4):
                angle = (i / 4) * math.pi * 2
                wave = math.sin(self.animation_frame * 0.1 + i) * 3
                start_x = self.x + math.cos(angle) * (size * 0.7)
                start_y = y + math.sin(angle) * (size * 0.7)
                end_x = start_x + math.cos(angle) * (size * 0.8) + wave
                end_y = start_y + math.sin(angle) * (size * 0.8) + size * 0.3
                pygame.draw.line(screen, self.color, (start_x, start_y), (end_x, end_y), 2)

            # Bioluminescent glow
            glow_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            glow_alpha = int(30 + pulse * 20)
            pygame.draw.circle(glow_surface, (*NEON_GREEN, glow_alpha),
                             (int(size * 1.5), int(size * 1.5)), size)
            screen.blit(glow_surface, (int(self.x - size * 1.5), int(y - size * 1.5)))

        # SHIELD NORMAL: Jellyfish Alien
        elif self.shield:
            size = self.radius
            y = self.y + bob * 1.5  # More floating motion

            # Dome/bell head
            dome_points = []
            for i in range(8):
                angle = (i / 8) * math.pi
                radius = size * (0.8 + pulse * 0.1)
                px = self.x + math.cos(angle + math.pi) * radius
                py = y - size + math.sin(angle + math.pi) * radius * 0.6
                dome_points.append((int(px), int(py)))
            pygame.draw.polygon(screen, self.color, dome_points)
            pygame.draw.polygon(screen, (100, 200, 255), dome_points, 2)

            # Glowing spots on dome
            for i in range(3):
                angle = (i / 3) * math.pi + math.pi
                spot_x = self.x + math.cos(angle) * (size * 0.5)
                spot_y = y - size * 0.7 + math.sin(angle) * (size * 0.3)
                spot_pulse = int(150 + pulse * 105)
                pygame.draw.circle(screen, (spot_pulse, spot_pulse, 255), (int(spot_x), int(spot_y)), 2)

            # Long flowing tentacles
            for i in range(6):
                angle = (i / 6) * math.pi * 2
                wave = math.sin(self.animation_frame * 0.08 + i) * 4
                wave2 = math.cos(self.animation_frame * 0.12 + i) * 3

                # Start from dome edge
                start_x = self.x + math.cos(angle) * (size * 0.6)
                start_y = y

                # Multiple segments for flowing effect
                for seg in range(3):
                    seg_len = size * 0.5
                    end_x = start_x + math.cos(angle) * seg_len + wave * (seg + 1)
                    end_y = start_y + seg_len + wave2 * (seg + 1)

                    alpha = 255 - seg * 60
                    tentacle_surf = pygame.Surface((abs(int(end_x - start_x)) + 10,
                                                   abs(int(end_y - start_y)) + 10), pygame.SRCALPHA)
                    pygame.draw.line(screen, (*self.color, alpha),
                                   (start_x, start_y), (end_x, end_y), 2)
                    start_x, start_y = end_x, end_y

            # Bioluminescent aura
            aura_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            aura_alpha = int(40 + pulse * 30)
            pygame.draw.circle(aura_surface, (100, 200, 255, aura_alpha),
                             (size * 2, size * 2), int(size * 1.5))
            screen.blit(aura_surface, (int(self.x - size * 2), int(y - size * 2)))

        # Draw health bar
        health_width = int(self.radius * 2)
        health_height = 4
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED,
                        (self.x - health_width//2, self.y - self.radius - 12,
                         health_width, health_height))
        pygame.draw.rect(screen, NEON_GREEN,
                        (self.x - health_width//2, self.y - self.radius - 12,
                         health_width * health_percent, health_height))

        # Draw freeze effect
        if self.slow_timer > 0:
            ice_alpha = int(100 + pulse * 50)
            ice_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(ice_surface, (*CYAN, ice_alpha),
                             (int(self.radius * 1.5), int(self.radius * 1.5)), self.radius + 3, 3)
            screen.blit(ice_surface, (int(self.x - self.radius * 1.5), int(self.y - self.radius * 1.5)))
