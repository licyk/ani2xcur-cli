"""文件操作工具"""

import os
import stat
import shutil
from pathlib import Path
from tqdm import tqdm
from ani2xcur.logger import get_logger
from ani2xcur.config import LOGGER_LEVEL, LOGGER_COLOR, LOGGER_NAME

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def remove_files(path: str | Path) -> None:
    """文件删除工具

    Args:
        path (str | Path): 要删除的文件路径
    Raises:
        ValueError: 删除的路径不存在时
        OSError: 删除文件失败时
    """

    def _handle_remove_readonly(_func, _path, _):
        """处理只读文件的错误处理函数"""
        if os.path.exists(_path):
            os.chmod(_path, stat.S_IWRITE)
            _func(_path)

    try:
        path_obj = Path(path)
        if path_obj.is_file():
            os.chmod(path_obj, stat.S_IWRITE)
            path_obj.unlink()

        if path_obj.is_dir():
            shutil.rmtree(path_obj, onerror=_handle_remove_readonly)

        logger.error("路径不存在: %s", path)
        raise ValueError(f"要删除的 {path} 路径不存在")
    except OSError as e:
        logger.error("删除失败: %s", e)
        raise e


def copy_files(src: Path | str, dst: Path | str) -> None:
    """复制文件或目录

    Args:
        src (Path | str): 源文件路径
        dst (Path | str): 复制文件到指定的路径
    Raises:
        PermissionError: 没有权限复制文件时
        OSError: 复制文件失败时
        FileNotFoundError: 源文件未找到时
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)

        # 检查源是否存在
        if not src_path.exists():
            logger.error("源路径不存在: %s", src)
            raise FileNotFoundError(f"源路径不存在: {src}")

        # 如果目标是目录, 创建完整路径
        if dst_path.is_dir():
            dst_file = dst_path / src_path.name
        else:
            dst_file = dst_path

        # 确保目标目录存在
        dst_file.parent.mkdir(parents=True, exist_ok=True)

        # 复制文件
        if src_path.is_file():
            shutil.copy2(src, dst_file)
        else:
            # 如果是目录, 使用 copytree
            if dst_file.exists():
                shutil.rmtree(dst_file)
            shutil.copytree(src, dst_file)

    except PermissionError as e:
        logger.error("权限错误, 请检查文件权限或以管理员身份运行: %s", e)
        raise e
    except OSError as e:
        logger.error("复制失败: %s", e)
        raise e


def get_file_list(
    path: Path,
    resolve: bool | None = False,
    max_depth: int | None = -1,
    show_progress: bool | None = True,
) -> list[Path]:
    """获取当前路径下的所有文件的绝对路径

    Args:
        path (Path): 要获取文件列表的目录
        resolve (bool | None): 将路径进行完全解析, 包括链接路径
        max_depth (int | None): 最大遍历深度, -1 表示不限制深度, 0 表示只遍历当前目录
        show_progress (bool | None): 是否显示 tqdm 进度条
    Returns:
        list[Path]: 文件列表的绝对路径
    """

    if not path or not path.exists():
        return []

    if path.is_file():
        return [path.resolve() if resolve else path.absolute()]

    base_depth = len(path.resolve().parts)

    file_list: list[Path] = []
    with tqdm(
        desc=f"扫描目录 {path}", position=0, leave=True, disable=not show_progress
    ) as dir_pbar:
        with tqdm(
            desc="发现文件数", position=1, leave=True, disable=not show_progress
        ) as file_pbar:
            for root, dirs, files in os.walk(path):
                root_path = Path(root)
                current_depth = len(root_path.resolve().parts) - base_depth

                # 超过最大深度则阻止继续向下遍历
                if max_depth != -1 and current_depth >= max_depth:
                    dirs.clear()

                for file in files:
                    file_path = root_path / file
                    file_list.append(
                        file_path.resolve() if resolve else file_path.absolute()
                    )
                    file_pbar.update(1)

                dir_pbar.update(1)

    return file_list


def create_symlink(target: Path, link: Path) -> None:
    """创建软链接, 当创建软链接失败时则尝试复制文件

    Args:
        target (Path): 源文件路径
        link (Path): 软链接到的目的路径
    """
    try:
        link.symlink_to(target)
        logger.debug("创建软链接: %s -> %s", target, link)
    except OSError:
        logger.debug("尝试创建软链接失败, 尝试复制文件: %s -> %s", target, link)
        copy_files(target, link)
