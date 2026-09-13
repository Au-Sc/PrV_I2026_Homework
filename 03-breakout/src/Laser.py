"""
ISPPV1 I2026

Author: A.A.R.S

This file contains the class Laser.
"""


from typing import Any, Tuple, Optional

import pygame

import settings

class Laser:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.width = 8
        self.height = 12

        self.vy = -120

        self.texture = settings.TEXTURES["spritesheet"]
        self.frame = settings.FRAMES["laser"]
        self.active = False

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides(self, another: Any) -> bool:
        return self.get_collision_rect().colliderect(another.get_collision_rect())

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        if self.y < -self.height :
            self.deactivate()

    def deactivate(self) -> None:
        self.active = False

    def activate(self, x: int, y: int) -> None:
        self.x = x
        self.y = y 
        self.active = True

    def render(self, surface):
        surface.blit(self.texture, (self.x, self.y), self.frame)
