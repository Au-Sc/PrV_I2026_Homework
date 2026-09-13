"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class LogPair: a top log
(rendered flipped upside down) and a bottom log, LOGS_GAP pixels
apart, that scroll left together and score once the bird passes them.
"""

import pygame

import settings
from typing import Optional


class LogPair:
    def __init__(self, x: float, y: float, gap: int) -> None:
        self.x: float = x
        self.y: float = y
        self.scored: bool = False
        self.gap = gap

    def get_top_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), settings.LOG_WIDTH, settings.LOG_HEIGHT)

    def get_bottom_rect(self) -> pygame.Rect:
        return pygame.Rect(
            round(self.x),
            round(self.y + self.gap + settings.LOG_HEIGHT),
            settings.LOG_WIDTH,
            settings.LOG_HEIGHT,
        )

    def collides(self, rect: pygame.Rect) -> bool:
        return self.get_top_rect().colliderect(rect) or self.get_bottom_rect().colliderect(rect)

    def update(self, dt: float) -> None:
        self.x += -settings.MAIN_SCROLL_SPEED * dt

    def is_out_of_game(self) -> bool:
        return self.x < -settings.LOG_WIDTH

    def update_scored(self, rect: pygame.Rect) -> bool:
        if self.scored:
            return False

        if rect.left > self.x + settings.LOG_WIDTH:
            self.scored = True
            return True

        return False

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["log_inverted"], self.get_top_rect())
        surface.blit(settings.TEXTURES["log"], self.get_bottom_rect())

class ClosingLogPair(LogPair):
    def __init__(self, x: float, y: float, gap : int) -> None:
        super().__init__(x, y, gap)
        self.closing_timer = 0.0
        self.original_gap = gap
        self.thumped = False

    def update(self, dt: float) -> None:
        super().update(dt)
        self.closing_timer += dt
        if self.closing_timer * 2 >= settings.CLOSING_LOGS_PERIOD and not self.thumped:
            settings.SOUNDS["thump"].stop()
            settings.SOUNDS["thump"].play()
            self.thumped = True

        if self.closing_timer >= settings.CLOSING_LOGS_PERIOD:
            self.closing_timer = self.closing_timer - settings.CLOSING_LOGS_PERIOD
            self.thumped = False

        self.gap = self.original_gap * abs(0.5 - self.closing_timer/settings.CLOSING_LOGS_PERIOD)
