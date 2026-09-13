"""
ISPPV1 I2026

Author: A.A.R.S

This file contains the specialization of PowerUp to turn the paddle sticky so it can catch the balls.
"""

from typing import TypeVar

import settings
from src.powerups.PowerUp import PowerUp


class MagneticBeam(PowerUp):
    """
    Power-up to attract balls horizontally to the center of the paddle.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 6)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.change_powerup = "magnetic_beam"

        self.active = False
