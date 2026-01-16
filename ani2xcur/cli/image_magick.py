"""ImageMagick 管理工具"""

import sys
import traceback
from typing import Annotated
from pathlib import Path

import typer

from ani2xcur.config import (
    LOGGER_NAME,
    LOGGER_LEVEL,
    LOGGER_COLOR,
    IMAGE_MAGICK_WINDOWS_INSTALL_PATH,
)
from ani2xcur.logger import get_logger
from ani2xcur.manager.image_magick_manager import (
    install_image_magick_windows,
    install_image_magick_linux,
    uninstall_image_magick_windows,
    uninstall_image_magick_linux,
)
from ani2xcur.utils import (
    is_admin_on_windows,
    is_root_on_linux,
)

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def install_image_magick(
    install_path: Annotated[
        Path | None,
        typer.Option(
            help="(仅 Windows 平台) 自定义安装 ImageMagick 的目录",
            resolve_path=True,
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="直接确认安装",
        ),
    ] = False,
) -> None:
    """安装 ImageMagick 到系统中"""
    if sys.platform == "win32":
        if not is_admin_on_windows():
            logger.error("当前未使用管理员权限运行 Ani2xcur, 无法安装 ImageMagick, 请使用管理员权限启动 Ani2xcur")
            sys.exit(1)

        if install_path is None:
            install_path = IMAGE_MAGICK_WINDOWS_INSTALL_PATH
            logger.info("未使用 --install-path 参数指定 ImageMagick 安装路径, 使用默认安装路径: '%s'", install_path)
        else:
            logger.info("安装 ImageMagick 的路径: '%s'", install_path)

        if not force:
            typer.confirm("确认安装 ImageMagick 吗?", abort=True)
        try:
            install_image_magick_windows(install_path=install_path)
        except PermissionError as e:
            traceback.print_exc()
            logger.error("安装 ImageMagick 时发生错误: %s\n请检查是否使用管理员权限运行 Ani2xcur", e)
            sys.exit(1)
    elif sys.platform == "linux":
        if not is_root_on_linux():
            logger.error("当前未使用 root 权限运行 Ani2xcur, 无法安装 ImageMagick, 请使用 root 权限启动 Ani2xcur")
            sys.exit(1)

        if not force:
            typer.confirm("确认安装 ImageMagick 吗?", abort=True)

        try:
            install_image_magick_linux()
        except RuntimeError as e:
            traceback.print_exc()
            logger.error("安装 ImageMagick 时发生错误: %s\n当前的 Linux 发行版可能不支持自动安装 ImageMagick, 请尝试手动安装 ImageMagick", e)
            sys.exit(1)

    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)


def uninstall_image_magick(
    force: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="直接确认卸载",
        ),
    ] = False,
) -> None:
    """将 ImageMagick 从系统中卸载"""
    if sys.platform == "win32":
        if not is_admin_on_windows():
            logger.error("当前未使用管理员权限运行 Ani2xcur, 无法卸载 ImageMagick, 请使用管理员权限启动 Ani2xcur")
            sys.exit(1)

        if not force:
            typer.confirm("确认卸载 ImageMagick 吗?", abort=True)

        try:
            uninstall_image_magick_windows()
        except PermissionError as e:
            traceback.print_exc()
            logger.error("安装 ImageMagick 时发生错误: %s\n请检查是否使用管理员权限运行 Ani2xcur", e)
            sys.exit(1)
    elif sys.platform == "linux":
        if not is_root_on_linux():
            logger.error("当前未使用 root 权限运行 Ani2xcur, 无法卸载 ImageMagick, 请使用 root 权限启动 Ani2xcur")
            sys.exit(1)

        if not force:
            typer.confirm("确认卸载 ImageMagick 吗?", abort=True)

        try:
            uninstall_image_magick_linux()
        except RuntimeError as e:
            traceback.print_exc()
            logger.error("安装 ImageMagick 时发生错误: %s\n当前的 Linux 发行版可能不支持自动安装 ImageMagick, 请尝试手动安装 ImageMagick", e)
            sys.exit(1)
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)
