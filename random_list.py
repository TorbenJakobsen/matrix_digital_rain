import random
from typing import Self


class RandomList:

    def __init__(self: Self, size: int) -> None:
        """Creates a list with integers in range

        e.g. `[0,1,2,3,4]`
        """
        self._list = list(range(size))

    def __len__(self: Self) -> int:
        return len(self._list)

    def pop_random(self: Self) -> int:
        """
        Chooses a random index, remove value from list and returns chosen value

        e.g. `[0,1,2,3,4]` -> `[0,1,2,4]` and returns `3`
        """
        if not self._list or len(self._list) == 0:
            raise ValueError("list has no elements to pop")

        chosen: int = self._list.pop(random.randrange(len(self._list)))
        return chosen

    def append(self: Self, number: int) -> None:
        self._list.append(number)
