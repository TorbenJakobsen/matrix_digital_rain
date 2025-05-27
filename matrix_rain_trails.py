from typing import Self

from matrix_rain_trail import MatrixRainTrail
from random_list import RandomList


class MatrixTrails:

    def __init__(self: Self, width: int) -> None:
        self._active: list[MatrixRainTrail] = []
        self._exhausted: list[MatrixRainTrail] = []
        self._available = RandomList(width)
