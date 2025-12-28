import asyncio
import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 40
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPACE_BG = (10, 10, 30)  # Dark space background
RED = (220, 50, 50)
BLUE = (50, 150, 255)  # Bright blue for laser
CYAN = (0, 255, 255)  # Cyan for freeze
YELLOW = (255, 255, 0)  # Bright yellow for lasers
PURPLE = (200, 50, 255)  # Purple for sniper
ORANGE = (255, 100, 0)  # Orange for missiles
GRAY = (80, 80, 100)  # Space gray for path
LIGHT_GRAY = (40, 40, 60)  # Dark UI
NEON_GREEN = (0, 255, 100)
STEEL_BLUE = (70, 130, 180)

# Game path (enemies follow this) - scaled for 16:9
PATH = [
    (0, 300),
    (480, 300),
    (480, 520),
    (800, 520),
    (800, 180),
    (1280, 180)
]


class Enemy:
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
        if enemy_type == "boss":
            self.radius = 20
        elif enemy_type == "tank":
            self.radius = 16
        else:
            self.radius = 12

        self.slow_timer = 0

    def move(self):
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
        # Shield enemies take reduced damage
        if self.shield:
            damage *= 0.5
        self.health -= damage
        return self.health <= 0

    def slow(self, duration):
        self.slow_timer = max(self.slow_timer, duration)

    def draw(self, screen):
        # Draw shield effect first (behind robot)
        if self.shield:
            shield_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (100, 200, 255, 80),
                             (self.radius * 1.5, self.radius * 1.5), int(self.radius * 1.3))
            screen.blit(shield_surface, (int(self.x - self.radius * 1.5), int(self.y - self.radius * 1.5)))

        # Draw robot body (sci-fi style)
        if self.enemy_type == "boss":
            # Boss robot - huge, intimidating
            size = self.radius
            # Body
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), size, 3)
            # Arms
            pygame.draw.rect(screen, self.color, (int(self.x - size - 8), int(self.y - 4), 8, 8))
            pygame.draw.rect(screen, self.color, (int(self.x + size), int(self.y - 4), 8, 8))
            # Eyes
            pygame.draw.circle(screen, RED, (int(self.x - 6), int(self.y - 4)), 4)
            pygame.draw.circle(screen, RED, (int(self.x + 6), int(self.y - 4)), 4)
        elif self.enemy_type == "tank":
            # Tank robot - larger, square body
            size = self.radius - 4
            pygame.draw.rect(screen, self.color,
                           (int(self.x) - size, int(self.y) - size, size*2, size*2))
            pygame.draw.rect(screen, NEON_GREEN,
                           (int(self.x) - size, int(self.y) - size, size*2, size*2), 2)
        elif self.enemy_type == "scout":
            # Scout robot - fast, triangular
            points = [
                (int(self.x), int(self.y) - self.radius),
                (int(self.x) - self.radius, int(self.y) + self.radius),
                (int(self.x) + self.radius, int(self.y) + self.radius)
            ]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, NEON_GREEN, points, 2)
        else:
            # Normal robot - circular
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, NEON_GREEN, (int(self.x), int(self.y)), self.radius, 2)
            # Add "eye"
            pygame.draw.circle(screen, NEON_GREEN, (int(self.x), int(self.y)), 4)

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
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.radius + 3, 2)


class Projectile:
    def __init__(self, x, y, target, damage, color=YELLOW, speed=8, tower_level=1, tower_type="basic"):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.color = color
        self.speed = speed
        self.radius = 5
        self.tower_level = tower_level
        self.tower_type = tower_type

    def move(self):
        if self.target.health <= 0:
            return True  # Target dead, remove projectile

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.speed:
            return True  # Hit target

        self.x += (dx / distance) * self.speed
        self.y += (dy / distance) * self.speed
        return False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 1)


class Tower:
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
        # Apply level multipliers
        self.range = self.base_range * (1 + (self.level - 1) * 0.25)
        self.damage = self.base_damage * (1 + (self.level - 1) * 0.5)
        self.fire_rate = max(10, self.base_fire_rate - (self.level - 1) * 10)

    def get_upgrade_cost(self):
        if self.level >= 3:
            return None  # Max level
        return int(self.cost * 0.6 * self.level)

    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.update_stats()
            return True
        return False

    def find_target(self, enemies):
        for enemy in enemies:
            dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if dist <= self.range:
                return enemy
        return None

    def shoot(self, target):
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
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.shoot_flash > 0:
            self.shoot_flash -= 1
        self.animation_frame = (self.animation_frame + 1) % 60  # Cycle every second at 60 FPS

    def draw_barrel_lines(self, screen, start_x, start_y, end_x, end_y, color, base_width=4):
        """Draw multiple parallel lines for barrel based on tower level"""
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
            pygame.draw.circle(screen, RED, (int(self.x), int(y_pos)), 3)

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
            pygame.draw.circle(screen, RED, (int(self.x), int(y_pos)), 4)

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


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Arthur's Tower Defense")
        self.clock = pygame.time.Clock()
        self.fullscreen = False

        self.money = 200
        self.lives = 20
        self.wave = 1
        self.score = 0

        self.enemies = []
        self.towers = []
        self.projectiles = []

        self.selected_tower_type = None
        self.selected_tower = None  # For upgrades
        self.spawn_timer = 0
        self.spawn_interval = 60  # frames between spawns
        self.enemies_to_spawn = 5
        self.wave_in_progress = False

        # Speed and auto-advance controls
        self.game_speed = 1  # 1x, 2x, or 3x
        self.auto_advance = False

        # Confirmation dialog state
        self.show_restart_confirmation = False

        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    def reset_game(self):
        """Reset the game to initial state"""
        self.money = 200
        self.lives = 20
        self.wave = 1
        self.score = 0
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.selected_tower_type = None
        self.selected_tower = None
        self.spawn_timer = 0
        self.enemies_to_spawn = 5
        self.wave_in_progress = False
        self.show_restart_confirmation = False

    def spawn_wave(self):
        if not self.wave_in_progress and len(self.enemies) == 0:
            self.wave_in_progress = True
            self.enemies_to_spawn = 5 + self.wave * 2
            self.spawn_timer = 0

    def spawn_enemy(self):
        # Speed multiplier increases every 3 waves
        speed_mult = 1 + (self.wave // 3) * 0.1

        # Different robot types based on wave
        if self.wave >= 7 and random.random() < 0.15:
            # Boss robot - huge health, slow, high reward
            return Enemy(400 + self.wave * 50, 0.8 * speed_mult, 30, PURPLE, "boss")
        elif self.wave >= 5 and random.random() < 0.25:
            # Shield robot - protected
            return Enemy(80 + self.wave * 15, 1.3 * speed_mult, 15, (100, 150, 255), "normal", shield=True)
        elif self.wave >= 5 and random.random() < 0.3:
            # Scout robot - fast and weak
            return Enemy(30 + self.wave * 5, 2.5 * speed_mult, 8, ORANGE, "scout")
        elif self.wave >= 3 and random.random() < 0.2:
            # Tank robot - slow but tough
            return Enemy(100 + self.wave * 20, 1 * speed_mult, 18, STEEL_BLUE, "tank")
        else:
            # Standard robot
            return Enemy(50 + self.wave * 10, 1.5 * speed_mult, 6, RED, "normal")

    def handle_click(self, pos, right_click=False):
        x, y = pos

        # Right click - select tower for upgrade
        if right_click and y < 620:
            for tower in self.towers:
                dist = math.sqrt((x - tower.x)**2 + (y - tower.y)**2)
                if dist < 30:
                    self.selected_tower = tower
                    return
            self.selected_tower = None
            return

        # Check tower selection buttons (8 towers in 2 rows)
        if y > 625:
            # Row 1
            if 630 <= y < 675:
                if 5 < x < 100 and self.money >= 50:
                    self.selected_tower_type = "basic"
                elif 105 < x < 200 and self.money >= 75:
                    self.selected_tower_type = "freeze"
                elif 205 < x < 300 and self.money >= 100:
                    self.selected_tower_type = "sniper"
                elif 305 < x < 400 and self.money >= 125:
                    self.selected_tower_type = "missile"
            # Row 2
            elif 680 <= y < 725:
                if 5 < x < 100 and self.money >= 200:
                    self.selected_tower_type = "tesla"
                elif 105 < x < 200 and self.money >= 350:
                    self.selected_tower_type = "plasma"
                elif 205 < x < 300 and self.money >= 500:
                    self.selected_tower_type = "ion"
                elif 305 < x < 400 and self.money >= 750:
                    self.selected_tower_type = "quantum"
            self.selected_tower = None
            return

        # Place tower
        if self.selected_tower_type and y < 620:
            tower = Tower(x, y, self.selected_tower_type)

            if self.money >= tower.cost:
                # Check if not placing on path
                too_close = False
                for px, py in PATH:
                    if math.sqrt((x - px)**2 + (y - py)**2) < 50:
                        too_close = True
                        break

                # Check if not overlapping other towers
                for other_tower in self.towers:
                    if math.sqrt((x - other_tower.x)**2 + (y - other_tower.y)**2) < 40:
                        too_close = True
                        break

                if not too_close:
                    self.towers.append(tower)
                    self.money -= tower.cost
                    self.selected_tower_type = None

    def handle_upgrade(self):
        if self.selected_tower:
            cost = self.selected_tower.get_upgrade_cost()
            if cost and self.money >= cost:
                if self.selected_tower.upgrade():
                    self.money -= cost

    def update(self):
        # Auto-advance: automatically start next wave
        if self.auto_advance and not self.wave_in_progress and len(self.enemies) == 0:
            self.spawn_wave()

        # Spawn wave
        if self.wave_in_progress:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval and self.enemies_to_spawn > 0:
                self.enemies.append(self.spawn_enemy())
                self.enemies_to_spawn -= 1
                self.spawn_timer = 0

            if self.enemies_to_spawn == 0 and len(self.enemies) == 0:
                self.wave_in_progress = False
                self.wave += 1
                self.money += 50  # Wave completion bonus

        # Move enemies
        for enemy in self.enemies[:]:
            if enemy.move():
                self.lives -= 1
                self.enemies.remove(enemy)

        # Update towers and shoot
        for tower in self.towers:
            tower.update()
            target = tower.find_target(self.enemies)
            if target:
                projectile = tower.shoot(target)
                if projectile:
                    self.projectiles.append(projectile)

        # Move projectiles and check hits
        for projectile in self.projectiles[:]:
            if projectile.move():
                if projectile.target in self.enemies:
                    killed = projectile.target.take_damage(projectile.damage)

                    # Special effects based on tower type
                    if projectile.color == CYAN:  # Freeze tower
                        projectile.target.slow(90)
                        # Level 3: Area freeze
                        if projectile.tower_level == 3:
                            for enemy in self.enemies:
                                dist = math.sqrt((enemy.x - projectile.target.x)**2 +
                                               (enemy.y - projectile.target.y)**2)
                                if dist < 100:
                                    enemy.slow(60)

                    elif projectile.color == ORANGE:  # Missile tower (area damage)
                        area_radius = 70 if projectile.tower_level < 3 else 100
                        for enemy in self.enemies:
                            dist = math.sqrt((enemy.x - projectile.target.x)**2 +
                                           (enemy.y - projectile.target.y)**2)
                            if dist < area_radius:
                                enemy.take_damage(projectile.damage // 2)

                    elif projectile.color == YELLOW:  # Laser tower
                        # Level 3: Chain lightning
                        if projectile.tower_level == 3 and not killed:
                            for enemy in self.enemies:
                                if enemy != projectile.target:
                                    dist = math.sqrt((enemy.x - projectile.target.x)**2 +
                                                   (enemy.y - projectile.target.y)**2)
                                    if dist < 80:
                                        enemy.take_damage(projectile.damage // 3)
                                        break  # Chain to one enemy

                    elif projectile.color == PURPLE:  # Sniper tower
                        # Level 3: Piercing shot (handled by hitting multiple enemies)
                        if projectile.tower_level == 3:
                            for enemy in self.enemies:
                                if enemy != projectile.target:
                                    # Check if enemy is along the shot path
                                    dist = math.sqrt((enemy.x - projectile.target.x)**2 +
                                                   (enemy.y - projectile.target.y)**2)
                                    if dist < 50:
                                        enemy.take_damage(projectile.damage // 2)

                    elif projectile.tower_type == "tesla":  # Tesla tower - chain lightning
                        # Chain to nearby enemies
                        chain_count = 2 + projectile.tower_level
                        chained = [projectile.target]
                        for _ in range(chain_count):
                            for enemy in self.enemies:
                                if enemy not in chained:
                                    # Check distance from last chained enemy
                                    dist = math.sqrt((enemy.x - chained[-1].x)**2 +
                                                   (enemy.y - chained[-1].y)**2)
                                    if dist < 100:
                                        enemy.take_damage(projectile.damage // 2)
                                        chained.append(enemy)
                                        break

                    elif projectile.tower_type == "plasma":  # Plasma cannon - huge damage + burn
                        # Extra damage over time (burn effect)
                        projectile.target.slow(30)  # "Stunned" by plasma hit

                    elif projectile.tower_type == "ion":  # Ion beam - continuous damage
                        # Already handled by fast fire rate, no special effect needed
                        pass

                    elif projectile.tower_type == "quantum":  # Quantum disruptor - teleport enemies back
                        # Push enemy back on the path
                        if projectile.target.path_index > 1:
                            projectile.target.path_index = max(0, projectile.target.path_index - 2)
                            projectile.target.x = PATH[projectile.target.path_index][0]
                            projectile.target.y = PATH[projectile.target.path_index][1]
                        # Level 3: Area teleport
                        if projectile.tower_level == 3:
                            for enemy in self.enemies:
                                if enemy != projectile.target:
                                    dist = math.sqrt((enemy.x - projectile.target.x)**2 +
                                                   (enemy.y - projectile.target.y)**2)
                                    if dist < 80 and enemy.path_index > 1:
                                        enemy.path_index = max(0, enemy.path_index - 1)
                                        enemy.x = PATH[enemy.path_index][0]
                                        enemy.y = PATH[enemy.path_index][1]

                    if killed:
                        self.money += projectile.target.reward
                        self.score += projectile.target.reward
                        self.enemies.remove(projectile.target)

                self.projectiles.remove(projectile)

    def draw(self):
        self.screen.fill(SPACE_BG)

        # Draw stars in background
        for i in range(80):  # More stars for larger screen
            star_x = (i * 137) % SCREEN_WIDTH
            star_y = (i * 193) % 620  # Adjusted for new height
            star_size = 1 + (i % 3)
            pygame.draw.circle(self.screen, WHITE, (star_x, star_y), star_size)

        # Draw path (metallic corridor)
        for i in range(len(PATH) - 1):
            pygame.draw.line(self.screen, GRAY, PATH[i], PATH[i + 1], 36)
            pygame.draw.line(self.screen, STEEL_BLUE, PATH[i], PATH[i + 1], 30)

        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

        # Draw UI background (adjusted for 720p height)
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, 620, SCREEN_WIDTH, 100))

        # Draw tower selection buttons (8 towers in 2 rows)
        # Row 1 - Basic towers
        button_width = 95
        button_height = 45
        row1_y = 630
        row2_y = 680

        self.draw_button(5, row1_y, button_width, button_height, BLUE, "Laser", "$50", self.selected_tower_type == "basic", 50)
        self.draw_button(105, row1_y, button_width, button_height, CYAN, "Freeze", "$75", self.selected_tower_type == "freeze", 75)
        self.draw_button(205, row1_y, button_width, button_height, PURPLE, "Sniper", "$100", self.selected_tower_type == "sniper", 100)
        self.draw_button(305, row1_y, button_width, button_height, ORANGE, "Missile", "$125", self.selected_tower_type == "missile", 125)

        # Row 2 - Advanced towers with updated colors
        tesla_color = (0, 200, 255)  # Electric blue
        plasma_color = (0, 200, 0)   # Dark green
        ion_color = (0, 255, 200)    # Teal
        quantum_color = (255, 215, 0)  # Gold

        self.draw_button(5, row2_y, button_width, button_height, tesla_color, "Tesla", "$200", self.selected_tower_type == "tesla", 200)
        self.draw_button(105, row2_y, button_width, button_height, plasma_color, "Plasma", "$350", self.selected_tower_type == "plasma", 350)
        self.draw_button(205, row2_y, button_width, button_height, ion_color, "Ion", "$500", self.selected_tower_type == "ion", 500)
        self.draw_button(305, row2_y, button_width, button_height, quantum_color, "Quantum", "$750", self.selected_tower_type == "quantum", 750)

        # Draw stats (compact, on the right side)
        stats_x = 420
        money_text = self.small_font.render(f"${self.money}", True, NEON_GREEN)
        lives_text = self.tiny_font.render(f"Lives: {self.lives}", True, RED if self.lives < 5 else WHITE)
        wave_text = self.tiny_font.render(f"Wave {self.wave}", True, YELLOW)

        self.screen.blit(money_text, (stats_x, 630))
        self.screen.blit(lives_text, (stats_x, 657))
        self.screen.blit(wave_text, (stats_x, 675))

        # Draw fullscreen button (top-right corner)
        fs_button_rect = pygame.Rect(SCREEN_WIDTH - 35, 5, 30, 30)
        pygame.draw.rect(self.screen, LIGHT_GRAY, fs_button_rect)
        pygame.draw.rect(self.screen, WHITE, fs_button_rect, 2)
        fs_icon = "□" if not self.fullscreen else "⊡"
        fs_text = self.small_font.render(fs_icon, True, WHITE)
        self.screen.blit(fs_text, (SCREEN_WIDTH - 28, 8))

        # Draw speed control (right side, between rows)
        speed_x = 510
        speed_y = 638
        speed_label = self.tiny_font.render("Speed:", True, WHITE)
        self.screen.blit(speed_label, (speed_x, speed_y))

        # Speed buttons (1x, 2x, 3x)
        for i, speed in enumerate([1, 2, 3]):
            btn_x = speed_x + 43 + i * 28
            btn_color = NEON_GREEN if self.game_speed == speed else GRAY
            pygame.draw.rect(self.screen, btn_color, (btn_x, speed_y - 2, 25, 18))
            pygame.draw.rect(self.screen, WHITE, (btn_x, speed_y - 2, 25, 18), 1)
            speed_text = self.tiny_font.render(f"{speed}x", True, BLACK)
            self.screen.blit(speed_text, (btn_x + 4, speed_y))

        # Auto-advance checkbox
        auto_x = 685
        auto_y = 638
        checkbox_size = 13
        pygame.draw.rect(self.screen, WHITE, (auto_x, auto_y, checkbox_size, checkbox_size), 2)
        if self.auto_advance:
            pygame.draw.line(self.screen, NEON_GREEN, (auto_x + 2, auto_y + 6), (auto_x + 5, auto_y + 10), 2)
            pygame.draw.line(self.screen, NEON_GREEN, (auto_x + 5, auto_y + 10), (auto_x + 11, auto_y + 2), 2)
        auto_label = self.tiny_font.render("Auto", True, WHITE)
        self.screen.blit(auto_label, (auto_x + 17, auto_y))

        # Draw restart button (below auto-advance)
        restart_x = 660
        restart_y = 680
        restart_button_rect = pygame.Rect(restart_x, restart_y, 80, 30)
        pygame.draw.rect(self.screen, (180, 50, 50), restart_button_rect)
        pygame.draw.rect(self.screen, WHITE, restart_button_rect, 2)
        restart_text = self.tiny_font.render("RESTART", True, WHITE)
        self.screen.blit(restart_text, (restart_x + 12, restart_y + 8))

        # Draw wave button (right side, below row 2)
        if not self.wave_in_progress and len(self.enemies) == 0 and not self.auto_advance:
            button_text = self.tiny_font.render("START WAVE", True, BLACK)
            button_rect = pygame.Rect(510, 695, 120, 22)
            pygame.draw.rect(self.screen, NEON_GREEN, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2)
            self.screen.blit(button_text, (520, 698))

        # Draw upgrade UI if tower selected
        if self.selected_tower:
            tower = self.selected_tower
            # Draw upgrade panel
            panel_x = tower.x + 40
            panel_y = tower.y - 60
            panel_w = 140
            panel_h = 80

            # Keep panel on screen
            if panel_x + panel_w > SCREEN_WIDTH:
                panel_x = tower.x - panel_w - 40
            if panel_y < 0:
                panel_y = 10

            pygame.draw.rect(self.screen, (30, 30, 50), (panel_x, panel_y, panel_w, panel_h))
            pygame.draw.rect(self.screen, YELLOW, (panel_x, panel_y, panel_w, panel_h), 2)

            # Tower info
            info_text = self.tiny_font.render(f"{tower.name} Lv.{tower.level}", True, WHITE)
            self.screen.blit(info_text, (panel_x + 5, panel_y + 5))

            # Stats
            dmg_text = self.tiny_font.render(f"DMG: {int(tower.damage)}", True, WHITE)
            rng_text = self.tiny_font.render(f"RNG: {int(tower.range)}", True, WHITE)
            self.screen.blit(dmg_text, (panel_x + 5, panel_y + 22))
            self.screen.blit(rng_text, (panel_x + 5, panel_y + 37))

            # Upgrade button
            upgrade_cost = tower.get_upgrade_cost()
            if upgrade_cost:
                can_afford_upgrade = self.money >= upgrade_cost
                btn_color = NEON_GREEN if can_afford_upgrade else (60, 60, 60)
                pygame.draw.rect(self.screen, btn_color, (panel_x + 5, panel_y + 54, panel_w - 10, 20))

                # Draw semi-transparent overlay if can't afford
                if not can_afford_upgrade:
                    overlay = pygame.Surface((panel_w - 10, 20), pygame.SRCALPHA)
                    pygame.draw.rect(overlay, (0, 0, 0, 100), (0, 0, panel_w - 10, 20))
                    self.screen.blit(overlay, (panel_x + 5, panel_y + 54))

                text_color = BLACK if can_afford_upgrade else RED
                upgrade_text = self.tiny_font.render(f"UPGRADE ${upgrade_cost}", True, text_color)
                self.screen.blit(upgrade_text, (panel_x + 10, panel_y + 57))
            else:
                max_text = self.tiny_font.render("MAX LEVEL!", True, YELLOW)
                self.screen.blit(max_text, (panel_x + 20, panel_y + 57))

        # Draw range indicator when placing tower
        if self.selected_tower_type:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[1] < 620:  # Only show in play area
                # Get tower stats to show range
                temp_tower = Tower(mouse_pos[0], mouse_pos[1], self.selected_tower_type)
                # Draw range circle (semi-transparent)
                range_surface = pygame.Surface((SCREEN_WIDTH, 620), pygame.SRCALPHA)
                pygame.draw.circle(range_surface, (255, 255, 255, 40), mouse_pos, int(temp_tower.range))
                pygame.draw.circle(range_surface, (255, 255, 255, 80), mouse_pos, int(temp_tower.range), 2)
                self.screen.blit(range_surface, (0, 0))

        # Draw restart confirmation dialog
        if self.show_restart_confirmation:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 180), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(overlay, (0, 0))

            # Draw dialog box
            dialog_w = 400
            dialog_h = 150
            dialog_x = SCREEN_WIDTH // 2 - dialog_w // 2
            dialog_y = SCREEN_HEIGHT // 2 - dialog_h // 2
            pygame.draw.rect(self.screen, (40, 40, 60), (dialog_x, dialog_y, dialog_w, dialog_h))
            pygame.draw.rect(self.screen, YELLOW, (dialog_x, dialog_y, dialog_w, dialog_h), 3)

            # Warning text
            warning_text = self.small_font.render("Restart Game?", True, YELLOW)
            warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, dialog_y + 30))
            self.screen.blit(warning_text, warning_rect)

            message_text = self.tiny_font.render("All progress will be lost!", True, WHITE)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, dialog_y + 60))
            self.screen.blit(message_text, message_rect)

            # Yes button
            yes_btn_x = dialog_x + 50
            yes_btn_y = dialog_y + 95
            yes_btn_w = 120
            yes_btn_h = 40
            pygame.draw.rect(self.screen, (180, 50, 50), (yes_btn_x, yes_btn_y, yes_btn_w, yes_btn_h))
            pygame.draw.rect(self.screen, WHITE, (yes_btn_x, yes_btn_y, yes_btn_w, yes_btn_h), 2)
            yes_text = self.small_font.render("YES", True, WHITE)
            yes_rect = yes_text.get_rect(center=(yes_btn_x + yes_btn_w // 2, yes_btn_y + yes_btn_h // 2))
            self.screen.blit(yes_text, yes_rect)

            # No button
            no_btn_x = dialog_x + 230
            no_btn_y = dialog_y + 95
            no_btn_w = 120
            no_btn_h = 40
            pygame.draw.rect(self.screen, (50, 150, 50), (no_btn_x, no_btn_y, no_btn_w, no_btn_h))
            pygame.draw.rect(self.screen, WHITE, (no_btn_x, no_btn_y, no_btn_w, no_btn_h), 2)
            no_text = self.small_font.render("NO", True, WHITE)
            no_rect = no_text.get_rect(center=(no_btn_x + no_btn_w // 2, no_btn_y + no_btn_h // 2))
            self.screen.blit(no_text, no_rect)

        # Game over
        if self.lives <= 0:
            game_over_text = self.font.render(f"GAME OVER! Score: {self.score}", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(self.screen, WHITE, text_rect.inflate(20, 20))
            self.screen.blit(game_over_text, text_rect)

        pygame.display.flip()

    def draw_button(self, x, y, width, height, color, text, cost_text, selected, cost):
        can_afford = self.money >= cost

        # Dim the color if can't afford
        if not can_afford:
            color = (color[0] // 3, color[1] // 3, color[2] // 3)

        border_color = YELLOW if selected else BLACK
        border_width = 4 if selected else 2

        pygame.draw.rect(self.screen, color, (x, y, width, height))
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), border_width)

        # Draw semi-transparent overlay if can't afford
        if not can_afford:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 128), (0, 0, width, height))
            self.screen.blit(overlay, (x, y))

        text_color = WHITE if can_afford else GRAY
        cost_color = RED if not can_afford else WHITE

        text_surface = self.tiny_font.render(text, True, text_color)
        cost_surface = self.tiny_font.render(cost_text, True, cost_color)

        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2 - 8))
        cost_rect = cost_surface.get_rect(center=(x + width // 2, y + height // 2 + 10))

        self.screen.blit(text_surface, text_rect)
        self.screen.blit(cost_surface, cost_rect)

    async def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    if event.button == 1:  # Left click
                        # Check confirmation dialog buttons (if showing)
                        if self.show_restart_confirmation:
                            dialog_w = 400
                            dialog_h = 150
                            dialog_x = SCREEN_WIDTH // 2 - dialog_w // 2
                            dialog_y = SCREEN_HEIGHT // 2 - dialog_h // 2

                            # Yes button
                            yes_btn_x = dialog_x + 50
                            yes_btn_y = dialog_y + 95
                            if yes_btn_x < pos[0] < yes_btn_x + 120 and yes_btn_y < pos[1] < yes_btn_y + 40:
                                self.reset_game()
                                continue

                            # No button
                            no_btn_x = dialog_x + 230
                            no_btn_y = dialog_y + 95
                            if no_btn_x < pos[0] < no_btn_x + 120 and no_btn_y < pos[1] < no_btn_y + 40:
                                self.show_restart_confirmation = False
                                continue

                            # Click outside dialog closes it
                            if not (dialog_x < pos[0] < dialog_x + dialog_w and
                                    dialog_y < pos[1] < dialog_y + dialog_h):
                                self.show_restart_confirmation = False
                                continue
                            continue

                        # Check fullscreen button
                        if SCREEN_WIDTH - 35 < pos[0] < SCREEN_WIDTH - 5 and 5 < pos[1] < 35:
                            self.toggle_fullscreen()
                            continue

                        # Check restart button
                        if 660 < pos[0] < 740 and 680 < pos[1] < 710:
                            self.show_restart_confirmation = True
                            continue

                        # Check speed buttons
                        for i, speed in enumerate([1, 2, 3]):
                            btn_x = 553 + i * 28
                            if btn_x < pos[0] < btn_x + 25 and 636 < pos[1] < 654:
                                self.game_speed = speed
                                continue

                        # Check auto-advance checkbox
                        if 685 < pos[0] < 698 and 638 < pos[1] < 651:
                            self.auto_advance = not self.auto_advance
                            continue

                        # Check upgrade button click
                        if self.selected_tower:
                            tower = self.selected_tower
                            panel_x = tower.x + 40
                            panel_y = tower.y - 60
                            if panel_x + 140 > SCREEN_WIDTH:
                                panel_x = tower.x - 140 - 40
                            if panel_y < 0:
                                panel_y = 10

                            # Check if clicked upgrade button
                            if (panel_x + 5 < pos[0] < panel_x + 135 and
                                panel_y + 54 < pos[1] < panel_y + 74):
                                self.handle_upgrade()
                                continue

                        # Check start wave button
                        if (510 < pos[0] < 630 and 695 < pos[1] < 717 and
                            not self.wave_in_progress and len(self.enemies) == 0):
                            self.spawn_wave()
                        else:
                            self.handle_click(pos)

                    elif event.button == 3:  # Right click
                        self.handle_click(pos, right_click=True)

            if self.lives > 0:
                # Run update multiple times based on game speed
                for _ in range(self.game_speed):
                    self.update()

            self.draw()
            self.clock.tick(FPS)
            await asyncio.sleep(0)

        pygame.quit()


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
