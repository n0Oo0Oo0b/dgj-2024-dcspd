from typing import TYPE_CHECKING, Literal

import arcade
import math

from life_on_land.constants import *
from life_on_land.level_effects import NoEffect, EFFECT_MAPPING

if TYPE_CHECKING:
    from life_on_land.game import GameWindow


class PlayerSprite(arcade.Sprite):
    FRICTION_FACTOR = 0.4
    PLAYER_SPEED = 5
    PLAYER_JUMP_FORCE = 10
    COYOTE_DURATION = 0.1
    MAP = {
        1: "GrassBiome",
        2: "DesertBiome",
        3: "IceBiome"
    }
    TEXTURE_PATH = ASSET_PATH / "player" / "Hero"

    def __init__(self, game_window: "GameWindow"):
        super().__init__(
            scale=2,
        )

        self.animation_tick_count = 0
        self.position = [100, 75]
        self.last_grounded: float = -1
        self.grounded_position = [0, 0]
        self.game_window: "GameWindow" = game_window
        self.special = NoEffect(self)
        self.texture_map: dict[Literal["idle", "walk", "side"], list[arcade.Texture]] = {}
        self.load_textures(self.TEXTURE_PATH / self.MAP[self.game_window.current_level])
        self.texture = self.texture_map['idle'][0]

    def load_textures(self, texture_dir):
        self.texture_map = {
            "idle": arcade.load_texture_pair(texture_dir / "Front" / "Front.png"),
            "walk": arcade.load_texture_pair(texture_dir / "Run" / "SideRun.png"),
            "side": arcade.load_texture_pair(texture_dir / "Side" / "Side.png"),
        }

    def on_update(self, delta_time: float = 1 / 60):
        # Update attributes
        game = self.game_window
        if game.engine.can_jump():
            self.last_grounded = game.global_time
            self.grounded_position = self.position

        # X movement
        right_pressed = InputType.RIGHT in game.pressed_inputs
        left_pressed = InputType.LEFT in game.pressed_inputs
        target_vel = (right_pressed - left_pressed) * self.PLAYER_SPEED
        facing = 1 if target_vel < 0 else 0
        if target_vel:
            if 3 < self.animation_tick_count < 10:
                self.texture = self.texture_map["walk"][facing]
            else:
                self.texture = self.texture_map["side"][facing]
            if self.animation_tick_count == 10:
                self.animation_tick_count = 0
            self.animation_tick_count += 1
        else:
            self.texture = self.texture_map["idle"][facing]

        vel_diff = target_vel - self.velocity[0]
        self.velocity[0] += vel_diff * self.FRICTION_FACTOR

        # Y movement (jump)
        if (
                game.is_buffered(InputType.UP)
                and self.last_grounded + self.COYOTE_DURATION >= game.global_time
        ):
            game.consume_buffer(InputType.UP)
            self.velocity[1] = self.PLAYER_JUMP_FORCE

        if self.position[1] < - 256 or self.collides_with_list(game.danger_sprites):
            difference = -1
            if self.position[0] < self.grounded_position[0]:
                difference = +1
            self.position = [round(self.grounded_position[0] / 32, 0) * 32 + difference * 16, self.grounded_position[1]]
            self.velocity = [0, 0]

        self.special.on_update()

    def draw(self, **kwargs):
        super().draw(**kwargs)
        self.special.draw()

    def apply_special(self):
        effect_cls = EFFECT_MAPPING[self.game_window.current_level]
        self.special = effect_cls(self)
        self.load_textures(self.TEXTURE_PATH / "GrassWithHose")
