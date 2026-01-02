import os
from pathlib import Path
from tempfile import TemporaryDirectory
from ani2xcur.inf_parse.win import dict_to_inf_strings_format
from ani2xcur.manager.base import LINUX_CURSOR_LINKS
from ani2xcur.manager.win_cur_manager import get_scheme_from_inf_file, generate_cursor_scheme_inf_string
from ani2xcur.manager.base import CURSOR_KEYS
from ani2xcur.manager.linux_cur_manager import get_scheme_from_desktop_entry_file
from ani2xcur.config import LINUX_CURSOR_SOURCE_PATH
from ani2xcur.cursor_conversion.win2xcur_warp import win2xcur_process, x2wincur_process, Win2xcurArgs, X2wincurArgs
from ani2xcur.file_operations.file_manager import copy_files, create_symlink


def win_cursor_to_x11(
    inf_file: Path,
    output_path: Path,
    win2x_args: Win2xcurArgs,
) -> Path:
    """将 Windows 鼠标指针包转换为 Linux 的鼠标指针包

    Args:
        inf_file (Path): Windows 鼠标指针包中的 INF 文件路径
        output_path (Path): 导出路径
        win2x_args (Win2xcurArgs): 传递给 win2xcur_process() 函数的参数
    Returns:
        Path: Linux 的鼠标指针包的完整路径
    """
    win_scheme = get_scheme_from_inf_file(inf_file)
    cursor_map = win_scheme["cursor_map"]
    cursor_name = win_scheme["scheme_name"]
    win2x_path_list: list[list[str, Path]] = []
    completed_cursor_list: list[list[str, Path]] = []
    link_file_list: list[list[Path, Path]] = []

    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        # 创建 cursors 文件夹用于存放鼠标指针
        cursors_dir = tmp_dir / cursor_name / "cursors"
        cursors_dir.mkdir(parents=True, exist_ok=True)

        # 生成要进行鼠标指针的转换列表
        for win, linux in zip(CURSOR_KEYS["win"], CURSOR_KEYS["linux"]):
            src = cursor_map[win]["src_path"]
            dst = cursors_dir / linux
            if src is None:
                # 使用补全文件
                src = LINUX_CURSOR_SOURCE_PATH / linux
                completed_cursor_list.append([src, dst])
                continue

            win2x_path_list.append([linux, src, dst])

        # 补全文件列表
        completed_cursor_list.append(
            [LINUX_CURSOR_SOURCE_PATH / "vertical-text", cursors_dir / "vertical-text"]
        )
        completed_cursor_list.append(
            [
                LINUX_CURSOR_SOURCE_PATH / "wayland-cursor",
                cursors_dir / "wayland-cursor",
            ]
        )
        completed_cursor_list.append(
            [LINUX_CURSOR_SOURCE_PATH / "zoom-out", cursors_dir / "zoom-out"]
        )
        completed_cursor_list.append(
            [LINUX_CURSOR_SOURCE_PATH / "zoom-in", cursors_dir / "zoom-in"]
        )

        # 链接文件列表
        link_file_list = [[Path(s), Path(v)] for s, v in LINUX_CURSOR_LINKS]

        # 转换鼠标指针文件
        for name, src, dst in win2x_path_list:
            win2x_args["input_file"] = src
            win2x_args["output_path"] = cursors_dir
            win2x_args["save_name"] = name
            win2xcur_process(**win2x_args)

        # 补全鼠标指针文件
        for src, dst in completed_cursor_list:
            copy_files(src, dst)

        # 创建链接文件
        current_path = Path().absolute()
        os.chdir(cursors_dir)
        for s, v in link_file_list:
            create_symlink(s, v)
        os.chdir(current_path)

        # 创建配置文件
        generate_linux_cursor_config(
            cursor_name=cursor_name,
            cursor_path=tmp_dir / cursor_name,
        )

        # 导出文件到输出文件夹
        copy_files((tmp_dir / cursor_name), output_path)

    return output_path / cursor_name


def generate_linux_cursor_config(
    cursor_name: str,
    cursor_path: Path,
) -> None:
    """生成鼠标指针配置文件

    Args:
        cursor_name (str): 鼠标指针名称
        cursor_path (Path): 配置文件的保存路径
    """
    cursor_config = f"""
[Icon Theme]
Name={cursor_name}
Inherits={cursor_name}
""".strip()
    index_config = f"""
[Icon Theme]
Name={cursor_name}
Comment={cursor_name} cursor for Linux
Inherits={cursor_name}
""".strip()
    with open((cursor_path / "cursor.theme"), "w", encoding="utf-8") as file:
        file.write(cursor_config)
    with open((cursor_path / "index.theme"), "w", encoding="utf-8") as file:
        file.write(index_config)


def x11_cursor_to_win(
    desktop_entry_file: Path,
    output_path: Path,
    x2win_args: X2wincurArgs,
) -> Path:
    """将 Linux 鼠标指针包转换为 Windows 的鼠标指针包

    Args:
        desktop_entry_file (Path): Windows 鼠标指针包中的 INF 文件路径
        output_path (Path): 导出路径
        x2win_args (X2wincurArgs): 传递给 x2wincur_process() 函数的参数
    Returns:
        Path: Linux 的鼠标指针包的完整路径
    """
    linux_scheme = get_scheme_from_desktop_entry_file(desktop_entry_file)
    cursor_map = linux_scheme["cursor_map"]
    cursor_name = linux_scheme["scheme_name"]
    x2win_path_list: list[list[str, Path]] = []
    cursor_save_paths: list[tuple[str, Path | None]] = []

    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        # 创建文件夹用于存放鼠标指针
        cursors_dir = tmp_dir / cursor_name
        cursors_dir.mkdir(parents=True, exist_ok=True)

        # 生成要进行鼠标指针的转换列表
        for win, linux in zip(CURSOR_KEYS["win"], CURSOR_KEYS["linux"]):
            src = cursor_map[win]["src_path"]
            dst = cursors_dir / linux
            if src is None:
                # 使用补全文件
                src = LINUX_CURSOR_SOURCE_PATH / linux
        
            x2win_path_list.append([win, src, dst])

        # 转换鼠标指针文件
        for name, src, dst in x2win_path_list:
            x2win_args["input_file"] = src
            x2win_args["output_path"] = cursors_dir
            x2win_args["save_name"] = name
            if src is not None:
                cursor_save_path = x2wincur_process(**x2win_args)
            else:
                cursor_save_path = None
            cursor_save_paths.append((name, cursor_save_path))

        # 创建配置文件
        generate_win_cursor_config(
            cursor_name=cursor_name,
            cursor_path=cursors_dir,
            cursor_save_paths=cursor_save_paths,
        )

        # 导出文件到输出文件夹
        copy_files((tmp_dir / cursor_name), output_path)

    return output_path / cursor_name

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
    destination_dirs = r'10,"%CUR_DIR%"'
    scheme_cur = ""
    strings: dict[str, str] = {}
    strings["SCHEME_NAME"] = cursor_name
    strings["CUR_DIR"] = rf"Cursors\{cursor_name}"
    scheme_reg = r'HKCU,"Control Panel\Cursors\Schemes","%SCHEME_NAME%",,"'
    wreg = r'HKCU,"Control Panel\Cursors",,0x00020000,"%SCHEME_NAME%"'
    for name, path in cursor_save_paths:
        scheme_reg += rf'%10%\%CUR_DIR%\%{name}%'
        if path is not None:
            scheme_cur += "\n"
            scheme_cur += rf'"{path.name}"'
            wreg += "\n"
            wreg += rf'HKCU,"Control Panel\Cursors",{name},0x00020000,"%10%\%CUR_DIR%\%{name}%"'
            strings[name] = path.name

        if name != cursor_save_paths[-1][0]:
            scheme_reg += ","

    scheme_reg += '"'
    wreg += "\n"
    wreg += r'HKLM,"SOFTWARE\Microsoft\Windows\CurrentVersion\Runonce\Setup\","",,"rundll32.exe shell32.dll,Control_RunDLL main.cpl @0"'
    inf = generate_cursor_scheme_inf_string(
        destination_dirs=destination_dirs,
        wreg=wreg,
        scheme_reg=scheme_reg,
        scheme_cur=scheme_cur,
        strings=dict_to_inf_strings_format(strings),
    )
    with open(cursor_path / "AutoSetup.inf", "w", encoding="utf-8") as f:
        f.write(inf)
