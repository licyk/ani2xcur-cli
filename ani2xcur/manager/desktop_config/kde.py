"""KDE 桌面环境配置工具"""

import shutil

from ani2xcur.cmd import run_cmd
from ani2xcur.utils import safe_convert_to_int


def get_kde_cursor_theme() -> str | None:
    """获取 KDE 桌面当前使用的鼠标指针配置名称

    Returns:
        (str | None): 当前使用的鼠标指针名称
    """
    if shutil.which("kreadconfig5"):
        executable = "kreadconfig5"
    elif shutil.which("kreadconfig6"):
        executable = "kreadconfig6"
    else:
        return None

    result = run_cmd(
        [
            executable,
            "--file",
            "kcminputrc",
            "--group",
            "Mouse",
            "--key",
            "cursorTheme",
        ],
        live=False,
        check=False,
    )

    if isinstance(result, str):
        result = result.strip()

    if result == "":
        result = None

    return result


def get_kde_cursor_size() -> int | None:
    """获取 KDE 桌面当前使用的鼠标指针大小

    Returns:
        (int | None): 当前使用的鼠标指针大小
    """
    if shutil.which("kreadconfig5"):
        executable = "kreadconfig5"
    elif shutil.which("kreadconfig6"):
        executable = "kreadconfig6"
    else:
        return None

    result = run_cmd(
        [
            executable,
            "--file",
            "kcminputrc",
            "--group",
            "Mouse",
            "--key",
            "cursorSize",
        ],
        live=False,
        check=False,
    )

    if isinstance(result, str):
        result = result.strip()

    if result == "":
        result = None

    return safe_convert_to_int(result)


def set_kde_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 KDE 桌面当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    """
    if shutil.which("kwriteconfig5"):
        executable = "kwriteconfig5"
    elif shutil.which("kwriteconfig6"):
        executable = "kwriteconfig6"
    else:
        return

    run_cmd(
        [executable, "--file", "kcminputrc", "--group", "Mouse", "--key", "cursorTheme", cursor_name],
        live=False,
        check=False,
    )


def set_kde_cursor_size(
    cursor_size: int,
) -> None:
    """设置 KDE 桌面当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    """
    if shutil.which("kwriteconfig5"):
        executable = "kwriteconfig5"
    elif shutil.which("kwriteconfig6"):
        executable = "kwriteconfig6"
    else:
        return

    run_cmd(
        [executable, "--file", "kcminputrc", "--group", "Mouse", "--key", "cursorSize", str(cursor_size)],
        live=False,
        check=False,
    )
