"""Ani2xcur 补丁"""

from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_COLOR,
    LOGGER_LEVEL,
    LOGGER_NAME,
)


logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def patch_win2xcur() -> None:
    """将补丁应用到 win2xcur 中"""
    try:
        import win2xcur  # pylint: disable=import-outside-toplevel
    except ImportError as e:
        logger.error("导入 win2xcur 模块发生错误, 无法应用补丁: %s\n这可能因 ImageMagick 未安装导致的问题, 请使用 Ani2xcur 的 ImageMagick 安装功能进行修复", e)
        raise e

    try:
        import win2xcur.scale  # pylint: disable=import-outside-toplevel
    except ImportError:
        from ani2xcur.win2xcur import scale  # pylint: disable=import-outside-toplevel

        win2xcur.scale = scale
