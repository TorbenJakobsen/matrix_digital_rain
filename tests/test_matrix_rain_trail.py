import pytest

from matrix_rain_trail import MatrixRainTrail

SCREEN_COLUMNS: int = 40
SCREEN_LINES: int = 24
COLUMN_NUMBER: int = 17

"""
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


def test_mrt_instantiate_colno_none_fails() -> None:
    with pytest.raises(Exception):
        _: MatrixRainTrail = MatrixRainTrail(None, SCREEN_COLUMNS, SCREEN_LINES)


def test_mrt_instantiate_cols_none_fails() -> None:
    with pytest.raises(Exception):
        _: MatrixRainTrail = MatrixRainTrail(COLUMN_NUMBER, None, SCREEN_LINES)


def test_mrt_instantiate_lines_none_fails() -> None:
    with pytest.raises(Exception):
        _: MatrixRainTrail = MatrixRainTrail(COLUMN_NUMBER, SCREEN_COLUMNS, None)


@pytest.mark.repeat(3)
def test_mrt_instantiate() -> None:
    # GIVEN
    sut: MatrixRainTrail = MatrixRainTrail(COLUMN_NUMBER, SCREEN_COLUMNS, SCREEN_LINES)
    # THEN
    assert sut.column_number == COLUMN_NUMBER
    assert sut.length() == len(sut)
    assert sut.MIN_LENGTH <= sut.length() <= sut.MAX_LENGTH

    assert sut.head_start() == -1
    assert sut.is_head_visible() is False

    assert sut.body_start() == sut.head_start() - 1
    assert sut.tail_start() == sut.head_start() - (sut.length() - 1)

    assert sut.is_tail_visible() is False


@pytest.mark.parametrize(
    "lines_to_move,head_visible,tail_visible",
    [
        pytest.param(0, False, False),  # Don't move - not visible
        pytest.param(1, True, False),  # Only head is visible
        pytest.param(SCREEN_LINES - 1, True, True),
        pytest.param(SCREEN_LINES, True, True),  # Moves to very last line
        pytest.param(SCREEN_LINES + 1, False, True),  # Only head is not visible
        pytest.param(SCREEN_LINES * 2, False, False),
    ],
)
def test_mrt_move_head(
    lines_to_move: int,
    head_visible: bool,
    tail_visible: bool,
) -> None:
    # GIVEN
    sut: MatrixRainTrail = MatrixRainTrail(COLUMN_NUMBER, SCREEN_COLUMNS, SCREEN_LINES)
    # Beware that length changes

    # WHEN
    for _ in range(lines_to_move):
        sut.move_forward()

    # THEN
    assert sut.head_start() == lines_to_move - 1
    assert sut.is_head_visible() is head_visible
    assert sut.is_tail_visible() is tail_visible

    assert sut.body_start() == sut.head_start() - 1
    assert sut.tail_start() == sut.head_start() - (sut.length() - 1)


@pytest.mark.repeat(3)
def test_mrt_move_tail() -> None:
    # GIVEN
    sut: MatrixRainTrail = MatrixRainTrail(COLUMN_NUMBER, SCREEN_COLUMNS, SCREEN_LINES)
    # Beware that length changes

    # WHEN
    for _ in range(SCREEN_LINES):
        sut.move_forward()

    # THEN
    assert sut.is_head_visible() is True
    assert sut.is_tail_visible() is True
    assert sut.is_visible() is True
    assert sut.is_exhausted() is False

    """
    109876543210
        ++++++++    lines=8
        HBBBBBT     length=7
        ^^    ^     offset
        ||    +---- 3      TAIL :: HEAD - (LENGTH-1)
        |+--------- 8      BODY :: HEAD - 1
        +---------- 9      HEAD :: HEAD
    """

    # Move head beyond
    sut.move_forward()

    """
    109876543210
        ++++++++    lines=8
       HBBBBBT      length=7
       ^^    ^     offset
       ||    +---- 4      TAIL :: HEAD - (LENGTH-1)
       |+--------- 9      BODY :: HEAD - 1
       +---------- 10     HEAD :: HEAD
    """

    assert sut.is_head_visible() is False
    assert sut.is_tail_visible() is True
    assert sut.is_visible() is True
    assert sut.is_exhausted() is False

    for _ in range(sut.length() - 1 - 1):
        sut.move_forward()
        assert sut.is_head_visible() is False
        assert sut.is_tail_visible() is True
        assert sut.is_visible() is True
        assert sut.is_exhausted() is False

    """
    5432109876543210
            ++++++++    lines=8
      HBBBBBT           length=7
      ^^    ^     offset
      ||    +---- 7      TAIL :: HEAD - (LENGTH-1)
      |+--------- 12     BODY :: HEAD - 1
      +---------- 13     HEAD :: HEAD
    """

    sut.move_forward()

    """
    5432109876543210
            ++++++++    lines=8
     HBBBBBT           length=7
     ^^    ^     offset
     ||    +---- 8      TAIL :: HEAD - (LENGTH-1)
     |+--------- 13     BODY :: HEAD - 1
     +---------- 14     HEAD :: HEAD
    """

    assert sut.is_head_visible() is False
    assert sut.is_tail_visible() is False
    assert sut.is_visible() is False
    assert sut.is_exhausted() is True
