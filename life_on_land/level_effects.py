from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import arcade

from life_on_land.constants import *

if TYPE_CHECKING:
    from life_on_land.player import PlayerSprite


class LevelEffect(ABC):
    def __init__(self, player: "PlayerSprite"):
        self.player = player

    @abstractmethod
    def on_update(self):
        raise NotImplementedError

    @abstractmethod
    def draw(self):
        raise NotImplementedError


class NoEffect(LevelEffect):
    def on_update(self):
        pass

    def draw(self):
        pass


class FireHoseEffect(LevelEffect):
    LAUNCH_VELOCITY = 7.5
    LAUNCH_ACCEL_FACTOR = 0.2
    LAUNCH_DURATION = 0.5

    def __init__(self, player: "PlayerSprite"):
        super().__init__(player)
        self.can_launch: bool = True
        self.last_launch: float = -1
        self.e = None
        self.BURST_PARTICLE_COUNT = 200
        self.WATER_TEXTURE = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"

    def on_update(self):
        game = self.player.game_window

        if self.can_launch and game.is_buffered(InputType.SPECIAL):
            self.can_launch = False
            game.consume_buffer(InputType.SPECIAL)
            self.last_launch = game.global_time
            self.e = arcade.Emitter(
                center_xy=self.player.position,
                emit_controller=arcade.EmitBurst(self.BURST_PARTICLE_COUNT // 4),
                particle_factory=lambda emitter: arcade.LifetimeParticle(
                    filename_or_texture=self.WATER_TEXTURE,
                    change_xy=arcade.rand_in_rect((-1,-5), 2, 4),
                    lifetime=1,
                    scale=1,
                    alpha=255,
                )
            )
            self.e = arcade.make_burst_emitter(
                center_xy=self.player.position,
                filenames_and_textures=(self.WATER_TEXTURE,),
                particle_count=50,
                particle_speed=3,
                particle_lifetime_min=1.0,
                particle_lifetime_max=2.5,
                particle_scale=0.3,
                fade_particles=True
            )

        elif InputType.SPECIAL not in game.pressed_inputs:
            self.last_launch = -1

        if self.last_launch + self.LAUNCH_DURATION >= game.global_time:
            vel_diff = self.LAUNCH_VELOCITY - self.player.velocity[1]
            self.player.velocity[1] += vel_diff * self.LAUNCH_ACCEL_FACTOR
        elif game.engine.can_jump():
            self.can_launch = True

    def draw(self):
        if self.e is not None:
            self.e.update()
            self.e.draw()
