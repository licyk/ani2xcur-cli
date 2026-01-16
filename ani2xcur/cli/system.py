"""其他工具"""

import importlib.metadata
import re
from typing import (
    Annotated,
    Any,
)

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from ani2xcur.config import (
    LOGGER_NAME,
    LOGGER_LEVEL,
    LOGGER_COLOR,
    IMAGE_MAGICK_WINDOWS_DOWNLOAD_URL,
    ANI2XCUR_REPOSITORY_URL,
    WIN2XCUR_REPOSITORY_URL,
    SMART_FINDER_SEARCH_DEPTH,
)
from ani2xcur.logger import get_logger
from ani2xcur.updater import self_update


logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def update(
    install_from_source: Annotated[
        bool,
        typer.Option(
            help="更新时是否从源码进行安装",
        ),
    ] = False,
    ani2xcur_source: Annotated[
        str | None,
        typer.Option(
            help="Ani2xcur 源仓库的 Git 链接",
        ),
    ] = None,
    win2xcur_source: Annotated[
        str | None,
        typer.Option(
            help="Win2xcur 源仓库的 Git 链接",
        ),
    ] = None,
) -> None:
    """更新 Ani2xcur"""
    self_update(
        install_from_source=install_from_source,
        ani2xcur_source=ani2xcur_source,
        win2xcur_source=win2xcur_source,
    )


def version() -> None:
    """显示 Ani2xcur 和其他组件的当前版本"""

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
        table.add_column("组件名", style="bold white", no_wrap=True)
        table.add_column("版本", justify="left", style="white")

        for item in items:
            table.add_row(
                item["require"],
                item["version"],
            )

        console.print(table)

    requires = importlib.metadata.requires("ani2xcur")
    requires.insert(0, "ani2xcur")
    info = []
    pkgs = [remove_optional_dependence_from_package(get_package_name(x)).split(";")[0].strip() for x in requires]
    for pkg in pkgs:
        try:
            ver = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            ver = None
        info.append({"require": pkg, "version": ver})

    _display_frame(info)


def get_package_name(
    package: str,
) -> str:
    """获取 Python 软件包的包名, 去除末尾的版本声明

    Args:
        package (str): Python 软件包名
    Returns:
        str: 返回去除版本声明后的 Python 软件包名
    """
    return package.split("===")[0].split("~=")[0].split("!=")[0].split("<=")[0].split(">=")[0].split("<")[0].split(">")[0].split("==")[0].strip()


def remove_optional_dependence_from_package(
    filename: str,
) -> str:
    """移除 Python 软件包声明中可选依赖

    Args:
        filename (str): Python 软件包名
    Returns:
        str: 移除可选依赖后的软件包名, e.g. diffusers[torch]==0.10.2 -> diffusers==0.10.2
    """
    return re.sub(r"\[.*?\]", "", filename)


def env() -> None:
    """列出 Ani2xcur 使用的环境变量"""

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
        table.add_column("环境变量", style="bold white", no_wrap=True)
        table.add_column("值", justify="left", style="white", overflow="fold")

        for item in items:
            table.add_row(
                item["key"],
                str(item["var"]),
            )

        console.print(table)

    info = [
        {"key": "ANI2XCUR_LOGGER_NAME", "var": LOGGER_NAME},
        {"key": "ANI2XCUR_LOGGER_LEVEL", "var": LOGGER_LEVEL},
        {"key": "ANI2XCUR_LOGGER_COLOR", "var": LOGGER_COLOR},
        {"key": "IMAGE_MAGICK_WINDOWS_DOWNLOAD_URL", "var": IMAGE_MAGICK_WINDOWS_DOWNLOAD_URL},
        {"key": "ANI2XCUR_REPOSITORY_URL", "var": ANI2XCUR_REPOSITORY_URL},
        {"key": "WIN2XCUR_REPOSITORY_URL", "var": WIN2XCUR_REPOSITORY_URL},
        {"key": "ANI2XCUR_SMART_FINDER_SEARCH_DEPTH", "var": SMART_FINDER_SEARCH_DEPTH},
    ]

    _display_frame(info)
