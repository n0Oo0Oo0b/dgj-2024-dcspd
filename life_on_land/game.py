import arcade
from pyglet.math import Vec2
from pytiled_parser import ObjectLayer

from life_on_land.constants import *
from life_on_land.objectives import ObjectiveSprite
from life_on_land.pickups import PickupSprite
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
        self.global_time: float = 0
        self.camera_sprites = arcade.Camera(self.width, self.height)
        self.current_level: Level = Level.GRASS
        self.player_sprite: PlayerSprite = PlayerSprite(self)
        self.ost = None
        self.background = ASSET_PATH / "textures" / "GRASS" / "Game Jam Background - Thorgatus.gif"
        self.debug_enabled: bool = False
        self.update_engine: bool = True
        self.background_sprites = [arcade.Sprite(self.background, 4) for i in range(56)]
        count = 0
        for j in range(4)[::-1]:
            for i in range(14):
                self.background_sprites[count].position = [(i - j/2) * 2160, j * (732 - 240) + 350]
                count += 1

        # Inputs
        k = arcade.key
        self.control_map: dict[int, InputType] = (
            dict.fromkeys([k.UP, k.W], InputType.UP)
            | dict.fromkeys([k.DOWN, k.S], InputType.DOWN)
            | dict.fromkeys([k.LEFT, k.A], InputType.LEFT)
            | dict.fromkeys([k.RIGHT, k.D], InputType.RIGHT)
            | dict.fromkeys([k.SPACE], InputType.SPECIAL)
            #| dict.fromkeys([k.E, k.C], InputType.TALK)
        )
        self.last_pressed: dict[InputType, float] = {}
        self.pressed_inputs: set[InputType] = set()

        # Level
        self.tilemap: arcade.TileMap | None = None
        self.scene: arcade.Scene | None = None
        self.engine: arcade.physics_engines.PhysicsEnginePlatformer | None = None
        self.objective_sprites: arcade.SpriteList = arcade.SpriteList()
        self.danger_sprites: arcade.SpriteList = arcade.SpriteList()
        self.pickup_sprite: arcade.Sprite | None = None
        self.camera_end = 0
        self.load_level("forest-final.tmx")

    def load_level(self, level_name: str):
        self.tilemap = arcade.load_tilemap(self.LEVEL_DIR / level_name)
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        self.ost = arcade.load_sound(ASSET_PATH / 'sounds' / 'Forest.wav')
        arcade.play_sound(self.ost, 0.8, 0.0, True, 1)
        self.objective_sprites.clear()
        self.danger_sprites = self.scene["Danger"]
        for sprite in self.danger_sprites:
            sprite._points = [(0, 0), (32, 0), (32, 1), (0, 1)]

        # Seems like it wasn't intended to use object layers in Tiled
        object_layer: ObjectLayer = self.tilemap.get_tilemap_layer("Game")  # type: ignore
        total_height = self.tilemap.height * self.tilemap.tile_height
        for obj in object_layer.tiled_objects:
            obj_x, obj_y = obj.coordinates
            obj_y = total_height - obj_y
            if obj.name == "Player":
                self.player_sprite.position = obj_x, obj_y
            elif obj.name == "Objective":
                self.objective_sprites.append(ObjectiveSprite(self, (obj_x, obj_y)))
            elif obj.name == "Unlock":
                self.pickup_sprite = PickupSprite(self, (obj_x, obj_y))
            elif obj.name == "End":
                self.camera_end = obj_x - self.SCREEN_WIDTH


        self.engine = arcade.physics_engines.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=[self.scene["Platforms"], self.objective_sprites],
        )

    def on_update(self, delta_time: float):
        self.global_time += delta_time

        if self.update_engine:
            self.engine.update()
        self.player_sprite.on_update(delta_time)

        if self.player_sprite.collides_with_sprite(self.pickup_sprite):
            self.pickup_sprite.center_y -= 10000
            self.player_sprite.apply_special()

        self.center_camera_to_player()

    def on_draw(self):
        self.clear()
        for sprite in self.background_sprites: sprite.draw()
        self.camera_sprites.use()
        self.scene.draw(pixelated=True)
        self.objective_sprites.draw()
        self.pickup_sprite.draw()
        self.player_sprite.draw()

        if self.debug_enabled:
            self.player_sprite.draw_hit_box((255, 0, 0), 2)
            self.objective_sprites.draw_hit_boxes((0, 0, 255), 2)

    def on_key_press(self, key, modifiers):
        if key in {arcade.key.ESCAPE, arcade.key.Q}:
            self.close()
            return
        elif key == arcade.key.GRAVE:
            self.debug_enabled = not self.debug_enabled
        elif key == arcade.key.P and self.debug_enabled:
            self.update_engine = not self.update_engine

        if (type_ := self.control_map.get(key)) is None:
            return
        self.last_pressed[type_] = self.global_time
        self.pressed_inputs.add(type_)

    def on_key_release(self, key, modifiers):
        if (type_ := self.control_map.get(key)) is None:
            return
        self.pressed_inputs.discard(type_)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.debug_enabled and button == 1:
            target = self.camera_sprites.position + Vec2(x, y)
            self.player_sprite.position = target
            self.player_sprite.velocity = [0, 0]

    def is_buffered(self, key: InputType):
        return self.last_pressed.get(key, -1) + self.INPUT_BUFFER_DURATION > self.global_time

    def consume_buffer(self, key: InputType):
        self.last_pressed[key] = -1

    def center_camera_to_player(self):
        print(self.camera_end)
        screen_center_x = self.player_sprite.center_x - (self.camera_sprites.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera_sprites.viewport_height / 2)

        # Set some limits on how far we scroll
        screen_center_x = min(max(screen_center_x, 0), self.camera_end)
        screen_center_y = max(screen_center_y, 0)

        # Here's our center, move to it
        player_centered = Vec2(screen_center_x, screen_center_y)
        self.camera_sprites.move_to(player_centered)
