"""LXQT 桌面环境配置工具"""

import configparser
from pathlib import Path

LXQT_CONFIG_PATH = Path("~/.config/lxqt/session.conf").expanduser()
"""LXQT 桌面的配置文件路径"""


def get_lxqt_cursor_theme() -> str | None:
    """获取 LXQT 桌面当前使用的鼠标指针配置名称

    Returns:
        (str | None): 当前使用的鼠标指针名称
    """
    config = configparser.ConfigParser()
    config.read(LXQT_CONFIG_PATH)
    if "General" in config and "cursor_theme" in config["General"]:
        return config.get("General", "cursor_theme")
    return None


def get_lxqt_cursor_size() -> int | None:
    """获取 LXQT 桌面当前使用的鼠标指针大小

    Returns:
        (int | None): 当前使用的鼠标指针大小
    """
    config = configparser.ConfigParser()
    config.read(LXQT_CONFIG_PATH)
    if "General" in config and "cursor_size" in config["General"]:
        return int(config.get("General", "cursor_size"))
    return None


def set_lxqt_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 LXQT 桌面当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    """
    LXQT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    config.read(LXQT_CONFIG_PATH)
    if "General" not in config:
        config["General"] = {}

    config["General"]["cursor_theme"] = cursor_name
    with open(LXQT_CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f, space_around_delimiters=False)


def set_lxqt_cursor_size(
    cursor_size: int,
) -> None:
    """设置 LXQT 桌面当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    """
    LXQT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    config.read(LXQT_CONFIG_PATH)
    if "General" not in config:
        config["General"] = {}

    config["General"]["cursor_size"] = str(cursor_size)
    with open(LXQT_CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f, space_around_delimiters=False)
