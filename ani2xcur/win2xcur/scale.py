"""鼠标指针缩放工具"""

from win2xcur.cursor import CursorFrame


def apply_to_frames(
    frames: list[CursorFrame],
    *,
    scale: float,
) -> None:
    """将缩放应用到鼠标指针文件的帧上

    Args:
        frames (list[CursorFrame]): 鼠标指针的帧列表
        scale (float): 缩放倍数
    """
    for frame in frames:
        for cursor in frame:
            cursor.image.scale(
                int(round(cursor.image.width * scale)),
                int(round(cursor.image.height) * scale),
            )
