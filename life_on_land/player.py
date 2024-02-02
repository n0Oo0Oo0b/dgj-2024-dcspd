import arcade

from life_on_land.constants import *


class PlayerSprite(arcade.Sprite):
    def __init__(self, game_window):
        super().__init__(
            scale=2,
        )
        self.texture = arcade.load_texture(ASSET_PATH / "player" / "idle-test.png")
        self.position = [100, 75]

        self.game_window = game_window

    def on_update(self, delta_time: float = 1 / 60):
        pass
