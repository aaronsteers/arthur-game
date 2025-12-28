"""Tower classes for Arthur's Tower Defense game."""

from .base import Tower
from .laser_tower import LaserTower
from .freeze_tower import FreezeTower
from .sniper_tower import SniperTower
from .missile_tower import MissileTower
from .tesla_tower import TeslaTower
from .plasma_tower import PlasmaTower
from .ion_tower import IonTower
from .quantum_tower import QuantumTower

# Tower type mapping for easy instantiation
TOWER_CLASSES = {
    "basic": LaserTower,
    "freeze": FreezeTower,
    "sniper": SniperTower,
    "missile": MissileTower,
    "tesla": TeslaTower,
    "plasma": PlasmaTower,
    "ion": IonTower,
    "quantum": QuantumTower,
}


def create_tower(tower_type, x, y):
    """Factory function to create a tower of the specified type."""
    tower_class = TOWER_CLASSES.get(tower_type)
    if tower_class:
        return tower_class(x, y)
    raise ValueError(f"Unknown tower type: {tower_type}")


__all__ = [
    "Tower",
    "LaserTower",
    "FreezeTower",
    "SniperTower",
    "MissileTower",
    "TeslaTower",
    "PlasmaTower",
    "IonTower",
    "QuantumTower",
    "TOWER_CLASSES",
    "create_tower",
]
