"""
ISPPV1 I2026

Author: A.A.R.S

This file contains a class that defines the usual processes that happen in PlayState, for updating, input handling and rendering.
"""

import pygame

from typing import TypeVar

from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import random
import settings
import src.powerups

class NoPowerPlayState(BaseState):
    def enter(self, **params: dict):
        self.context = params["context"]
        self.context.change_powerup = None

    def update(self, dt: float) -> None:
        self.paddle_update(dt)
        
        for ball in self.context.balls:
            self.ball_update(dt, ball)
            self.ball_world_collisions(ball)
            self.ball_paddle_collision(ball)
            if not self.ball_brick_collisions(ball):
                continue
            self.check_earn_life()
            self.check_paddle_growth()

        self.balls_cleanup()
        self.laser_update(dt)
        self.brickset_update(dt)
        self.check_defeat()
        self.check_victory()
        self.powerups_update_and_cleanup(dt)    

    def render(self, surface: pygame.Surface) -> None:
        self.render_hearts(surface)
        self.render_text(surface)
        self.render_bricks(surface)
        self.render_paddle(surface)
        self.render_balls(surface)
        self.render_laser(surface)
        self.render_powerups(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "move_left":
            if input_data.pressed:
                self.context.paddle.vx = -settings.PADDLE_SPEED
            elif input_data.released and self.context.paddle.vx < 0:
                self.context.paddle.vx = 0
        elif input_id == "move_right":
            if input_data.pressed:
                self.context.paddle.vx = settings.PADDLE_SPEED
            elif input_data.released and self.context.paddle.vx > 0:
                self.context.paddle.vx = 0
        elif input_id == "pause" and input_data.pressed:
            self.context.state_machine.change(
                "pause",
                level=self.context.level,
                score=self.context.score,
                lives=self.context.lives,
                paddle=self.context.paddle,
                balls=self.context.balls,
                brickset=self.context.brickset,
                points_to_next_live=self.context.points_to_next_live,
                live_factor=self.context.live_factor,
                powerups=self.context.powerups,
                play_state_machine=self.context.play_state_machine,
                laser_pair=self.context.laser_pair
            )


    # Game logic methods


    def paddle_update(self, dt: float) -> None:
        self.context.paddle.update(dt)
    
    def ball_update(self, dt: float, ball: TypeVar("Ball")) -> None:
        ball.update(dt)

    def ball_world_collisions(self, ball: TypeVar("Ball")) -> None:
        ball.solve_world_boundaries()
    
    def ball_paddle_collision(self, ball: TypeVar("Ball")) -> None:
        # Check collision with the paddle
        if ball.collides(self.context.paddle):
            settings.SOUNDS["paddle_hit"].stop()
            settings.SOUNDS["paddle_hit"].play()
            ball.rebound(self.context.paddle)
            ball.push(self.context.paddle)

    def ball_brick_collisions(self, ball: TypeVar("Ball")) -> bool:
        # Check collision with brickset
        if not ball.collides(self.context.brickset):
            return False

        brick = self.context.brickset.get_colliding_brick(ball.get_collision_rect())

        if brick is None:
            return False

        brick.hit()
        self.context.score += brick.score()
        ball.rebound(brick)

        self.roll_powerup_gen(brick.get_collision_rect())

        return True

    def roll_powerup_gen(self, r: pygame.Rect) -> None:
        # Chance to generate a power up
        rand = random.random()
        if rand < 0.15:
            powerup_name = "TwoMoreBall"
            if rand < 0.112:
                powerup_name = "StickyPaddle"
            if rand < 0.075:
                powerup_name = "MagneticBeam"
            if rand < 0.037:
                powerup_name = "LaserGun"

            self.context.powerups.append(
                self.context.powerups_abstract_factory.get_factory(powerup_name).create(
                    r.centerx - 8, r.centery - 8
                )
            )

    def laser_update(self, dt: float) -> None:
        for l in self.context.laser_pair:
            if not l.active:
                continue
            
            l.update(dt)
            
            if not l.collides(self.context.brickset):
                continue

            brick = self.context.brickset.get_colliding_brick(l.get_collision_rect())

            if brick is None:
                continue

            brick.hit()
            self.context.score += brick.score()
            l.deactivate()

            self.roll_powerup_gen(brick.get_collision_rect())

            return True

    def check_earn_life(self) -> None:
        # Check earn life
        if self.context.score >= self.context.points_to_next_live:
            settings.SOUNDS["life"].play()
            self.context.lives = min(3, self.context.lives + 1)
            self.context.live_factor += 0.5
            self.context.points_to_next_live += settings.LIVE_POINTS_BASE * self.context.live_factor

    def check_paddle_growth(self) -> None:
        # Check growing up of the paddle
        if self.context.score >= self.context.points_to_next_grow_up:
            settings.SOUNDS["grow_up"].play()
            self.context.points_to_next_grow_up += (
                settings.PADDLE_GROW_UP_POINTS * (self.context.paddle.size + 1) * self.context.level
            )
            self.context.paddle.inc_size()

    def balls_cleanup(self) -> None:
        # Removing all balls that are not in play
        self.context.balls = [ball for ball in self.context.balls if ball.active]

    def brickset_update(self, dt: float) -> None:
        self.context.brickset.update(dt)

    def check_defeat(self) -> None:
        if not self.context.balls:
            self.context.lives -= 1
            if self.context.lives == 0:
                self.context.state_machine.change("game_over", score=self.context.score)
            else:
                self.context.paddle.dec_size()
                self.context.state_machine.change(
                    "serve",
                    level=self.context.level,
                    score=self.context.score,
                    lives=self.context.lives,
                    paddle=self.context.paddle,
                    brickset=self.context.brickset,
                    points_to_next_live=self.context.points_to_next_live,
                    live_factor=self.context.live_factor,
                )

    def check_victory(self) -> None:
        # Check victory
        if self.context.brickset.size == 1 and next(
            (True for _, b in self.context.brickset.bricks.items() if b.broken), False
        ):
            self.context.paddle.vx = 0
            self.context.state_machine.change(
                "victory",
                lives=self.context.lives,
                level=self.context.level,
                score=self.context.score,
                paddle=self.context.paddle,
                balls=self.context.balls,
                points_to_next_live=self.context.points_to_next_live,
                live_factor=self.context.live_factor,
            )

    def powerups_update_and_cleanup(self, dt: float) -> None:
        # Update powerups
        for powerup in self.context.powerups:
            powerup.update(dt)

            if powerup.collides(self.context.paddle):
                powerup.take(self.context)
        
        self.context.powerups = [p for p in self.context.powerups if p.active]

        if not self.context.change_powerup == None:
            self.context.play_state_machine.change(self.context.change_powerup, context=self.context)

    # Game rendering methods


    def render_hearts(self, surface: pygame.Surface) -> None:
        heart_x = settings.VIRTUAL_WIDTH - 120

        i = 0
        # Draw filled hearts
        while i < self.context.lives:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][0]
            )
            heart_x += 11
            i += 1

        # Draw empty hearts
        while i < 3:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][1]
            )
            heart_x += 11
            i += 1

    def render_text(self, surface: pygame.Surface) -> None:
        render_text(
            surface,
            f"Score: {self.context.score}",
            settings.FONTS["tiny"],
            settings.VIRTUAL_WIDTH - 80,
            5,
            (255, 255, 255),
        )

    def render_bricks(self, surface: pygame.Surface) -> None:
        self.context.brickset.render(surface)

    def render_paddle(self, surface: pygame.Surface) -> None:
        self.context.paddle.render(surface)

    def render_balls(self, surface: pygame.Surface) -> None:
        for ball in self.context.balls:
            ball.render(surface)

    def render_laser(self, surface: pygame.Surface) -> None:
        for laser in self.context.laser_pair:
            if laser.active:
                laser.render(surface)

    def render_powerups(self, surface: pygame.Surface) -> None:
        for powerup in self.context.powerups:
            powerup.render(surface)
