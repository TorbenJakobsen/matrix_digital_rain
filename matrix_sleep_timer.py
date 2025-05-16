import time
from typing import Self


class MatrixSleepTimer:

    def __init__(
        self: Self,
        sleep_sec: float = 0.1,  # 100 msec
        change_factor: float = 1.6,
    ):

        if not sleep_sec or float(sleep_sec) < 0:
            raise ValueError("Sleep value must be 0 or positive")

        if not change_factor or float(change_factor) <= 0:
            raise ValueError("Change factor must be positive")

        self.sleep_sec = sleep_sec
        self.change_factor = change_factor

    def increment_sleep(
        self: Self,
    ) -> None:
        """Increase sleep time by the factor (multiplication) used when initializing this instance."""
        self.sleep_sec *= self.change_factor

    def decrement_sleep(
        self: Self,
    ) -> None:
        """Decrease sleep time by the factor (division) used when initializing this instance."""
        self.sleep_sec /= self.change_factor

    def sleep(self: Self) -> None:
        time.sleep(self.sleep_sec)
