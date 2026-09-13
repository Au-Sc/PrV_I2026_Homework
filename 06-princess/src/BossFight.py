

import random
from typing import Any, Callable, List, Optional, TypeVar

import pygame

import settings
from src.definitions.entity import ENTITY_DEFS
from src.Entity import Entity
from src.states.entity.EntityStaticState import EntityStaticState
from src.Projectile import Projectile
from gale.animation import Animation
import math

_BOSS_DEF = ENTITY_DEFS["boss"]

_BOSS_SPAWN_SPOTS = {
    "left": (
        settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - _BOSS_DEF["height"]
    ),
    "right": (
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - settings.TILE_SIZE - _BOSS_DEF["width"],
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - _BOSS_DEF["height"]//2
    ),
    "top": (
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - _BOSS_DEF["width"]//2,
        settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE
    ),
    "bottom": (
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - _BOSS_DEF["width"]//2,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE - settings.TILE_SIZE - _BOSS_DEF["height"]
    ),
}

_OPOSITE_SIDE = {
    "left": "right",
    "right": "left",
    "top": "bottom",
    "bottom": "top"
}


_RECOVERY_TIME = 7
_ORBIT_INTERVAL = 2
_ORBIT_RADIUS = 20
_FIRING_INTERVAL = 1.5
_QUICK_FIRING_INTERVAL = 0.7
_FIRE_SPEED = 30
_FIRST_HEALTH_TRESHOLD = 6
_SECOND_HEALTH_TRESHOLD = 3

_ORIENTATION_FRAME_INDEXES = {
    "left" : [1,2,3,4],
    "up" : [5,6,7,8],
    "right" : [9,10,11,12],
    "down" : [13,14,15,16],
}

class DarkFire:
    def __init__(self, x: float, y: float, orientation: str):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = 16
        self.height = 16
        self.active = True
        
        self.animation = Animation(
            _ORIENTATION_FRAME_INDEXES[orientation],
            0.1,
            None
            )
        self.animation.texture_id = "dark_fire"

    def update(self, dt: float) -> None:
        if not self.active:
            return

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.animation.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if not self.active:
            return
        
        surface.blit(
            settings.TEXTURES[self.animation.texture_id],
            (self.x, self.y),
            settings.frame("dark_fire", self.animation.get_current_frame())
        )

class BossFight:
    def __init__(self, room: TypeVar("Room")) -> None:
        self.room = room
        enter_side = room.single_door_render or "bottom"

        self.side = _OPOSITE_SIDE[enter_side]

        spot = _BOSS_SPAWN_SPOTS[self.side]
        self.boss = Entity(
            x=spot[0],
            y=spot[1],
            width=_BOSS_DEF["width"],
            height=_BOSS_DEF["height"],
            walk_speed=0,
            health=_BOSS_DEF["health"],
            animation_defs=_BOSS_DEF["animations"],
            states={},
            typename="boss"
        )
        self.boss.state_machine.states = {
                "static": lambda sm, e=self.boss: EntityStaticState(e, sm),
            }
        self.boss.change_state("static")
        self.boss.inmune = True
        room.entities.append(self.boss)

        self.recovery_timer : float = 0

        self.fires = []
        self.orbiting_fires = []
        for _ in range(7):
            f = self.spawn_fire(self.boss.x, self.boss.y, "down", True)
        self.activate_orbiting_fires(False)
        self.orbit_timer : float = 0
        self.firing_timer : float = 0
        self.can_fire = False
        self.firing_interval = _FIRING_INTERVAL
            
    def room_ready(self):
        self.activate_orbiting_fires(True)
        self.orbit_timer = 0
        self.recovery_timer = 0
        self.firing_timer = 0
        self.can_fire = True
        self.phase = 0

    def spawn_fire(self, x: float, y: float, orientation: str, orbit: bool) -> DarkFire:
        fire = DarkFire(x, y, orientation)

        self.fires.append(fire)
        if orbit:
            self.orbiting_fires.append(fire)
        return fire

    def activate_orbiting_fires(self, state: bool):
        for fire in self.orbiting_fires:
            fire.active = state

    def update_orbiting_fires(self, dt: float):
        self.orbit_timer = (self.orbit_timer + dt) % _ORBIT_INTERVAL
        rate = self.orbit_timer/_ORBIT_INTERVAL

        for i in range(len(self.orbiting_fires)):
            angle = 360 * rate
            angle_offset = 360/len(self.orbiting_fires) * (i - 1)
            
            self.orbiting_fires[i-1].x = (
                self.boss.x 
                + self.boss.width/2
                + math.cos(math.radians(angle + angle_offset)) * _ORBIT_RADIUS 
                - self.orbiting_fires[i-1].width/2
            )
            self.orbiting_fires[i-1].y = (
                self.boss.y
                + self.boss.height/2
                + math.sin(math.radians(angle + angle_offset)) * _ORBIT_RADIUS 
                - self.orbiting_fires[i-1].height/2
            )

    def update(self, dt: float) -> None:
        for projectile in list(self.room.projectiles):
            if projectile.dead:
                break

            if projectile.collides(self.boss):
                self.boss.inmune = False
                self.activate_orbiting_fires(False)
                self.boss.go_invulnerable(0.3)
                settings.SOUNDS["hit-enemy"].play()
                projectile.dead = True

        if self.boss.inmune:
            self.recovery_timer = 0
        else:
            self.recovery_timer += dt
            if self.recovery_timer >= _RECOVERY_TIME:
                self.boss.inmune = True
                self.activate_orbiting_fires(True)

        if (
            (
                self.boss.health <= _FIRST_HEALTH_TRESHOLD 
                and self.phase == 0
            )
            or (
                self.boss.health <= _SECOND_HEALTH_TRESHOLD 
                and self.phase == 1
            )
        ):
            side = _OPOSITE_SIDE[self.side]
            spot = _BOSS_SPAWN_SPOTS[side]
            self.side = side
            self.boss.inmunity = True
            self.recovery_timer = 0
            self.firing_timer = 0
            self.boss.x = spot[0]
            self.boss.y = spot[1]
            self.activate_orbiting_fires(True)
            self.update_orbiting_fires(dt)
            self.phase += 1
            if self.phase == 2:
                self.firing_interval = _QUICK_FIRING_INTERVAL

        if self.can_fire and self.boss.inmune:
            self.firing_timer += dt
            if self.firing_timer >= self.firing_interval:
                self.firing_timer = 0

                vec = pygame.math.Vector2(
                    self.room.player.x - self.boss.x,
                    self.room.player.y - self.boss.y 
                ).normalize()

                orientation = "right"
                if abs(vec.y) > abs(vec.x):
                    if vec.y > 0:
                        orientation = "down"
                    else:
                        orientation = "up"
                elif abs(vec.x) > abs(vec.y) and vec.x < 0:
                    orientation = "left"

                f = self.spawn_fire(self.boss.x, self.boss.y, orientation, False)
                f.vx = vec.x * _FIRE_SPEED
                f.vy = vec.y * _FIRE_SPEED
        
        for fire in self.fires:
            if not fire.active:
                continue

            fire.update(dt)
            if self.room.player.collides(fire):
                self.room.on_game_over()

        self.update_orbiting_fires(dt)

    def render(
        self,
        surface: pygame.Surface,
        camera_offset_x: float = 0,
        camera_offset_y: float = 0,
    ) -> None:
        for fire in self.fires:
            fire.render(surface)

