
from typing import TypeVar
from gale.factory import Factory
from src.GameObject import GameObject
from src.Projectile import Projectile
from src.definitions.game_objects import GAME_OBJECT_DEFS
from gale.timer import Timer

import pygame

import settings

COOL_DOWN_DURATION = 0.7

class Bow:
    def __init__(self, dungeon: TypeVar("Dungeon")) -> None:
        self.x = 0
        self.y = 0
        self.frame_index = 0
        self.dungeon = dungeon
        self.arrow_factory = Factory(GameObject)
        self.cooling_down = False

    def cooled_down(self) -> None:
        self.cooling_down = False

    def fire(self, x: float, y: float, direction: str) -> None:
        if not self.cooling_down:        
            self.x = x
            self.y = y
            arrow = self.arrow_factory.create(x, y, {"definition" : GAME_OBJECT_DEFS["arrow"]})
            arrow.state = direction        
            self.dungeon.current_room.projectiles.append(
                Projectile(arrow, direction)
            )
            self.cooling_down = True
            Timer.after(COOL_DOWN_DURATION, self.cooled_down)

    def render(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        frame_index = self.states[self.state].get("frame", self.frame_index)
        surface.blit(
            settings.TEXTURES[self.texture_id],
            (self.x + offset_x, self.y + offset_y),
            settings.frame(self.texture_id, frame_index),
        )
