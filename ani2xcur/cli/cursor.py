"""系统鼠标指针管理工具"""

import sys
import traceback
from typing import (
    Annotated,
    Any,
)
from pathlib import Path
from tempfile import TemporaryDirectory

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from ani2xcur.manager.base import (
    WINDOWS_USER_CURSOR_PATH,
    LINUX_USER_ICONS_PATH,
)
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
from ani2xcur.smart_finder import (
    find_inf_file,
    find_desktop_entry_file,
)

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def install_cursor(
    input_path: Annotated[
        Path,
        typer.Argument(
            help="鼠标指针文件的路径, 输入鼠标指针压缩包文件路径, 或者: Windows 平台中输入 inf / ani / cur 文件路径; Linux 平台输入 index.theme 文件路径",
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
    use_inf_config_path: Annotated[
        bool,
        typer.Option(
            help="(仅 Windows 平台) 使用 INF 配置文件中的鼠标指针安装路径",
        ),
    ] = False,
) -> None:
    """将鼠标指针安装到系统中"""
    if sys.platform == "win32":
        if install_path is None:
            if use_inf_config_path:
                logger.info("使用 INF 配置文件中的鼠标指针安装路径")
            else:
                install_path = WINDOWS_USER_CURSOR_PATH
                logger.info("未指定鼠标指针安装路径, 使用默认鼠标指针安装路径: '%s'", install_path)
        else:
            logger.info("使用自定义鼠标指针安装路径: '%s'", install_path)

        logger.info("安装的 Windows 鼠标指针: '%s'", input_path)
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            inf_file = find_inf_file(
                input_file=input_path,
                temp_dir=temp_dir,
                depth=SMART_FINDER_SEARCH_DEPTH,
            )
            if inf_file is None:
                logger.error("未找到鼠标指针的 INF 配置文件路径, 该鼠标指针文件无法安装")
                sys.exit(1)

            try:
                install_windows_cursor(
                    inf_file=inf_file,
                    cursor_install_path=install_path,
                )
            except PermissionError as e:
                traceback.print_exc()
                logger.error(
                    "在 Windows 系统上安装鼠标指针时发生错误: '%s'\n请检查是否使用管理员权限运行 Ani2xcur 运行, 或者尝试使用 --install-path 参数指定其他鼠标指针的安装路径", e
                )
                sys.exit(1)
    elif sys.platform == "linux":
        if install_path is None:
            install_path = LINUX_USER_ICONS_PATH
            logger.info("未指定鼠标指针安装路径, 使用默认鼠标指针安装路径: '%s'", install_path)
        else:
            logger.info("使用自定义鼠标指针安装路径: '%s'", install_path)

        logger.info("安装的 Linux 鼠标指针: '%s'", input_path)
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

            try:
                install_linux_cursor(
                    desktop_entry_file=desktop_entry_file,
                    cursor_install_path=install_path,
                )
            except (FileNotFoundError, RuntimeError) as e:
                traceback.print_exc()
                logger.error(
                    "在 Windows 系统上安装鼠标指针时发生错误: %s\n请检查是否使用管理员权限运行 Ani2xcur 运行, 或者尝试使用 --install-path 参数指定其他鼠标指针的安装路径\n鼠标指针文件可能也出现损坏, 也请检查鼠标指针文件的完整性",
                    e,
                )
                sys.exit(1)
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)


def uninstall_cursor(
    cursor_name: Annotated[
        str,
        typer.Argument(
            help="要删除的鼠标指针名称",
        ),
    ],
) -> None:
    """删除系统中指定的鼠标指针"""
    if sys.platform == "win32":
        try:
            delete_windows_cursor(cursor_name)
        except RuntimeError as e:
            traceback.print_exc()
            logger.error("删除鼠标指针时发生错误: %s\n可能为没有权限进行删除鼠标指针文件, 可尝试使用管理员权限运行 Ani2xcur", e)
            sys.exit(1)
        except ValueError as e:
            traceback.print_exc()
            logger.error("删除鼠标指针时发生错误: %s\n请检查要删除的鼠标指针是否存在或者正在使用", e)
            sys.exit(1)
    elif sys.platform == "linux":
        try:
            delete_linux_cursor(cursor_name)
        except RuntimeError as e:
            traceback.print_exc()
            logger.error("删除鼠标指针时发生错误: %s\n可能为没有权限进行删除鼠标指针文件, 可尝试使用 root 权限运行 Ani2xcur", e)
            sys.exit(1)
        except ValueError as e:
            traceback.print_exc()
            logger.error("删除鼠标指针时发生错误: %s\n请检查要删除的鼠标指针是否存在", e)
            sys.exit(1)
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)


def export_cursor(
    cursor_name: Annotated[
        str,
        typer.Argument(
            help="要导出的鼠标指针名称",
        ),
    ],
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
    ] = None,
) -> None:
    """将鼠标指针从系统中导出"""
    if sys.platform == "win32":
        try:
            path = export_windows_cursor(
                cursor_name=cursor_name,
                output_path=output_path,
                custom_install_path=custom_install_path,
            )
            logger.info("Windows 鼠标指针导出完成, 导出路径: '%s'", path)
        except ValueError as e:
            traceback.print_exc()
            logger.error("导出鼠标指针发生错误: %s\n请检查导出的鼠标指针是否存在于系统中", e)
            sys.exit(1)
    elif sys.platform == "linux":
        try:
            path = export_linux_cursor(
                cursor_name=cursor_name,
                output_path=output_path,
                custom_install_path=custom_install_path,
            )
            logger.info("Windows 鼠标指针导出完成, 导出路径: '%s'", path)
        except ValueError as e:
            traceback.print_exc()
            logger.error("导出鼠标指针发生错误: %s\n请检查导出的鼠标指针是否存在于系统中", e)
            sys.exit(1)
        except RuntimeError as e:
            traceback.print_exc()
            logger.error("导出鼠标指针发生错误: %s\n可能为导出路径无权限读写, 可尝试修改导出路径进行尝试, 或者使用 root 权限运行 Ani2xcur", e)
            sys.exit(1)
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)


def set_cursor_theme(
    cursor_name: Annotated[
        str,
        typer.Argument(
            help="要指定的鼠标指针名称",
        ),
    ],
) -> None:
    """设置系统要使用的鼠标指针主题"""
    if sys.platform == "win32":
        try:
            set_windows_cursor_theme(cursor_name)
        except ValueError as e:
            traceback.print_exc()
            logger.error("设置鼠标指针主题时发生错误: %s\n请检查要设置的鼠标指针主题是否安装到系统中", e)
            sys.exit(1)
    elif sys.platform == "linux":
        try:
            set_linux_cursor_theme(cursor_name)
        except ValueError as e:
            traceback.print_exc()
            logger.error("设置鼠标指针主题时发生错误: %s\n请检查要设置的鼠标指针主题是否安装到系统中", e)
            sys.exit(1)
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)


def set_cursor_size(
    cursor_size: Annotated[
        int,
        typer.Argument(
            help="要指定的鼠标指针大小",
        ),
    ],
) -> None:
    """设置系统要使用的鼠标指针大小"""
    if sys.platform == "win32":
        try:
            set_windows_cursor_size(cursor_size)
        except TypeError as e:
            traceback.print_exc()
            logger.error("设置鼠标指针大小时发生错误: %s\n请检查鼠标指针大小的是否为整数", e)
            sys.exit(1)
        except ValueError as e:
            traceback.print_exc()
            logger.error("设置鼠标指针大小时发生错误: %s\n请检查鼠标指针大小的值是否在合法范围", e)
            sys.exit(1)
    elif sys.platform == "linux":
        try:
            set_linux_cursor_size(cursor_size)
        except TypeError as e:
            traceback.print_exc()
            logger.error("设置鼠标指针大小时发生错误: %s\n请检查鼠标指针大小的是否为整数", e)
            sys.exit(1)
        except ValueError as e:
            traceback.print_exc()
            logger.error("设置鼠标指针大小时发生错误: %s\n请检查鼠标指针大小的值是否在合法范围", e)
            sys.exit(1)
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)


def list_cursor() -> None:
    """列出当前系统中已安装的鼠标指针"""

    def _display_frame(
        items: list[dict[str, Any]],
    ) -> None:
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
        table.add_column("数量", justify="left", style="white")
        table.add_column("安装路径", style="cyan", overflow="fold")

        for item in items:
            path = ", ".join([str(x) for x in item["install_paths"]])
            count = len(item["cursor_files"])

            table.add_row(item["name"], str(count), path)

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

    def _display_frame(
        items: list[dict[str, Any]],
    ) -> None:
        console = Console()

        # 设置表格整体样式
        table = Table(
            header_style="bright_yellow",
            border_style="bright_black",
            box=box.ROUNDED,
        )

        # 设置列样式
        # style 参数控制该列所有单元格的默认样式
        table.add_column("平台", style="bold white", no_wrap=True)
        table.add_column("鼠标指针主题", justify="left", style="white")
        table.add_column("鼠标指针大小", style="cyan", overflow="fold")

        for item in items:
            platform = item["platform"]
            cursor_name = item["cursor_name"]
            cursor_size = item["cursor_size"]

            table.add_row(platform, str(cursor_name), str(cursor_size))

        console.print(table)

    if sys.platform == "win32":
        info = get_windows_cursor_info()
    elif sys.platform == "linux":
        info = get_linux_cursor_info()
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)

    _display_frame(info)
