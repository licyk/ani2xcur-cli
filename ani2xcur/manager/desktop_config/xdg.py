"""XDG 环境配置工具"""

import configparser
from pathlib import Path

XDG_CONFIG_PATH = Path("~/.icons/default/index.theme").expanduser()
"""XDG 配置文件路径"""

XDG_CONFIG_SHARE_PATH = Path("~/.local/share/icons/default/index.theme").expanduser()
"""XDG 配置文件路径 (共享路径)"""


def get_xdg_cursor_theme() -> tuple[str, str] | None:
    """获取 XDG 标准方案的当前使用的鼠标指针配置名称

    Returns:
        (tuple[str, str] | None): 当前使用的鼠标指针名称
    """
    config = configparser.ConfigParser()
    config_share = configparser.ConfigParser()
    config.read(XDG_CONFIG_PATH)
    config_share.read(XDG_CONFIG_SHARE_PATH)
    cursor_name = config.get("Icon Theme", "Inherits") if "Icon Theme" in config and "Inherits" in config["Icon Theme"] else None
    cursor_name_share = config_share.get("Icon Theme", "Inherits") if "Icon Theme" in config_share and "Inherits" in config_share["Icon Theme"] else None
    return (cursor_name, cursor_name_share)


def set_xdg_cursor_theme(cursor_name: str) -> None:
    """设置 XDG 标准方案的当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    """
    XDG_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    XDG_CONFIG_SHARE_PATH.parent.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    config_share = configparser.ConfigParser()
    config.read(XDG_CONFIG_PATH)
    config_share.read(XDG_CONFIG_SHARE_PATH)
    if "Icon Theme" not in config:
        config["Icon Theme"] = {}

    if "Icon Theme" not in config_share:
        config_share["Icon Theme"] = {}

    config["Icon Theme"]["Inherits"] = cursor_name
    config_share["Icon Theme"]["Inherits"] = cursor_name

    with open(XDG_CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f, space_around_delimiters=False)

    with open(XDG_CONFIG_SHARE_PATH, "w", encoding="utf-8") as f:
        config_share.write(f, space_around_delimiters=False)
