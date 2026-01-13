import importlib.metadata
import re
from typing import Annotated

import typer
import pandas as pd

from ani2xcur.config import (
    LOGGER_NAME,
    LOGGER_LEVEL,
    LOGGER_COLOR,
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
        bool, typer.Option(help="更新时是否从源码进行安装")
    ] = False,
    ani2xcur_source: Annotated[
        str | None, typer.Option(help="Ani2xcur 源仓库的 Git 链接")
    ] = None,
    win2xcur_source: Annotated[
        str | None, typer.Option(help="Win2xcur 源仓库的 Git 链接")
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
    requires = importlib.metadata.requires("ani2xcur")
    info = []
    pkgs = [
        remove_optional_dependence_from_package(get_package_name(x))
        .split(";")[0]
        .strip()
        for x in requires
    ]
    for pkg in pkgs:
        try:
            ver = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            ver = None
        info.append({"组件名": pkg, "版本": ver})

    df = pd.DataFrame(info)
    print(df)


def get_package_name(package: str) -> str:
    """获取 Python 软件包的包名, 去除末尾的版本声明

    Args:
        package (str): Python 软件包名
    Returns:
        str: 返回去除版本声明后的 Python 软件包名
    """
    return (
        package.split("===")[0]
        .split("~=")[0]
        .split("!=")[0]
        .split("<=")[0]
        .split(">=")[0]
        .split("<")[0]
        .split(">")[0]
        .split("==")[0]
        .strip()
    )


def remove_optional_dependence_from_package(filename: str) -> str:
    """移除 Python 软件包声明中可选依赖

    Args:
        filename (str): Python 软件包名
    Returns:
        str: 移除可选依赖后的软件包名, e.g. diffusers[torch]==0.10.2 -> diffusers==0.10.2
    """
    return re.sub(r"\[.*?\]", "", filename)
