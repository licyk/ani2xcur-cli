"""X.Org 环境配置工具"""

import re
from pathlib import Path

from ani2xcur.utils import safe_convert_to_int

X_RESOURCES_PATH = Path("~/.Xresources").expanduser()
"""X resources 配置文件路径"""


def read_x_resources_config(
    config_path: Path,
) -> dict[str, str]:
    """读取 X resources 配置文件并返回配置字典

    Args:
        config_path (Path): X resources 配置文件路径
    Returns:
        (dict[str, str]): X resources 配置字典
    """
    config = {}

    with open(config_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            # 跳过注释行和空行
            if line.startswith("#") or not line:
                continue

            # 匹配格式: key: value
            match = re.match(r"^([^:]+):\s*(.*)$", line)
            if match:
                key, value = match.groups()
                key = key.strip()
                value = value.strip()

                config[key] = value

    return config


def write_x_resources_config(
    config_path: Path,
    updates: dict[str, str],
) -> None:
    """修改 X resources 配置文件

    Args:
        config_path (Path): 配置文件路径
        updates (dict[str, str]): 要更新的内容字典
    """
    lines = []
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    new_lines = []
    found_keys = set()

    # 遍历现有行进行更新
    for line in lines:
        stripped = line.strip()
        # Xresources 注释通常以 '!' 开头，但也兼容 '#'
        if not stripped or stripped.startswith("!") or stripped.startswith("#"):
            new_lines.append(line)
            continue

        match = re.match(r"^([^:]+):", stripped)
        if match:
            key = match.group(1).strip()
            if key in updates:
                new_lines.append(f"{key}: {updates[key]}\n")
                found_keys.add(key)
                continue

        new_lines.append(line)

    # 追加新配置项
    for key, val in updates.items():
        if key not in found_keys:
            new_lines.append(f"{key}: {val}\n")

    with open(config_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def get_x_resources_cursor_theme() -> str | None:
    """获取 X11 标准方案的当前使用的鼠标指针配置名称

    Returns:
        (str | None): 当前使用的鼠标指针名称
    """
    if not X_RESOURCES_PATH.is_file():
        return None

    config = read_x_resources_config(X_RESOURCES_PATH)
    return config.get("Xcursor.theme")


def get_x_resources_cursor_size() -> int | None:
    """获取 X11 标准方案的当前使用的鼠标指针大小

    Returns:
        (int | None): 当前使用的鼠标指针大小
    """
    if not X_RESOURCES_PATH.is_file():
        return None

    config = read_x_resources_config(X_RESOURCES_PATH)
    return safe_convert_to_int(config.get("Xcursor.size"))


def set_x_resources_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 X11 标准方案的当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    """
    X_RESOURCES_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_x_resources_config(config_path=X_RESOURCES_PATH, updates={"Xcursor.theme": cursor_name})


def set_x_resources_cursor_size(
    cursor_size: int,
) -> None:
    """设置 X11 标准方案的当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    """
    X_RESOURCES_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_x_resources_config(config_path=X_RESOURCES_PATH, updates={"Xcursor.size": str(cursor_size)})
