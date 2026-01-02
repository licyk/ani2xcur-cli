"""配置管理"""

import os
import logging
from pathlib import Path

LOGGER_NAME = os.getenv("ANI2XCUR_LOGGER_NAME", "Ani2xcur")
"""日志器名字"""

LOGGER_LEVEL = int(os.getenv("ANI2XCUR_LOGGER_LEVEL", str(logging.INFO)))
"""日志等级"""

LOGGER_COLOR = os.getenv("ANI2XCUR_LOGGER_COLOR") not in ["0", "False", "false", "None", "none", "null"]
"""日志颜色"""

ROOT_PATH = Path(__file__).parent
"""Ani2xcur 根目录"""

LINUX_CURSOR_SOURCE_PATH = ROOT_PATH / "source"
"""Linux 鼠标指针补全文件目录"""
