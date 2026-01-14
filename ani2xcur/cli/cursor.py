import sys
from typing import Annotated
from pathlib import Path
from tempfile import TemporaryDirectory

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from ani2xcur.manager.win_cur_manager import (
    install_windows_cursor,
    delete_windows_cursor,
    export_windows_cursor,
    set_windows_cursor_theme,
    set_windows_cursor_size,
    list_windows_cursors,
    get_windows_cursor_info,
)
from ani2xcur.manager.linux_cur_manager import (
    install_linux_cursor,
    delete_linux_cursor,
    export_linux_cursor,
    set_linux_cursor_theme,
    set_linux_cursor_size,
    list_linux_cursors,
    get_linux_cursor_info,
)
from ani2xcur.config import (
    LOGGER_NAME,
    LOGGER_LEVEL,
    LOGGER_COLOR,
    SMART_FINDER_SEARCH_DEPTH,
)
from ani2xcur.logger import get_logger
from ani2xcur.smart_finder import find_inf_file, find_desktop_entry_file

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def install_cursor(
    input_path: Annotated[
        Path,
        typer.Argument(
            help="Linux 鼠标指针文件的路径, 可以为 index.theme 文件路径, 或者鼠标指针压缩包文件路径",
            resolve_path=True,
        ),
    ],
    install_path: Annotated[
        Path | None,
        typer.Option(
            help="自定义鼠标指针文件安装路径, 默认为鼠标指针配置文件中指定的安装路径",
            resolve_path=True,
        ),
    ] = None,
) -> None:
    """将鼠标指针安装到系统中"""
    if sys.platform == "win32":
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            inf_file = find_inf_file(
                input_file=input_path,
                temp_dir=temp_dir,
                depth=SMART_FINDER_SEARCH_DEPTH,
            )
            if inf_file is None:
                logger.error(
                    "未找到鼠标指针的 INF 配置文件路径, 该鼠标指针文件无法安装"
                )
                sys.exit(1)

            install_windows_cursor(
                inf_file=inf_file,
                cursor_install_path=install_path,
            )
    elif sys.platform == "linux":
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            desktop_entry_file = find_desktop_entry_file(
                input_file=input_path,
                temp_dir=temp_dir,
                depth=SMART_FINDER_SEARCH_DEPTH,
            )

            if desktop_entry_file is None:
                logger.error("未找到鼠标指针的 DesktopEntry 配置文件路径")
                sys.exit(1)

            if not (desktop_entry_file.parent / "cursors").is_dir():
                logger.error("鼠标指针目录缺失, 无法进行鼠标指针转换")
                sys.exit(1)

            install_linux_cursor(
                desktop_entry_file=desktop_entry_file,
                cursor_install_path=install_path,
            )
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)


def uninstall_cursor(
    cursor_name: Annotated[str, typer.Argument(help="要删除的鼠标指针名称")]
) -> None:
    """删除系统中指定的鼠标指针"""
    if sys.platform == "win32":
        delete_windows_cursor(cursor_name)
    elif sys.platform == "linux":
        delete_linux_cursor(cursor_name)
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)

def export_cursor(
    cursor_name: Annotated[str, typer.Argument(help="要导出的鼠标指针名称")],
    output_path: Annotated[
        Path,
        typer.Argument(
            help="鼠标指针的导出路径",
            resolve_path=True,
        ),
    ],
    custom_install_path: Annotated[
        Path | None,
        typer.Option(
            help="自定义鼠标指针配置文件在安装时的文件安装路径",
            resolve_path=True,
        ),
    ],
) -> None:
    """将鼠标指针从系统中导出"""
    if sys.platform == "win32":
        path = export_windows_cursor(
                cursor_name=cursor_name,
                output_path=output_path,
                custom_install_path=custom_install_path,
        )
        logger.info("Windows 鼠标指针导出完成, 导出路径: %s", path)
    elif sys.platform == "linux":
        path = export_linux_cursor(
                cursor_name=cursor_name,
                output_path=output_path,
                custom_install_path=custom_install_path,
            )
        logger.info("Windows 鼠标指针导出完成, 导出路径: %s", path)
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)

def set_cursor_theme(
    cursor_name: Annotated[str, typer.Argument(help="要指定的鼠标指针名称")],
) -> None:
    """设置系统要使用的鼠标指针主题"""
    if sys.platform == "win32":
        set_windows_cursor_theme(cursor_name)
    elif sys.platform == "linux":
        set_linux_cursor_theme(cursor_name)
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)


def set_cursor_size(
    cursor_size: Annotated[int, typer.Argument(help="要指定的鼠标指针大小")]
)-> None:
    """设置系统要使用的鼠标指针大小"""
    if sys.platform == "win32":
        set_windows_cursor_size(cursor_size)
    elif sys.platform == "linux":
        set_linux_cursor_size(cursor_size)
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)

def list_cursor() -> None:
    """列出当前系统中已安装的鼠标指针"""

    def _display_frame(items) -> None:
        console = Console()
        
        # 设置表格整体样式
        table = Table(
            header_style="bright_yellow",
            border_style="bright_black",
            box=box.ROUNDED,
        )
        
        # 设置列样式
        # style 参数控制该列所有单元格的默认样式
        table.add_column("鼠标指针名称", style="bold white", no_wrap=True)
        table.add_column("数量", justify="right", style="white")
        table.add_column("安装路径", style="cyan")

        for item in items:
            path = ", ".join([str(x) for x in item["install_paths"]])
            count = len(item["cursor_files"])
            count_str = str(count)

            table.add_row(
                item["name"],
                count_str,
                path
            )

        console.print(table)

    if sys.platform == "win32":
        logger.info("获取 Windows 系统中已安装的鼠标指针列表")
        cursors = list_windows_cursors()
    elif sys.platform == "linux":
        logger.info("获取 Linux 系统中已安装的鼠标指针列表")
        cursors = list_linux_cursors()
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)

    _display_frame(cursors)


def get_current_cursor() -> None:
    """显示当前系统中设置的鼠标指针名称和大小"""
    def _display_frame(items) -> None:
        console = Console()
        
        # 设置表格整体样式
        table = Table(
            header_style="bright_yellow",
            border_style="bright_black",
            box=box.ROUNDED,
        )
        
        # 设置列样式
        # style 参数控制该列所有单元格的默认样式
        table.add_column("鼠标指针名称", style="bold white", no_wrap=True)
        table.add_column("数量", justify="right", style="white")
        table.add_column("安装路径", style="cyan")

        for item in items:
            platform = item["platform"]
            cursor_name = item["cursor_name"]
            cursor_size = item["cursor_size"]

            table.add_row(
                platform,
                cursor_name,
                cursor_size
            )

        console.print(table)

    if sys.platform == "win32":
        info = get_windows_cursor_info()
    elif sys.platform == "linux":
        info = get_linux_cursor_info()
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)

    _display_frame(info)

    