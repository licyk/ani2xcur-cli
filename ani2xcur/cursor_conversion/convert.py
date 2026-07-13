"""鼠标指针包转换工具"""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from tqdm import tqdm

from ani2xcur.config_parse.win import dict_to_inf_strings_format
from ani2xcur.manager.base import LINUX_CURSOR_LINKS
from ani2xcur.manager.win_cur_manager import (
    extract_scheme_info_from_inf,
    generate_cursor_scheme_inf_string,
)
from ani2xcur.manager.base import CURSOR_KEYS
from ani2xcur.manager.linux_cur_manager import (
    extract_scheme_info_from_desktop_entry,
    generate_install_script,
)
from ani2xcur.config import (
    LINUX_CURSOR_SOURCE_PATH,
    LOGGER_NAME,
    LOGGER_LEVEL,
    LOGGER_COLOR,
)
from ani2xcur.logger import get_logger
from ani2xcur.cursor_conversion.native_cursor import (
    win2xcur_process,
    x2wincur_process,
    Win2xcurArgs,
    X2wincurArgs,
)
from ani2xcur.cursor_conversion.native_cursor.parsers import parse_blob
from ani2xcur.cursor_conversion.native_cursor.transforms import (
    DEFAULT_XCURSOR_SIZES,
    normalize_xcursor_sizes,
)
from ani2xcur.cursor_conversion.native_cursor.writers import to_xcursor
from ani2xcur.file_operations.file_manager import (
    copy_files,
    copy_files_merge,
    save_create_symlink,
)

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def win_cursor_to_x11(
    inf_file: Path,
    output_path: Path,
    win2x_args: Win2xcurArgs,
) -> Path:
    """将 Windows 鼠标指针包转换为 Linux 的鼠标指针包

    Args:
        inf_file (Path): Windows 鼠标指针包中的 INF 文件路径
        output_path (Path): 导出路径
        win2x_args (Win2xcurArgs): 传递给原生 Windows -> Xcursor 转换器的参数
    Returns:
        Path: Linux 的鼠标指针包的完整路径
    """
    win_scheme = extract_scheme_info_from_inf(inf_file)
    logger.debug("INF 鼠标指针配置文件内容: %s", win_scheme)
    cursor_map = win_scheme["cursor_map"]
    cursor_name = win_scheme["scheme_name"]
    win2x_path_list: list[tuple[str, Path, Path]] = []
    completed_cursor_list: list[tuple[Path, Path]] = []
    link_file_list: list[tuple[Path, Path]] = []

    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        # 创建 cursors 文件夹用于存放鼠标指针
        cursors_dir = tmp_dir / cursor_name / "cursors"
        cursors_dir.mkdir(parents=True, exist_ok=True)

        logger.info("配置 '%s' 鼠标指针的转换参数", cursor_name)

        # 生成要进行鼠标指针的转换列表
        for win, linux in zip(CURSOR_KEYS["win"], CURSOR_KEYS["linux"]):
            src = cursor_map[win]["src_path"]
            dst = cursors_dir / linux
            if src is None:
                # 使用补全文件
                src = LINUX_CURSOR_SOURCE_PATH / linux
                logger.debug("添加补全列表: Windows 鼠标指针 `%s` -> Linux 鼠标指针 '%s'", src, dst)
                completed_cursor_list.append((src, dst))
                continue

            logger.debug("添加转换列表: Windows 鼠标指针 `%s` -> Linux 鼠标指针 '%s'", src, dst)
            win2x_path_list.append((linux, src, dst))

        # 补全文件列表
        completed_cursor_list.append((LINUX_CURSOR_SOURCE_PATH / "vertical-text", cursors_dir / "vertical-text"))
        completed_cursor_list.append(
            (
                LINUX_CURSOR_SOURCE_PATH / "wayland-cursor",
                cursors_dir / "wayland-cursor",
            )
        )
        completed_cursor_list.append((LINUX_CURSOR_SOURCE_PATH / "zoom-out", cursors_dir / "zoom-out"))
        completed_cursor_list.append((LINUX_CURSOR_SOURCE_PATH / "zoom-in", cursors_dir / "zoom-in"))

        # 链接文件列表
        link_file_list = [(Path(s), Path(v)) for s, v in LINUX_CURSOR_LINKS]

        # 转换鼠标指针文件
        logger.debug("要进行转换的鼠标指针列表: %s", win2x_path_list)
        logger.debug(
            "Windows -> Linux 转换计划: convert=%s, complete=%s, links=%s",
            len(win2x_path_list),
            len(completed_cursor_list),
            len(link_file_list),
        )
        for name, src, dst in tqdm(win2x_path_list, desc="转换鼠标指针文件"):
            win2x_args["input_file"] = src
            win2x_args["output_path"] = cursors_dir
            win2x_args["save_name"] = name
            logger.debug("调用原生 Windows -> Xcursor 转换器使用的参数: %s", win2x_args)
            win2xcur_process(**win2x_args)

        # 补全鼠标指针文件
        logger.debug("要进行补全的鼠标指针列表: %s", completed_cursor_list)
        for src, dst in tqdm(completed_cursor_list, desc="补全鼠标指针文件"):
            copy_files(src, dst)

        # 创建链接文件
        current_path = Path().absolute()
        os.chdir(cursors_dir)
        logger.debug("要进行链接的鼠标指针别名: %s", link_file_list)
        for s, v in tqdm(link_file_list, desc="链接鼠标指针别名"):
            save_create_symlink(s, v)

        os.chdir(current_path)

        _normalize_xcursor_theme_files(cursors_dir, win2x_args.get("xcursor_sizes"))
        _generate_cinnamon_cursor_thumbnail(cursors_dir)

        # 创建配置文件
        generate_linux_cursor_config(
            cursor_name=cursor_name,
            cursor_path=tmp_dir / cursor_name,
        )

        # 创建安装脚本
        generate_install_script(
            cursor_name=cursor_name,
            save_dir=tmp_dir / cursor_name,
        )

        save_dir = output_path / cursor_name

        # 导出文件到输出文件夹
        copy_files_merge((tmp_dir / cursor_name), save_dir)

    return save_dir


def generate_linux_cursor_config(
    cursor_name: str,
    cursor_path: Path,
) -> None:
    """生成鼠标指针配置文件

    Args:
        cursor_name (str): 鼠标指针名称
        cursor_path (Path): 配置文件的保存路径
    """
    inherited_theme = _linux_cursor_inherited_theme(cursor_name)
    cursor_config = f"""
[Icon Theme]
Name={cursor_name}
Inherits={inherited_theme}
""".strip()
    index_config = f"""
[Icon Theme]
Name={cursor_name}
Comment={cursor_name} cursor for Linux
Inherits={inherited_theme}
""".strip()

    logger.debug("鼠标指针配置文件内容:\n\n- cursor.theme:\n```\n%s\n```\n\n- index.theme:\n```\n%s\n```", cursor_config, index_config)
    with open((cursor_path / "cursor.theme"), "w", encoding="utf-8") as file:
        file.write(cursor_config)
    with open((cursor_path / "index.theme"), "w", encoding="utf-8") as file:
        file.write(index_config)


def _linux_cursor_inherited_theme(cursor_name: str) -> str:
    """返回不会递归继承自身的回退光标主题名称。

    Args:
        cursor_name (str): 当前光标主题名称。
    Returns:
        str: 回退光标主题名称。
    """
    if cursor_name.casefold() == "default":
        return "Adwaita"
    return "default"


def _normalize_xcursor_theme_files(
    cursors_dir: Path,
    xcursor_sizes: list[int] | None,
) -> None:
    """补齐主题目录中真实 Xcursor 文件的名义尺寸列表。

    Args:
        cursors_dir (Path): Xcursor 主题的 cursors 目录。
        xcursor_sizes (list[int] | None): 目标名义尺寸列表。
    """
    target_sizes = DEFAULT_XCURSOR_SIZES if xcursor_sizes is None else xcursor_sizes
    normalized_count = 0
    skipped_count = 0
    logger.debug("开始补齐主题 Xcursor 尺寸: cursors_dir='%s', target_sizes=%s", cursors_dir, target_sizes)
    for cursor_file in cursors_dir.iterdir():
        if cursor_file.is_symlink():
            skipped_count += 1
            logger.debug("跳过 Xcursor 尺寸补齐软链接: '%s'", cursor_file)
            continue
        if not cursor_file.is_file():
            skipped_count += 1
            logger.debug("跳过 Xcursor 尺寸补齐非文件路径: '%s'", cursor_file)
            continue

        try:
            frames = parse_blob(cursor_file.read_bytes())
            source_sizes = sorted({cursor.nominal for frame in frames for cursor in frame.images})
            normalize_xcursor_sizes(frames, target_sizes)
        except ValueError as e:
            skipped_count += 1
            logger.debug("跳过无法补齐尺寸的光标文件: '%s', 原因: %s", cursor_file, e)
            continue

        cursor_file.write_bytes(to_xcursor(frames))
        normalized_count += 1
        target_summary = sorted({cursor.nominal for frame in frames for cursor in frame.images})
        logger.debug(
            "补齐 Xcursor 文件尺寸完成: '%s', source_sizes=%s, target_sizes=%s",
            cursor_file,
            source_sizes,
            target_summary,
        )
    logger.debug(
        "主题 Xcursor 尺寸补齐完成: cursors_dir='%s', normalized=%s, skipped=%s",
        cursors_dir,
        normalized_count,
        skipped_count,
    )


def _generate_cinnamon_cursor_thumbnail(
    cursors_dir: Path,
    target_size: int = 32,
) -> Path | None:
    """为 Cinnamon 主题选择器生成光标缩略图。

    Cinnamon 优先读取 ``cursors/thumbnail.png``，而不是直接从 Xcursor
    文件渲染预览。这里优先使用 ``left_ptr``，并在缺失时尝试
    ``default``，取第一帧中名义尺寸最接近目标尺寸的图像。

    Args:
        cursors_dir (Path): Xcursor 主题的 cursors 目录。
        target_size (int): Cinnamon 选择器中的目标预览尺寸。
    Returns:
        Path | None: 生成的 PNG 路径；没有可用光标图像时返回 None。
    """
    for cursor_name in ["left_ptr", "default"]:
        cursor_path = cursors_dir / cursor_name
        if not cursor_path.is_file():
            continue

        try:
            frames = parse_blob(cursor_path.read_bytes())
        except (OSError, ValueError) as e:
            logger.debug("无法从 '%s' 生成 Cinnamon 光标缩略图: %s", cursor_path, e)
            continue

        if not frames or not frames[0].images:
            continue

        cursor_image = min(
            frames[0].images,
            key=lambda image: (abs(image.nominal - target_size), image.nominal),
        )
        thumbnail_path = cursors_dir / "thumbnail.png"
        cursor_image.image.convert("RGBA").save(thumbnail_path, format="PNG")
        logger.debug(
            "生成 Cinnamon 光标缩略图: source='%s', nominal_size=%s, actual_size=%s, output='%s'",
            cursor_path,
            cursor_image.nominal,
            cursor_image.image.size,
            thumbnail_path,
        )
        return thumbnail_path

    logger.warning("光标主题中没有可用的 left_ptr/default 图像，无法生成 Cinnamon 预览图: '%s'", cursors_dir)
    return None


def x11_cursor_to_win(
    desktop_entry_file: Path,
    output_path: Path,
    x2win_args: X2wincurArgs,
) -> Path:
    """将 Linux 鼠标指针包转换为 Windows 的鼠标指针包

    Args:
        desktop_entry_file (Path): Linux 鼠标指针包中的 DesktopEntry 文件路径
        output_path (Path): 导出路径
        x2win_args (X2wincurArgs): 传递给原生 Xcursor -> Windows 转换器的参数
    Returns:
        Path: Linux 的鼠标指针包的完整路径
    """
    linux_scheme = extract_scheme_info_from_desktop_entry(desktop_entry_file)
    logger.debug("DesktopEntry 鼠标指针配置文件内容: %s", linux_scheme)
    cursor_map = linux_scheme["cursor_map"]
    cursor_name = linux_scheme["scheme_name"]
    x2win_path_list: list[tuple[str, Path, Path]] = []
    cursor_save_paths: list[tuple[str, Path | None]] = []

    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        # 创建文件夹用于存放鼠标指针
        cursors_dir = tmp_dir / cursor_name
        cursors_dir.mkdir(parents=True, exist_ok=True)

        logger.info("配置 '%s' 鼠标指针的转换参数", cursor_name)

        # 生成要进行鼠标指针的转换列表
        for win, linux in zip(CURSOR_KEYS["win"], CURSOR_KEYS["linux"]):
            src = cursor_map[win]["src_path"]
            dst = cursors_dir / linux
            if src is None:
                # 使用补全文件
                src = LINUX_CURSOR_SOURCE_PATH / linux

            x2win_path_list.append((win, src, dst))

        # 转换鼠标指针文件
        logger.debug("要进行转换的鼠标指针列表: %s", x2win_path_list)
        logger.debug("Linux -> Windows 转换计划: convert=%s", len(x2win_path_list))
        for name, src, dst in tqdm(x2win_path_list, desc="转换鼠标指针文件"):
            x2win_args["input_file"] = src
            x2win_args["output_path"] = cursors_dir
            x2win_args["save_name"] = name
            logger.debug("调用原生 Xcursor -> Windows 转换器的参数: %s", x2win_args)
            if src is not None:
                cursor_save_path = x2wincur_process(**x2win_args)
            else:
                cursor_save_path = None

            logger.debug("添加转换列表: Linux 鼠标指针 `%s` -> Windows 鼠标指针 '%s'", src, dst)
            cursor_save_paths.append((name, cursor_save_path))

        # 创建配置文件
        generate_win_cursor_config(
            cursor_name=cursor_name,
            cursor_path=cursors_dir,
            cursor_save_paths=cursor_save_paths,
        )

        save_dir = output_path / cursor_name

        # 导出文件到输出文件夹
        copy_files_merge((tmp_dir / cursor_name), save_dir)

    return save_dir


def generate_win_cursor_config(
    cursor_name: str,
    cursor_path: Path,
    cursor_save_paths: list[tuple[str, Path | None]],
) -> None:
    """生成 Windows 鼠标指针配置文件

    Args:
        cursor_name (str): 鼠标指针名称
        cursor_path (Path): 鼠标指针包路径
        cursor_save_paths (list[tuple[str, Path | None]]): 鼠标指针类型对应的保存路径
    """

    cursor_paths: list[Path] = []  # 用于导出的路径列表
    strings: dict[str, str] = {}  # [Strings] 部分
    wreg_list: list[str] = []  # [Wreg] 部分
    paths_to_reg: list[str] = []  # [Scheme.Reg] 部分

    destination_dirs = r'10,"%CUR_DIR%"'
    strings["SCHEME_NAME"] = cursor_name
    strings["CUR_DIR"] = rf"Cursors\{cursor_name}"
    wreg_list.append(r'HKCU,"Control Panel\Cursors",,0x00020000,"%SCHEME_NAME%"')

    for name, path in cursor_save_paths:
        if path is not None:
            cursor_paths.append(path)
            wreg_list.append(rf'HKCU,"Control Panel\Cursors",{name},0x00020000,"%10%\%CUR_DIR%\%{name}%"')
            strings[name] = path.name
            paths_to_reg.append(rf"%10%\%CUR_DIR%\%{name}%")
        else:
            paths_to_reg.append("")

    # 配置 [Wreg] 字段
    wreg_list.append(r'HKLM,"SOFTWARE\Microsoft\Windows\CurrentVersion\Runonce\Setup\","",,"rundll32.exe shell32.dll,Control_RunDLL main.cpl @0"')
    wreg = "\n".join(wreg_list)

    # 配置 [Scheme.Reg] 字段
    paths_to_reg_string = ",".join(paths_to_reg)
    scheme_reg = rf'HKCU,"Control Panel\Cursors\Schemes","%SCHEME_NAME%",0x00020000,"{paths_to_reg_string}"'

    # 配置 [Scheme.Cur] 字段
    scheme_cur = "\n".join([f'"{x.name}"' for x in cursor_paths])

    inf = generate_cursor_scheme_inf_string(
        destination_dirs=destination_dirs,
        wreg=wreg,
        scheme_reg=scheme_reg,
        scheme_cur=scheme_cur,
        strings=dict_to_inf_strings_format(strings),
    )

    logger.debug("鼠标指针配置文件内容:\n```\n%s\n```", inf)
    with open(cursor_path / "AutoSetup.inf", "w", encoding="gbk") as f:
        f.write(inf)
