try:
    import winreg
except ImportError:
    winreg = None

import ctypes
import os
import re
from typing import TypedDict
from pathlib import Path

from ani2xcur.inf_parse.win import get_cursor_scheme_data_from_inf
from ani2xcur.logger import get_logger
from ani2xcur.config import LOGGER_LEVEL, LOGGER_COLOR, LOGGER_NAME
from ani2xcur.file_operations.file_manager import remove_files, copy_files
from ani2xcur.inf_parse.win import (
    dict_to_inf_strings_format,
)
from ani2xcur.manager.base import CURSOR_KEYS, CursorMap, WinCursorsConfig
from ani2xcur.utils import extend_list_to_length, lowercase_dict_keys

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


class CursorSchemes(TypedDict):
    """鼠标指针方案配置"""

    name: str
    """方案名称"""

    dtype: int
    """类型"""

    data: str
    """指针方案数据"""


CursorSchemesList = list[CursorSchemes]
"""鼠标指针方案配置列表"""


def get_current_cursors() -> WinCursorsConfig:
    """获取当前鼠标指针的配置

    Returns:
        WinCursorsConfig: 鼠标指针配置字典
    """
    path = r"Control Panel\Cursors"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
        result: WinCursorsConfig = {}
        for name in CURSOR_KEYS["win"]:
            try:
                value = winreg.QueryValueEx(key, name)[0]
                result[name] = value
            except FileNotFoundError:
                result[name] = None
        return result


def list_schemes() -> CursorSchemesList:
    """获取鼠标指针方案列表

    Returns:
        CursorSchemesList: 鼠标指针方案列表
    """
    path = r"Control Panel\Cursors\Schemes"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
        schemes: CursorSchemesList = []
        i = 0
        try:
            while True:
                name, data, dtype = winreg.EnumValue(key, i)
                schemes.append({"name": name, "data": data, "dtype": dtype})
                i += 1
        except OSError:
            pass
        return schemes


def get_scheme(scheme_name: str) -> str:
    """获取指定鼠标指针预设

    Args:
        scheme_name (str): 鼠标指针预设名称
    Returns:
        str: 鼠标指针预设的数据
    Raises:
        ValueError: 未找到鼠标指针预设时
    """
    schemes = list_schemes()
    for scheme in schemes:
        if scheme["name"] == scheme_name:
            return scheme["data"]
    raise ValueError(f"未找到指定的鼠标指针预设: {scheme_name}")


def resolve_env_vars(text: str) -> str:
    """解析字符串中的环境变量

    Args:
        text (str): 包含环境变量的字符串, 例如 "%SYSTEMROOT%\\Cursors\\..."
    Returns:
        str: 解析后的字符串, 环境变量会被替换为实际值
    """

    def _replace_env_var(match: re.Match) -> str:
        env_var = match.group(1)
        return os.environ.get(env_var, match.group(0))

    pattern = r"%([^%]+)%"
    result = re.sub(pattern, _replace_env_var, text)
    return result


def apply_scheme(scheme_name: str) -> None:
    """应用指定的鼠标指针方案

    Args:
        scheme_name (str): 鼠标指针预设名称
    """
    scheme_data = get_scheme(scheme_name)
    schemes_path = scheme_data.split(",")
    reg_path = r"Control Panel\Cursors"
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, scheme_name)
        for name, path in zip(CURSOR_KEYS["win"], schemes_path):
            if not os.path.exists(resolve_env_vars(path)):
                continue

            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, path)

    refresh_system_params()


def delete_scheme(scheme_name: str) -> None:
    """删除指定鼠标指针方案

    Args:
        scheme_name (str): 鼠标指针方案名称
    Raises:
        ValueError: 当要删除的方案是当前应用的方案时
        FileNotFoundError: 未找到指定鼠标指针方案
    """
    cursors_path = r"Control Panel\Cursors"
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, cursors_path, 0, winreg.KEY_READ
        ) as key:
            current_scheme, _ = winreg.QueryValueEx(key, "")
            if current_scheme == scheme_name:
                raise ValueError(f"无法删除当前正在使用的鼠标指针方案: {scheme_name}")
    except FileNotFoundError:
        pass

    path = r"Control Panel\Cursors\Schemes"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE) as key:
        try:
            winreg.DeleteValue(key, scheme_name)
            delete_scheme_file(scheme_name)
        except FileNotFoundError as e:
            logger.error("未找到指定鼠标指针方案: %s", scheme_name)
            raise FileNotFoundError(f"未找到指定鼠标指针方案: {scheme_name}") from e


def delete_scheme_file(scheme_name: str) -> None:
    """删除指定鼠标指针方案对应的鼠标指针文件

    Args:
        scheme_name (str): 鼠标指针方案名称
    Raises:
        OSError: 删除鼠标指针文件失败时
    """
    delete_file_list: list[Path] = []
    cursor_path_list: list[Path] = []
    schemes = list_schemes()
    current_cursor_path_set = set(
        [
            Path(resolve_env_vars(p))
            for p in get_scheme(scheme_name).split(",")
            if p.strip() != "" and Path(resolve_env_vars(p)).is_file()
        ]
    )
    for scheme in schemes:
        if scheme["name"] == scheme_name:
            continue

        cursor_path_list += [
            Path(resolve_env_vars(p))
            for p in scheme["data"].split(",")
            if p.strip() != "" and Path(resolve_env_vars(p)).is_file()
        ]
    cursor_path_set = set(cursor_path_list)
    for cursor in current_cursor_path_set:
        if cursor not in cursor_path_set and cursor not in delete_file_list:
            delete_file_list.append(cursor)

    errors = []
    delete_failed_files: list[Path] = []

    for file in delete_file_list:
        try:
            remove_files(file)
        except Exception as e:
            logger.error(
                "删除鼠标指针文件 %s 失败, 可尝试使用管理员权限运行 Ani2xcur, 或尝试手动删除该文件",
                file,
            )
            errors.append(e)
            delete_failed_files.append(file)

    if errors:
        failed_files_str = "\n - ".join([""] + [str(x) for x in delete_failed_files])
        raise OSError(
            f"删除鼠标指针文件时发生 {len(errors)} 个错误, 以下鼠标指针文件删除失败: \n{failed_files_str}\n\n可尝试手动删除以上删除失败的鼠标指针文件"
        )


def install_cursor_scheme(
    scheme_name: str,
    scheme_data: str,
) -> None:
    """将鼠标指针方案安装到系统中

    Args:
        scheme_name (str): 鼠标指针方案名称
        scheme_data (str): 鼠标指针方案数据，以逗号分隔的光标文件路径
    Raises:
        ValueError: 鼠标指针方案数据格式不正确时
        FileNotFoundError: 未找到鼠标指针方案中对应的文件时
    """
    paths = scheme_data.split(",")
    if len(paths) != len(CURSOR_KEYS["win"]):
        raise ValueError(
            f"鼠标指针方案数据格式不正确, 应包含 {len(CURSOR_KEYS['win'])} 个路径, 实际包含 {len(paths)} 个路径"
        )

    for path in paths:
        if path.strip() == "":
            continue

        resolved_path = resolve_env_vars(path.strip())
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(
                f"{scheme_name} 鼠标指针文件不存在: {resolved_path}"
            )

    schemes_path = r"Control Panel\Cursors\Schemes"
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, schemes_path, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, scheme_name, 0, winreg.REG_SZ, scheme_data)


def install_cursor(
    inf_file: Path,
    cursor_install_path: Path | None = None,
) -> None:
    """通过 INF 配置文件安装鼠标指针

    Args:
        inf_file (Path): 鼠标指针配置文件路径
        cursor_install_path (Path | None): 自定义鼠标指针文件安装路径, 当为 None 时使用 INF 配置文件中的路径
    """
    install_scheme_info = get_scheme_from_inf_file(inf_file)
    vars_dict = install_scheme_info["vars_dict"]

    def _get_real_path(x: str) -> Path:
        return Path(
            resolve_env_vars_with_dict(x.replace('"', "").replace("'", ""), vars_dict)
        )

    if cursor_install_path is not None:
        reg_config = install_scheme_info["default_reg"].split(",")

        cursor_reg_info = reg_config[:4]
        cursor_reg_paths = [
            str(cursor_install_path / _get_real_path(x).name)
            for x in reg_config[4:]
            if _get_real_path(x).is_file()
        ]
        reg_config = ",".join(
            cursor_reg_info
            + [
                f'"{",".join(extend_list_to_length(cursor_reg_paths, target_length=len(CURSOR_KEYS["win"])))}"'
            ]
        )
        file_paths = [
            Path(p["src_path"])
            for _, p in install_scheme_info["cursor_map"].items()
            if p["src_path"] is not None and Path(p["src_path"]).is_file()
        ]
        cursor_install_path.mkdir(parents=True, exist_ok=True)
        for p in file_paths:
            copy_files(p, cursor_install_path)
    else:
        reg_config = install_scheme_info["default_reg"]
        for _, p in install_scheme_info["cursor_map"].items():
            src = p["src_path"]
            dst = p["dst_path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            copy_files(src, dst)

    scheme_name = install_scheme_info["scheme_name"]
    scheme_data = ",".join(
        [x.replace('"', "").replace("'", "") for x in reg_config.split(",")[4:]]
    )

    install_cursor_scheme(
        scheme_name=scheme_name,
        scheme_data=scheme_data,
    )


def refresh_system_params() -> None:
    """通知系统刷新设置以应用更改"""
    ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, None, 0x01 | 0x02)


class InstallWinSchemeInfo(TypedDict):
    """Windows 鼠标指针安装信息"""

    scheme_name: str
    """鼠标指针名称"""

    cursor_paths: list[Path]
    """鼠标指针文件列表"""

    default_reg: str
    """默认安装到注册表的鼠标指针方案"""

    default_dst_cursor_paths: list[Path]
    """默认复制到的目的路径的鼠标指针文件列表"""

    vars_dict: dict[str, str]
    """INF 文件中的变量表"""

    cursor_map: CursorMap
    """鼠标指针类型与对应的路径地图"""


def resolve_env_vars_with_dict(text: str, vars_dict: dict[str, str]) -> str:
    """将字符串中的 %var% 变量进行替换, 并优先查找变量表中的值

    Args:
        text (str): 需要处理的字符串
        vars_dict (dict[str, str]): 变量字典
    Returns:
        str: 处理后的字符串
    """

    def _replace_env_var(match: re.Match) -> str:
        env_var = match.group(1)
        env_var_lower = match.group(1).lower().strip()
        return vars_dict.get(env_var_lower, os.environ.get(env_var, match.group(0)))

    pattern = r"%([^%]+)%"
    vars_dict = lowercase_dict_keys(vars_dict)
    result = re.sub(pattern, _replace_env_var, text.replace(r"%10%", r"%SYSTEMROOT%"))
    return result


def get_scheme_from_inf_file(
    inf_file: Path,
) -> InstallWinSchemeInfo:
    """从 INF 文件中获取鼠标指针配置

    Args:
        inf_file (Path): INF 文件路径
    Returns:
        InstallSchemeInfo: 鼠标指针安装配置
    Raises:
        ValueError: 鼠标指针配置文件中的注册表信息不合法时
    """

    def _get_real_path(x: str) -> Path:
        return Path(
            resolve_env_vars_with_dict(x.replace('"', "").replace("'", ""), vars_dict)
        )

    scheme_info: InstallWinSchemeInfo = {}
    inf_file_content = get_cursor_scheme_data_from_inf(inf_file)
    reg_config = inf_file_content["Scheme.Reg"][0].split(
        ","
    )  # ["Scheme.Reg"]["files"][0].split(",")
    vars_dict = inf_file_content["Strings"]
    scheme_name = vars_dict["SCHEME_NAME"]
    cursor_files = inf_file_content["Scheme.Cur"]
    if len(reg_config) <= 4:
        raise ValueError(
            f"鼠标指针配置中的注册表配置不合法, 配置长度: {len(reg_config)}"
        )

    cursor_reg_info = reg_config[:4]
    cursor_reg_path = [
        x.replace('"', "").replace("'", "")
        for x in extend_list_to_length(reg_config[4:], target_length=len(CURSOR_KEYS["win"]))
    ]
    default_reg = ",".join(cursor_reg_info + [f'"{",".join(cursor_reg_path)}"'])
    default_dst_cursor_paths = [
        _get_real_path(x) for x in reg_config[4:] if _get_real_path(x).is_file()
    ]
    cursor_map: CursorMap = {}
    for key, value in zip(CURSOR_KEYS["win"], cursor_reg_path):
        if value.strip() != "":
            dst_path = _get_real_path(value)
            src_path = inf_file.parent / dst_path.name
            if not src_path.is_file():
                src_path = None
        else:
            dst_path = None
            src_path = None

        cursor_map[key] = {
            "dst_path": dst_path,
            "src_path": src_path,
        }
    cursor_paths = [
        inf_file.parent / x for x in cursor_files if (inf_file.parent / x).is_file()
    ]
    scheme_info["scheme_name"] = scheme_name
    scheme_info["cursor_paths"] = cursor_paths
    scheme_info["default_reg"] = default_reg
    scheme_info["vars_dict"] = vars_dict
    scheme_info["default_dst_cursor_paths"] = default_dst_cursor_paths
    scheme_info["cursor_map"] = cursor_map
    return scheme_info


def export_cursor_scheme(
    scheme_name: str,
    output_path: Path,
    custom_install_path: Path | None = None,
) -> Path:
    """将系统中指定的鼠标指针方案导出为文件

    Args:
        scheme_name (str): 要导出的鼠标指针方案的名称
        output_path (Path): 鼠标指针导出的路径
        custom_install_path (Path | None): 自定义鼠标指针安装文件
    Returns:
        Path: 鼠标指针导出的文件路径
    """
    config_dict = generate_cursor_scheme_config(
        scheme_name=scheme_name,
        custom_install_path=custom_install_path,
    )

    reg_content = generate_cursor_scheme_inf_string(
        destination_dirs=config_dict["destination_dirs"],
        wreg=config_dict["wreg"],
        scheme_reg=config_dict["scheme_reg"],
        scheme_cur=config_dict["scheme_cur"],
        strings=config_dict["strings"],
    )

    save_dir = output_path / scheme_name
    inf_file_path = save_dir / "install_cursor.inf"
    for cursor in config_dict["cursor_src_file"]:
        copy_files(cursor, save_dir)

    with open(inf_file_path, "w", encoding="utf-8") as file:
        file.write(reg_content)

    return save_dir


def generate_cursor_scheme_config(
    scheme_name: str,
    custom_install_path: Path | None = None,
) -> dict[str, str]:
    """生成鼠标指针的配置

    Args:
        scheme_name (str): 要导出的鼠标指针方案的名称
        custom_install_path (Path | None): 自定义鼠标指针安装文件
    Returns:
        (dict[str, str]): 鼠标指针的配置字典
    """
    config_dict: dict[str, str] = {}
    config_dict["cursor_src_file"] = []
    scheme_data = get_scheme(scheme_name)
    cursor_list = extend_list_to_length(
        scheme_data.split(","), target_length=len(CURSOR_KEYS["win"])
    )
    paths_dict: dict[str, str | None] = {}
    for name, path in zip(CURSOR_KEYS["win"], cursor_list):
        if (
            path.strip() != ""
            and Path(resolve_env_vars_with_dict(text=path, vars_dict={})).is_file()
        ):
            cursor_src_file = Path(resolve_env_vars_with_dict(text=path, vars_dict={}))
            config_dict["cursor_src_file"].append(cursor_src_file)
            cursor_file_name = cursor_src_file.name
        else:
            cursor_file_name = None
        cursor_file = None
        if cursor_file_name is not None:
            if custom_install_path is not None:
                cursor_file = str(custom_install_path / scheme_name / cursor_file_name)
            else:
                cursor_file = rf"%SYSTEMROOT%\Cursors\{scheme_name}\{cursor_file_name}"
        paths_dict[name] = cursor_file

    scheme_cur = ""
    strings_dict = {k: Path(v).name for k, v in paths_dict.items() if v is not None}
    strings_dict["SCHEME_NAME"] = scheme_name
    scheme_reg = r'HKCU,"Control Panel\Cursors\Schemes","%SCHEME_NAME%",,"'
    wreg = r'HKCU,"Control Panel\Cursors",,0x00020000,"%SCHEME_NAME%"'
    if custom_install_path is not None:
        destination_dirs = rf'"{str(custom_install_path / scheme_name)}"'
        for cursor_key in CURSOR_KEYS["win"]:
            if paths_dict[cursor_key] is not None:
                cursor_path = str(
                    custom_install_path / scheme_name / rf"%{cursor_key}%"
                )
                wreg += "\n"
                wreg += rf'HKCU,"Control Panel\Cursors",{cursor_key},0x00020000,"{cursor_path}"'
            else:
                cursor_path = ""
            scheme_cur += "\n"
            scheme_cur += (
                rf'"{Path(strings_dict[cursor_key]).name}"'
                if strings_dict.get(cursor_key) is not None
                else ""
            )
            scheme_reg += cursor_path
            if cursor_key != CURSOR_KEYS["win"][-1]:
                scheme_reg += ","
        scheme_reg += '"'
        strings_dict["CUR_DIR"] = str(custom_install_path / scheme_name)
    else:
        destination_dirs = r'10,"%CUR_DIR%"'
        for cursor_key in CURSOR_KEYS["win"]:
            if paths_dict[cursor_key] is not None:
                cursor_path = rf"%SYSTEMROOT%\%CUR_DIR%\%{cursor_key}%"
                wreg += "\n"
                wreg += rf'HKCU,"Control Panel\Cursors",{cursor_key},0x00020000,"{cursor_path}"'
            else:
                cursor_path = ""
            scheme_cur += "\n"
            scheme_cur += (
                rf'"{Path(strings_dict[cursor_key]).name}"'
                if strings_dict.get(cursor_key) is not None
                else ""
            )
            scheme_reg += cursor_path
            if cursor_key != CURSOR_KEYS["win"][-1]:
                scheme_reg += ","
        scheme_reg += '"'
        strings_dict["CUR_DIR"] = rf"Cursors\{scheme_name}"

    wreg += "\n"
    wreg += r'HKLM,"SOFTWARE\Microsoft\Windows\CurrentVersion\Runonce\Setup\","",,"rundll32.exe shell32.dll,Control_RunDLL main.cpl @0"'
    strings = dict_to_inf_strings_format(strings_dict)
    config_dict["destination_dirs"] = destination_dirs
    config_dict["wreg"] = wreg
    config_dict["scheme_reg"] = scheme_reg
    config_dict["scheme_cur"] = scheme_cur
    config_dict["strings"] = strings
    return config_dict


def generate_cursor_scheme_inf_string(
    destination_dirs: str, wreg: str, scheme_reg: str, scheme_cur: str, strings: str
) -> str:
    """生成鼠标指针安装配置文件

    Args:
        destination_dirs (str): [DestinationDirs] 字段
        wreg (str): [Wreg] 字段
        scheme_reg (str): [Scheme.Reg] 字段
        scheme_cur (str): [Scheme.Cur] 字段
        strings (str): [Strings] 字段
    Returns:
        str: 鼠标指针的 INF 字符串
    """
    reg_content = r"""
[Version]
signature="$CHICAGO$"


[DefaultInstall]
CopyFiles = Scheme.Cur
AddReg    = Scheme.Reg,Wreg


[DestinationDirs]
Scheme.Cur = {{DESTINATION_DIRS}}


[Scheme.Reg]
{{SCHEME_REG}}


[Wreg]
{{WREG}}


[Scheme.Cur]
{{SCHEME_CUR}}


[Strings]
{{STRING_VARS}}

""".strip()

    return (
        reg_content.replace(r"{{DESTINATION_DIRS}}", destination_dirs.strip())
        .replace(r"{{WREG}}", wreg.strip())
        .replace(r"{{SCHEME_REG}}", scheme_reg.strip())
        .replace(r"{{SCHEME_CUR}}", scheme_cur.strip())
        .replace(r"{{STRING_VARS}}", strings.strip())
    )
