from typing import TYPE_CHECKING

import arcade

from life_on_land.constants import *
from life_on_land.level_effects import FireHoseEffect

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

    def __init__(self, game_window: "GameWindow"):
        super().__init__(
            scale=2,
        )

        self.animation_tick_count = 0
        self.position = [100, 75]
        self.last_grounded: float = -1
        self.grounded_position = [0, 0]
        self.game_window: "GameWindow" = game_window
        self.special = FireHoseEffect(self)
        self.texture_map = {
            'idle': arcade.load_texture(ASSET_PATH / "player" / "Hero" / self.MAP[self.game_window.current_level] / "Front" / "Front.png"),
            'walk': arcade.load_texture(ASSET_PATH / "player" / "Hero" / self.MAP[self.game_window.current_level] / "Run" / "SideRun.png"),
            'side': arcade.load_texture(ASSET_PATH / "player" / "Hero" / self.MAP[self.game_window.current_level] / "Side" / "Side.png")
        }
        self.texture = self.texture_map['idle']

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
        if target_vel:
            if 3 < self.animation_tick_count < 10:
                self.texture = self.texture_map["walk"]
            else:
                self.texture = self.texture_map["side"]
            if self.animation_tick_count == 10:
                self.animation_tick_count = 0
            self.animation_tick_count += 1
        else:
            self.texture = self.texture_map["idle"]

        vel_diff = target_vel - self.velocity[0]
        self.velocity[0] += vel_diff * self.FRICTION_FACTOR

        # Y movement (jump)
        if (
                game.is_buffered(InputType.UP)
                and self.last_grounded + self.COYOTE_DURATION >= game.global_time
        ):
            game.consume_buffer(InputType.UP)
            self.velocity[1] = self.PLAYER_JUMP_FORCE

        if self.position[1] < - 256:
            self.position = self.grounded_position
            self.velocity = [0, 0]

        self.special.on_update()

    def draw(self, **kwargs):
        super().draw(**kwargs)
        self.special.draw()
