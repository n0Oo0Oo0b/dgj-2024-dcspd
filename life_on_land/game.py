import arcade

from life_on_land.constants import *
from life_on_land.player import PlayerSprite

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Life on Land"
INPUT_BUFFER_DURATION = 0.1


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

        # Game related
        self.player_sprite: PlayerSprite = PlayerSprite(self)
        self.global_time: float = 0

        # Inputs
        k = arcade.key
        self.control_map: dict[int, InputType] = (
            dict.fromkeys([k.UP, k.W, k.SPACE], InputType.UP)
            | dict.fromkeys([k.DOWN, k.S], InputType.DOWN)
            | dict.fromkeys([k.LEFT, k.A], InputType.LEFT)
            | dict.fromkeys([k.RIGHT, k.D], InputType.RIGHT)
        )
        self.last_pressed: dict[InputType, float] = {}
        self.pressed_inputs: set[InputType] = set()

    def on_update(self, delta_time: float):
        self.global_time += delta_time

        self.player_sprite.on_update(delta_time)

    def on_draw(self):
        pass

    def on_key_press(self, key, modifiers):
        if key in {arcade.key.ESCAPE, arcade.key.Q}:
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
        return self.last_pressed.get(key, -1) + INPUT_BUFFER_DURATION > self.global_time

    def consume_buffer(self, key: InputType):
        self.last_pressed[key] = -1
