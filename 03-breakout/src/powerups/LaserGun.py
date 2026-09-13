"""
ISPPV1 I2026

Author: A.A.R.S

This file contains the specialization of PowerUp to give laser guns to the paddle.
"""

from typing import TypeVar

import settings
from src.powerups.PowerUp import PowerUp


class LaserGun(PowerUp):

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 9)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.change_powerup = "laser_gun"

        self.active = False
