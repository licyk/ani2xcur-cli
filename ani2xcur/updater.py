"""Ani2xcur 更新工具"""

import sys
from pathlib import Path

from ani2xcur.cmd import run_cmd
from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_COLOR,
    LOGGER_LEVEL,
    LOGGER_NAME,
    ANI2XCUR_REPOSITORY_URL,
    WIN2XCUR_REPOSITORY_URL,
)


logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def self_update(
    install_from_source: bool | None = False,
    ani2xcur_source: str | None = None,
    win2xcur_source: str | None = None,
    enable_log: bool | None = True,
) -> None:
    """更新 Ani2xcur

    Args:
        install_from_source (bool | None): 是否从源码进行安装
        ani2xcur_source (str | None): Ani2xcur 源仓库的 Git 链接
        win2xcur_source (str | None): win2xcur 源仓库的 Git 链接
        enable_log (bool | None): 是否显示更新日志
    Raises:
        RuntimeError: 更新失败时
    """

    if ani2xcur_source is None:
        ani2xcur_source = ANI2XCUR_REPOSITORY_URL

    if win2xcur_source is None:
        win2xcur_source = WIN2XCUR_REPOSITORY_URL

    cmd = [Path(sys.executable).as_posix(), "-m", "pip", "install", "--upgrade"]
    if install_from_source:
        cmd += [f"git+{ani2xcur_source}", f"git+{win2xcur_source}"]
    else:
        cmd += ["ani2xcur"]

    try:
        logger.info("更新 Ani2xcur 中")
        run_cmd(cmd, live=enable_log)
        logger.info("Ani2xcur 更新成功")
    except RuntimeError as e:
        logger.error("更新 Ani2xcur 时发生错误: %s", e)
        raise RuntimeError(f"更新 Ani2xcur 时发生错误: {e}") from e
