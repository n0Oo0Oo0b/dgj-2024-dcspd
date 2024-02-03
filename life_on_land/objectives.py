import random
from pathlib import Path
from typing import TYPE_CHECKING

import arcade
from pyglet.math import Vec2

from life_on_land.constants import ASSET_PATH, Level, InputType

if TYPE_CHECKING:
    from life_on_land.game import GameWindow


class ObjectiveSprite(arcade.Sprite):
    TEXTURE_MAP: dict[Level, Path] = {
        Level.GRASS: ASSET_PATH / "textures" / "GRASS" / "objective",
        Level.DESERT: ASSET_PATH / "textures" / "DESERT" / "objective",
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
        self.e: arcade.Emitter | None = None

    @staticmethod
    def random_target(src, dest):
        x2, y2 = dest
        rand_dest = arcade.rand_in_rect((x2-16, y2-40), 32, 80)
        return (Vec2(*src) - Vec2(*rand_dest)).scale(-0.05)

    def update(self):
        if self.e:
            self.e.update()

        game = self.game_window
        diff = Vec2(*game.player_sprite.position) - Vec2(*self.position)
        if diff.mag > 120:
            return
        if game.is_buffered(InputType.TALK):
            game.consume_buffer(InputType.TALK)
            self.texture = self.texture_map["after"]
            self.hit_box = [(0, 0)]
            water_textures = list((ASSET_PATH / "textures" / "MISC" / "Particles" / "Water").iterdir())
            self.e = arcade.Emitter(
                self.game_window.player_sprite.position,
                arcade.EmitBurst(150),
                lambda emitter: arcade.FadeParticle(
                    random.choice(water_textures),
                    self.random_target(game.player_sprite.position, self.position),  # type: ignore
                    0.5,
                )
            )

    def draw(self, **kwargs):
        super().draw(**kwargs)
        if self.e:
            self.e.draw()

