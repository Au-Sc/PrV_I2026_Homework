"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class TitleScreenState.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.World import World


class TitleScreenState(BaseState):
    def enter(self) -> None:
        self.world = World()
        self.option = 0

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        render_text(
            surface,
            "Flappy Bird",
            settings.FONTS["flappy"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 4,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
        render_text(
            surface,
            "Press Enter to start",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            2 * settings.VIRTUAL_HEIGHT / 4,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
        render_text(
            surface,
            "* Easy Mode" if self.option == 0 else "Easy Mode",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            3 * settings.VIRTUAL_HEIGHT / 4 - 10,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
        render_text(
            surface,
            "* Hard Mode" if self.option == 1 else "Hard Mode",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            3 * settings.VIRTUAL_HEIGHT / 4 + 10,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "confirm" and input_data.pressed:
            self.state_machine.change("count_down", hard_mode = self.option==1)
        if input_id == "move_up" and input_data.pressed:
            self.option = (self.option - 1) % 2
        if input_id == "move_down" and input_data.pressed:
            self.option = (self.option + 1) % 2
