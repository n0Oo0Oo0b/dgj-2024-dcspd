from pathlib import Path
from typing import TYPE_CHECKING

import arcade

from life_on_land.constants import ASSET_PATH, Level

if TYPE_CHECKING:
    from life_on_land.game import GameWindow


class PickupSprite(arcade.Sprite):
    TEXTURE_MAP: dict[Level, Path] = {
        Level.GRASS: ASSET_PATH / "textures" / "MISC" / "FireExtinguisher" / "HoseAnim-1.png",
    }

    def __init__(self, game_window: "GameWindow", position):
        super().__init__(
            scale=2,
        )
        self.position = list(position)
        self.texture = arcade.load_texture(self.TEXTURE_MAP[game_window.current_level])
        self.position[1] += self.texture.height // 2

        self.game_window = game_window
