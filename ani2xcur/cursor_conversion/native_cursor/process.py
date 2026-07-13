"""原生 Pillow 转换器的公开入口。"""

from pathlib import Path
from typing import TypedDict

from ani2xcur.cursor_conversion.native_cursor.models import CursorFrame
from ani2xcur.config import (
    LOGGER_COLOR,
    LOGGER_LEVEL,
    LOGGER_NAME,
)
from ani2xcur.cursor_conversion.native_cursor.parsers import parse_blob
from ani2xcur.cursor_conversion.native_cursor.transforms import (
    DEFAULT_XCURSOR_SIZES,
    add_shadow_to_frames,
    normalize_xcursor_sizes,
    scale_frames,
)
from ani2xcur.cursor_conversion.native_cursor.writers import (
    to_smart,
    to_xcursor,
)
from ani2xcur.logger import get_logger
from ani2xcur.utils import (
    open_file_as_bytes,
    save_bytes_to_file,
)

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def _frames_debug_summary(frames: list[CursorFrame]) -> dict[str, object]:
    """生成光标帧的调试摘要。

    Args:
        frames (list[CursorFrame]): 光标帧列表。
    Returns:
        dict[str, object]: 可写入日志的光标摘要。
    """
    nominal_sizes = sorted({image.nominal for frame in frames for image in frame.images})
    actual_sizes = sorted({image.image.size for frame in frames for image in frame.images})
    hotspots = sorted({image.hotspot for frame in frames for image in frame.images})
    delays = sorted({round(frame.delay, 4) for frame in frames})
    return {
        "frame_count": len(frames),
        "nominal_sizes": nominal_sizes,
        "actual_sizes": actual_sizes,
        "hotspots": hotspots[:20],
        "delay_seconds": delays[:20],
    }


class Win2xcurArgs(TypedDict, total=False):
    """Windows 光标转换为 Xcursor 的参数。"""

    input_file: Path
    output_path: Path
    save_name: str | None
    shadow: bool | None
    shadow_opacity: int | None
    shadow_radius: float | None
    shadow_sigma: float | None
    shadow_x: float | None
    shadow_y: float | None
    shadow_color: str | None
    scale: float | None
    xcursor_sizes: list[int] | None


def win2xcur_process(
    input_file: Path,
    output_path: Path,
    save_name: str | None = None,
    shadow: bool | None = False,
    shadow_opacity: int | None = 50,
    shadow_radius: float | None = 0.1,
    shadow_sigma: float | None = 0.1,
    shadow_x: float | None = 0.05,
    shadow_y: float | None = 0.05,
    shadow_color: str | None = "#000000",
    scale: float | None = None,
    xcursor_sizes: list[int] | None = None,
) -> Path:
    """将 Windows CUR/ANI 光标文件转换为 Xcursor 文件。

    Args:
        input_file (Path): 输入的 Windows 光标文件路径。
        output_path (Path): 转换结果的输出目录。
        save_name (str | None): 输出文件名, 为 None 时使用输入文件名。
        shadow (bool | None): 是否添加阴影。
        shadow_opacity (int | None): 阴影不透明度。
        shadow_radius (float | None): 阴影半径比例。
        shadow_sigma (float | None): 阴影模糊比例。
        shadow_x (float | None): 阴影水平偏移比例。
        shadow_y (float | None): 阴影垂直偏移比例。
        shadow_color (str | None): 阴影颜色。
        scale (float | None): 图像缩放倍率。
        xcursor_sizes (list[int] | None): 要写入的 Xcursor 名义尺寸列表。
    Returns:
        Path: 转换后保存的 Xcursor 文件路径。
    """
    if save_name is None:
        save_name = input_file.stem

    logger.debug(
        "开始 Windows -> Xcursor 转换: input='%s', output_path='%s', save_name=%r, scale=%r, shadow=%r, xcursor_sizes=%r",
        input_file,
        output_path,
        save_name,
        scale,
        shadow,
        xcursor_sizes,
    )
    frames = _read_cursor_file(input_file)
    logger.debug("读取 Windows 光标文件完成: %s", _frames_debug_summary(frames))
    if scale:
        scale_frames(frames, scale=scale)
        logger.debug("缩放光标帧完成: scale=%s, summary=%s", scale, _frames_debug_summary(frames))
    if shadow:
        add_shadow_to_frames(
            frames,
            color="#000000" if shadow_color is None else shadow_color,
            opacity=50 if shadow_opacity is None else shadow_opacity,
            radius=0.1 if shadow_radius is None else shadow_radius,
            sigma=0.1 if shadow_sigma is None else shadow_sigma,
            xoffset=0.05 if shadow_x is None else shadow_x,
            yoffset=0.05 if shadow_y is None else shadow_y,
        )
        logger.debug(
            "添加光标阴影完成: opacity=%r, radius=%r, sigma=%r, x=%r, y=%r, color=%r, summary=%s",
            shadow_opacity,
            shadow_radius,
            shadow_sigma,
            shadow_x,
            shadow_y,
            shadow_color,
            _frames_debug_summary(frames),
        )
    normalize_xcursor_sizes(frames, DEFAULT_XCURSOR_SIZES if xcursor_sizes is None else xcursor_sizes)
    logger.debug("补齐 Xcursor 尺寸完成: %s", _frames_debug_summary(frames))

    output_file = output_path / save_name
    save_bytes_to_file(to_xcursor(frames), output_file)
    logger.debug("Windows -> Xcursor 转换完成: output='%s'", output_file)
    return output_file


class X2wincurArgs(TypedDict, total=False):
    """Xcursor 转换为 Windows 光标的参数。"""

    input_file: Path
    output_path: Path
    save_name: str | None
    scale: float | None


def x2wincur_process(
    input_file: Path,
    output_path: Path,
    save_name: str | None = None,
    scale: float | None = None,
) -> Path:
    """将 Xcursor/CUR/ANI 光标文件转换为 Windows CUR/ANI 文件。

    Args:
        input_file (Path): 输入的光标文件路径。
        output_path (Path): 转换结果的输出目录。
        save_name (str | None): 输出文件名, 为 None 时使用输入文件名。
        scale (float | None): 图像缩放倍率。
    Returns:
        Path: 转换后保存的 Windows 光标文件路径。
    """
    if save_name is None:
        save_name = input_file.stem

    logger.debug(
        "开始 Xcursor -> Windows 转换: input='%s', output_path='%s', save_name=%r, scale=%r",
        input_file,
        output_path,
        save_name,
        scale,
    )
    frames = _read_cursor_file(input_file)
    logger.debug("读取 Xcursor 光标文件完成: %s", _frames_debug_summary(frames))
    if scale:
        scale_frames(frames, scale=scale)
        logger.debug("缩放光标帧完成: scale=%s, summary=%s", scale, _frames_debug_summary(frames))

    extension, result = to_smart(frames)
    output_file = output_path / f"{save_name}{extension}"
    save_bytes_to_file(result, output_file)
    logger.debug("Xcursor -> Windows 转换完成: output='%s', extension='%s'", output_file, extension)
    return output_file


def _read_cursor_file(input_file: Path) -> list[CursorFrame]:
    logger.debug("读取光标文件: '%s'", input_file)
    blob = open_file_as_bytes(input_file)
    try:
        frames = parse_blob(blob)
        logger.debug("解析光标文件完成: input='%s', summary=%s", input_file, _frames_debug_summary(frames))
        return frames
    except ValueError as error:
        logger.error("解析光标文件失败: input='%s', error='%s'", input_file, error)
        raise
    except Exception as e:
        logger.error("打开光标文件时发生未知错误: %s", e)
        raise
