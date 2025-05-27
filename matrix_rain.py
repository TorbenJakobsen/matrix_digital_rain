import argparse
import curses
from collections.abc import Sequence
from typing import Optional

import _curses  # to be able to catch the proper exception

from matrix_rain_characters import MatrixRainCharacters
from matrix_rain_trail import MatrixRainTrail
from matrix_rain_trails import MatrixRainTrails
from matrix_screen import (
    BLANK,
    COLOR_PAIR_HEAD,
    COLOR_PAIR_TAIL,
    VALID_COLORS,
    Action,
    MatrixScreen,
)
from matrix_sleep_timer import MatrixSleepTimer

sleep_timer: MatrixSleepTimer = MatrixSleepTimer(0.1, 1.6)
"""Determines sleep interval to regulate rain trail descent on screen."""


class MatrixRainException(Exception):
    pass


def head_at_lower_right_corner(scr: MatrixScreen, trail: MatrixRainTrail) -> bool:
    """
    `True` if position is at the bottom right corner of screen; otherwise `False`.

    If `curses` add a char at bottom right corner the cursor will be moved outside the screen and raise an error.
    """
    return scr.at_lower_right_corner(trail.head_start(), trail.column_number)


def tail_at_lower_right_corner(scr: MatrixScreen, trail: MatrixRainTrail) -> bool:
    """
    `True` if position is at the bottom right corner of screen; otherwise `False`.

    If `curses` add a char at bottom right corner the cursor will be moved outside the screen and raise an error.
    """
    return scr.at_lower_right_corner(trail.tail_start(), trail.column_number)


def setup_screen(
    screen: curses.window,
    args: argparse.Namespace,
) -> MatrixScreen:
    mscreen: MatrixScreen = MatrixScreen(screen)
    # Read from parsed arguments
    args_color: str = str(args.color)  # tail color
    args_background: str = str(args.background)
    args_head_color: str = str(args.head_color)
    mscreen.setup_screen(args_head_color, args_color, args_background)
    return mscreen


def process_trail(
    mscreen: MatrixScreen,
    matrix_rain_trails: MatrixRainTrails,
    active_trail: MatrixRainTrail,
) -> None:

    char_itr: MatrixRainCharacters = MatrixRainCharacters()

    #
    # Head becomes tail ()
    #

    if not head_at_lower_right_corner(mscreen, active_trail):
        if active_trail.is_head_visible():
            mscreen.addstr(
                active_trail.head_start(),
                active_trail.column_number,
                next(char_itr),
                curses.color_pair(COLOR_PAIR_TAIL),
            )

    #
    # Tail becomes 'blank'
    #

    if not tail_at_lower_right_corner(mscreen, active_trail):
        if active_trail.is_tail_visible():
            mscreen.addstr(
                active_trail.tail_start(),
                active_trail.column_number,
                BLANK,
                curses.color_pair(COLOR_PAIR_TAIL),
            )

    #
    # move forward
    #

    active_trail.move_forward()

    if active_trail.is_exhausted():
        # Flag as exhausted for later processing when leaving loop
        matrix_rain_trails.exhaust(active_trail)
        return

    #
    # New head
    #

    if not head_at_lower_right_corner(mscreen, active_trail):
        if active_trail.is_head_visible():
            mscreen.addstr(
                active_trail.head_start(),
                active_trail.column_number,
                next(char_itr),
                curses.color_pair(COLOR_PAIR_HEAD),
            )


def process_trails(
    mscreen: MatrixScreen,
    matrix_rain_trails: MatrixRainTrails,
) -> None:
    for active_trail in matrix_rain_trails.active_trails:
        try:
            process_trail(mscreen, matrix_rain_trails, active_trail)
            # Some trails can have been moved off screen and are marked as exhausted
        except _curses.error as e:
            msg: str = (
                f"[[H:{mscreen.height},W:{mscreen.width}] Y:{active_trail.head_start()} X:{active_trail.column_number} "
            )
            raise ValueError(msg) from e
    # If any trails were marked as exhausted by `process_trail` put them back as available
    matrix_rain_trails.replenish_exhausted()


def main_loop(
    screen: curses.window,
    args: argparse.Namespace,
) -> None:
    """Actual code is run here.

    Call is initiated by the curses wrapper setup in `main()`.
    """

    mscreen: MatrixScreen = setup_screen(screen, args)

    # ---

    matrix_rain_trails = MatrixRainTrails(mscreen.width, mscreen.height)

    TO_ACTIVATE = 2
    MIN_AVAILABLE_COLUMNS = 0  # Leave columns possibly without trails?

    while True:

        #
        # Handle screen resize
        #

        screen_is_resized: bool = mscreen.validate_screen_size()
        if screen_is_resized:
            matrix_rain_trails = MatrixRainTrails(mscreen.width, mscreen.height)
            mscreen.clear()
            mscreen.refresh()
            # -> continue infinite loop from loop start
            continue

        #
        # Activate trails if any are available; bare the minimum
        #

        matrix_rain_trails.activate_if_available(TO_ACTIVATE, MIN_AVAILABLE_COLUMNS)

        #
        # Process trails
        #

        process_trails(mscreen, matrix_rain_trails)

        #
        # Refresh screen and sleep for some time to make it humanly possible to see the screen output
        #

        mscreen.refresh()
        sleep_timer.sleep()

        #
        # Handle keypresses (if any) and terminates loop if needed.
        # This logic needs to be at end of loop as it intentionally can break out of loop
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

    mscreen.erase()
    mscreen.refresh()


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
