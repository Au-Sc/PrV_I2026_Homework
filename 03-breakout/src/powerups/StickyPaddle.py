"""
ISPPV1 I2026

Author: A.A.R.S

This file contains the specialization of PowerUp to turn the paddle sticky so it can catch the balls.
"""

from typing import TypeVar

import settings
from src.powerups.PowerUp import PowerUp


class StickyPaddle(PowerUp):
    """
    Power-up to turn the paddle sticky.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 7)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.change_powerup = "sticky_paddle"

        self.active = False
