"""Mate 桌面环境配置工具"""

import shutil

from ani2xcur.cmd import run_cmd
from ani2xcur.utils import safe_convert_to_int


def get_mate_cursor_theme() -> str | None:
    """获取 Mate 桌面当前使用的鼠标指针配置名称

    Returns:
        (str | None): 当前使用的鼠标指针名称
    """
    if not shutil.which("gsettings"):
        return None

    result = run_cmd(
        ["gsettings", "get", "org.mate.peripherals-mouse", "cursor-theme"],
        live=False,
        check=False,
    )

    if isinstance(result, str):
        result = result.strip()

    if result == "":
        result = None

    return result


def get_mate_cursor_size() -> int | None:
    """获取 Mate 桌面当前使用的鼠标指针大小

    Returns:
        (int | None): 当前使用的鼠标指针大小
    """
    if not shutil.which("gsettings"):
        return None

    result = run_cmd(
        ["gsettings", "get", "org.mate.peripherals-mouse", "cursor-size"],
        live=False,
        check=False,
    )
    if isinstance(result, str):
        result = result.strip()

    if result == "":
        result = None

    return safe_convert_to_int(result)


def set_mate_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 Mate 桌面当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    """
    if not shutil.which("gsettings"):
        return

    run_cmd(
        ["gsettings", "set", "org.mate.peripherals-mouse", "cursor-theme", cursor_name],
        live=False,
        check=False,
    )


def set_mate_cursor_size(
    cursor_size: int,
) -> None:
    """设置 Mate 桌面当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    """
    if not shutil.which("gsettings"):
        return

    run_cmd(
        ["gsettings", "get", "org.mate.peripherals-mouse", "cursor-size", str(cursor_size)],
        live=False,
        check=False,
    )
