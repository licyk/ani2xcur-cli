"""Windows 桌面环境配置工具"""

import ctypes
import os
import re
from pathlib import Path
from typing import Literal

try:
    import win32gui
    import win32con
    import win32com.client
except ImportError:
    win32gui = NotImplemented
    win32con = NotImplemented
    win32com = NotImplemented  # pylint: disable=invalid-name

from ani2xcur.manager.regedit import (
    registry_query_value,
    registry_set_value,
    registry_enum_values,
    RegistryAccess,
    RegistryRootKey,
    RegistryValueType,
)
from ani2xcur.utils import (
    extend_list_to_length,
    lowercase_dict_keys,
)
from ani2xcur.manager.base import CURSOR_KEYS

WINDOWS_CURSOR_CURSORS_PATH = r"Control Panel\Cursors"
"""Windows 鼠标指针配置路径"""

WINDOWS_CURSOR_CURSORS_SCHEME_PATH = r"Control Panel\Cursors\Schemes"
"""Windows 鼠标指针方案路径"""

WINDOWS_ACCESSIBILITY_PATH = r"Software\Microsoft\Accessibility"
"""Windows 无障碍配置路径"""


def has_var_string(
    text: str,
) -> bool:
    """检测字符串中是否包含 %var% 格式的变量

    Args:
        text (str): 需要检测的字符串
    Returns:
        bool: 如果字符串中存在 %var% 格式的变量则返回 True, 否则返回 False
    """
    pattern = r"%([^%]+)%"
    return bool(re.search(pattern, text))


def expand_var_string(
    text: str,
    vars_dict: dict[str, str] = None,
) -> str:
    """将字符串中的 %var% 变量进行替换, 并优先查找变量表中的值

    Args:
        text (str): 需要处理的字符串
        vars_dict (dict[str, str] | None): 变量字典
    Returns:
        str: 处理后的字符串
    """

    def _replace_env_var(
        match: re.Match,
    ) -> str:
        env_var = match.group(1)
        env_var_lower = match.group(1).lower().strip()
        return vars_dict.get(env_var_lower, os.environ.get(env_var, match.group(0)))

    if vars_dict is None:
        vars_dict = {}

    pattern = r"%([^%]+)%"
    text = text.replace(r"%10%", r"%SYSTEMROOT%")
    vars_dict = lowercase_dict_keys(vars_dict)
    result = re.sub(pattern, _replace_env_var, text)
    return result


def refresh_system_params() -> None:
    """通知系统刷新设置以应用更改"""
    ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, None, 0x01 | 0x02)


def get_windows_cursor_theme() -> str:
    """获取 Windows 桌面当前使用的鼠标指针配置名称

    Returns:
        (str | None): 当前使用的鼠标指针名称
    """
    return registry_query_value(
        name="",
        sub_key=WINDOWS_CURSOR_CURSORS_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.READ,
    )


def get_windows_cursor_size() -> int | None:
    """获取 Windows 桌面当前使用的鼠标指针大小

    Returns:
        (int | None): 当前使用的鼠标指针大小
    """
    return registry_query_value(
        name="CursorSize",
        sub_key=WINDOWS_ACCESSIBILITY_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.READ,
    )


def set_windows_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 Windows 桌面当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    """
    # 获取鼠标指针方案列表
    schemes = registry_enum_values(
        sub_key=WINDOWS_CURSOR_CURSORS_SCHEME_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.READ,
    )
    if cursor_name not in schemes:
        return

    scheme_data = schemes[cursor_name]
    cursor_paths = [x for x in extend_list_to_length(scheme_data.split(","), target_length=len(CURSOR_KEYS["win"]))]

    # 设置方案名称
    registry_set_value(
        name="",
        value=cursor_name,
        reg_type=RegistryValueType.SZ,
        sub_key=WINDOWS_CURSOR_CURSORS_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.SET_VALUE,
    )

    # 设置鼠标指针对应的文件路径
    for cursor, path in zip(CURSOR_KEYS["win"], cursor_paths):
        reg_type = RegistryValueType.EXPAND_SZ if has_var_string(path) else RegistryValueType.SZ
        registry_set_value(
            name=cursor,
            value=path,
            reg_type=reg_type,
            sub_key=WINDOWS_CURSOR_CURSORS_PATH,
            key=RegistryRootKey.CURRENT_USER,
            access=RegistryAccess.SET_VALUE,
        )

    refresh_system_params()


def set_windows_cursor_size(
    cursor_size: int,
) -> None:
    """设置 Windows 桌面当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    """
    registry_set_value(
        name="CursorSize",
        value=cursor_size,
        reg_type=RegistryValueType.DWORD,
        sub_key=WINDOWS_ACCESSIBILITY_PATH,
        key=RegistryRootKey.CURRENT_USER,
        access=RegistryAccess.SET_VALUE,
    )
    refresh_system_params()


def broadcast_settings_change(
    area_name: Literal["Environment", "Policy", "intl"] | None = "Environment",
) -> bool:
    """发送 WM_SETTINGCHANGE 广播消息通知系统设置已更改

    Args:
        area_name (Literal["Environment", "Policy", "intl"] | None):
            更改的区域名称
            - 如果是环境变量, 传入 `Environment`
            - 如果是通过注册表更改了策略或通用设置, 传入 `Policy`
            - 如果是鼠标/字体等, 传入 `intl` 或留空
    Returns:
        bool: 通知结果
    """
    # WM_SETTINGCHANGE 的消息数值在 win32con 中已定义
    # HWND_BROADCAST: 0xFFFF (发送给所有顶层窗口)
    # SMTO_ABORTIFHUNG: 如果目标窗口挂起，则立即返回

    result = win32gui.SendMessageTimeout(  # pylint: disable=c-extension-no-member,no-member
        win32con.HWND_BROADCAST,
        win32con.WM_SETTINGCHANGE,
        0,
        area_name,
        win32con.SMTO_ABORTIFHUNG,
        5000,  # 等待每个窗口响应的最大毫秒数
    )
    return result


def create_windows_shortcut(
    target_path: Path,
    shortcut_path: Path,
    description: str | None = "",
    working_dir: Path | None = None,
    icon_path: Path | None = None,
) -> None:
    """创建 Windows 快捷方式

    Args:
        target_path (Path): 目标文件路径
        shortcut_path (Path): 快捷方式保存路径 (应以 .lnk 结尾)
        description (str | None): 快捷方式描述
        working_dir (Path | None): 工作目录
        icon_path (Path | None): 图标路径
    """
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(target_path)
    shortcut.WorkingDirectory = str(working_dir) or str(target_path.parent)
    if description:
        shortcut.Description = description
    if icon_path is not None:
        shortcut.IconLocation = str(icon_path)
    shortcut.save()
