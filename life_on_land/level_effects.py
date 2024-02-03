import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import arcade

from life_on_land.constants import *

if TYPE_CHECKING:
    from life_on_land.player import PlayerSprite


def glob_textures(fp: Path) -> list[arcade.Texture]:
    return [arcade.load_texture(file) for file in sorted(fp.iterdir())]


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


class WaterEmitController(arcade.EmitController):
    def __init__(self, effect: "FireHoseEffect"):
        self.effect_obj = effect

    def how_many(self, delta_time: float, current_particle_count: int) -> int:
        return self.effect_obj.is_launching * 5

    def is_complete(self) -> bool:
        return False


class FireHoseEffect(LevelEffect):
    LAUNCH_VELOCITY = 7.5
    LAUNCH_ACCEL_FACTOR = 0.2
    LAUNCH_DURATION = 0.5
    BURST_PARTICLE_COUNT = 200
    WATER_TEXTURE = glob_textures(ASSET_PATH / "textures" / "MISC" / "Particles" / "Water")

    def __init__(self, player: "PlayerSprite"):
        super().__init__(player)
        self.can_launch: bool = True
        self.last_launch: float = -1
        self.e: arcade.Emitter = arcade.Emitter(
            (0, -16),
            WaterEmitController(self),
            particle_factory=lambda emitter: arcade.FadeParticle(
                random.choice(self.WATER_TEXTURE),
                arcade.rand_vec_spread_deg(-90, 50, 3),
                0.8,
                self.player.position,
                start_alpha=128,
            )
        )

    @property
    def is_launching(self):
        return self.last_launch + self.LAUNCH_DURATION >= self.player.game_window.global_time

    def on_update(self):
        game = self.player.game_window

        if self.can_launch and game.is_buffered(InputType.SPECIAL):
            self.can_launch = False
            game.consume_buffer(InputType.SPECIAL)
            self.last_launch = game.global_time
        elif InputType.SPECIAL not in game.pressed_inputs:
            self.last_launch = -1

        if self.is_launching:
            vel_diff = self.LAUNCH_VELOCITY - self.player.velocity[1]
            self.player.velocity[1] += vel_diff * self.LAUNCH_ACCEL_FACTOR
        elif game.engine.can_jump():
            self.can_launch = True

    def draw(self):
        self.e.update()
        self.e.draw()


EFFECT_MAPPING: dict[Level, type[LevelEffect]] = {
    Level.GRASS: FireHoseEffect,
}
