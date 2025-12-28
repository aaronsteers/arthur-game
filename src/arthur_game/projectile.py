"""Projectile class for tower defense game."""

import pygame
import math
from .constants import YELLOW, BLACK


class Projectile:
    """Represents a projectile fired by a tower."""

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
        """Move projectile toward target. Returns True if hit or target is dead."""
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
        """Draw the projectile on screen."""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 1)
