from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from life_on_land.constants import *

if TYPE_CHECKING:
    from life_on_land.player import PlayerSprite


class LevelEffect(ABC):
    def __init__(self, player: "PlayerSprite"):
        self.player = player

    @abstractmethod
    def on_update(self):
        raise NotImplementedError


class NoEffect(LevelEffect):
    def on_update(self):
        pass


class FireHoseEffect(LevelEffect):
    LAUNCH_VELOCITY = 7.5
    LAUNCH_ACCEL_FACTOR = 0.2
    LAUNCH_DURATION = 0.5

    def __init__(self, player: "PlayerSprite"):
        super().__init__(player)
        self.can_launch: bool = True
        self.last_launch: float = -1

    def on_update(self):
        game = self.player.game_window

        if self.can_launch and game.is_buffered(InputType.SPECIAL):
            self.can_launch = False
            game.consume_buffer(InputType.SPECIAL)
            self.last_launch = game.global_time
        elif InputType.SPECIAL not in game.pressed_inputs:
            self.last_launch = -1

        if self.last_launch + self.LAUNCH_DURATION >= game.global_time:
            vel_diff = self.LAUNCH_VELOCITY - self.player.velocity[1]
            self.player.velocity[1] += vel_diff * self.LAUNCH_ACCEL_FACTOR
        elif game.engine.can_jump():
            pass
