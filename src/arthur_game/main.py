"""Main entry point for Arthur's Tower Defense Game."""

import asyncio
import argparse
import pygame
from arthur_game.game import Game


def estimate_money_by_wave(wave: int) -> int:
    """
    Estimate cumulative money earned by a given wave, assuming 90% kill rate.

    Args:
        wave: The wave number to calculate up to

    Returns:
        Estimated total money (starting money + earnings from all previous waves)
    """
    if wave <= 1:
        return 200  # Starting money

    total_money = 200  # Starting money

    # Simulate earnings for each wave from 1 to wave-1
    for w in range(1, wave):
        if w == 50:
            # Wave 50: 1 king (500) + 10 elite minions (avg ~35 each)
            enemies_count = 11
            avg_reward = (500 + 10 * 35) / 11  # ~77
        else:
            # Reduced by 35%: (5 + wave * 2) * 0.65 = 3 + wave * 1.3
            enemies_count = max(3, int(3 + w * 1.3))

            # Average reward based on wave composition
            if w >= 10:
                # Mix includes UFOs (25), bosses (30), shields (15), scouts (8), tanks (18), normal (6)
                avg_reward = 12  # Weighted average
            elif w >= 7:
                # Mix includes bosses, shields, scouts, tanks, normal
                avg_reward = 11
            elif w >= 5:
                # Mix includes shields, scouts, tanks, normal
                avg_reward = 10
            elif w >= 3:
                # Mix includes tanks and normal
                avg_reward = 9
            else:
                # Mostly normal
                avg_reward = 6

        # 90% kill rate (10% escape)
        wave_earnings = int(enemies_count * avg_reward * 0.9)
        total_money += wave_earnings

    return total_money


async def async_main(starting_wave: int = 1, starting_money: int = 200):
    """Run the game asynchronously."""
    pygame.init()
    game = Game(starting_wave=starting_wave, starting_money=starting_money)
    await game.run()


def main():
    """Entry point for the game (wraps async function)."""
    parser = argparse.ArgumentParser(description="Arthur's Tower Defense Game")
    parser.add_argument(
        "--wave",
        type=int,
        default=1,
        help="Starting wave number (default: 1, use 50 to test Alien King boss)",
    )
    parser.add_argument(
        "--money",
        type=int,
        default=None,
        help="Starting money amount (default: auto-calculated based on wave with 90%% kill rate)",
    )

    args = parser.parse_args()

    # Validate inputs
    if args.wave < 1:
        print("Error: Wave must be at least 1")
        return

    # Auto-calculate money if not provided and wave > 1
    if args.money is None:
        starting_money = estimate_money_by_wave(args.wave)
        if args.wave > 1:
            print(f"Auto-calculated starting money: ${starting_money} (based on wave {args.wave} with 90% kill rate)")
    else:
        starting_money = args.money
        if starting_money < 0:
            print("Error: Money cannot be negative")
            return

    asyncio.run(async_main(starting_wave=args.wave, starting_money=starting_money))


if __name__ == "__main__":
    main()
