"""
Game class for Arthur's Tower Defense.

Manages the main game loop, state, rendering, and event handling.
"""

import asyncio
import pygame
import math
import random

from .constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    WHITE,
    BLACK,
    SPACE_BG,
    RED,
    BLUE,
    CYAN,
    YELLOW,
    PURPLE,
    ORANGE,
    GRAY,
    LIGHT_GRAY,
    NEON_GREEN,
    STEEL_BLUE,
    PATH,
)
from .enemy import Enemy
from .towers import create_tower
from .projectile import Projectile


class Game:
    """
    Main game class that manages the tower defense game state, rendering, and event handling.

    Attributes:
        screen: Pygame display surface
        clock: Pygame clock for FPS control
        fullscreen: Whether the game is in fullscreen mode
        money: Current player money
        lives: Remaining player lives
        wave: Current wave number
        score: Current game score
        enemies: List of active enemies
        towers: List of placed towers
        projectiles: List of active projectiles
        selected_tower_type: Currently selected tower type for placement
        selected_tower: Currently selected tower for upgrades
        spawn_timer: Timer for enemy spawning
        spawn_interval: Frames between enemy spawns
        enemies_to_spawn: Number of enemies left to spawn in current wave
        wave_in_progress: Whether a wave is currently active
        game_speed: Game speed multiplier (1x, 2x, or 3x)
        auto_advance: Whether to automatically start next wave
        show_restart_confirmation: Whether to show restart confirmation dialog
    """

    def __init__(self, starting_wave: int = 1, starting_money: int = 200):
        """
        Initialize the game.

        Args:
            starting_wave: Initial wave number (default: 1)
            starting_money: Initial money amount (default: 200)
        """
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Arthur's Tower Defense")
        self.clock = pygame.time.Clock()
        self.fullscreen = False

        self.money = starting_money
        self.lives = 20
        self.wave = starting_wave
        self.score = 0

        # Store initial values for reset
        self.initial_money = starting_money
        self.initial_wave = starting_wave

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
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    def reset_game(self):
        """Reset the game to initial state (respects starting wave/money from CLI)."""
        self.money = self.initial_money
        self.lives = 20
        self.wave = self.initial_wave
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
        """Start spawning a new wave of enemies."""
        if not self.wave_in_progress and len(self.enemies) == 0:
            self.wave_in_progress = True
            # Wave 50: Special boss wave with 1 king + minions
            if self.wave == 50:
                self.enemies_to_spawn = 11  # 1 king + 10 minions
                self.alien_king_spawned = False  # Track if king has been spawned
            else:
                # Reduced by 35%: (5 + wave * 2) * 0.65 = 3 + wave * 1.3
                self.enemies_to_spawn = max(3, int(3 + self.wave * 1.3))
            self.spawn_timer = 0

    def spawn_enemy(self):
        """
        Create a new enemy for the current wave.

        Returns different enemy types based on wave number.
        """
        # Speed multiplier increases every 3 waves
        speed_mult = 1 + (self.wave // 3) * 0.1

        # WAVE 50: ALIEN KING BOSS - Epic final boss with minions
        if self.wave == 50:
            # First spawn: The Alien King (only once!)
            if not hasattr(self, 'alien_king_spawned') or not self.alien_king_spawned:
                self.alien_king_spawned = True
                # Massive alien king with crown - 5x size, extremely tough, immune to freeze and knockback
                boss = Enemy(20000, 0.5 * speed_mult, 500, (150, 0, 150), "alien_king")
                boss.immune_to_knockback = True
                boss.immune_to_freeze = True
                return boss
            else:
                # Elite minions: Mix of tough enemies to support the king
                roll = random.random()
                if roll < 0.4:
                    # Elite battleships
                    return Enemy(800, 0.8 * speed_mult, 40, PURPLE, "boss")
                elif roll < 0.7:
                    # Elite UFOs
                    return Enemy(400, 1.8 * speed_mult, 35, (180, 180, 200), "ufo")
                else:
                    # Elite tanks
                    return Enemy(600, 1.0 * speed_mult, 30, STEEL_BLUE, "tank")

        # Different enemy types based on wave
        if self.wave >= 10 and random.random() < 0.2:
            # UFO - Flying saucer, stronger than scout
            return Enemy(120 + self.wave * 15, 1.8 * speed_mult, 25, (180, 180, 200), "ufo")
        elif self.wave >= 7 and random.random() < 0.15:
            # Boss battleship - huge health, slow, high reward
            return Enemy(400 + self.wave * 50, 0.8 * speed_mult, 30, PURPLE, "boss")
        elif self.wave >= 5 and random.random() < 0.25:
            # Shield jellyfish - protected
            return Enemy(80 + self.wave * 15, 1.3 * speed_mult, 15, (100, 150, 255), "normal", shield=True)
        elif self.wave >= 5 and random.random() < 0.3:
            # Scout dart ship - fast and weak
            return Enemy(30 + self.wave * 5, 2.5 * speed_mult, 8, ORANGE, "scout")
        elif self.wave >= 3 and random.random() < 0.2:
            # Tank beetle - slow but tough
            return Enemy(100 + self.wave * 20, 1 * speed_mult, 18, STEEL_BLUE, "tank")
        else:
            # Standard blob alien
            return Enemy(50 + self.wave * 10, 1.5 * speed_mult, 6, RED, "normal")

    def handle_click(self, pos, right_click=False):
        """
        Handle mouse clicks for tower placement, selection, and UI interactions.

        Args:
            pos: Tuple of (x, y) mouse position
            right_click: Whether this is a right-click (default: False)
        """
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
            tower = create_tower(self.selected_tower_type, x, y)

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
        """Handle tower upgrade when upgrade button is clicked."""
        if self.selected_tower:
            cost = self.selected_tower.get_upgrade_cost()
            if cost and self.money >= cost:
                if self.selected_tower.upgrade():
                    self.money -= cost

    def update(self):
        """
        Update game state: spawn enemies, move entities, handle collisions, and update towers.

        This includes:
        - Spawning enemies in waves
        - Moving enemies along the path
        - Updating towers and shooting
        - Moving and checking projectile hits
        - Applying special effects based on tower types
        """
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
                        # Push enemy back on the path (unless immune to knockback)
                        if not projectile.target.immune_to_knockback and projectile.target.path_index > 1:
                            projectile.target.path_index = max(0, projectile.target.path_index - 2)
                            projectile.target.x = PATH[projectile.target.path_index][0]
                            projectile.target.y = PATH[projectile.target.path_index][1]
                        # Level 3: Area teleport
                        if projectile.tower_level == 3:
                            for enemy in self.enemies:
                                if enemy != projectile.target:
                                    dist = math.sqrt((enemy.x - projectile.target.x)**2 +
                                                   (enemy.y - projectile.target.y)**2)
                                    if dist < 80 and not enemy.immune_to_knockback and enemy.path_index > 1:
                                        enemy.path_index = max(0, enemy.path_index - 1)
                                        enemy.x = PATH[enemy.path_index][0]
                                        enemy.y = PATH[enemy.path_index][1]

                    if killed:
                        self.money += projectile.target.reward
                        self.score += projectile.target.reward
                        self.enemies.remove(projectile.target)

                self.projectiles.remove(projectile)

    def draw(self):
        """
        Render all game elements to the screen.

        Includes:
        - Background and path
        - Towers, enemies, and projectiles
        - UI elements (buttons, stats, panels)
        - Upgrade interface and range indicators
        - Game over and confirmation dialogs
        """
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
                temp_tower = create_tower(self.selected_tower_type, mouse_pos[0], mouse_pos[1])
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
        """
        Draw a tower selection button.

        Args:
            x: X position of button
            y: Y position of button
            width: Button width in pixels
            height: Button height in pixels
            color: RGB color tuple for button
            text: Button label text
            cost_text: Cost display text (e.g., "$50")
            selected: Whether the button is currently selected
            cost: Tower cost in money
        """
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
        """
        Main async game loop.

        Handles:
        - Event processing (clicks, keyboard, window)
        - Game state updates
        - Rendering
        - Frame rate control
        """
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
