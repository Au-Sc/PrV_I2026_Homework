"""
ISPPV1 I2026

Author: A.A.R.S

This file contains the base with the common behavior between states that manage the game logic of the play state during a powerup's duration
"""

import pygame

from typing import override

from gale.input_handler import InputData

import settings

from src.powerupstates.NoPowerPlayState import NoPowerPlayState

class PowerPlayStateBase(NoPowerPlayState):    
    @override
    def enter(self, name: str, duration: int, icon_index: int, color: tuple[int,int,int], **params: dict):
        super().enter(**params)
        self.duration = duration
        self.timer = duration
        self.name = name 
        self.icon_index = icon_index
        self.color = color

    @override
    def update(self, dt: float) -> None:
        if self.timer <= 0:
            self.context.play_state_machine.change("no_power", context=self.context)
        self.timer -= dt
    
        super().update(dt)

    @override
    def render(self, surface: pygame.Surface) -> None:
        super().render(surface)
        self.render_powerup_hud(surface)

    def render_powerup_hud(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(
            surface, self.color, (0,settings.VIRTUAL_HEIGHT - 4, settings.VIRTUAL_WIDTH * self.timer / self.duration , 4)
        )
        surface.blit(
            settings.TEXTURES["spritesheet"], (8, settings.VIRTUAL_HEIGHT - 24), settings.FRAMES["powerups"][self.icon_index]
        )
    
    @override
    def powerups_update_and_cleanup(self, dt: float) -> None:
        # Update powerups
        for powerup in self.context.powerups:
            powerup.update(dt)

            if powerup.collides(self.context.paddle):
                powerup.take(self.context)
        
        self.context.powerups = [p for p in self.context.powerups if p.active]

        if self.context.change_powerup == self.name:
            self.timer = self.duration
            self.context.change_powerup = None
        elif not self.context.change_powerup == None:
            self.context.play_state_machine.change(self.context.change_powerup, context=self.context)
