from enum import IntEnum
from pathlib import Path


ASSET_PATH = Path("assets/")


class InputType(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    SPECIAL = 4
