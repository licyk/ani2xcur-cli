"""Linux 鼠标指针管理工具"""

import stat
from typing import TypedDict
from pathlib import Path

from ani2xcur.manager.base import (
    CurrentCursorInfo,
    CurrentCursorInfoList,
    CursorMap,
    CURSOR_KEYS,
    LocalCursor,
)
from ani2xcur.config_parse.linux import parse_desktop_entry_content
from ani2xcur.file_operations.file_manager import (
    copy_files,
    get_file_list,
    remove_files,
)
from ani2xcur.manager.base import (
    CursorSchemesList,
    LINUX_ICONS_PATH,
    LINUX_USER_ICONS_PATH,
)
from ani2xcur.manager.desktop_config.base import check_linux_cursor_size_value
from ani2xcur.manager.desktop_config.cinnamon import (
    set_cinnamon_cursor_size,
    set_cinnamon_cursor_theme,
    get_cinnamon_cursor_size,
    get_cinnamon_cursor_theme,
)
from ani2xcur.manager.desktop_config.gnome import (
    set_gnome_cursor_size,
    set_gnome_cursor_theme,
    get_gnome_cursor_size,
    get_gnome_cursor_theme,
)
from ani2xcur.manager.desktop_config.gtk import (
    set_gtk2_cursor_size,
    set_gtk2_cursor_theme,
    set_gtk3_cursor_size,
    set_gtk3_cursor_theme,
    set_gtk4_cursor_size,
    set_gtk4_cursor_theme,
    get_gtk2_cursor_size,
    get_gtk2_cursor_theme,
    get_gtk3_cursor_size,
    get_gtk3_cursor_theme,
    get_gtk4_cursor_size,
    get_gtk4_cursor_theme,
)
from ani2xcur.manager.desktop_config.kde import (
    set_kde_cursor_size,
    set_kde_cursor_theme,
    get_kde_cursor_size,
    get_kde_cursor_theme,
)
from ani2xcur.manager.desktop_config.lxqt import (
    set_lxqt_cursor_size,
    set_lxqt_cursor_theme,
    get_lxqt_cursor_size,
    get_lxqt_cursor_theme,
)
from ani2xcur.manager.desktop_config.mate import (
    set_mate_cursor_size,
    set_mate_cursor_theme,
    get_mate_cursor_size,
    get_mate_cursor_theme,
)
from ani2xcur.manager.desktop_config.x_org import (
    set_x_resources_cursor_size,
    set_x_resources_cursor_theme,
    get_x_resources_cursor_size,
    get_x_resources_cursor_theme,
)
from ani2xcur.manager.desktop_config.xdg import (
    set_xdg_cursor_theme,
    get_xdg_cursor_theme,
)
from ani2xcur.manager.desktop_config.xfce import (
    set_xfce_cursor_size,
    set_xfce_cursor_theme,
    get_xfce_cursor_size,
    get_xfce_cursor_theme,
)
from ani2xcur.manager.desktop_config.xsettings import (
    set_gtk_xsettings_cursor_size,
    set_gtk_xsettings_cursor_theme,
    get_gtk_xsettings_cursor_size,
    get_gtk_xsettings_cursor_theme,
)
from ani2xcur.config import (
    LOGGER_LEVEL,
    LOGGER_COLOR,
    LOGGER_NAME,
)
from ani2xcur.logger import get_logger

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


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


def extract_scheme_info_from_desktop_entry(
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
    desktop_entry_content = parse_desktop_entry_content(desktop_entry_file)
    scheme_name = desktop_entry_content["Icon Theme"]["Name"]
    cursor_path = desktop_entry_file.parent / "cursors"
    if not cursor_path.is_dir():
        raise FileNotFoundError(f"未找到 {cursor_path} 目录, 无法搜索已有的鼠标指针文件")

    cursor_paths = get_file_list(
        path=desktop_entry_file.parent / "cursors",
        max_depth=0,
    )
    cursor_key_paths = {x.name: x for x in cursor_paths}
    cursor_map: CursorMap = {}
    vars_dict = desktop_entry_content["Icon Theme"]
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


def list_linux_cursors() -> CursorSchemesList:
    """列出 Linux 系统中已有的鼠标指针

    Returns:
        CursorSchemesList: 本地已安装的鼠标指针列表
    """
    cursors_list: CursorSchemesList = []
    icon_user_paths = get_file_list(LINUX_USER_ICONS_PATH, max_depth=0, include_dirs=True)
    icon_system_paths = get_file_list(LINUX_ICONS_PATH, max_depth=0, include_dirs=True)
    logger.debug("用户图标目录文件列表: %s", icon_user_paths)
    logger.debug("系统图标目录文件列表: %s", icon_system_paths)
    icon_paths = icon_user_paths + icon_system_paths
    for path in icon_paths:
        cursors_dir = path / "cursors"
        if not cursors_dir.is_dir():
            logger.debug("'%s' 缺少鼠标指针文件夹", path)
            continue

        logger.debug("获取 '%s' 鼠标指针的文件列表", path)
        cursor_files = get_file_list(cursors_dir)
        cursors: LocalCursor = {}
        cursors["name"] = path.name
        cursors["cursor_files"] = cursor_files
        cursors["install_paths"] = [path]
        cursors_list.append(cursors)

    return cursors_list


def set_linux_cursor_theme(
    cursor_name: str,
) -> None:
    """设置 Linux 桌面当前使用的鼠标指针配置名称

    Args:
        cursor_name (str): 要设置的鼠标指针配置名称
    Raises:
        ValueError: 鼠标指针不存在时
    """
    cursors = [x["name"] for x in list_linux_cursors()]
    if cursor_name not in cursors:
        logger.error("鼠标指针 '%s' 不存在", cursor_name)
        raise ValueError(f"鼠标指针 {cursor_name} 不存在")

    logger.info("将 Linux 系统中使用的鼠标指针主题设置为 '%s'", cursor_name)
    set_cinnamon_cursor_theme(cursor_name)
    set_gnome_cursor_theme(cursor_name)
    set_gtk2_cursor_theme(cursor_name)
    set_gtk3_cursor_theme(cursor_name)
    set_gtk4_cursor_theme(cursor_name)
    set_kde_cursor_theme(cursor_name)
    set_lxqt_cursor_theme(cursor_name)
    set_mate_cursor_theme(cursor_name)
    set_x_resources_cursor_theme(cursor_name)
    set_xdg_cursor_theme(cursor_name)
    set_xfce_cursor_theme(cursor_name)
    set_gtk_xsettings_cursor_theme(cursor_name)
    logger.info("Linux 鼠标指针主题已设置为 '%s'", cursor_name)


def set_linux_cursor_size(
    cursor_size: int,
) -> None:
    """设置 Linux 桌面当前使用的鼠标指针大小

    Args:
        cursor_size (int): 要设置的鼠标指针大小
    Raises:
        TypeError: 鼠标指针大小的值不是整数时
        ValueError: 鼠标指针大小的值超过合法范围时
    """
    try:
        check_linux_cursor_size_value(cursor_size)
    except TypeError as e:
        raise TypeError("鼠标指针大小的值必须为整数") from e
    except ValueError as e:
        raise ValueError("鼠标指针大小的值超过合法范围") from e

    logger.info("将 Linux 系统中使用的鼠标指针大小设置为 %s", cursor_size)
    set_cinnamon_cursor_size(cursor_size)
    set_gnome_cursor_size(cursor_size)
    set_gtk2_cursor_size(cursor_size)
    set_gtk3_cursor_size(cursor_size)
    set_gtk4_cursor_size(cursor_size)
    set_kde_cursor_size(cursor_size)
    set_lxqt_cursor_size(cursor_size)
    set_mate_cursor_size(cursor_size)
    set_x_resources_cursor_size(cursor_size)
    set_xfce_cursor_size(cursor_size)
    set_gtk_xsettings_cursor_size(cursor_size)
    logger.info("鼠标指针大小已设置为 %s", cursor_size)


def get_linux_cursor_info() -> CurrentCursorInfoList:
    """获取 Linux 当前鼠标指针信息

    Returns:
        CurrentCursorInfoList: 桌面平台的当前鼠标指针信息列表
    """
    logger.info("获取 Linux 系统的鼠标指针状态")
    info_list: CurrentCursorInfoList = []

    # Cinnamon
    cinnamon: CurrentCursorInfo = {}
    cinnamon["platform"] = "Cinnamon"
    cinnamon["cursor_name"] = get_cinnamon_cursor_theme()
    cinnamon["cursor_size"] = get_cinnamon_cursor_size()
    info_list.append(cinnamon)

    # Gnome
    gnome: CurrentCursorInfo = {}
    gnome["platform"] = "Gnome"
    gnome["cursor_name"] = get_gnome_cursor_theme()
    gnome["cursor_size"] = get_gnome_cursor_size()
    info_list.append(gnome)

    # GTK 2.0
    gtk2: CurrentCursorInfo = {}
    gtk2["platform"] = "GTK 2.0"
    gtk2["cursor_name"] = get_gtk2_cursor_theme()
    gtk2["cursor_size"] = get_gtk2_cursor_size()
    info_list.append(gtk2)

    # GTK 3.0
    gtk3: CurrentCursorInfo = {}
    gtk3["platform"] = "GTK 3.0"
    gtk3["cursor_name"] = get_gtk3_cursor_theme()
    gtk3["cursor_size"] = get_gtk3_cursor_size()
    info_list.append(gtk3)

    # GTK 4.0
    gtk4: CurrentCursorInfo = {}
    gtk4["platform"] = "GTK 4.0"
    gtk4["cursor_name"] = get_gtk4_cursor_theme()
    gtk4["cursor_size"] = get_gtk4_cursor_size()
    info_list.append(gtk4)

    # KDE
    kde: CurrentCursorInfo = {}
    kde["platform"] = "KDE"
    kde["cursor_name"] = get_kde_cursor_theme()
    kde["cursor_size"] = get_kde_cursor_size()
    info_list.append(kde)

    # LXQT
    lxqt: CurrentCursorInfo = {}
    lxqt["platform"] = "LXQT"
    lxqt["cursor_name"] = get_lxqt_cursor_theme()
    lxqt["cursor_size"] = get_lxqt_cursor_size()
    info_list.append(lxqt)

    # Mate
    mate: CurrentCursorInfo = {}
    mate["platform"] = "Mate"
    mate["cursor_name"] = get_mate_cursor_theme()
    mate["cursor_size"] = get_mate_cursor_size()
    info_list.append(mate)

    # X.Org
    x_org: CurrentCursorInfo = {}
    x_org["platform"] = "X.Org"
    x_org["cursor_name"] = get_x_resources_cursor_theme()
    x_org["cursor_size"] = get_x_resources_cursor_size()
    info_list.append(x_org)

    # XDG
    xdg: CurrentCursorInfo = {}
    xdg["platform"] = "XDG"
    xdg["cursor_name"] = ",".join([str(x) for x in get_xdg_cursor_theme()])
    xdg["cursor_size"] = None
    info_list.append(xdg)

    # Xfce
    xfce: CurrentCursorInfo = {}
    xfce["platform"] = "Xfce"
    xfce["cursor_name"] = get_xfce_cursor_theme()
    xfce["cursor_size"] = get_xfce_cursor_size()
    info_list.append(xfce)

    # X Settings
    xfce: CurrentCursorInfo = {}
    xfce["platform"] = "X Settings"
    xfce["cursor_name"] = get_gtk_xsettings_cursor_theme()
    xfce["cursor_size"] = get_gtk_xsettings_cursor_size()
    info_list.append(xfce)

    return info_list


def delete_linux_cursor(
    cursor_name: str,
) -> None:
    """删除 Linux 系统上指定的鼠标指针

    Args:
        cursor_name (str): 要删除的鼠标指针名称
    Raises:
        RuntimeError: 删除鼠标指针文件失败时
        ValueError: 指定的鼠标指针不存在时
    """
    cursors = list_linux_cursors()
    if cursor_name not in [x["name"] for x in cursors]:
        raise ValueError(f"鼠标指针 {cursor_name} 不存在")

    logger.info("从 Linux 系统删除 '%s' 鼠标指针中", cursor_name)
    for scheme in cursors:
        if cursor_name == scheme["name"]:
            # 清理鼠标指针文件
            for file in scheme["cursor_files"]:
                if not file.exists():
                    logger.debug("鼠标指针文件 '%s' 不存在", file)
                    continue

                try:
                    logger.debug("清理鼠标指针文件 '%s'", file)
                    remove_files(file)
                except OSError as e:
                    logger.error("删除 '%s' 鼠标指针所使用的指针文件 '%s' 发生错误: %s\n可尝试使用管理员权限运行 Ani2xcur 进行删除, 或者尝试手动删除文件")
                    raise RuntimeError(f"删除 {cursor_name} 鼠标指针所使用的指针文件 {file} 发生错误: {e}\n可尝试使用管理员权限运行 Ani2xcur 进行删除, 或者尝试手动删除文件") from e

            # 清理鼠标指针的父文件夹
            for file in scheme["install_paths"]:
                if not file.is_dir():
                    logger.debug("鼠标指针文件的父文件夹 '%s' 不存在", file)
                    continue

                try:
                    logger.debug("清理鼠标指针文件的父文件夹 '%s'", file)
                    remove_files(file)
                except OSError as e:
                    logger.error("清理 '%s' 鼠标指针文件的残留文件夹 '%s' 发生错误: %s\n可尝试使用管理员权限运行 Ani2xcur 进行删除, 或者尝试手动删除文件", cursor_name, file, e)
                    raise RuntimeError(f"清理 {cursor_name} 鼠标指针文件的残留文件夹 {file} 发生错误: {e}\n可尝试使用管理员权限运行 Ani2xcur 进行删除, 或者尝试手动删除文件") from e

    logger.info("从 Linux 系统删除 '%s' 鼠标指针完成", cursor_name)


def install_linux_cursor(
    desktop_entry_file: Path,
    cursor_install_path: Path | None = None,
) -> None:
    """通过 DesktopEntry 配置文件安装鼠标指针

    Args:
        desktop_entry_file (Path): 鼠标指针配置文件路径
        cursor_install_path (Path | None): 自定义鼠标指针文件安装路径, 当为 None 时使用默认安装路径
    Raises:
        FileNotFoundError: 鼠标指针中缺少 cursors 文件夹时
        RuntimeError:  复制鼠标指针文件夹发生失败时
    """
    cursors_path = desktop_entry_file.parent / "cursors"
    if not cursors_path.is_dir():
        raise FileNotFoundError(f"在 {cursors_path} 中缺少 cursors 文件夹, 鼠标指针已损坏")

    scheme_info = extract_scheme_info_from_desktop_entry(desktop_entry_file)
    logger.debug("解析到的 DesktopEntry 配置: %s", scheme_info)
    cursor_name = scheme_info["scheme_name"]
    src = desktop_entry_file.parent
    if cursor_install_path is not None:
        dst = cursor_install_path / cursor_name
    else:
        dst = LINUX_USER_ICONS_PATH / cursor_name

    logger.info("将 '%s' 鼠标指针安装到 '%s' 中", cursor_name, dst)

    try:
        copy_files(src, dst)
    except OSError as e:
        logger.error("复制鼠标指针 '%s' 到 '%s' 时发生错误: %s\n可尝试使用 root 权限运行 Ani2xcur 进行鼠标指针安装操作", src, dst, e)
        raise RuntimeError(f"复制鼠标指针 {src} 到 {dst} 时发生错误: {e}\n可尝试使用 root 权限运行 Ani2xcur 进行鼠标指针安装操作") from e

    logger.info("'%s' 鼠标指针已安装到 '%s'", cursor_name, dst)


def export_linux_cursor(
    cursor_name: str,
    output_path: Path,
    custom_install_path: Path | None = None,
) -> Path:
    """将系统中指定的鼠标指针方案导出为文件

    Args:
        cursor_name (str): 要导出的鼠标指针方案的名称
        output_path (Path): 鼠标指针导出的路径
        custom_install_path (Path | None): 自定义鼠标指针安装时的文件安装路径
    Returns:
        Path: 鼠标指针导出的文件路径
    Raises:
        ValueError: 鼠标指针在当前环境中不存在时
        RuntimeError: 导出鼠标指针文件发生失败时
    """
    cursors = list_linux_cursors()
    cursor_data = None
    for data in cursors:
        if data["name"] == cursor_name:
            cursor_data = data

    if cursor_data is None:
        raise ValueError(f"鼠标指针 {cursor_name} 不存在")

    src = cursor_data["install_paths"][0]
    save_dir = output_path / cursor_name

    logger.info("将 '%s' 鼠标指针导出到 '%s' 中", cursor_name, save_dir)

    try:
        copy_files(src, save_dir)
    except OSError as e:
        logger.error("从 '%s' 导出鼠标指针文件到 '%s' 时发生错误: %s", src, save_dir, e)
        raise RuntimeError(f"从 {src} 导出鼠标指针文件到 {save_dir} 时发生错误: {e}") from e

    generate_install_script(
        cursor_name=cursor_name,
        save_dir=save_dir,
        custom_install_path=custom_install_path,
    )

    logger.info("'%s' 鼠标指针导出到 '%s' 完成", cursor_name, save_dir)
    return save_dir


def generate_install_script(
    cursor_name: str,
    save_dir: Path,
    custom_install_path: Path | None = None,
) -> None:
    """生成 Linux 鼠标指针安装脚本

    Args:
        cursor_name (str): 鼠标指针名称
        save_dir (Path): 安装脚本保存路径
        custom_install_path (Path | None): 自定义鼠标指针安装文件
    """
    install_path = str(custom_install_path) if custom_install_path is not None else "${HOME}/.icons"
    sh_content = r"""
#!/bin/bash

cursor_path=$(cd "$(dirname "$0")" ; pwd)

install_cursor() {
    mkdir -p "{{__INSTALL_PATH__}}" || return 1
    cp -r "${cursor_path}" "{{__INSTALL_PATH__}}" || return 1
    return 0
}

get_cursor_set_command() {
    local cursor_name=$1
    cat<<EOF
Cinnamon:
    gsettings set org.cinnamon.desktop.interface cursor-theme "${cursor_name}"

Gnome:
    gsettings set org.gnome.desktop.interface cursor-theme "${cursor_name}"

Mate:
    gsettings set org.mate.peripherals-mouse cursor-theme "${cursor_name}"

KDE:
    kwriteconfig5 --file kcminputrc --group Mouse --key cursorTheme "${cursor_name}"

Xfce:
    xfconf-query --channel xsettings --property /Gtk/CursorThemeName --set "${cursor_name}"
EOF
}

echo "将鼠标指针安装至 '{{__INSTALL_PATH__}}/{{__CURSOR_NAME__}}'"

if install_cursor; then
    echo "'{{__CURSOR_NAME__}}' 鼠标指针安装完成, 可使用运行下面的命令启用该鼠标指针"
    get_cursor_set_command "{{__CURSOR_NAME__}}"
else
    echo "鼠标指针安装到 '{{__INSTALL_PATH__}}/{{__CURSOR_NAME__}}' 失败, 请检查是否有 root 权限或者检查目录是否存在"
    exit 1
fi
""".strip()
    sh_content = sh_content.replace("{{__INSTALL_PATH__}}", install_path).replace("{{__CURSOR_NAME__}}", cursor_name)

    sh_path = save_dir / "install_cursor.sh"
    with open(sh_path, "w", encoding="utf-8") as f:
        f.write(sh_content)

    current_permissions = sh_path.stat().st_mode
    sh_path.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
