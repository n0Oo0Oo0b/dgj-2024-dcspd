import arcade
from pyglet.math import Vec2
from pytiled_parser import ObjectLayer

from life_on_land.constants import *
from life_on_land.player import PlayerSprite


class GameWindow(arcade.Window):
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    SCREEN_TITLE = "Life on Land"
    INPUT_BUFFER_DURATION = 0.1
    LEVEL_DIR = ASSET_PATH / "levels"

    def __init__(self):
        super().__init__(
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            self.SCREEN_TITLE,
            resizable=True,
        )

        # Game related
        self.player_sprite: PlayerSprite = PlayerSprite(self)
        self.global_time: float = 0
        self.camera_sprites = arcade.Camera(self.width, self.height)
        self.current_level: Level = Level.GRASS

        # Inputs
        k = arcade.key
        self.control_map: dict[int, InputType] = (
            dict.fromkeys([k.UP, k.W], InputType.UP)
            | dict.fromkeys([k.DOWN, k.S], InputType.DOWN)
            | dict.fromkeys([k.LEFT, k.A], InputType.LEFT)
            | dict.fromkeys([k.RIGHT, k.D], InputType.RIGHT)
            | dict.fromkeys([k.SPACE], InputType.SPECIAL)
        )
        self.last_pressed: dict[InputType, float] = {}
        self.pressed_inputs: set[InputType] = set()

        # self.tilemap: arcade.TileMap = arcade.load_tilemap(":resources:tiled_maps/map.json", 0.3)
        # self.scene: arcade.Scene = arcade.Scene.from_tilemap(self.tilemap)
        self.tilemap: arcade.TileMap | None = None
        self.scene: arcade.Scene | None = None
        self.engine: arcade.physics_engines.PhysicsEnginePlatformer | None = None
        self.load_level("forest-final.tmx")

    def load_level(self, level_name: str):
        self.tilemap = arcade.load_tilemap(self.LEVEL_DIR / level_name)
        self.scene = arcade.Scene.from_tilemap(self.tilemap)

        # Seems like it wasn't intended to use object layers in Tiled
        object_layer: ObjectLayer = self.tilemap.get_tilemap_layer("Game")  # type: ignore
        for obj in object_layer.tiled_objects:
            if obj.name == "Player":
                player_x, player_y = obj.coordinates
                total_height = self.tilemap.height * self.tilemap.tile_height
                self.player_sprite.position = player_x, total_height - player_y

        self.engine = arcade.physics_engines.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.scene["Platforms"],
        )

    def on_update(self, delta_time: float):
        self.global_time += delta_time

        self.engine.update()
        self.player_sprite.on_update(delta_time)

        self.center_camera_to_player()

    def on_draw(self):
        self.clear()
        self.camera_sprites.use()
        self.scene.draw(pixelated=True)
        self.player_sprite.draw()


    def on_key_press(self, key, modifiers):
        if key in {arcade.key.ESCAPE, arcade.key.Q}:
            self.close()
            return

        if (type_ := self.control_map.get(key)) is None:
            return
        self.last_pressed[type_] = self.global_time
        self.pressed_inputs.add(type_)

    def on_key_release(self, key, modifiers):
        if (type_ := self.control_map.get(key)) is None:
            return
        self.pressed_inputs.discard(type_)

    def is_buffered(self, key: InputType):
        return self.last_pressed.get(key, -1) + self.INPUT_BUFFER_DURATION > self.global_time

    def consume_buffer(self, key: InputType):
        self.last_pressed[key] = -1

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera_sprites.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera_sprites.viewport_height / 2)

        # Set some limits on how far we scroll
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        # Here's our center, move to it
        player_centered = Vec2(screen_center_x, screen_center_y)
        self.camera_sprites.move_to(player_centered)
