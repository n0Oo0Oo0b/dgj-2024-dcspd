from pathlib import Path
from typing import TYPE_CHECKING

import arcade

from life_on_land.constants import ASSET_PATH, Level

if TYPE_CHECKING:
    from life_on_land.game import GameWindow


class ObjectiveSprite(arcade.Sprite):
    TEXTURE_MAP: dict[Level, Path] = {
        Level.GRASS: ASSET_PATH / "textures" / "GRASS" / "objective",
    }

    def __init__(self, game_window: "GameWindow", position):
        super().__init__(
            scale=4,
        )
        self.position = list(position)
        texture_dir = self.TEXTURE_MAP[game_window.current_level]
        self.texture_map = {
            "before": arcade.load_texture(texture_dir / "before.png", hit_box_algorithm="None"),
            "after": arcade.load_texture(texture_dir / "after.png", hit_box_algorithm="None"),
        }
        self.texture = self.texture_map["before"]
        self.position[1] += self.texture.height * 1.25

        self.game_window = game_window

    def resolve(self):
        self.texture = self.texture_map["after"]
        self.hit_box = [(0, 0)]
