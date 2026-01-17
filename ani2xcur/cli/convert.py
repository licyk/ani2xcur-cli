"""鼠标指针转换工具"""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

import typer
import click

from ani2xcur.cursor_conversion.convert import (
    win_cursor_to_x11,
    x11_cursor_to_win,
)
from ani2xcur.cursor_conversion.win2xcur_warp import (
    Win2xcurArgs,
    X2wincurArgs,
)
from ani2xcur.smart_finder import (
    find_inf_file,
    find_desktop_entry_file,
)
from ani2xcur.config import (
    LOGGER_NAME,
    LOGGER_LEVEL,
    LOGGER_COLOR,
    SMART_FINDER_SEARCH_DEPTH,
)
from ani2xcur.logger import get_logger
from ani2xcur.file_operations.archive_manager import (
    create_archive,
    SUPPORTED_ARCHIVE_FORMAT,
)
from ani2xcur.manager.image_magick_manager import check_image_magick_is_installed
from ani2xcur.utils import is_http_or_https

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def win2xcur(
    input_path: Annotated[
        str,
        typer.Argument(
            help="Windows 鼠标指针文件的路径, 可以为 inf / ani / cur 文件路径, 或者鼠标指针压缩包文件路径, 也可以是鼠标指针压缩包的下载链接",
        ),
    ],
    output_path: Annotated[
        Path | None,
        typer.Option(
            help="保存转换后的鼠标指针路径",
            resolve_path=True,
        ),
    ] = None,
    shadow: Annotated[
        bool,
        typer.Option(
            help="是否模拟 Windows 的阴影效果",
        ),
    ] = False,
    shadow_opacity: Annotated[
        int,
        typer.Option(
            help="阴影的不透明度 (0 到 255)",
            min=0,
            max=255,
        ),
    ] = 50,
    shadow_radius: Annotated[
        float,
        typer.Option(
            help="阴影模糊效果的半径 (宽度的分数值)",
        ),
    ] = 0.1,
    shadow_sigma: Annotated[
        float,
        typer.Option(
            help="阴影模糊效果的西格玛值 (宽度的分数值)",
        ),
    ] = 0.1,
    shadow_x: Annotated[
        float,
        typer.Option(
            help="阴影的 x 偏移量 (宽度的分数值)",
        ),
    ] = 0.05,
    shadow_y: Annotated[
        float,
        typer.Option(
            help="阴影的 y 偏移量 (高度的分数值)",
        ),
    ] = 0.05,
    shadow_color: Annotated[
        str,
        typer.Option(
            help="阴影的颜色 (十六进制颜色格式)",
        ),
    ] = "#000000",
    scale: Annotated[
        float | None,
        typer.Option(
            help="按指定倍数缩放光标",
        ),
    ] = None,
    compress: Annotated[
        bool,
        typer.Option(
            help="转换完成后将鼠标指针打包成压缩包",
        ),
    ] = False,
    compress_format: Annotated[
        str,
        typer.Option(
            help="打包成压缩包时使用的压缩包格式",
            click_type=click.Choice(SUPPORTED_ARCHIVE_FORMAT),
        ),
    ] = ".zip",
) -> None:
    """将 Windows 鼠标指针文件包转换为 Linux 鼠标指针文件包"""
    if not check_image_magick_is_installed():
        logger.error("未安装 ImageMagick, 无法进行鼠标指针转换, 请使用 ani2xcur imagemagick install 命令进行安装")
        sys.exit(1)

    logger.info("将 '%s' 的 Windows 鼠标指针主题包转换为 Linux 鼠标指针主题包中", input_path)

    win2x_args: Win2xcurArgs = {
        "shadow": shadow,
        "shadow_opacity": shadow_opacity,
        "shadow_radius": shadow_radius,
        "shadow_sigma": shadow_sigma,
        "shadow_x": shadow_x,
        "shadow_y": shadow_y,
        "shadow_color": shadow_color,
        "scale": scale,
    }

    if output_path is None:
        if is_http_or_https(input_path):
            # 如果是 URL, 默认保存在当前执行目录下
            output_path = Path.cwd()
        else:
            # 如果是本地路径, 保存在输入文件的父目录
            output_path = Path(input_path).resolve().parent

    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        inf_file = find_inf_file(
            input_file=input_path,
            temp_dir=temp_dir,
            depth=SMART_FINDER_SEARCH_DEPTH,
        )

        if inf_file is None:
            logger.error("未找到鼠标指针的 INF 配置文件路径")
            sys.exit(1)

        save_path = win_cursor_to_x11(
            inf_file=inf_file,
            output_path=output_path,
            win2x_args=win2x_args,
        )

    logger.info("鼠标指针转换完成, 保存路径: '%s'", save_path)
    if compress:
        logger.info("将鼠标指针进行打包")
        archive_path = output_path / f"{save_path.name}{compress_format}"
        create_archive(
            sources=save_path,
            archive_path=archive_path,
        )
        logger.info("鼠标指针打包完成, 保存路径: '%s'", archive_path)


def x2wincur(
    input_path: Annotated[
        str,
        typer.Argument(
            help="Linux 鼠标指针文件的路径, 可以为 index.theme 文件路径, 或者鼠标指针压缩包文件路径, 也可以是鼠标指针压缩包的下载链接",
        ),
    ],
    output_path: Annotated[
        Path | None,
        typer.Option(
            help="保存转换后的鼠标指针路径",
            resolve_path=True,
        ),
    ] = None,
    scale: Annotated[
        float | None,
        typer.Option(
            help="按指定倍数缩放光标",
        ),
    ] = None,
    compress: Annotated[
        bool,
        typer.Option(
            help="转换完成后将鼠标指针打包成压缩包",
        ),
    ] = False,
    compress_format: Annotated[
        str,
        typer.Option(
            help="打包成压缩包时使用的压缩包格式",
            click_type=click.Choice(SUPPORTED_ARCHIVE_FORMAT),
        ),
    ] = ".zip",
) -> None:
    """将 Linux 鼠标指针文件包转换为 Windows 鼠标指针文件包"""
    if not check_image_magick_is_installed():
        logger.error("未安装 ImageMagick, 无法进行鼠标指针转换, 请使用 ani2xcur imagemagick install 命令进行安装")
        sys.exit(1)

    logger.info("将 '%s' 的 Linux 鼠标指针主题包转换为 Windows 鼠标指针主题包中", input_path)
    x2win_args: X2wincurArgs = {
        "scale": scale,
    }

    if output_path is None:
        if is_http_or_https(input_path):
            # 如果是 URL, 默认保存在当前执行目录下
            output_path = Path.cwd()
        else:
            # 如果是本地路径, 保存在输入文件的父目录
            output_path = Path(input_path).resolve().parent

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

        save_path = x11_cursor_to_win(
            desktop_entry_file=desktop_entry_file,
            output_path=output_path,
            x2win_args=x2win_args,
        )

    logger.info("鼠标指针转换完成, 保存路径: '%s'", save_path)
    if compress:
        logger.info("将鼠标指针进行打包")
        archive_path = output_path / f"{save_path.name}{compress_format}"
        create_archive(
            sources=save_path,
            archive_path=archive_path,
        )
        logger.info("鼠标指针打包完成, 保存路径: '%s'", archive_path)
