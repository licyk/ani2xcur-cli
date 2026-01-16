"""文件操作工具"""

import os
import stat
import shutil
from pathlib import Path

from tqdm import tqdm

from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_LEVEL,
    LOGGER_COLOR,
    LOGGER_NAME,
)

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def remove_files(
    path: Path,
) -> None:
    """文件删除工具，支持删除只读文件和非空文件夹。

    Args:
        path (str | Path): 要删除的文件或目录路径
    Raises:
        ValueError: 路径不存在时
        OSError: 删除过程中的系统错误
    """

    if not path.exists():
        logger.error("路径不存在: '%s'", path)
        raise ValueError(f"要删除的 {path} 路径不存在")

    def _handle_remove_readonly(
        func,
        path_str,
        _,
    ):
        """处理只读文件的错误处理函数"""
        if os.path.exists(path_str):
            os.chmod(path_str, stat.S_IWRITE)
            func(path_str)

    try:
        if path.is_file() or path.is_symlink():
            # 处理文件或符号链接
            os.chmod(path, stat.S_IWRITE)
            path.unlink()

        elif path.is_dir():
            # 处理文件夹
            shutil.rmtree(path, onerror=_handle_remove_readonly)

    except OSError as e:
        logger.error("删除失败: '%s' - 原因: %s", path, e)
        raise e


def copy_files(
    src: Path | str,
    dst: Path | str,
) -> None:
    """复制文件或目录

    Args:
        src (Path | str): 源文件路径
        dst (Path | str): 复制文件到指定的路径
    Raises:
        PermissionError: 没有权限复制文件时
        OSError: 复制文件失败时
        FileNotFoundError: 源文件未找到时
        ValueError: 路径逻辑错误（如循环复制）时
    """
    try:
        # 转换为绝对路径以进行准确的路径比对
        src_path = src.resolve()
        dst_path = dst.resolve()

        # 检查源是否存在
        if not src_path.exists():
            logger.error("源路径不存在: '%s'", src)
            raise FileNotFoundError(f"源路径不存在: {src}")

        # 防止递归复制（例如将目录复制到其自身的子目录中）
        if src_path.is_dir() and dst_path.is_relative_to(src_path):
            logger.error("不能将目录复制到自身或其子目录中: '%s'", src)
            raise ValueError(f"不能将目录复制到自身或其子目录中: {src}")

        # 如果目标是已存在的目录, 则在其下创建同名项
        if dst_path.exists() and dst_path.is_dir():
            dst_file = dst_path / src_path.name
        else:
            dst_file = dst_path

        # 确保目标父目录存在
        dst_file.parent.mkdir(parents=True, exist_ok=True)

        # 复制操作
        if src_path.is_file():
            # copy2 会尽量保留文件元数据
            shutil.copy2(src_path, dst_file)
        else:
            # symlinks=True: 保留软链接本身而非复制指向的内容
            # dirs_exist_ok=True: 实现合并逻辑，如果目标目录已存在则覆盖同名文件
            try:
                shutil.copytree(src_path, dst_file, symlinks=True, dirs_exist_ok=True)
            except shutil.Error:
                # Linux 中遇到已存在的软链接会导致失败, 则使用 symlinks=False 重试
                shutil.copytree(src_path, dst_file, symlinks=False, dirs_exist_ok=True)

    except PermissionError as e:
        logger.error("权限错误, 请检查文件权限或以管理员身份运行: %s", e)
        raise e
    except OSError as e:
        logger.error("复制失败: %s", e)
        raise e
    except Exception as e:
        logger.error("发生非预期错误: %s", e)
        raise e


def get_file_list(
    path: Path,
    resolve: bool | None = False,
    max_depth: int | None = -1,
    show_progress: bool | None = True,
    include_dirs: bool | None = False,
) -> list[Path]:
    """获取当前路径下的所有文件（和可选的目录）的绝对路径

    Args:
        path (Path): 要获取列表的目录
        resolve (bool | None): 将路径进行完全解析, 包括链接路径
        max_depth (int | None): 最大遍历深度, -1 表示不限制深度, 0 表示只遍历当前目录
        show_progress (bool | None): 是否显示 tqdm 进度条
        include_dirs (bool | None): 是否在结果中包含目录路径
    Returns:
        (list[Path]): 路径列表的绝对路径
    """

    if not path or not path.exists():
        return []

    if path.is_file():
        return [path.resolve() if resolve else path.absolute()]

    base_depth = len(path.resolve().parts)

    file_list: list[Path] = []
    with tqdm(desc=f"扫描目录 {path}", position=0, leave=True, disable=not show_progress) as dir_pbar:
        with tqdm(desc="发现条目数", position=1, leave=True, disable=not show_progress) as file_pbar:
            for root, dirs, files in os.walk(path):
                root_path = Path(root)
                current_depth = len(root_path.resolve().parts) - base_depth

                # 超过最大深度则阻止继续向下遍历
                if max_depth != -1 and current_depth >= max_depth:
                    # 如果需要包含目录, 虽然停止深挖, 但当前层的目录仍可加入
                    if include_dirs:
                        for d in dirs:
                            dir_path = root_path / d
                            file_list.append(dir_path.resolve() if resolve else dir_path.absolute())
                            file_pbar.update(1)
                    dirs.clear()
                else:
                    # 如果启用，将当前层级的目录加入列表
                    if include_dirs:
                        for d in dirs:
                            dir_path = root_path / d
                            file_list.append(dir_path.resolve() if resolve else dir_path.absolute())
                            file_pbar.update(1)

                for file in files:
                    file_path = root_path / file
                    file_list.append(file_path.resolve() if resolve else file_path.absolute())
                    file_pbar.update(1)

                dir_pbar.update(1)

    return file_list


def save_create_symlink(
    target: Path,
    link: Path,
) -> None:
    """创建软链接, 当创建软链接失败时则尝试复制文件

    Args:
        target (Path): 源文件路径
        link (Path): 软链接到的目的路径
    """
    try:
        link.symlink_to(target)
        logger.debug("创建软链接: '%s' -> '%s'", target, link)
    except OSError:
        logger.debug("尝试创建软链接失败, 尝试复制文件: '%s' -> '%s'", target, link)
        copy_files(target, link)
