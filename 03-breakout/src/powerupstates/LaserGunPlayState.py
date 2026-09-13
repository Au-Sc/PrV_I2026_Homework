"""
ISPPV1 I2026

Author: A.A.R.S

This file contains the state that manages the game logic of the play state during the laser gun powerup's duration
"""

import pygame

from typing import TypeVar, override

from gale.input_handler import InputData

import settings

from src.powerupstates.PowerPlayStateBase import PowerPlayStateBase

class LaserGunPlayState(PowerPlayStateBase):
    @override
    def enter(self, **params: dict):
        super().enter("laser_gun", 20, 9, (250, 100, 100), **params)

    @override
    def render(self, surface: pygame.Surface) -> None:
        super().render(surface)
        surface.blit(
            settings.TEXTURES["spritesheet"],
            (self.context.paddle.x, self.context.paddle.y - 4),
            settings.FRAMES["lasergun"]
        )
        surface.blit(
            settings.TEXTURES["spritesheet"],
            (self.context.paddle.x + self.context.paddle.width - 16, self.context.paddle.y - 4),
            settings.FRAMES["lasergun"]
        )

    @override
    def on_input(self, input_id: str, input_data: InputData) -> None:
        super().on_input(input_id, input_data)

        if (
            input_id == "enter"
            and input_data.pressed
            and all(not laser.active for laser in self.context.laser_pair)
        ) :            
            self.shoot_lasers()

    def shoot_lasers(self) -> None:
        self.context.laser_pair[0].activate(
            self.context.paddle.x + 4,
            self.context.paddle.y
        )
        self.context.laser_pair[1].activate(
            self.context.paddle.x + self.context.paddle.width - 12, 
            self.context.paddle.y
        )
