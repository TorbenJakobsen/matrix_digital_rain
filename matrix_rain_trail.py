import random
from typing import Self


class IllegalArgumentError(ValueError):
    pass


class MatrixRainTrail:
    """
    HBBBBBT     length=7
    ^^    ^     offset
    ||    +---- 0       TAIL :: HEAD - (LENGTH-1)
    |+--------- 5       BODY :: HEAD - 1
    +---------- 6       HEAD :: HEAD
    """

    def __init__(
        self: Self,
        column_number: int,
        screen_columns: int,
        screen_lines: int,
    ):
        #
        # Argument validation and sanity checks
        #

        if column_number is None:
            raise IllegalArgumentError("Column number is None")

        if screen_columns is None:
            raise IllegalArgumentError("Screen columns is None")

        if screen_lines is None:
            raise IllegalArgumentError("Screen lines is None")

        if not isinstance(column_number, int):
            raise IllegalArgumentError("Column number is not an integer")

        if not isinstance(screen_columns, int):
            raise IllegalArgumentError("Screen columns is not an integer")

        if not isinstance(screen_lines, int):
            raise IllegalArgumentError("Screen lines is not an integer")

        if column_number < 0:
            raise IllegalArgumentError(f"Column number '{column_number}' is negative")

        if screen_columns < 0:
            raise IllegalArgumentError(f"Screen columns '{screen_columns}' is negative")

        if screen_lines < 0:
            raise IllegalArgumentError(f"Screen lines '{screen_lines}' is negative")

        if column_number > screen_columns:
            raise IllegalArgumentError(
                f"Column number '{column_number}' is greater than available screen columns '{screen_columns}'"
            )

        #
        #
        #

        self.column_number: int = column_number
        self._screen_columns: int = screen_columns
        self._screen_lines: int = screen_lines

        self.MIN_LENGTH = 3
        self.MAX_LENGTH = screen_lines - 3

        self._length: int = random.randint(self.MIN_LENGTH, self.MAX_LENGTH)
        # `randint` includes endpoints

        self._head_position = -1

    def __len__(self: Self) -> int:
        return self._length

    def __str__(self: Self) -> str:
        """
        Intended as a convenience when debugging or writing to log.

        :return: _description_
        :rtype: str
        """
        return f"C:{self.column_number} L:{self.head_start()} | HV:{self.is_head_visible()} | TV:{self.is_tail_visible()} | X:{self.is_exhausted()}"

    #
    # ---
    #

    def length(self) -> int:
        return self._length

    def is_exhausted(self: Self) -> bool:
        """
        `True` if trail has moved past bottom of screen.

        HBBBBBT     length=7
        ^^    ^     offset
        ||    +---- 0       TAIL :: HEAD - (LENGTH-1)
        |+--------- 5       BODY :: HEAD - 1
        +---------- 6       HEAD :: HEAD

        32109876543210
              ++++++++   lines=8
        HBBBBBT     offset
        ||    +---- 7       TAIL :: HEAD - (LENGTH-1)
        |+--------- 12      BODY :: HEAD - 1
        +---------- 13      HEAD :: HEAD

        """
        return self.tail_start() >= self._screen_lines

    def is_head_visible(self) -> bool:
        """
        `True` if head is visble.

        HBBBBBT     length=7
        ^^    ^     offset
        ||    +---- 0       TAIL :: HEAD - (LENGTH-1)
        |+--------- 5       BODY :: HEAD - 1
        +---------- 6       HEAD :: HEAD

        32109876543210
              ++++++++   columns=8
                   HBBBBBT     offset
                   ||    +---- -4     TAIL :: HEAD - (LENGTH-1)
                   |+--------- 1      BODY :: HEAD - 1
                   +---------- 2      HEAD :: HEAD
        """
        return 0 <= self.head_start() < self._screen_lines

    def is_tail_visible(self) -> bool:
        """
        `True` if tail is visble.

        HBBBBBT     length=7
        ^^    ^     offset
        ||    +---- 0       TAIL :: HEAD - (LENGTH-1)
        |+--------- 5       BODY :: HEAD - 1
        +---------- 6       HEAD :: HEAD

        32109876543210
              ++++++++   columns=8
        HBBBBBT     offset
        ||    +---- 7       TAIL :: HEAD - (LENGTH-1)
        |+--------- 12      BODY :: HEAD - 1
        +---------- 13      HEAD :: HEAD
        """
        return 0 <= self.tail_start() < self._screen_lines

    def is_visible(self) -> bool:
        return self.is_head_visible() or self.is_tail_visible()

    def move_forward(self, force: bool = True) -> int:
        if force:
            self._head_position += 1
            return True
        return False

    def head_start(self) -> int:
        """The head start is also the end of the head."""
        return self._head_position

    def body_start(self) -> int:
        return self.head_start() - 1

    def body_end(self) -> int:
        return self.tail_start() + 1

    def tail_start(self) -> int:
        """The tail start is also the end of the tail."""
        return self.head_start() - (self._length - 1)
