import sys
from typing import Annotated
from pathlib import Path

import typer

from ani2xcur.config import (
    LOGGER_NAME,
    LOGGER_LEVEL,
    LOGGER_COLOR,
)
from ani2xcur.logger import get_logger
from ani2xcur.image_magick_manager import (install_image_magick_windows, install_image_magick_linux, uninstall_image_magick_windows, uninstall_image_magick_linux)
from ani2xcur.utils import (is_admin_on_windows, is_root_on_linux)

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)

def install_image_magick(install_path: Annotated[Path | None, typer.Option(help="自定义安装 ImageMagick 的目录", resolve_path=True)] = None) -> None:
    """安装 ImageMagick 到系统中"""
    if sys.platform == "win32":
        if not is_admin_on_windows():
            logger.error("当前未使用管理员权限运行 Ani2xcur, 无法安装 ImageMagick, 请使用管理员权限启动 Ani2xcur")
            sys.exit(1)
        install_image_magick_windows(
            install_path=install_path
        )
    elif sys.platform == "linux":
        if not is_root_on_linux():
            logger.error("当前未使用 root 权限运行 Ani2xcur, 无法安装 ImageMagick, 请使用 root 权限启动 Ani2xcur")
            sys.exit(1)
        install_image_magick_linux()
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)

def uninstall_image_magick() -> None:
    """将 ImageMagick 从系统中卸载"""
    if sys.platform == "win32":
        if not is_admin_on_windows():
            logger.error("当前未使用管理员权限运行 Ani2xcur, 无法卸载 ImageMagick, 请使用管理员权限启动 Ani2xcur")
            sys.exit(1)
        uninstall_image_magick_windows()
    elif sys.platform == "linux":
        if not is_root_on_linux():
            logger.error("当前未使用 root 权限运行 Ani2xcur, 无法卸载 ImageMagick, 请使用 root 权限启动 Ani2xcur")
            sys.exit(1)
        uninstall_image_magick_linux()
    else:
        logger.error("不支持的系统: %s", sys.platform)
        sys.exit(1)
