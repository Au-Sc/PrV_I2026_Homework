"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class EntityIdleState.
"""

import random
from typing import TypeVar

import pygame

from src.states.entity.BaseEntityState import BaseEntityState


class EntityStaticState(BaseEntityState):
    def enter(self) -> None:
        self.entity.change_animation("idle-static")

    def process_ai(self, room: TypeVar("Room"), dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
