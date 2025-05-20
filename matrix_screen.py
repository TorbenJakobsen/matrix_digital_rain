import curses
from enum import Enum
from typing import Self


class Action(Enum):
    NONE = 0
    CONTINUE = 1
    BREAK = 2
    KEY_UP = 3
    KEY_DOWN = 4


class MatrixScreen:
    """
    Wraps a curses window object and exposes cnvenience mtthods.
    """

    MIN_SCREEN_HEIGHT = 8
    MIN_SCREEN_WIDTH = 8

    def __init__(
        self: Self,
        screen: curses.window,
    ):
        self._screen = screen
        self._width = MatrixScreen.MIN_SCREEN_WIDTH
        self._height = MatrixScreen.MIN_SCREEN_HEIGHT

    @property
    def height(self: Self) -> int:
        return self._height

    @property
    def width(self: Self) -> int:
        return self._width

    def validate_screen_size(self: Self) -> bool:
        """Checks if screen is resized.

        If resized returns `True` and update internal representation of dimensions;
        otherwise returns `False`.

        Raises `ValueErrror` if sizes are outside contraints.
        """
        if curses.is_term_resized(self._height, self._width):
            self._height, self._width = self._screen.getmaxyx()
            if self._height < MatrixScreen.MIN_SCREEN_HEIGHT:
                raise ValueError("Error: screen height is too short.")
            if self._width < MatrixScreen.MIN_SCREEN_WIDTH:
                raise ValueError("Error: screen width is too narrow.")
            return True
        # Not resized
        return False

    def handle_key_presses(self: Self) -> Action:

        Q_CHAR_SET: set[int] = {ord("q"), ord("Q")}
        F_CHAR_SET: set[int] = {ord("f"), ord("F")}

        ch: int = self._screen.getch()
        if ch == -1:
            # no input
            return Action.CONTINUE

        if ch == curses.KEY_UP:
            # Quit
            return Action.KEY_UP

        if ch == curses.KEY_DOWN:
            # Quit
            return Action.KEY_DOWN

        if ch in Q_CHAR_SET:
            # Quit
            return Action.BREAK

        if ch in F_CHAR_SET:
            # Freeze
            quit_loop = False
            while True:
                ch = self._screen.getch()
                if ch in F_CHAR_SET:
                    # Unfreeze
                    break
                elif ch in Q_CHAR_SET:
                    # Quit
                    quit_loop = True
                    break
            if quit_loop:
                return Action.BREAK

        return Action.NONE
