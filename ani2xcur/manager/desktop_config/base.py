"""桌面环境配置"""

from typing import NamedTuple


class IntRange(NamedTuple):
    """整数范围"""

    min: int
    """最小值"""

    max: int
    """最大值"""


WINDOWS_CURSOR_SIZE_RANGE = IntRange(1, 48)
"""Windows 鼠标指针大小有效值范围"""

LINUX_CURSOR_SIZE_RANGE = IntRange(16, 96)
"""Windows 鼠标指针大小有效值范围"""


def check_windows_cursor_size_value(
    value: int,
) -> int:
    """检查设置的 Windows 鼠标指针大小是否符合范围

    Args:
        value (int): 鼠标指针大小
    Raises:
        TypeError: 鼠标指针大小不是 int 时
        ValueError: 鼠标指针大小超过有效范围时
    """
    rng = WINDOWS_CURSOR_SIZE_RANGE
    if not isinstance(value, int):
        raise TypeError(f"Windows 鼠标指针大小值应为 int 类型, 但得到 {type(value).__name__} 类型")
    if rng.min <= value <= rng.max:
        return value
    raise ValueError(f"Windows 鼠标指针大小的值 {value} 超过有效范围 [{rng.min}, {rng.max}]")


def check_linux_cursor_size_value(
    value: int,
) -> int:
    """检查设置的 Linux 鼠标指针大小是否符合范围

    Args:
        value (int): 鼠标指针大小
    Raises:
        TypeError: 鼠标指针大小不是 int 时
        ValueError: 鼠标指针大小超过有效范围时
    """
    rng = LINUX_CURSOR_SIZE_RANGE
    if not isinstance(value, int):
        raise TypeError(f"Linux 鼠标指针大小值应为 int 类型, 但得到 {type(value).__name__} 类型")
    if rng.min <= value <= rng.max:
        return value
    raise ValueError(f"Linux 鼠标指针大小的值 {value} 超过有效范围 [{rng.min}, {rng.max}]")
