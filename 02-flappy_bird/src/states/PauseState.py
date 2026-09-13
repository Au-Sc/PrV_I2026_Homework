"""
ISPPV1 I2026

Author: A.A.R.S

This file contains the definition of the class PauseState.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings


class PauseState(BaseState):
    def enter(self, **params: dict) -> None:
        self.world = params["world"]
        self.bird = params["bird"]
        self.score = params["score"]
        self.movement_input_fnc = params["movement_input_fnc"]
        self.play_update_fnc = params["play_update_fnc"]
        self.hard_mode = params["hard_mode"]

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )

        render_text(
            surface,
            f"PAUSED",
            settings.FONTS["huge"],
            settings.VIRTUAL_WIDTH/2 - settings.HUGE_TEXT_SIZE * 2,
            settings.VIRTUAL_HEIGHT/2 - settings.HUGE_TEXT_SIZE / 2,
            settings.COLOR_WHITE,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "confirm" and input_data.pressed:
            self.state_machine.change(
                "playing",
                world=self.world,
                bird=self.bird,
                score=self.score,
                movement_input_fnc=self.movement_input_fnc,
                play_update_fnc=self.play_update_fnc,
                hard_mode=self.hard_mode,
            )
            settings.SOUNDS["score"].play()
