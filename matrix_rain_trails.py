from typing import Self

from matrix_rain_trail import MatrixRainTrail
from random_list import RandomList


class MatrixTrails:

    def __init__(self: Self, width: int) -> None:

        # argument validation
        if type(width) is not int:
            raise ValueError("argument is not integer")
        if width < 1:
            raise ValueError(f"argument is {width}; expected >= 1")

        self._active: list[MatrixRainTrail] = []
        self._exhausted: list[MatrixRainTrail] = []
        self._available = RandomList(width)

    def available_column_numbers(self: Self) -> RandomList:
        return self._available
