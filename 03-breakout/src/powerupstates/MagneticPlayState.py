"""
ISPPV1 I2026

Author: A.A.R.S

This file contains the state that manages the game logic of the play state during the Magnetic paddle powerup's duration
"""

import pygame

from typing import TypeVar, override

from gale.input_handler import InputData

import random
import settings

from src.powerupstates.PowerPlayStateBase import PowerPlayStateBase

class MagneticPlayState(PowerPlayStateBase):

    min_accel = 5
    max_accel = 20
    cap_value = 10
    effect_copies = 5
    effect_timer = 0
    effect_time_period = 4

    @override
    def enter(self, **params: dict):
        super().enter("magnetic_beam", 20, 6, (250, 250, 100), **params)
    
    @override
    def update(self, dt: float) -> None:        
        super().update(dt)
        self.effect_timer = (self.effect_timer + dt) % self.effect_time_period

    @override
    def render(self, surface: pygame.Surface) -> None:
        for i in range(self.effect_copies):   
            beam = pygame.Surface((2,settings.VIRTUAL_HEIGHT),pygame.SRCALPHA)

            rate = (self.effect_timer / self.effect_time_period + i / self.effect_copies) % 1

            beam.fill( (self.color[0],self.color[1],self.color[2], 35*(1 - rate)) )

            paddle_x_rate = (self.context.paddle.x + self.context.paddle.width/2) / settings.VIRTUAL_WIDTH

            surface.blit(beam, (settings.VIRTUAL_WIDTH * paddle_x_rate * rate, 0))
            surface.blit(beam, (settings.VIRTUAL_WIDTH - settings.VIRTUAL_WIDTH * (1 - paddle_x_rate) * rate, 0))

        super().render(surface)

    @override
    def ball_update(self, dt: float, ball: TypeVar("Ball")) -> None:
        dx = self.context.paddle.x + self.context.paddle.width / 2 - (ball.x + ball.width / 2) 
       
        intensity = min(2 * abs(dx) / settings.VIRTUAL_WIDTH, 1)

        accel = self.min_accel + (self.max_accel - self.min_accel) * intensity * intensity
        accel = -accel if dx < 0 else accel

        ball.vx += 0 if ball.vx/accel > self.cap_value else accel

        ball.update(dt)
