import curses
from enum import Enum
from typing import Self

# Colors are numbered, and start_color() initializes 8 basic colors when it activates color mode.
# Color pair 0 is hard-wired to white on black, and cannot be changed.
# Coordinates are always passed in the order y,x, and the top-left corner of a window is coordinate (0,0)
# Writing lower right corner...
# https://docs.python.org/3/howto/curses.html


class Action(Enum):
    NONE = 0
    CONTINUE = 1
    BREAK = 2
    KEY_UP = 3
    KEY_DOWN = 4


VALID_COLORS = {
    "black": curses.COLOR_BLACK,
    "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN,
    "yellow": curses.COLOR_YELLOW,
    "blue": curses.COLOR_BLUE,
    "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN,
    "white": curses.COLOR_WHITE,
}
"""
Translates color names to `curses` constants.

The colors are the default initial `curses` colors.
"""

COLOR_PAIR_HEAD: int = 10
COLOR_PAIR_TAIL: int = 9

BLANK: str = " "


class MatrixScreen:
    """
    Wraps a `curses` window object and exposes cnvenience mtthods.
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

        Raises `ValueErrror` if sizes are below contraints.
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

    def setup_screen(
        self: Self,
        head_color: str,
        tail_color: str,
        back_color: str,
    ) -> None:
        """Sets up curses screen (window) using arguments and defaults."""

        #
        # Set up curses and terminal window
        #

        INVISIBLE = 0
        curses.curs_set(INVISIBLE)  # Set the cursor to invisible.
        self._screen.timeout(0)  # No blocking for `screen.getch()`.

        curses.init_pair(
            COLOR_PAIR_HEAD,
            VALID_COLORS[head_color],
            VALID_COLORS[back_color],
        )
        curses.init_pair(
            COLOR_PAIR_TAIL,
            VALID_COLORS[tail_color],
            VALID_COLORS[back_color],
        )

    def refresh(self: Self) -> None:
        self._screen.refresh()

    def clear(self: Self) -> None:
        self._screen.clear()

    def erase(self: Self) -> None:
        self._screen.erase()

    def addstr(self: Self, y_coord: int, x_coord: int, s: str, attr: int) -> None:
        self._screen.addstr(y_coord, x_coord, s, attr)

    def at_lower_right_corner(self: Self, line: int, col: int) -> bool:
        """
        `True` if position is at the bottom right corner of screen; otherwise `False`.
        """
        return (line, col) == (self._height - 1, self._width - 1)
