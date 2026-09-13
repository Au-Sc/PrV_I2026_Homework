"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class PlayingState.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.Bird import Bird
from src.World import World
from typing import Protocol


class PlayingState(BaseState):
    def enter(self, **params: dict) -> None:
        self.hard_mode : bool = params.get("hard_mode", False)
        self.movement_input_fnc : MovementInputProtocol
        self.play_update_fnc : PlayUpdateProtocol

        if (
            params.get("world")
            and params.get("movement_input_fnc")
            and params.get("play_update_fnc")
        ):
            self.world = params.get("world")
            self.movement_input_fnc = params.get("movement_input_fnc")
            self.play_update_fnc = params.get("play_update_fnc")
        else:
            self.world =World()
            self.world.reset(True)
            self.set_difficulty_strategies(self.hard_mode)
            self.world.set_difficulty_strategies(self.hard_mode)

        self.bird = params.get("bird")
        if self.bird is None:
            self.bird = Bird(
                settings.VIRTUAL_WIDTH / 2 - settings.BIRD_WIDTH / 2,
                settings.VIRTUAL_HEIGHT / 2 - settings.BIRD_HEIGHT / 2,
                settings.BIRD_WIDTH,
                settings.BIRD_HEIGHT,
            )
        self.score = params.get("score", 0)

    def update(self, dt: float) -> None:
        self.play_update_fnc(dt, self)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.bird.render(surface)
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.movement_input_fnc(input_id, input_data, self.bird)

        if input_id == "confirm" and input_data.pressed:
            self.state_machine.change(
                "pause",
                world=self.world,
                bird=self.bird,
                score=self.score,
                movement_input_fnc=self.movement_input_fnc,
                play_update_fnc=self.play_update_fnc,
                hard_mode=self.hard_mode,
            )
            settings.SOUNDS["score"].play()

    def set_difficulty_strategies(self, hard_mode: bool) -> None:
        if hard_mode:
            self.movement_input_fnc = MovementInputHard()
            self.play_update_fnc = PlayUpdateHard()
        else:
            self.movement_input_fnc = MovementInputNormal()
            self.play_update_fnc = PlayUpdateNormal()

class MovementInputProtocol(Protocol):
    def __call__(self, input_id: str, input_data: InputData, bird: Bird) -> None:
        pass

class MovementInputNormal:
    def __call__(self, input_id: str, input_data: InputData, bird: Bird) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.jump()

class MovementInputHard:
    def __call__(self, input_id: str, input_data: InputData, bird: Bird) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.jump()

        if input_id == "move_left":
            if input_data.pressed:
                bird.vx = -settings.BIRD_MOVEMENT_SPEED
            elif input_data.released and bird.vx < 0:
                bird.vx = 0
        if input_id == "move_right":
            if input_data.pressed:
                bird.vx = settings.BIRD_MOVEMENT_SPEED
            elif input_data.released and bird.vx > 0:
                bird.vx = 0

class PlayUpdateProtocol(Protocol):
    def __call__(self, dt: float, context: PlayingState) -> None:
        pass

class PlayUpdateNormal:
    def __call__(self, dt: float, context: PlayingState) -> None:
        context.bird.update(dt)
        context.bird.y = max(0, context.bird.y)
    
        context.world.update(dt)

        if context.world.collides(context.bird.get_rect()):
            settings.SOUNDS["explosion"].play()
            settings.SOUNDS["hurt"].play()
            context.state_machine.change("count_down", hard_mode=context.hard_mode)
            return

        if context.world.update_scored(context.bird.get_rect()):
            context.score += 1
            settings.SOUNDS["score"].play()

class PlayUpdateHard:
    def __init__(self):
        self.powerup_timer : float = 0
        self.blinking_timer : float = 0

    def __call__(self, dt: float, context: PlayingState) -> None:
        context.bird.update(dt)
        context.bird.y = max(0, min(context.bird.y, settings.VIRTUAL_HEIGHT - context.bird.height))
        context.bird.x = max(0, min(context.bird.x, settings.VIRTUAL_WIDTH - context.bird.width))

        context.world.update(dt)

        if not context.world.ghost_orb == None:
            if context.world.ghost_orb.collides(context.bird.get_rect()):
                context.world.ghost_orb.active = False
                context.bird.ghost_form = True
                self.powerup_timer = settings.POWERUP_DURATION
                pygame.mixer.music.load(settings.TRACKS["wavy"])
                pygame.mixer.music.play(loops=-1)
                
        if self.powerup_timer > 0:        
            self.powerup_timer -= dt
            if self.powerup_timer <= 3:
                self.blinking_timer -= dt
                if self.blinking_timer <= 0:
                    self.blinking_timer = 0.5
                    context.bird.ghost_form = not context.bird.ghost_form
                    
            if self.powerup_timer <= 0:
                context.bird.ghost_form = False
                pygame.mixer.music.load(settings.TRACKS["normal"])
                pygame.mixer.music.play(loops=-1)
                
        elif context.world.collides(context.bird.get_rect()):
            settings.SOUNDS["explosion"].play()
            settings.SOUNDS["hurt"].play()
            context.state_machine.change("count_down",hard_mode=context.hard_mode)
            return

        if context.world.update_scored(context.bird.get_rect()):
            context.score += 1
            settings.SOUNDS["score"].play()
