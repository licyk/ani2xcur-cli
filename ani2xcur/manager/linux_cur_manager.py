from typing import TypedDict
from pathlib import Path

from ani2xcur.manager.base import CursorMap, CURSOR_KEYS
from ani2xcur.inf_parse.linux import get_cursor_scheme_data_from_desktop_entry
from ani2xcur.file_operations.file_manager import get_file_list



class InstallLinuxSchemeInfo(TypedDict):
    """Linux 鼠标指针安装信息"""
    scheme_name: str
    """鼠标指针名称"""

    cursor_paths: list[Path]
    """鼠标指针文件列表"""

    vars_dict: dict[str, str]
    """INF 文件中的变量表"""

    cursor_map: CursorMap
    """鼠标指针类型与对应的路径地图"""


def get_scheme_from_desktop_entry_file(
    desktop_entry_file: Path,
) -> InstallLinuxSchemeInfo:
    """从 Desktop Entry 文件中获取鼠标指针配置

    Args:
        desktop_entry_file (Path): Desktop Entry 文件路径
    Returns:
        InstallLinuxSchemeInfo: 鼠标指针安装配置
    Raises:
        FileNotFoundError: 鼠标指针文件缺失时
    """
    scheme_info: InstallLinuxSchemeInfo = {}
    desktop_entry_content = get_cursor_scheme_data_from_desktop_entry(desktop_entry_file)
    scheme_name = desktop_entry_content['Icon Theme']["Name"]
    cursor_path = desktop_entry_file.parent / "cursors"
    if not cursor_path.is_dir():
        raise FileNotFoundError(f"未找到 {cursor_path} 目录, 无法搜索已有的鼠标指针文件")

    cursor_paths = get_file_list(
        path=desktop_entry_file.parent / "cursors",
        max_depth=0,
    )
    cursor_key_paths = {
        x.name: x
        for x in cursor_paths
    }
    cursor_map: CursorMap = {}
    vars_dict = desktop_entry_content['Icon Theme']
    for win, linux in zip(CURSOR_KEYS["win"], CURSOR_KEYS["linux"]):
        if linux in cursor_key_paths:
            src = dst = cursor_key_paths[linux]
        else:
            src = dst = None
        cursor_map[win] = {
            "src_path": src,
            "dst_path": dst,
        }
    
    scheme_info["scheme_name"] = scheme_name
    scheme_info["cursor_paths"] = cursor_paths
    scheme_info["vars_dict"] = vars_dict
    scheme_info["cursor_map"] = cursor_map
    return scheme_info