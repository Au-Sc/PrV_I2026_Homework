"""
ISPPV1 I2026

Author: A.A.R.S

This file contains the state that manages the game logic of the play state during the Sticky paddle powerup's duration
"""

import pygame

from typing import TypeVar, override

from gale.input_handler import InputData

import random
import settings

from src.powerupstates.PowerPlayStateBase import PowerPlayStateBase

class StickyPlayState(PowerPlayStateBase):    
    @override
    def enter(self, **params: dict):
        super().enter("sticky_paddle", 15, 7, (100, 230, 50), **params)
        self.stuck_balls = []

    def exit(self):
        self.launch_stuck_balls()

    @override
    def update(self, dt: float) -> None:
        super().update(dt)
        for b in self.stuck_balls:
            b[0].x = self.context.paddle.x + b[1]

    @override
    def on_input(self, input_id: str, input_data: InputData) -> None:
        super().on_input(input_id, input_data)

        if input_id == "enter" and input_data.pressed:
            self.launch_stuck_balls()

    def launch_stuck_balls(self) -> None:
        for b in self.stuck_balls:
            b[0].vx = self.context.paddle.vx + random.randint(-20,20)
            b[0].vy = random.randint(-130,-100)
        self.stuck_balls.clear()

    @override
    def ball_paddle_collision(self, ball: TypeVar("Ball")) -> None:
        # Check collision with the paddle
        if ball.collides(self.context.paddle):
            settings.SOUNDS["paddle_hit"].stop()
            settings.SOUNDS["paddle_hit"].play()
            ball.y = self.context.paddle.y - ball.width            
            ball.vy = 0
            ball.vx = 0
            self.stuck_balls.append(
                (
                ball,
                max(0, min(ball.x - self.context.paddle.x, self.context.paddle.width - ball.width))
                )
            )            
