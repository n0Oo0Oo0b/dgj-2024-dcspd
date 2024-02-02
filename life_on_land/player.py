from typing import TYPE_CHECKING

import arcade

from life_on_land.constants import *

if TYPE_CHECKING:
    from life_on_land.game import GameWindow


FRICTION_FACTOR = 0.4
PLAYER_SPEED = 5
PLAYER_JUMP_FORCE = 10
COYOTE_DURATION = 0.1


class PlayerSprite(arcade.Sprite):
    def __init__(self, game_window: "GameWindow"):
        super().__init__(
            scale=2,
        )
        self.texture = arcade.load_texture(ASSET_PATH / "player" / "idle-test.png")
        self.position = [100, 75]

        self.last_grounded: float = -1
        self.game_window: "GameWindow" = game_window

        self.level_1_unlocked = True

    def on_update(self, delta_time: float = 1 / 60):
        # Update attributes
        game = self.game_window
        if game.engine.can_jump():
            self.last_grounded = game.global_time

        # X movement
        right_pressed = InputType.RIGHT in game.pressed_inputs
        left_pressed = InputType.LEFT in game.pressed_inputs
        target_vel = (right_pressed - left_pressed) * PLAYER_SPEED

        vel_diff = target_vel - self.velocity[0]
        self.velocity[0] += vel_diff * FRICTION_FACTOR

        # Y movement (jump)
        if (
            game.is_buffered(InputType.UP)
            and self.last_grounded + COYOTE_DURATION >= game.global_time
        ):
            game.consume_buffer(InputType.UP)
            self.velocity[1] = PLAYER_JUMP_FORCE

        if self.level_1_unlocked:
            self.level_1_special()

    def level_1_special(self):
        game = self.game_window
        if game.is_buffered(InputType.SPECIAL):
            game.consume_buffer(InputType.SPECIAL)
            print("Special Activated")
            self.velocity[1] = 15
