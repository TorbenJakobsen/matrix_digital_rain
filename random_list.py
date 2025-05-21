import random
from typing import Self


class RandomList:
    """
    A list of integers that are initially has the range from ``0`` to size argument (not inclusive).

    There is no guarantee, that the order is preserved as numbers can be appendend.

    >>> from random_list import RandomList
    >>> rl = RandomList(5)
    """

    def __init__(self: Self, size: int) -> None:
        """
        Creates a list with integers as a range.

        e.g. `[0,1,2,3,4]`
        """
        if type(size) is not int:
            raise ValueError("argument size is not 'int'")
        self._arg_size = size
        self._list = list(range(size))

    def __len__(self: Self) -> int:
        """Return the number of items in the list."""
        return len(self._list)

    def pop_random(self: Self) -> int:
        """
        Chooses a random index, remove item from list and returns chosen value.

        e.g. ``[0,2,4]`` -> ``[0,4]`` and returns ``2``

        >>> from random_list import RandomList
        >>> rl = RandomList(5)
        >>> print(rl.pop_random())
        3
        """
        if not self._list or len(self._list) == 0:
            raise ValueError("list has no elements to pop")

        chosen: int = self._list.pop(random.randrange(len(self._list)))
        return chosen

    def append(self: Self, number: int) -> None:
        if type(number) is not int:
            raise ValueError("argument is not 'int'")
        if number < 0 or number >= self._arg_size:
            raise ValueError(f"{number} is outside boundary [0,{self._arg_size}[")
        if number in self._list:
            raise ValueError(f"{number} is already in list")
        self._list.append(int(number))
