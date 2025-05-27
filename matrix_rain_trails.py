from typing import Self

from matrix_rain_trail import MatrixRainTrail
from random_list import RandomList


class MatrixRainTrails:

    def __init__(self: Self, width: int, height: int) -> None:

        # argument validation
        if type(width) is not int:
            raise ValueError("argument width is not integer")
        if width < 1:
            raise ValueError(f"argument width is {width}; expected >= 1")
        if type(height) is not int:
            raise ValueError("argument height is not integer")
        if height < 1:
            raise ValueError(f"argument height is {height}; expected >= 1")

        self._active: list[MatrixRainTrail] = []
        self._exhausted: list[MatrixRainTrail] = []
        self._available = RandomList(width)
        self._width = width
        self._height = height

    @property
    def available_column_numbers(self: Self) -> RandomList:
        return self._available

    def replenish_exhausted(self: Self):
        """Remove trails marked as exhausted from active trails and make trails available."""
        for exhausted_trail in self._exhausted:
            self._active.pop(self._active.index(exhausted_trail))
            self._available.append(exhausted_trail.column_number)
        self._exhausted.clear()

    def activate_trail(self: Self) -> None:
        """Activate a trail randomly chosen from available."""
        chosen_column_number: int = self._available.pop_random()
        # activate trail by chosen number
        self._active.append(
            MatrixRainTrail(
                chosen_column_number,
                self._width,
                self._height,
            )
        )

    @property
    def active_trails(self: Self) -> list[MatrixRainTrail]:
        return self._active

    def exhaust(self: Self, trail: MatrixRainTrail) -> None:
        self._exhausted.append(trail)

    def has_available_trails(self: Self, requested_size: int) -> bool:
        return len(self._available) >= requested_size
