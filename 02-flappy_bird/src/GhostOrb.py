"""

This file contains the definition of the class GhostOrb.
"""

import pygame

import settings

class GhostOrb:
    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: float = settings.GHOST_ORB_WIDTH
        self.height: float = settings.GHOST_ORB_HEIGHT
        self.active: bool = True

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def collides(self, rect: pygame.Rect) -> bool:
        return self.get_rect().colliderect(rect)

    def update(self, dt: float) -> None:
        self.x += -settings.MAIN_SCROLL_SPEED * dt

    def is_out_of_game(self) -> bool:
        return self.x < -self.width

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["ghost_orb"], self.get_rect())
