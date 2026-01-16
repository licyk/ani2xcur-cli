"""Win2xcur 调用工具"""

from pathlib import Path
from typing import TypedDict

from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_COLOR,
    LOGGER_LEVEL,
    LOGGER_NAME,
)
from ani2xcur.utils import (
    open_file_as_bytes,
    save_bytes_to_file,
)
from ani2xcur.win2xcur.patch import patch_win2xcur

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


class Win2xcurArgs(TypedDict, total=False):
    """调用 win2xcur_process() 时输入的参数字典"""

    input_file: Path
    """光标文件的路径"""

    output_path: Path
    """保存转换后的光标文件的路径"""

    save_name: str | None
    """保存的文件名"""

    shadow: bool | None
    """是否模拟 Windows 的阴影效果"""

    shadow_opacity: int | None
    """阴影的不透明度 (0 到 255)"""

    shadow_radius: float | None
    """阴影模糊效果的半径 (宽度的分数值)"""

    shadow_sigma: float | None
    """阴影模糊效果的西格玛值 (宽度的分数值)"""

    shadow_x: float | None
    """阴影的 x 偏移量 (宽度的分数值)"""

    shadow_y: float | None
    """阴影的 y 偏移量 (高度的分数值)"""

    shadow_color: str | None
    """阴影的颜色 (十六进制颜色格式)"""

    scale: float | None
    """按指定倍数缩放光标"""


def win2xcur_process(
    input_file: Path,
    output_path: Path,
    save_name: str | None = None,
    shadow: bool | None = False,
    shadow_opacity: int | None = 50,  # pylint: disable=unused-argument
    shadow_radius: float | None = 0.1,
    shadow_sigma: float | None = 0.1,
    shadow_x: float | None = 0.05,
    shadow_y: float | None = 0.05,
    shadow_color: str | None = "#000000",
    scale: float | None = None,
) -> Path:
    """win2xcur 处理过程

    Args:
        input_file (Path): 光标文件的路径
        output_path (Path): 保存转换后的光标文件的路径
        save_name (str | None): 保存的文件名
        shadow (bool | None): 是否模拟 Windows 的阴影效果
        shadow_opacity (int | None): 阴影的不透明度 (0 到 255)
        shadow_radius (float | None): 阴影模糊效果的半径 (宽度的分数值)
        shadow_sigma (float | None): 阴影模糊效果的西格玛值 (宽度的分数值)
        shadow_x (float | None): 阴影的 x 偏移量 (宽度的分数值)
        shadow_y (float | None): 阴影的 y 偏移量 (高度的分数值)
        shadow_color (str | None): 阴影的颜色 (十六进制颜色格式)
        scale (float | None): 按指定倍数缩放光标
    Returns:
        Path: 光标保存路径
    Raises:
        ValueError: 读取不支持的光标文件格式时
        Exception: 发生未知错误时
    """
    try:
        # 依赖关系: win2xcur -> wand -> ImageMagick
        # 当 ImageMagick 未安装时将导致 win2xcur 导入失败
        patch_win2xcur()
        from win2xcur.scale import apply_to_frames as apply_to_frames_for_scale  # pylint: disable=import-outside-toplevel
        from win2xcur.shadow import apply_to_frames as apply_to_frames_for_shadow  # pylint: disable=import-outside-toplevel
        from win2xcur.parser import open_blob  # pylint: disable=import-outside-toplevel
        from win2xcur.writer import to_x11  # pylint: disable=import-outside-toplevel
    except ImportError as e:
        raise ImportError(f"导入 win2xcur 模块时发生错误: {e}\n这可能因 ImageMagick 未安装导致的问题, 请使用 Ani2xcur 的 ImageMagick 安装功能进行修复") from e

    if save_name is None:
        save_name = input_file.stem

    blob = open_file_as_bytes(input_file)

    try:
        cursor = open_blob(blob)
    except ValueError as e:
        logger.error("不支持的光标文件格式: '%s'", input_file.suffix)
        raise e
    except Exception as e:
        logger.error("打开光标文件时发生未知错误: %s", e)
        raise e

    if scale:
        apply_to_frames_for_scale(cursor.frames, scale=scale)

    if shadow:
        apply_to_frames_for_shadow(
            cursor.frames,
            color=shadow_color,
            radius=shadow_radius,
            sigma=shadow_sigma,
            xoffset=shadow_x,
            yoffset=shadow_y,
        )
    result = to_x11(cursor.frames)
    output_path = output_path / save_name
    save_bytes_to_file(result, output_path)
    return output_path


class X2wincurArgs(TypedDict, total=False):
    """调用 x2wincur_process() 时输入的参数字典"""

    input_file: Path
    """光标文件的路径"""

    output_path: Path
    """保存转换后的光标文件的路径"""

    save_name: str | None
    """保存的文件名 (不包括扩展名)"""

    scale: float | None
    """按指定倍数缩放光标"""


def x2wincur_process(
    input_file: Path,
    output_path: Path,
    save_name: str | None = None,
    scale: float | None = None,
) -> None:
    """x2wincur 处理过程

    Args:
        input_file (Path): 光标文件的路径
        output_path (Path): 保存转换后的光标文件的路径
        save_name (str | None): 保存的文件名 (不包括扩展名)
        scale (float | None): 按指定倍数缩放光标
    Returns:
        Path: 光标保存路径
    Raises:
        ValueError: 读取不支持的光标文件格式时
        Exception: 发生未知错误时
        ImportError: 当导入 win2xcur 模块发生失败时
    """
    try:
        # 依赖关系: win2xcur -> wand -> ImageMagick
        # 当 ImageMagick 未安装时将导致 win2xcur 导入失败
        patch_win2xcur()
        from win2xcur.scale import apply_to_frames as apply_to_frames_for_scale  # pylint: disable=import-outside-toplevel
        from win2xcur.parser import open_blob  # pylint: disable=import-outside-toplevel
        from win2xcur.writer import to_smart  # pylint: disable=import-outside-toplevel
    except ImportError as e:
        raise ImportError(f"导入 win2xcur 模块时发生错误: {e}\n这可能因 ImageMagick 未安装导致的问题, 请使用 Ani2xcur 的 ImageMagick 安装功能进行修复") from e

    if save_name is None:
        save_name = input_file.stem

    blob = open_file_as_bytes(input_file)

    try:
        cursor = open_blob(blob)
    except ValueError as e:
        logger.error("不支持的光标文件格式: '%s'", input_file.suffix)
        raise e
    except Exception as e:
        logger.error("打开光标文件时发生未知错误: %s", e)
        raise e

    if scale:
        apply_to_frames_for_scale(cursor.frames, scale=scale)

    ext, result = to_smart(cursor.frames)
    output_path = output_path / f"{save_name}{ext}"
    save_bytes_to_file(result, output_path)
    return output_path
