import arcade


class PlayerSprite(arcade.Sprite):
    def __init__(self, game_window):
        super().__init__()

        self.game_window = game_window

    def on_update(self, delta_time: float = 1 / 60):
        pass

    def draw(self, **_):
        pass
