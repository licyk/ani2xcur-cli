"""配置管理"""

import os
import logging
import sys
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

IMAGE_MAGICK_WINDOWS_DOWNLOAD_URL = os.getenv(
    "IMAGE_MAGICK_WINDOWS_DOWNLOAD_URL", "https://modelscope.cn/models/licyks/invokeai-core-model/resolve/master/pypatchmatch/ImageMagick-7.1.2-Q16-HDRI.zip"
)
"""下载 ImageMagick Windows 版的 URL"""

IMAGE_MAGICK_WINDOWS_INSTALL_PATH = Path(os.getenv("ProgramFiles", r"C:\Program Files")) / "ImageMagick-7.1.2-Q16-HDRI"
"""Windows 默认 ImageMagick 安装路径"""

ANI2XCUR_REPOSITORY_URL = os.getenv("ANI2XCUR_REPOSITORY_URL", "https://github.com/licyk/ani2xcur-cli")
"""Ani2xcur 仓库地址"""

WIN2XCUR_REPOSITORY_URL = os.getenv("WIN2XCUR_REPOSITORY_URL", "https://github.com/quantum5/win2xcur")
"""Win2xcur 仓库地址"""

ANI2XCUR_CONFIG_PATH = (Path("~").expanduser() / "AppData" / "Roaming" / "ani2xcur") if sys.platform == "win32" else (Path("~").expanduser() / ".config" / "ani2xcur")
"""Ani2xcur 配置文件路径"""

SMART_FINDER_SEARCH_DEPTH = int(os.getenv("ANI2XCUR_SMART_FINDER_SEARCH_DEPTH", "3"))
"""Ani2xcur 智能搜索鼠标指针配置文件的深度"""
