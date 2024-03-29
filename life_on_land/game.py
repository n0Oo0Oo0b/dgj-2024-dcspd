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
        self.media_player = None
        self.global_time: float = 0
        self.current_level: Level = Level.GRASS
        self.ost = None

        self.camera_sprites = arcade.Camera(self.width, self.height)
        self.player_sprite: PlayerSprite = PlayerSprite(self)
        self.background = ASSET_PATH / "textures" / "GRASS" / "Game Jam Background - Thorgatus.gif"
        self.background_sprite = arcade.Sprite(self.background, 4)

        self.debug_enabled: bool = False
        self.update_engine: bool = True

        # Inputs
        k = arcade.key
        self.control_map: dict[int, InputType] = (
            dict.fromkeys([k.UP, k.W], InputType.UP)
            | dict.fromkeys([k.DOWN, k.S], InputType.DOWN)
            | dict.fromkeys([k.LEFT, k.A], InputType.LEFT)
            | dict.fromkeys([k.RIGHT, k.D], InputType.RIGHT)
            | dict.fromkeys([k.SPACE], InputType.SPECIAL)
            | dict.fromkeys([k.E, k.C], InputType.TALK)
        )
        self.last_pressed: dict[InputType, float] = {}
        self.pressed_inputs: set[InputType] = set()

        # Level
        self.tilemap: arcade.TileMap | None = None
        self.scene: arcade.Scene | None = None
        self.engine: arcade.physics_engines.PhysicsEnginePlatformer | None = None
        self.objective_sprites: arcade.SpriteList = arcade.SpriteList()
        self.danger_sprites: arcade.SpriteList = arcade.SpriteList()
        self.crumbling_sprites: arcade.SpriteList = arcade.SpriteList()
        self.pickup_sprite: arcade.Sprite | None = None
        self.camera_end = 0
        self.load_level("forest-final.tmx")
        self.text = [[["OH NO THE TREES ARE ON FIRE!", 2700, 480],
                      ["We've received a distress call from the forest", 300, 400],
                      ["(SEE README.MD for controls)", 300, 350],
                      ["We must find the find hose first to put out the fire!", 2700, 430],
                      ["Pick up the fire hose (hold space to boost)", 1400, 850],
                      ["Press E next to tree to use", 3300, 230],
                      ["I'VE TRAVELLED at least 3 miles ", 14000, 32*14],
                      ["to your location PLEASE HELP US ", 14000, 32*12],
                      ["AT THE DESERT!!!", 14000, 32 * 10]]]
        if self.current_level == 1:
            self.ostrich = arcade.Sprite(ASSET_PATH / 'textures' / 'MISC' / 'Animals' / 'ostrich.png', 4)
            self.ostrich.position = [14200, 32 * 7]

    def load_level(self, level_name: str):
        try:
            self.media_player.pause()
        except AttributeError:
            pass
        self.tilemap = arcade.load_tilemap(self.LEVEL_DIR / level_name)
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        if self.current_level == 1:
            self.ost = arcade.load_sound(ASSET_PATH / 'sounds' / 'Forest.wav')
        else:
            self.ost = arcade.load_sound(ASSET_PATH / 'sounds' / 'Desert.wav')
        self.media_player = self.ost.play()
        self.objective_sprites.clear()
        self.danger_sprites = self.scene["Danger"]
        if self.current_level == 2:
            self.crumbling_sprites = self.scene["Crumbling"]
        for sprite in self.danger_sprites:
            sprite._points = [(10, 0), (20, 0), (20, 1), (10, 1)]

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
            walls=[self.scene["Platforms"], self.objective_sprites, self.crumbling_sprites],
        )

    def on_update(self, delta_time: float):
        self.global_time += delta_time

        if self.update_engine:
            self.engine.update()
        self.player_sprite.on_update(delta_time)
        self.objective_sprites.update()

        if self.current_level == 1:
            if self.player_sprite.collides_with_sprite(self.pickup_sprite):
                self.pickup_sprite.center_y -= 10000
                self.player_sprite.apply_special()

        self.center_camera_to_player()

        self.background_sprite.center_x = self.camera_sprites.position[0] + self.SCREEN_WIDTH/2
        self.background_sprite.center_y = self.camera_sprites.position[1] + self.SCREEN_HEIGHT/2

    def on_draw(self):
        self.clear()
        self.background_sprite.draw()
        self.camera_sprites.use()
        for i in self.objective_sprites:
            i.draw(pixelated=True)
        self.scene.draw(pixelated=True)
        self.player_sprite.draw(pixelated=True)
        if self.current_level == 1:
            for text in self.text[self.current_level-1]:
                arcade.draw_text(
                    text[0],
                    text[1],
                    text[2],
                    arcade.color.BLACK,
                    30,
                    font_name="Kenney High Square"
                )
            self.pickup_sprite.draw(pixelated=True)
            self.ostrich.draw(pixelated=True)

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
        screen_center_x = self.player_sprite.center_x - (self.camera_sprites.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera_sprites.viewport_height / 2)

        # Set some limits on how far we scroll
        screen_center_x = min(max(screen_center_x, 0), self.camera_end)
        screen_center_y = max(screen_center_y, 0)

        # Here's our center, move to it
        player_centered = Vec2(screen_center_x, screen_center_y)
        self.camera_sprites.move_to(player_centered)
