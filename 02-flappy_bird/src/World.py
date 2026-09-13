"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class World: the scrolling
background/ground, and the log pairs the bird must fly through.
"""

import random
from typing import List, Optional

import pygame

from gale.factory import Factory

import settings
from src.LogPair import LogPair, ClosingLogPair
from src.GhostOrb import GhostOrb
from typing import Protocol


class World:
    def __init__(self, generate_logs: bool = False) -> None:
        self.generate_logs: bool = generate_logs
        self.background_x: float = 0.0
        self.ground_x: float = 0.0
        self.logs: List[LogPair] = []
        self.world_update_fnc : WorldUpdateProtocol = WorldUpdateNormal()
        self.ghost_orb : Optional["GhostOrb"] = None

    def reset(self, generate_logs: bool) -> None:
        self.generate_logs = generate_logs

    def collides(self, rect: pygame.Rect) -> bool:
        if rect.bottom >= settings.VIRTUAL_HEIGHT:
            return True

        return any(log_pair.collides(rect) for log_pair in self.logs)

    def update_scored(self, rect: pygame.Rect) -> bool:
        return any(log_pair.update_scored(rect) for log_pair in self.logs)

    def update(self, dt: float) -> None:
        self.world_update_fnc(dt, self)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["background"], (round(self.background_x), 0))

        for log_pair in self.logs:
            log_pair.render(surface)

        surface.blit(
            settings.TEXTURES["ground"],
            (round(self.ground_x), settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT),
        )

        if not self.ghost_orb == None:
            self.ghost_orb.render(surface)

    def set_difficulty_strategies(self, hard_mode: bool) -> None:
        if hard_mode:
            self.world_update_fnc = WorldUpdateHard()
        else:
            self.world_update_fnc = WorldUpdateNormal()

class WorldUpdateProtocol(Protocol):
    def __call__(self, dt: float, context: World) -> None:
        pass

class WorldUpdateNormal:
    def __init__(self):        
        self.logs_spawn_timer: float = 0.0
        self.last_log_y: float = settings.MIN_LOG_Y + random.randint(0, 80) + 20
        self.log_pair_factory: Factory = Factory(LogPair)

    def __call__(self, dt: float, context: World) -> None:
        if context.generate_logs:
            self.object_generation(dt, context)

        context.background_x += -settings.BACK_SCROLL_SPEED * dt

        if context.background_x <= -settings.BACKGROUND_LOOPING_POINT:
            context.background_x = 0

        context.ground_x += -settings.MAIN_SCROLL_SPEED * dt

        if context.ground_x <= -settings.VIRTUAL_WIDTH:
            context.ground_x = 0

        for log_pair in context.logs:
            log_pair.update(dt)

        context.logs = [log_pair for log_pair in context.logs if not log_pair.is_out_of_game()]

    def object_generation(self, dt: float, context: World) -> None:
        self.logs_spawn_timer += dt

        if self.logs_spawn_timer >= settings.MIN_TIME_TO_SPAWN_LOGS:
            self.logs_spawn_timer = 0.0
            y = max(
                settings.MIN_LOG_Y,
                min(
                    self.last_log_y + random.randint(-20, 20),
                    settings.MAX_LOG_Y - settings.NORMAL_LOGS_GAP,
                ),
            )
            self.last_log_y = y
            context.logs.append(self.log_pair_factory.create(settings.VIRTUAL_WIDTH, y, {"gap" : settings.NORMAL_LOGS_GAP}))

class WorldUpdateHard(WorldUpdateNormal):
    def __init__(self):
        super().__init__()
        self.target_spawn_time = settings.MIN_TIME_TO_SPAWN_LOGS
        self.closing_log_pair_factory: Factory = Factory(ClosingLogPair)
        self.ghost_orb_factory: Factory = Factory(GhostOrb)

    def __call__(self, dt: float, context: World) -> None:
        super().__call__(dt, context)
        if not context.ghost_orb == None:
            context.ghost_orb.update(dt)
            if (
                context.ghost_orb.x <= -context.ghost_orb.width 
                or not context.ghost_orb.active
            ):
                context.ghost_orb = None

    def object_generation(self, dt: float, context: World) -> None:
        self.logs_spawn_timer += dt

        if self.logs_spawn_timer >= self.target_spawn_time:
            self.logs_spawn_timer = 0.0
            xrate = self.target_spawn_time/settings.MIN_TIME_TO_SPAWN_LOGS
            log_gap = random.randint(settings.MIN_LOGS_GAP, settings.MAX_LOGS_GAP)
            log_factory = self.log_pair_factory

            if random.random() <= 0.3:
                log_gap = settings.MAX_LOGS_GAP * 1.5
                log_factory = self.closing_log_pair_factory

            y = max(
                settings.MIN_LOG_Y,
                min(
                    self.last_log_y + random.randint(-20, 20)*xrate*xrate,
                    settings.MAX_LOG_Y - log_gap,
                ),
            )
            self.last_log_y = y
            context.logs.append(log_factory.create(settings.VIRTUAL_WIDTH, y, {"gap" : log_gap}))

            self.target_spawn_time = (
                settings.MIN_TIME_TO_SPAWN_LOGS 
                + (settings.MAX_TIME_TO_SPAWN_LOGS - settings.MIN_TIME_TO_SPAWN_LOGS)*random.random()
            )

            if context.ghost_orb == None and random.random() <= 0.2:
                orb_y = self.last_log_y + settings.LOG_HEIGHT + log_gap/2 - settings.GHOST_ORB_HEIGHT/2
                if self.last_log_y + settings.LOG_HEIGHT + log_gap/2 >= settings.VIRTUAL_HEIGHT/2:
                    orb_y = max(44, orb_y - settings.VIRTUAL_HEIGHT/4)
                else:
                    orb_y = min(settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT - 44, orb_y + settings.VIRTUAL_HEIGHT/4)

                context.ghost_orb = self.ghost_orb_factory.create(
                    settings.VIRTUAL_WIDTH + settings.GHOST_ORB_WIDTH/2 + self.target_spawn_time * settings.MAIN_SCROLL_SPEED/2 ,
                    orb_y
                    )
