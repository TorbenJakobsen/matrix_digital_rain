import argparse
import curses
import random
import time
from collections.abc import Sequence
from enum import Enum
from typing import Optional

from matrix_rain_characters import MatrixRainCharacters
from matrix_rain_trail import MatrixRainTrail

# Colors are numbered, and start_color() initializes 8 basic colors when it activates color mode.
# Color pair 0 is hard-wired to white on black, and cannot be changed.
# Coordinates are always passed in the order y,x, and the top-left corner of a window is coordinate (0,0)
# Writing lower right corner...
# https://docs.python.org/3/howto/curses.html


COLOR_PAIR_HEAD: int = 10
COLOR_PAIR_TAIL: int = 9

BLANK: str = " "

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


MIN_SCREEN_SIZE_Y = 8
MIN_SCREEN_SIZE_X = 8

DELAY_SPEED_SEC: float = 0.1
"""Determines sleep interval in seconds to regulate rain trail descent on screen."""


class MatrixRainException(Exception):
    pass


def at_lower_right_corner(line, col) -> bool:
    return (line, col) == (curses.LINES - 1, curses.COLS - 1)


def head_at_lower_right_corner(trail: MatrixRainTrail) -> bool:
    """
    `True` if position is at the bottom right corner of screen; otherwise `False`.

    If `curses` add a char at bottom right corner the cursor will be moved outside the screen and raise an error.
    """
    return at_lower_right_corner(trail.head_start(), trail.column_number)


def tail_at_lower_right_corner(trail: MatrixRainTrail) -> bool:
    """
    `True` if position is at the bottom right corner of screen; otherwise `False`.

    If `curses` add a char at bottom right corner the cursor will be moved outside the screen and raise an error.
    """
    return at_lower_right_corner(trail.tail_start(), trail.column_number)


def setup_screen(
    screen: curses.window,
    args: argparse.Namespace,
) -> None:

    args_color: str = str(args.color)  # tail color
    args_background: str = str(args.background)
    args_head_color: str = str(args.head_color)

    #
    # Set up curses and terminal window
    #

    INVISIBLE = 0
    curses.curs_set(INVISIBLE)  # Set the cursor to invisible.
    screen.timeout(0)  # No blocking for `screen.getch()`.

    curses.init_pair(
        COLOR_PAIR_HEAD,
        VALID_COLORS[args_head_color],
        VALID_COLORS[args_background],
    )
    curses.init_pair(
        COLOR_PAIR_TAIL,
        VALID_COLORS[args_color],
        VALID_COLORS[args_background],
    )


class Action(Enum):
    NONE = 0
    CONTINUE = 1
    BREAK = 2
    KEY_UP = 3
    KEY_DOWN = 4


def handle_key_presses(screen: curses.window) -> Action:

    Q_CHAR_SET: set[int] = {ord("q"), ord("Q")}
    F_CHAR_SET: set[int] = {ord("f"), ord("F")}

    ch: int = screen.getch()
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
            ch = screen.getch()
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


def pop_random_from_list(available: list[int]) -> int:
    """
    Chooses a random index, remove value from list and returns chosen value

    e.g. [0,1,2,3,4] -> [0,1,2,4] and returns 3
    """
    chosen: int = available.pop(random.randrange(len(available)))
    return chosen


def main_loop(
    screen: curses.window,
    args: argparse.Namespace,
) -> None:

    #
    # Read from parsed arguments
    #

    setup_screen(screen, args)

    # ---

    delay_speed_sec: float = DELAY_SPEED_SEC

    char_itr: MatrixRainCharacters = MatrixRainCharacters()

    active_trails_list: list[MatrixRainTrail] = []

    # Initial ("invalid" as too small) values -> will force a size recalculation later
    screen_max_x: int = 1  # columns
    screen_max_y: int = 1  # lines

    available_column_numbers: list[int] = []

    exhausted_trails_list: list[MatrixRainTrail] = []

    while True:

        #
        # Handle screen resize
        #

        if curses.is_term_resized(screen_max_y, screen_max_x):
            screen_max_y, screen_max_x = screen.getmaxyx()
            if screen_max_y < MIN_SCREEN_SIZE_Y:
                raise MatrixRainException("Error: screen height is too short.")
            if screen_max_x < MIN_SCREEN_SIZE_X:
                raise MatrixRainException("Error: screen width is too narrow.")

            # Free up all the columns - no activated columns
            available_column_numbers = list(range(screen_max_x))
            active_trails_list.clear()

            screen.clear()
            screen.refresh()
            # -> continue loop from start
            continue

        #
        # If available columns are not all used -> create new trails
        #

        TO_ACTIVATE = 2
        MIN_AVAILABLE_COLUMNS = 0  # Leave some columns without trails

        for _ in range(TO_ACTIVATE):
            # Keep minimum available columns also after activation
            if len(available_column_numbers) <= MIN_AVAILABLE_COLUMNS:
                break

            chosen_column_number: int = pop_random_from_list(available_column_numbers)

            # activate trail by chosen number
            active_trails_list.append(
                MatrixRainTrail(chosen_column_number, screen_max_x, screen_max_y)
            )

        # ---

        exhausted_trails_list.clear()

        for active_trail in active_trails_list:

            # Modify the head and the tail (ignore body between)

            if not head_at_lower_right_corner(active_trail):
                if active_trail.is_head_visible():
                    screen.addstr(
                        active_trail.head_start(),
                        active_trail.column_number,
                        next(char_itr),
                        curses.color_pair(COLOR_PAIR_TAIL),
                    )

            if not tail_at_lower_right_corner(active_trail):
                if active_trail.is_tail_visible():
                    screen.addstr(
                        active_trail.tail_start(),
                        active_trail.column_number,
                        BLANK,
                        curses.color_pair(COLOR_PAIR_TAIL),
                    )

            active_trail.move_forward()

            if active_trail.is_exhausted():
                # Flag as exhausted for later processing when leaving loop
                # Just removing from `active_trails_list` messes up loop
                exhausted_trails_list.append(active_trail)
                continue

            if not head_at_lower_right_corner(active_trail):
                if active_trail.is_head_visible():
                    screen.addstr(
                        active_trail.head_start(),
                        active_trail.column_number,
                        next(char_itr),
                        curses.color_pair(COLOR_PAIR_HEAD),
                    )

        # ---

        screen.refresh()
        time.sleep(delay_speed_sec)

        #
        # Remove exhausted from active trails and make column available
        #

        for exhausted_trail in exhausted_trails_list:
            active_trails_list.pop(active_trails_list.index(exhausted_trail))
            available_column_numbers.append(exhausted_trail.column_number)

        exhausted_trails_list.clear()

        #
        # Handle keypresses (if any) and terminates loop if needed.
        # This logic needs to be at end of loop as it intentionally break out of loop
        #

        action = handle_key_presses(screen)
        if action is Action.KEY_UP:
            # decrease sleep delay
            delay_speed_sec = delay_speed_sec / 1.6
            continue
        if action is Action.KEY_DOWN:
            # increase sleep delay
            delay_speed_sec = delay_speed_sec * 1.6
            continue
        if action is Action.BREAK:
            break

        #
        # END OF LOOP
        #

    #
    # Exited loop -> clean up
    #

    screen.erase()
    screen.refresh()


#
# Parse and validate arguments
#


def validate_color(color: str) -> str:
    lower_color = color.lower()
    if lower_color in VALID_COLORS.keys():
        return lower_color
    raise argparse.ArgumentTypeError(f"'{color}' is not a valid color name")


def argument_parsing(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "-C",
        dest="color",
        type=validate_color,
        default="green",
        help="Set trail color.  Default is green",
    )
    # '-h' is used for help
    parser.add_argument(
        "-H",
        dest="head_color",
        type=validate_color,
        default="white",
        help="Set the head character color.  Default is white",
    )
    parser.add_argument(
        "-b",
        "-B",
        dest="background",
        type=validate_color,
        default="black",
        help="set background color. Default is black.",
    )
    return parser.parse_args(argv)


#
# MAIN
#


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = argument_parsing(argv)

    try:
        # Sets up curses including 8 default color pairs
        curses.wrapper(main_loop, args)
    except KeyboardInterrupt:
        # Ignore ctrl-C
        pass
    except MatrixRainException as e:
        print(e)
        return


if __name__ == "__main__":
    main()
