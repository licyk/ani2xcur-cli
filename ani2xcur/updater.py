"""Ani2xcur 更新工具"""

import sys
import importlib.metadata
from pathlib import Path
from datetime import (
    datetime,
    timedelta,
)

from ani2xcur.cmd import run_cmd
from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_COLOR,
    LOGGER_LEVEL,
    LOGGER_NAME,
    ANI2XCUR_REPOSITORY_URL,
    WIN2XCUR_REPOSITORY_URL,
    ANI2XCUR_CONFIG_PATH,
)
from ani2xcur.file_operations.file_manager import remove_files


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


def auto_check_update() -> None:
    """检查 Ani2xcur 的更新并提示信息"""
    import requests

    if not check_update_time():
        return

    logger.debug("检查 Ani2xcur 更新中")
    current = importlib.metadata.version("ani2xcur")

    try:
        response = requests.get(url="https://pypi.org/pypi/ani2xcur/json", timeout=2)
        json_data = response.json()
        latest = json_data["info"]["version"]
    except requests.exceptions.ConnectTimeout as e:
        logger.error("获取 Ani2xcur 版本信息时发生错误: %s", e)
        return
    except requests.exceptions.JSONDecodeError as e:
        logger.error("解析 Ani2xcur 版本信息时发生错误: %s", e)
        return

    if current != latest:
        logger.info("新版 Ani2xcur (%s) 可用, 当前使用的版本为 %s\n更新 Ani2xcur 请使用命令: ani2xcur update", latest, current)


def check_update_time() -> bool:
    """检查是否到达检查更新时间

    Args:
        bool: 当时间间隔达到检查更新要求时
    """
    ANI2XCUR_CONFIG_PATH.mkdir(parents=True, exist_ok=True)
    time_record_file = ANI2XCUR_CONFIG_PATH / "update_time"
    current = datetime.now()
    time_span = timedelta(hours=24)
    time_format = r"%Y-%m-%d %H:%M:%S"

    def _save_time_record(
        _record: datetime,
        _time_record_file: Path,
    ) -> None:
        try:
            with open(_time_record_file, "w", encoding="utf-8") as f:
                f.write(_record.strftime(time_format))
        except (PermissionError, OSError) as e:
            logger.debug("保存检查更新时间记录发生错误: %s", e)

    # 清除无效的更新时间记录文件夹
    if time_record_file.is_dir():
        remove_files(time_record_file)

    # 读取上次更新时间记录
    if time_record_file.is_file():
        try:
            with open(time_record_file, "r", encoding="utf-8") as f:
                record = datetime.strptime(f.read(), time_format)
                logger.debug("上次检查更新时间: %s", record)
        except (PermissionError, OSError, ValueError):
            logger.debug("解析更新时间记录失败, 尝试覆盖时间记录文件")
            record = datetime.now()
            _save_time_record(record, time_record_file)
    else:
        logger.debug("未找到更新时间记录文件, 尝试生成中")
        record = datetime.now() - time_span
        _save_time_record(record, time_record_file)

    # 检查上次更新时间与当前时间的间隔
    if current - record >= time_span:
        _save_time_record(current, time_record_file)
        return True

    return False
