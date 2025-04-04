import curses
import random
import time


def rand_cordinates():
    y = random.randint(0, curses.LINES - 1)
    x = random.randint(0, curses.COLS - 1)
    return y, x


def main_loop(
    screen: curses.window,
) -> None:

    #
    # Set up curses and terminal window
    #

    curses.curs_set(0)  # Set the cursor to invisible.
    screen.timeout(0)  # No blocking for `screen.getch()`.

    curses.init_pair(
        9,
        curses.COLOR_BLUE,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        10,
        curses.COLOR_RED,
        curses.COLOR_BLACK,
    )
    screen.bkgd(" ", curses.color_pair(9))

    while True:

        y, x = rand_cordinates()

        screen.addstr(
            y,
            x,
            "X",
            curses.color_pair(9),
        )

        screen.refresh()
        time.sleep(1.0)

        screen.addstr(
            y,
            x,
            " ",
            curses.color_pair(10),
        )

        screen.refresh()
        time.sleep(1.0)


def main() -> None:

    try:
        # Sets up curses including 8 default color pairs
        curses.wrapper(main_loop)
    except KeyboardInterrupt:
        # Ignore ctrl-C
        pass
    except Exception as e:
        print(e)
        return


if __name__ == "__main__":
    main()
