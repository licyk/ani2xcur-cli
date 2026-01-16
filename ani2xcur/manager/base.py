"""管理工具基础配置"""

from pathlib import Path
from typing import (
    TypeAlias,
    TypedDict,
)


WIN_CURSOR_KEYS = [
    "Arrow",  # 正常选择
    "Help",  # 帮助选择
    "AppStarting",  # 后台运行
    "Wait",  # 忙
    "Crosshair",  # 精确选择
    "IBeam",  # 文本选择
    "NWPen",  # 手写
    "No",  # 不可用
    "SizeNS",  # 垂直调整大小
    "SizeWE",  # 水平调整大小
    "SizeNWSE",  # 沿对角线调整大小 1
    "SizeNESW",  # 沿对角线调整大小 2
    "SizeAll",  # 移动
    "UpArrow",  # 候选
    "Hand",  # 链接选择
    "Pin",  # 位置选择
    "Person",  # 个人选择
]
"""Windows 鼠标指针对应的键列表"""

LINUX_CURSOR_KEYS = [
    "left_ptr",  # 正常选择
    "question_arrow",  # 帮助选择
    "left_ptr_watch",  # 后台运行
    "wait",  # 忙
    "cross",  # 精确选择
    "xterm",  # 文本选择
    "pencil",  # 手写
    "circle",  # 不可用
    "bottom_side",  # 垂直调整大小
    "left_side",  # 水平调整大小
    "bottom_right_corner",  # 沿对角线调整大小 1
    "bottom_left_corner",  # 沿对角线调整大小 2
    "move",  # 移动
    "dotbox",  # 候选
    "hand2",  # 链接选择
    "center_ptr",  # 位置选择
    "right_ptr",  # 个人选择
]
"""Linux 鼠标指针对应的键列表"""


class CursorKeys(TypedDict):
    """鼠标指针键名表"""

    win: list[str]
    """Windows 鼠标指针对应的键列表"""

    linux: list[str]
    """Linux 鼠标指针对应的键列表"""


CURSOR_KEYS: CursorKeys = {"win": WIN_CURSOR_KEYS, "linux": LINUX_CURSOR_KEYS}
"""鼠标指针对应的键值表 (Windows / Linux)"""


class CursorFilePair(TypedDict):
    """单个光标文件的源路径与目标路径"""

    dst_path: Path | None
    """复制到系统的目标路径"""

    src_path: Path | None
    """原始文件路径"""


class KnownCursorMap(TypedDict, total=False):
    """Windows / Linux 标准鼠标指针类型, 键名以 Windows 中的作为标准"""

    Arrow: CursorFilePair | None
    """正常选择 (Arrow <-> left_ptr)"""

    Help: CursorFilePair | None
    """帮助选择 (Help <-> question_arrow)"""

    AppStarting: CursorFilePair | None
    """后台运行 (AppStarting <-> left_ptr_watch)"""

    Wait: CursorFilePair | None
    """忙 (Wait <-> wait)"""

    Crosshair: CursorFilePair | None
    """精确选择 (Crosshair <-> cross)"""

    IBeam: CursorFilePair | None
    """文本选择 (IBeam <-> xterm)"""

    NWPen: CursorFilePair | None
    """手写 (NWPen <-> pencil)"""

    No: CursorFilePair | None
    """不可用 (No <-> circle)"""

    SizeNS: CursorFilePair | None
    """垂直调整大小 (SizeNS <-> bottom_side)"""

    SizeWE: CursorFilePair | None
    """水平调整大小 (SizeWE <-> left_side)"""

    SizeNWSE: CursorFilePair | None
    """沿对角线调整大小 1 (SizeNWSE <-> bottom_right_corner)"""

    SizeNESW: CursorFilePair | None
    """沿对角线调整大小 2 (SizeNESW <-> bottom_left_corner)"""

    SizeAll: CursorFilePair | None
    """移动 (SizeAll <-> move)"""

    UpArrow: CursorFilePair | None
    """候选 (UpArrow <-> dotbox)"""

    Hand: CursorFilePair | None
    """链接选择 (Hand <-> hand2)"""

    Pin: CursorFilePair | None
    """位置选择 (Pin <-> center_ptr)"""

    Person: CursorFilePair | None
    """个人选择 (Person <-> right_ptr)"""


CursorMap: TypeAlias = dict[str, CursorFilePair] | KnownCursorMap
"""鼠标指针类型与对应的路径地图"""


class WinCursorsConfig(TypedDict, total=False):
    """Windows 鼠标指针配置信息"""

    Arrow: str | None
    """正常选择 (Arrow -> left_ptr)"""

    Help: str | None
    """帮助选择 (Help -> question_arrow)"""

    AppStarting: str | None
    """后台运行 (AppStarting -> left_ptr_watch)"""

    Wait: str | None
    """忙 (Wait -> wait)"""

    Crosshair: str | None
    """精确选择 (Crosshair -> cross)"""

    IBeam: str | None
    """文本选择 (IBeam -> xterm)"""

    NWPen: str | None
    """手写 (NWPen -> pencil)"""

    No: str | None
    """不可用 (No -> circle)"""

    SizeNS: str | None
    """垂直调整大小 (SizeNS -> bottom_side)"""

    SizeWE: str | None
    """水平调整大小 (SizeWE -> left_side)"""

    SizeNWSE: str | None
    """沿对角线调整大小 1 (SizeNWSE -> bottom_right_corner)"""

    SizeNESW: str | None
    """沿对角线调整大小 2 (SizeNESW -> bottom_left_corner)"""

    SizeAll: str | None
    """移动 (SizeAll -> move)"""

    UpArrow: str | None
    """候选 (UpArrow -> dotbox)"""

    Hand: str | None
    """链接选择 (Hand -> hand2)"""

    Pin: str | None
    """位置选择 (Pin -> center_ptr)"""

    Person: str | None
    """个人选择 (Person -> right_ptr)"""


class LinuxCursorsConfig(TypedDict, total=False):
    """Linux 标准鼠标指针类型"""

    left_ptr: str | None
    """正常选择 (left_ptr -> Arrow)"""

    question_arrow: str | None
    """帮助选择 (question_arrow -> Help)"""

    left_ptr_watch: str | None
    """后台运行 (left_ptr_watch -> AppStarting)"""

    wait: str | None
    """忙 (wait -> Wait)"""

    cross: str | None
    """精确选择 (cross -> Crosshair)"""

    xterm: str | None
    """文本选择 (xterm -> IBeam)"""

    pencil: str | None
    """手写 (pencil -> NWPen)"""

    circle: str | None
    """不可用 (circle -> No)"""

    bottom_side: str | None
    """垂直调整大小 (bottom_side -> SizeNS)"""

    left_side: str | None
    """水平调整大小 (left_side -> SizeWE)"""

    bottom_right_corner: str | None
    """沿对角线调整大小 1 (bottom_right_corner -> SizeNWSE)"""

    bottom_left_corner: str | None
    """沿对角线调整大小 2 (bottom_left_corner -> SizeNESW)"""

    move: str | None
    """移动 (move -> SizeAll)"""

    dotbox: str | None
    """候选 (dotbox -> UpArrow)"""

    hand2: str | None
    """链接选择 (hand2 -> Hand)"""

    center_ptr: str | None
    """位置选择 (center_ptr -> Pin)"""

    right_ptr: str | None
    """个人选择 (right_ptr -> Person)"""


LINUX_CURSOR_LINKS = [
    # left_ptr
    ["left_ptr", "context-menu"],
    ["left_ptr", "grabbing"],
    ["left_ptr", "hand1"],
    ["left_ptr", "arrow"],
    ["left_ptr", "closedhand"],
    ["left_ptr", "default"],
    ["left_ptr", "dnd-none"],
    ["left_ptr", "grab"],
    ["left_ptr", "openhand"],
    ["left_ptr", "top_left_arrow"],
    ["left_ptr", "fcf21c00b30f7e3f83fe0dfd12e71cff"],
    # left_ptr_watch
    ["left_ptr_watch", "progress"],
    ["left_ptr_watch", "00000000000000020006000e7e9ffc3f"],
    ["left_ptr_watch", "08e8e1c95fe2fc01f976f1e063a24ccd"],
    ["left_ptr_watch", "3ecb610c1bf2410f44200f48c40d3599"],
    # right_ptr
    ["right_ptr", "draft_large"],
    ["right_ptr", "draft_small"],
    ["right_ptr", "e-resize"],
    # move
    ["move", "all-scroll"],
    ["move", "fleur"],
    ["move", "size_all"],
    ["move", "4498f0e0c1937ffe01fd06f973665830"],
    ["move", "9081237383d90e509aa00f00170e968f"],
    # question_arrow
    ["question_arrow", "dnd-ask"],
    ["question_arrow", "help"],
    ["question_arrow", "left_ptr_help"],
    ["question_arrow", "whats_this"],
    ["question_arrow", "5c6cd98b3f3ebcb1f9c7f1c204630408"],
    ["question_arrow", "d9ce0ab605698f320427677b458ad60b"],
    # xterm
    ["xterm", "ibeam"],
    ["xterm", "text"],
    # wait
    ["wait", "watch"],
    # hand2
    ["hand2", "pointer"],
    ["hand2", "pointing_hand"],
    ["hand2", "9d800788f1b08800ae810202380a0822"],
    ["hand2", "e29285e634086352946a0e7090d73106"],
    # pencil
    ["pencil", "copy"],
    ["pencil", "dnd-copy"],
    ["pencil", "dnd-move"],
    ["pencil", "dnd-link"],
    ["pencil", "link"],
    ["pencil", "pointer-move"],
    ["pencil", "alias"],
    ["pencil", "draft"],
    ["pencil", "1081e37283d90000800003c07f3ef6bf"],
    ["pencil", "3085a0e285430894940527032f8b26df"],
    ["pencil", "6407b0e94181790501fd1e167b474872"],
    ["pencil", "640fb0e74195791501fd1ed57b41487f"],
    ["pencil", "a2a266d0498c3104214a47bd64ab0fc8"],
    ["pencil", "b66166c04f8c3109214a4fbd64a50fc8"],
    # circle
    ["circle", "crossed_circle"],
    ["circle", "dnd_no_drop"],
    ["circle", "X_cursor"],
    ["circle", "x-cursor"],
    ["circle", "forbidden"],
    ["circle", "no-drop"],
    ["circle", "not-allowed"],
    ["circle", "pirate"],
    ["circle", "03b6e0fcb3499374a867c041f52298f0"],
    # cross
    ["cross", "crosshair"],
    ["cross", "tcross"],
    ["cross", "color-picker"],
    ["cross", "cross_reverse"],
    ["cross", "diamond_cross"],
    # bottom_left_corner
    ["bottom_left_corner", "fd_double_arrow"],
    ["bottom_left_corner", "ll_angle"],
    ["bottom_left_corner", "top_right_corner"],
    ["bottom_left_corner", "ur_angle"],
    ["bottom_left_corner", "ne-resize"],
    ["bottom_left_corner", "nesw-resize"],
    ["bottom_left_corner", "size_bdiag"],
    ["bottom_left_corner", "sw-resize"],
    ["bottom_left_corner", "fcf1c3c7cd4491d801f1e1c78f100000"],
    # bottom_right_corner
    ["bottom_right_corner", "bd_double_arrow"],
    ["bottom_right_corner", "lr_angle"],
    ["bottom_right_corner", "top_left_corner"],
    ["bottom_right_corner", "ul_angle"],
    ["bottom_right_corner", "nw-resize"],
    ["bottom_right_corner", "nwse-resize"],
    ["bottom_right_corner", "se-resize"],
    ["bottom_right_corner", "size_fdiag"],
    ["bottom_right_corner", "c7088f0f3e6c8088236ef8e1e3e70000"],
    # bottom_side
    ["bottom_side", "bottom_tee"],
    ["bottom_side", "plus"],
    ["bottom_side", "sb_down_arrow"],
    ["bottom_side", "sb_up_arrow"],
    ["bottom_side", "sb_v_double_arrow"],
    ["bottom_side", "top_side"],
    ["bottom_side", "top_tee"],
    ["bottom_side", "cell"],
    ["bottom_side", "double_arrow"],
    ["bottom_side", "down-arrow"],
    ["bottom_side", "n-resize"],
    ["bottom_side", "ns-resize"],
    ["bottom_side", "row-resize"],
    ["bottom_side", "s-resize"],
    ["bottom_side", "up-arrow"],
    ["bottom_side", "v_double_arrow"],
    ["bottom_side", "size_ver"],
    ["bottom_side", "00008160000006810000408080010102"],
    ["bottom_side", "2870a09082c31050810ffdffffe0204"],
    # left_side
    ["left_side", "left_tee"],
    ["left_side", "right_side"],
    ["left_side", "right_tee"],
    ["left_side", "sb_h_double_arrow"],
    ["left_side", "sb_left_arrow"],
    ["left_side", "sb_right_arrow"],
    ["left_side", "col-resize"],
    ["left_side", "ew-resize"],
    ["left_side", "h_double_arrow"],
    ["left_side", "left-arrow"],
    ["left_side", "right-arrow"],
    ["left_side", "size-hor"],
    ["left_side", "size-ver"],
    ["left_side", "split_h"],
    ["left_side", "split_v"],
    ["left_side", "w-resize"],
    ["left_side", "size_hor"],
    ["left_side", "028006030e0e7ebffc7f7070c0600140"],
    ["left_side", "14fef782d02440884392942c1120523"],
    # dotbox
    ["dotbox", "dot_box_mask"],
    ["dotbox", "draped_box"],
    ["dotbox", "icon"],
    ["dotbox", "target"],
]
"""Linux 鼠标指针需要链接的别名"""


class LocalCursor(TypedDict):
    """本地已安装的鼠标指针配置"""

    name: str
    """鼠标指针配置名称"""

    cursor_files: list[Path]
    """鼠标指针文件列表"""

    install_paths: list[Path]
    """鼠标指针安装路径列表 (鼠标指针文件所在父路径)"""


CursorSchemesList: TypeAlias = list[LocalCursor]
"""本地已安装的鼠标指针配置列表"""

LINUX_ICONS_PATH = Path("/usr/share/icons")
"""Linux 图标目录"""

LINUX_USER_ICONS_PATH = Path("~/.icons").expanduser()
"""Linux 用户图标目录"""


class CurrentCursorInfo(TypedDict):
    """当前桌面平台使用的鼠标指针名称和大小信息"""

    platform: str
    """桌面平台"""

    cursor_name: str
    """鼠标指针名称"""

    cursor_size: int
    """鼠标指针大小"""


CurrentCursorInfoList: TypeAlias = list[CurrentCursorInfo]
"""当前桌面平台使用的鼠标指针名称和大小信息列表"""

WINDOWS_USER_CURSOR_PATH = Path("~").expanduser() / "AppData" / "Local" / "Cursors"
"""Windows 系统安装鼠标的用户目录路径"""
