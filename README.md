# Arthur's Tower Defense Game

A sci-fi tower defense game built with Pygame Community Edition, featuring 8 unique tower types with stunning visual effects!

## Features

- **16:9 Widescreen Display** (1280x720)
- **8 Unique Tower Types** with distinct abilities and visual effects
- **3 Upgrade Levels** per tower with visual indicators (multiple barrels, satellites, beams)
- **Variable Game Speed** (1x, 2x, 3x)
- **Auto-Advance Waves**
- **Range Indicators** when placing towers
- **Fullscreen Support**

## Tower Types

### Basic Towers
- **Laser Tower** ($50): Fast shooting laser with multi-barrel upgrades
- **Freeze Tower** ($75): Slows enemies with icy projectiles
- **Sniper Tower** ($100): Long-range precision with multi-barrel sniper rifle
- **Missile Tower** ($125): Area damage explosive missiles

### Advanced Towers
- **Tesla Tower** ($200): Chain lightning with orbiting satellites (3/5/7 based on level)
- **Plasma Tower** ($350): Devastating green plasma cannon with massive splash damage
- **Ion Beam** ($500): Continuous teal beam weapon with multi-beam upgrades
- **Quantum Tower** ($750): Golden teleporting laser that pierces through enemies

## Controls

- **Left Click**: Select and place towers, interact with UI
- **Right Click**: Select tower for upgrade
- **Speed Buttons**: Control game speed (1x, 2x, 3x)
- **Auto Checkbox**: Auto-advance to next wave
- **Restart Button**: Reset the game (with confirmation)
- **Fullscreen Button**: Toggle fullscreen mode (top-right corner)

## Installation & Running

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Quick Start

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Run the game:
```bash
uv run arthur-game
```

That's it! uv will automatically create a virtual environment and install dependencies.

### Development

Run the game in development mode:
```bash
uv run python -m arthur_game.main
```

Install the package locally:
```bash
uv pip install -e .
```

### Debug/Testing Mode

Test specific waves with auto-calculated appropriate money:
```bash
uv run arthur-game --wave 10    # Auto-calculates money for wave 10 (~$1,389)
uv run arthur-game --wave 50    # Test Alien King boss with ~$29,021
```

Or specify exact money amount:
```bash
uv run arthur-game --wave 10 --money 5000
```

The auto-calculation assumes a 90% enemy kill rate through previous waves.

## Project Structure

```
arthur-game/
├── src/
│   └── arthur_game/
│       ├── __init__.py       # Package initialization
│       ├── main.py           # Entry point
│       ├── constants.py      # Colors, paths, screen settings
│       ├── enemy.py          # Enemy class
│       ├── projectile.py     # Projectile class
│       ├── game.py           # Main game logic
│       └── towers/           # Tower classes (OOP design)
│           ├── __init__.py   # Tower factory
│           ├── base.py       # Base Tower class
│           ├── laser_tower.py
│           ├── freeze_tower.py
│           ├── sniper_tower.py
│           ├── missile_tower.py
│           ├── tesla_tower.py
│           ├── plasma_tower.py
│           ├── ion_tower.py
│           └── quantum_tower.py
├── pyproject.toml            # Project configuration
└── README.md
```

## Building with Pygbag (Web Version)

To build for web deployment:
```bash
uv run pygbag src/arthur_game/
```

Then open your browser to `http://localhost:8000`

## License

MIT
