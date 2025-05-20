import argparse
import curses
import random
from collections.abc import Sequence
from typing import Optional

import _curses  # to be able to catch the proper exception

from matrix_rain_characters import MatrixRainCharacters
from matrix_rain_trail import MatrixRainTrail
from matrix_screen import Action, MatrixScreen
from matrix_sleep_timer import MatrixSleepTimer

# Colors are numbered, and start_color() initializes 8 basic colors when it activates color mode.
# Color pair 0 is hard-wired to white on black, and cannot be changed.
# Coordinates are always passed in the order y,x, and the top-left corner of a window is coordinate (0,0)
# Writing lower right corner...
# https://docs.python.org/3/howto/curses.html


# Initial ("invalid" as too small) values -> will force a size recalculation later
screen_max_x: int = 1  # columns
screen_max_y: int = 1  # lines


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

sleep_timer: MatrixSleepTimer = MatrixSleepTimer(0.1, 1.6)
"""Determines sleep interval to regulate rain trail descent on screen."""


class MatrixRainException(Exception):
    pass


def at_lower_right_corner(line, col) -> bool:
    """
    `True` if position is at the bottom right corner of screen; otherwise `False`.
    """
    return (line, col) == (screen_max_y - 1, screen_max_x - 1)


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
    """Sets up curses screen (window) using arguments and defaults."""

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


def pop_random_from_list(available: list[int]) -> int:
    """
    Chooses a random index, remove value from list and returns chosen value

    e.g. `[0,1,2,3,4]` -> `[0,1,2,4]` and returns `3`
    """
    if not available or len(available) == 0:
        raise ValueError("argument list has no elements to pop")

    chosen: int = available.pop(random.randrange(len(available)))
    return chosen


def main_loop(
    screen: curses.window,
    args: argparse.Namespace,
) -> None:
    """Actual code is run here.

    Call is initiated by the curses setup in `main()`.
    """
    global screen_max_y
    global screen_max_x

    mscreen = MatrixScreen(screen)

    #
    # Read from parsed arguments
    #

    setup_screen(screen, args)

    # ---

    char_itr: MatrixRainCharacters = MatrixRainCharacters()

    active_trails_list: list[MatrixRainTrail] = []

    available_column_numbers: list[int] = []

    exhausted_trails_list: list[MatrixRainTrail] = []

    TO_ACTIVATE = 2
    MIN_AVAILABLE_COLUMNS = 0  # Leave some columns without trails

    while True:

        #
        # Handle screen resize
        #

        screen_is_resized = mscreen.validate_screen_size()

        if screen_is_resized:
            screen_max_y = mscreen.height
            screen_max_x = mscreen.width

            # Free up all the columns - no activated columns
            available_column_numbers = list(range(mscreen.width))
            active_trails_list.clear()

            screen.clear()
            screen.refresh()
            # -> continue loop from start
            continue

        #
        # If available columns are not all used -> create new trails
        #

        for _ in range(TO_ACTIVATE):
            # Keep minimum available columns also after activation
            if len(available_column_numbers) <= MIN_AVAILABLE_COLUMNS:
                break

            chosen_column_number: int = pop_random_from_list(available_column_numbers)

            # activate trail by chosen number
            active_trails_list.append(
                MatrixRainTrail(
                    chosen_column_number,
                    screen_max_x,
                    screen_max_y,
                )
            )

        # ---

        exhausted_trails_list.clear()

        for active_trail in active_trails_list:

            # Modify the head and the tail (ignore body between)
            try:
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
            except _curses.error as e:
                msg: str = (
                    f"[L:{curses.LINES},C:{curses.COLS}] [MY:{screen_max_y},MX:{screen_max_x}] Y:{active_trail.head_start()} X:{active_trail.column_number} "
                )
                raise ValueError(msg) from e

        # ---

        screen.refresh()
        sleep_timer.sleep()

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

        action = mscreen.handle_key_presses()
        if action is Action.KEY_UP:
            sleep_timer.decrement_sleep()
            continue
        if action is Action.KEY_DOWN:
            # increase sleep delay
            sleep_timer.increment_sleep()
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
    lower_color: str = color.lower()
    if lower_color in VALID_COLORS.keys():
        return lower_color
    raise argparse.ArgumentTypeError(f"'{color}' is not a valid color name")


def argument_parsing(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
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
    args: argparse.Namespace = argument_parsing(argv)

    try:
        # Sets up curses including 8 default color pairs
        # then runs main loop with curses
        curses.wrapper(main_loop, args)
    except KeyboardInterrupt:
        # Ignore ctrl-C
        pass
    except MatrixRainException as e:
        print(e)
        return


if __name__ == "__main__":
    main()
