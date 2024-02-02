from typing import TYPE_CHECKING

import arcade

from life_on_land.constants import *

if TYPE_CHECKING:
    from life_on_land.game import GameWindow


class PlayerSprite(arcade.Sprite):
    def __init__(self, game_window: "GameWindow"):
        super().__init__(
            scale=2,
        )
        self.texture = arcade.load_texture(ASSET_PATH / "player" / "idle-test.png")
        self.position = [100, 75]

        self.game_window = game_window

        self.PLAYER_X_VEL = 0
        self.VEL_DIFFERENCE = 0
        self.TARGET_VEL = 0
        self.FRICTION_FACTOR = 0.3

    def on_update(self, delta_time: float = 1 / 60):
        right_pressed = InputType.RIGHT in self.game_window.pressed_inputs
        left_pressed = InputType.LEFT in self.game_window.pressed_inputs

        self.TARGET_VEL = 0
        if right_pressed and left_pressed:
            self.TARGET_VEL = 0
        elif right_pressed:
            self.TARGET_VEL = 5
        elif left_pressed:
            self.TARGET_VEL = -5

        self.VEL_DIFFERENCE = self.TARGET_VEL - self.PLAYER_X_VEL
        self.PLAYER_X_VEL += self.VEL_DIFFERENCE * self.FRICTION_FACTOR

        self.change_x = self.PLAYER_X_VEL

        if (
            self.game_window.is_buffered(InputType.UPSSSS)
            and self.game_window.engine.can_jump()
        ):
            self.game_window.consume_buffer(InputType.UP)
