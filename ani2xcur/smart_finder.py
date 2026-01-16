"""鼠标指针配置文件智能搜索"""

from pathlib import Path

from ani2xcur.config_parse.win import parse_inf_file_content
from ani2xcur.config_parse.linux import parse_desktop_entry_content
from ani2xcur.file_operations.archive_manager import (
    is_supported_archive_format,
    extract_archive,
)
from ani2xcur.file_operations.file_manager import get_file_list
from ani2xcur.utils import generate_random_string
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


def find_desktop_entry_file(
    input_file: Path,
    temp_dir: Path,
    depth: int | None = 0,
    visited: set[Path] | None = None,
    is_toplevel: bool = True,  # pylint: disable=unused-argument
) -> Path | None:
    """搜索 DesktopEntry 文件路径

    Args:
        input_file (Path): 任意文件路径
        temp_dir (Path): 临时文件夹, 用于保存寻找文件时产生的临时文件
        depth (int | None): 递归搜索文件的深度
        visited (set[Path] | None): 已访问路径集合, 用于防止死循环
        is_toplevel (bool): 是否为顶层调用
    Returns:
        (Path | None): 当找到 DesktopEntry 文件时则返回其路径, 否则返回 None
    """

    # 初始化去重集合
    if visited is None:
        visited = set()

    logger.debug("已搜索路径: '%s'", visited)
    logger.debug("查找路径: '%s'", input_file)

    # 获取绝对路径并验证存在性
    try:
        abs_path = input_file.resolve()
    except OSError:
        return None

    if not abs_path.exists():
        return None

    # 防止循环递归遍历
    if abs_path in visited:
        return None
    visited.add(abs_path)

    # 递归搜索深度控制
    if depth < 0:
        return None

    # 验证 DesktopEntry 文件完整性
    if abs_path.is_file() and abs_path.name.lower().endswith(".theme"):
        try:
            _ = parse_desktop_entry_content(abs_path)
            logger.debug("搜索到 DesktopEntry 文件路径: '%s'", abs_path)
            return abs_path
        except ValueError:
            return None

    # 文件为压缩包时则尝试解压并遍历解压的文件夹
    if is_supported_archive_format(abs_path):
        logger.debug("从 '%s' 搜索文件中", abs_path)
        extract_path = temp_dir / generate_random_string()
        extract_archive(
            archive_path=abs_path,
            extract_to=extract_path,
        )
        # 递归调用 (标记 is_toplevel=False)
        return find_desktop_entry_file(
            input_file=extract_path,
            temp_dir=temp_dir,
            depth=depth,
            visited=visited,
            is_toplevel=False,
        )

    # 如果是文件夹则尝试遍历文件夹中的文件
    if abs_path.is_dir():
        logger.debug("搜索 '%s' 文件夹", abs_path)
        # 获取下级文件列表
        paths = get_file_list(
            path=abs_path,
            max_depth=0,
            include_dirs=True,
        )
        for path in paths:
            file = find_desktop_entry_file(
                input_file=path,
                temp_dir=temp_dir,
                depth=depth - 1,
                visited=visited,
                is_toplevel=False,
            )
            if file is not None:
                return file

    return None


def find_inf_file(
    input_file: Path,
    temp_dir: Path,
    depth: int | None = 0,
    visited: set[Path] | None = None,
    is_toplevel: bool = True,
) -> Path | None:
    """搜索 INF 文件路径

    Args:
        input_file (Path): 任意文件路径
        temp_dir (Path): 临时文件夹, 用于保存寻找文件时产生的临时文件
        depth (int | None): 递归搜索文件的深度
        visited (set[Path] | None): 已访问路径集合, 用于防止死循环
        is_toplevel (bool): 是否为顶层调用, 用于控制是否修正光标文件路径
    Returns:
        (Path | None): 当找到 INF 文件时则返回其路径, 否则返回 None
    """

    # 初始化去重集合
    if visited is None:
        visited = set()

    logger.debug("已搜索路径: '%s'", visited)
    logger.debug("查找路径: '%s'", input_file)

    # 智能路径修正 (仅在首次调用且输入为光标文件时触发)
    # 该目录可能为鼠标指针路径, 则尝试定位到其父文件夹
    if is_toplevel and input_file.is_file():
        if input_file.name.lower().endswith((".ani", ".cur")):
            input_file = input_file.parent

    # 获取绝对路径并验证存在性
    try:
        abs_path = input_file.resolve()
    except OSError:
        return None

    if not abs_path.exists():
        return None

    # 防止循环递归遍历
    if abs_path in visited:
        return None
    visited.add(abs_path)

    # 递归搜索深度控制
    if depth < 0:
        return None

    # 验证 INF 文件完整性
    if abs_path.is_file() and abs_path.name.lower().endswith(".inf"):
        try:
            _ = parse_inf_file_content(abs_path)
            logger.debug("搜索到 INF 文件路径: '%s'", abs_path)
            return abs_path
        except ValueError:
            return None

    # 文件为压缩包时则尝试解压并遍历解压的文件夹
    if is_supported_archive_format(abs_path):
        logger.debug("从 '%s' 搜索文件中", abs_path)
        extract_path = temp_dir / generate_random_string()
        extract_archive(
            archive_path=abs_path,
            extract_to=extract_path,
        )
        # 递归调用 (标记 is_toplevel=False)
        return find_inf_file(
            input_file=extract_path,
            temp_dir=temp_dir,
            depth=depth,  # 解压内容通常可视作当前层级或下一层级, 这里维持原逻辑
            visited=visited,
            is_toplevel=False,
        )

    # 如果是文件夹则尝试遍历文件夹中的文件
    if abs_path.is_dir():
        logger.debug("搜索 '%s' 文件夹", abs_path)
        # 获取下级文件列表
        paths = get_file_list(
            path=abs_path,
            max_depth=0,
            include_dirs=True,
        )
        for path in paths:
            file = find_inf_file(
                input_file=path,
                temp_dir=temp_dir,
                depth=depth - 1,
                visited=visited,
                is_toplevel=False,
            )
            if file is not None:
                return file

    return None
