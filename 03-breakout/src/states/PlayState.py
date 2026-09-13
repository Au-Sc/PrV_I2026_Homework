"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class to define the Play state.
"""

import random

import pygame

from gale.factory import AbstractFactory
from gale.state import BaseState, StateMachine
from gale.input_handler import InputData

import settings
import src.powerups
from src.Laser import Laser

from src import powerupstates

class PlayState(BaseState):
    def enter(self, **params: dict):
        self.level = params["level"]
        self.score = params["score"]
        self.lives = params["lives"]
        self.paddle = params["paddle"]
        self.balls = params["balls"]
        self.brickset = params["brickset"]
        self.live_factor = params["live_factor"]
        self.points_to_next_live = params["points_to_next_live"]
        self.points_to_next_grow_up = (
            self.score
            + settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
        )
        self.powerups = params.get("powerups", [])

        if not params.get("resume", False):
            self.balls[0].vx = random.randint(-80, 80)
            self.balls[0].vy = random.randint(-170, -100)
            settings.SOUNDS["paddle_hit"].play()

        self.powerups_abstract_factory = AbstractFactory("src.powerups")

        self.play_state_machine = params.get("play_state_machine")

        if self.play_state_machine == None:
            self.play_state_machine = StateMachine(
                {
                    "no_power" : powerupstates.NoPowerPlayState,
                    "sticky_paddle" : powerupstates.StickyPlayState,
                    "magnetic_beam" : powerupstates.MagneticPlayState,
                    "laser_gun" : powerupstates.LaserGunPlayState,
                }
            )
            self.play_state_machine.change("no_power",context=self)

        self.laser_pair = params.get("laser_pair")

        if self.laser_pair == None:
            self.laser_pair = (Laser(0,-12), Laser(0,-12))

    def update(self, dt: float) -> None:
        self.play_state_machine.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.play_state_machine.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.play_state_machine.on_input(input_id, input_data)
