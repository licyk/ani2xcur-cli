"""ImageMagick 管理工具"""

import os
import re
import getpass
import ctypes.util
import itertools
import platform
import shutil
from typing import Generator
from tempfile import TemporaryDirectory
from pathlib import Path
from datetime import datetime

try:
    import winreg
except ImportError:
    winreg = NotImplemented

from ani2xcur.downloader import download_file_from_url
from ani2xcur.file_operations.archive_manager import extract_archive
from ani2xcur.cmd import run_cmd
from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_COLOR,
    LOGGER_LEVEL,
    LOGGER_NAME,
    IMAGE_MAGICK_WINDOWS_DOWNLOAD_URL,
    IMAGE_MAGICK_WINDOWS_INSTALL_PATH,
)
from ani2xcur.manager.win_env_val_manager import (
    add_path_to_env_path,
    add_val_to_env,
    delete_val_from_env,
    delete_path_from_env_path,
)
from ani2xcur.utils import (
    is_admin_on_windows,
    is_root_on_linux,
)
from ani2xcur.manager.regedit import (
    RegistryAccess,
    RegistryRootKey,
    RegistryValueType,
    registry_set_value,
    registry_create_path,
    registry_delete_tree,
    registry_query_value,
)
from ani2xcur.file_operations.file_manager import remove_files
from ani2xcur.manager.desktop_config.windows import create_windows_shortcut

logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


IMAGE_MAGICK_WINDOWS_REGISTRY_CONFIG_PATH = r"SOFTWARE\ImageMagick\Current"
"""ImageMagick 注册表配置信息"""

IMAGE_MAGICK_WINDOWS_REGISTRY_UNINSTALL_CONFIG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ImageMagick 7.1.2 Q16-HDRI (64-bit)_is1"
"""ImageMagick 注册表卸载面板信息"""

IMAGE_MAGICK_WINDOWS_ICON_PATH = Path(os.getenv("ProgramData", "C:/ProgramData")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "ImageMagick 7.1.2 Q16-HDRI (64-bit)"
"""ImageMagick 快捷方式路径"""


def install_image_magick_windows(
    install_path: Path | None = None,
) -> None:
    """在 Windows 系统中安装 ImageMagick

    Args:
        install_path (Path | None): 安装 ImageMagick 的目录
    Raises:
        PermissionError: 当未使用管理员权限运行时
    """
    if check_image_magick_is_installed():
        logger.info("ImageMagick 已安装在 Windows 系统中")
        return

    if not is_admin_on_windows():
        raise PermissionError("当前未使用管理员权限运行 Ani2xcur, 无法安装 ImageMagick, 请使用管理员权限进行重试")

    if install_path is None:
        install_path = IMAGE_MAGICK_WINDOWS_INSTALL_PATH

    # 注册表配置
    registry_config: list[tuple[str, str | int, RegistryValueType]] = [
        ("Version", "7.1.2", RegistryValueType.SZ),
        ("QuantumDepth", 10, RegistryValueType.DWORD),
        ("LibPath", str(install_path), RegistryValueType.SZ),
        (
            "FilterModulesPath",
            str(install_path / "modules" / "filters"),
            RegistryValueType.SZ,
        ),
        ("ConfigurePath", str(install_path), RegistryValueType.SZ),
        (
            "CoderModulesPath",
            str(install_path / "modules" / "coders"),
            RegistryValueType.SZ,
        ),
        ("BinPath", str(install_path), RegistryValueType.SZ),
    ]
    registry_sub_config: list[tuple[str, str | int, RegistryValueType]] = [
        ("LibPath", str(install_path), RegistryValueType.SZ),
        (
            "FilterModulesPath",
            str(install_path / "modules" / "filters"),
            RegistryValueType.SZ,
        ),
        ("ConfigurePath", str(install_path), RegistryValueType.SZ),
        (
            "CoderModulesPath",
            str(install_path / "modules" / "coders"),
            RegistryValueType.SZ,
        ),
        ("BinPath", str(install_path), RegistryValueType.SZ),
    ]
    uninstall_exe = str(install_path / "unins000.exe")
    uninstall_config: list[tuple[str, str | int, RegistryValueType]] = [
        ("DisplayIcon", str(install_path / "ImageMagick.ico"), RegistryValueType.SZ),
        (
            "DisplayName",
            "ImageMagick 7.1.2-12 Q16-HDRI (64-bit) (2025-12-28)",
            RegistryValueType.SZ,
        ),
        ("DisplayVersion", "7.1.2.12", RegistryValueType.SZ),
        ("EstimatedSize", int("eb6f", 16), RegistryValueType.DWORD),
        ("HelpLink", "http://www.imagemagick.org/", RegistryValueType.SZ),
        ("Inno Setup: App Path", str(install_path), RegistryValueType.SZ),
        (
            "Inno Setup: Deselected Tasks",
            "legacy_support,install_devel,install_perlmagick",
            RegistryValueType.SZ,
        ),
        (
            "Inno Setup: Icon Group",
            "ImageMagick 7.1.2 Q16-HDRI (64-bit)",
            RegistryValueType.SZ,
        ),
        ("Inno Setup: Language", "default", RegistryValueType.SZ),
        ("Inno Setup: Selected Tasks", "modifypath", RegistryValueType.SZ),
        ("Inno Setup: Setup Version", "6.2.0", RegistryValueType.SZ),
        ("Inno Setup: User", getpass.getuser(), RegistryValueType.SZ),
        ("InstallDate", datetime.now().strftime(r"%Y%m%d"), RegistryValueType.SZ),
        ("InstallLocation", str(install_path), RegistryValueType.SZ),
        ("MajorVersion", 7, RegistryValueType.DWORD),
        ("MinorVersion", 1, RegistryValueType.DWORD),
        ("NoModify", 1, RegistryValueType.DWORD),
        ("NoRepair", 1, RegistryValueType.DWORD),
        ("Publisher", "ImageMagick Studio LLC", RegistryValueType.SZ),
        ("QuietUninstallString", f'"{uninstall_exe}" /SILENT', RegistryValueType.SZ),
        ("UninstallString", uninstall_exe, RegistryValueType.SZ),
        ("URLInfoAbout", "http://www.imagemagick.org/", RegistryValueType.SZ),
        (
            "URLUpdateInfo",
            "http://www.imagemagick.org/script/download.php",
            RegistryValueType.SZ,
        ),
        ("VersionMajor", 7, RegistryValueType.DWORD),
        ("VersionMinor", 1, RegistryValueType.DWORD),
    ]

    logger.info("将 ImageMagick 安装到 Windows 系统中, 安装路径: '%s'", install_path)
    # 下载并解压 ImageMagick
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        logger.debug("从 '%s' 下载 ImageMagick", IMAGE_MAGICK_WINDOWS_DOWNLOAD_URL)
        image_magick_archive_path = download_file_from_url(
            url=IMAGE_MAGICK_WINDOWS_DOWNLOAD_URL,
            save_path=tmp_dir,
        )
        extract_archive(
            archive_path=image_magick_archive_path,
            extract_to=install_path,
        )

    # 创建快捷方式
    shortcut_path = IMAGE_MAGICK_WINDOWS_ICON_PATH / "ImageMagick Web Pages.lnk"
    IMAGE_MAGICK_WINDOWS_ICON_PATH.mkdir(parents=True, exist_ok=True)
    logger.debug("为 ImageMagick 创建快捷方式, 创建路径: '%s'", shortcut_path)
    create_windows_shortcut(target_path=install_path / "index.html", shortcut_path=shortcut_path, description="ImageMagick Web Pages", working_dir=install_path)

    # 获取 ImageMagick 版本信息
    magick_bin = install_path / "magick.exe"
    version_number, quality_setting, _ = get_image_magick_version(magick_bin)
    if version_number is not None:
        version_number = version_number.split("-")[0]
    else:
        version_number = "7.1.2"
    if quality_setting is not None:
        quality_setting = re.sub(r"([A-Z]+)(\d+)", r"\1:\2", quality_setting.split("-")[0])
    else:
        quality_setting = "Q:16"

    # ImageMagick 注册表配置信息 (子表路径)
    image_magick_windows_registry_sub_config_path = rf"SOFTWARE\ImageMagick\{version_number}\{quality_setting}"

    logger.debug("写入 ImageMagick 信息到注册表中")
    # ImageMagick 配置信息
    registry_create_path(
        sub_key=IMAGE_MAGICK_WINDOWS_REGISTRY_CONFIG_PATH,
        key=RegistryRootKey.LOCAL_MACHINE,
        access=RegistryAccess.WRITE,
    )
    for key, value, dtype in registry_config:
        registry_set_value(
            name=key,
            value=value,
            reg_type=dtype,
            sub_key=IMAGE_MAGICK_WINDOWS_REGISTRY_CONFIG_PATH,
            key=RegistryRootKey.LOCAL_MACHINE,
            access=RegistryAccess.SET_VALUE,
        )

    registry_create_path(
        sub_key=image_magick_windows_registry_sub_config_path,
        key=RegistryRootKey.LOCAL_MACHINE,
        access=RegistryAccess.WRITE,
    )
    for key, value, dtype in registry_sub_config:
        registry_set_value(
            name=key,
            value=value,
            reg_type=dtype,
            sub_key=image_magick_windows_registry_sub_config_path,
            key=RegistryRootKey.LOCAL_MACHINE,
            access=RegistryAccess.SET_VALUE,
        )

    # ImageMagick 卸载配置信息
    registry_create_path(
        sub_key=IMAGE_MAGICK_WINDOWS_REGISTRY_UNINSTALL_CONFIG_PATH,
        key=RegistryRootKey.LOCAL_MACHINE,
        access=RegistryAccess.WRITE,
    )
    for key, value, dtype in uninstall_config:
        registry_set_value(
            name=key,
            value=value,
            reg_type=dtype,
            sub_key=IMAGE_MAGICK_WINDOWS_REGISTRY_UNINSTALL_CONFIG_PATH,
            key=RegistryRootKey.LOCAL_MACHINE,
            access=RegistryAccess.SET_VALUE,
        )

    # 配置环境变量
    logger.debug("为 ImageMagick 配置环境变量")
    add_image_magick_to_path(install_path)
    logger.info("ImageMagick 已安装到 Windows 系统中")


def get_image_magick_version(
    magick_bin: Path,
) -> tuple[str, str, str]:
    """获取 ImageMagick 版本号, 质量设置和架构

    Args:
        magick_bin (Path): ImageMagick 可执行文件路径
    Returns:
        (tuple[str | None, str | None, str | None]): ImageMagick 的版本号, 质量设置, 架构
    """
    try:
        result = run_cmd([magick_bin.as_posix(), "-version"], live=False)
    except RuntimeError as e:
        logger.debug("获取 ImageMagick 版本失败: %s", e)
        return None, None, None

    pattern = r"ImageMagick\s+([0-9.-]+)\s+([A-Z0-9-]+)\s+([a-zA-Z0-9]+)"
    match = re.search(pattern, result)
    if match:
        version_number = match.group(1)  # 版本号
        quality_setting = match.group(2)  # 质量设置
        architecture = match.group(3)  # 架构
    else:
        version_number = None
        quality_setting = None
        architecture = None

    logger.debug("获取 ImageMagick 的版本信息: 版本号 '%s', 质量设置 '%s', 架构 '%s'", version_number, quality_setting, architecture)
    return version_number, quality_setting, architecture


def add_image_magick_to_path(
    install_path: Path,
) -> None:
    """将 ImageMagick 添加到环境变量中

    Args:
        install_path (Path): ImageMagick 安装路径
    """
    add_path_to_env_path(
        new_path=str(install_path),
        dtype="system",
    )
    add_path_to_env_path(
        new_path=str(install_path),
        dtype="user",
    )
    add_val_to_env(name="MAGICK_HOME", value=str(install_path), dtype="system")
    add_val_to_env(
        name="MAGICK_HOME",
        value=str(install_path),
        dtype="user",
    )


def delete_image_magick_to_path(
    install_path: Path,
) -> None:
    """将 ImageMagick 从环境变量删除

    Args:
        install_path (Path): ImageMagick 安装路径
    """
    delete_path_from_env_path(key_path=str(install_path), dtype="system")
    delete_path_from_env_path(key_path=str(install_path), dtype="user")
    delete_val_from_env(name="MAGICK_HOME", dtype="system")
    delete_val_from_env(name="MAGICK_HOME", dtype="user")


def uninstall_image_magick_windows() -> None:
    """将 ImageMagick 从 Windows 系统上卸载

    Raises:
        PermissionError: 未使用管理员权限运行时
        FileNotFoundError: 当 ImageMagick 存在于系统但未找到 ImageMagick 安装路径时
        RuntimeError: 删除 ImageMagick 文件发生失败时
    """

    if not check_image_magick_is_installed():
        logger.info("ImageMagick 未安装在 Windows 系统中")
        return

    if not is_admin_on_windows():
        raise PermissionError("当前未使用管理员权限运行 Ani2xcur, 卸载安装 ImageMagick, 请使用管理员权限进行重试")

    # 查找 ImageMagick 安装路径
    install_path = find_image_magick_install_path_windows()

    if install_path is None:
        raise FileNotFoundError("未找到 ImageMagick 安装路径, 无法卸载 ImageMagick")

    logger.info("从 Windows 系统中卸载 ImageMagick 中, ImagwMagick 路径: '%s'", install_path)
    # 删除 ImageMagick 文件
    if install_path.exists():
        logger.debug("删除 ImageMagick 主文件")
        try:
            remove_files(install_path)
        except OSError as e:
            logger.error("尝试删除 ImageMagick 时发生错误: %s\n可尝试手动卸载 ImageMagick", e)
            raise RuntimeError(f"尝试删除 ImageMagick 时发生错误: {e}\n可尝试手动卸载 ImageMagick") from e

    # 删除 ImageMagick 启动图标
    if IMAGE_MAGICK_WINDOWS_ICON_PATH.exists():
        logger.debug("删除 ImageMagick 快捷方式")
        try:
            remove_files(IMAGE_MAGICK_WINDOWS_ICON_PATH)
        except OSError as e:
            logger.error("删除 ImageMagick 图标时发生错误: %s", e)
            raise RuntimeError(f"删除 ImageMagick 图标时发生错误: {e}") from e

    logger.debug("清除 ImageMagick 的注册表信息")
    # 删除注册表中的 ImageMagick 信息
    registry_delete_tree(
        sub_key=str(Path(IMAGE_MAGICK_WINDOWS_REGISTRY_CONFIG_PATH).parent),
        key=RegistryRootKey.LOCAL_MACHINE,
    )

    # 删除注册表中在卸载列表的 ImageMagick 信息
    registry_delete_tree(
        sub_key=IMAGE_MAGICK_WINDOWS_REGISTRY_UNINSTALL_CONFIG_PATH,
        key=RegistryRootKey.LOCAL_MACHINE,
    )

    logger.debug("清除 ImageMagick 的环境变量")
    # 将 ImageMagick 从环境变量中移除
    delete_image_magick_to_path(install_path)
    logger.info("从 Windows 系统卸载 ImageMagick 完成")


def find_image_magick_install_path_windows() -> Path | None:
    """在 Windows 系统中查找 ImageMagick 安装路径

    Returns:
        (Path | None): ImageMagick 安装路径, 当未找到 ImageMagick 安装路径时则返回 None
    """
    install_path = None
    for name in ["BinPath", "ConfigurePath", "LibPath"]:
        try:
            logger.debug("在 '%s' 查找 ImageMagick 的键: '%s'", IMAGE_MAGICK_WINDOWS_REGISTRY_CONFIG_PATH, name)
            install_path = registry_query_value(
                name=name,
                sub_key=IMAGE_MAGICK_WINDOWS_REGISTRY_CONFIG_PATH,
                key=RegistryRootKey.LOCAL_MACHINE,
            )
            install_path = Path(install_path)
            if not install_path.is_dir():
                install_path = None
                continue
        except FileNotFoundError:
            continue

    if install_path is None:
        try:
            logger.debug("在 '%s' 查找 ImageMagick 的键: InstallLocation", IMAGE_MAGICK_WINDOWS_REGISTRY_UNINSTALL_CONFIG_PATH)
            install_path = registry_query_value(
                name="InstallLocation",
                sub_key=IMAGE_MAGICK_WINDOWS_REGISTRY_UNINSTALL_CONFIG_PATH,
                key=RegistryRootKey.LOCAL_MACHINE,
                access=RegistryAccess.READ,
            )
            install_path = Path(install_path)
            if not install_path.is_dir():
                install_path = None
        except FileNotFoundError:
            pass

    return install_path


def install_image_magick_linux() -> None:
    """在 Linux 系统中安装 ImageMagick

    Raises:
        RuntimeError: 当 Linux 不支持自动安装 ImageMagick 时
    """
    if check_image_magick_is_installed():
        logger.info("ImageMagick 已安装在 Linux 系统中")
        return

    if not is_root_on_linux():
        raise PermissionError("当前未使用管理员权限运行 Ani2xcur, 卸载安装 ImageMagick, 请使用管理员权限进行重试")

    logger.info("安装 ImageMagick 到 Linux 系统中")
    cmd: list[list[str]] = []

    if shutil.which("apt"):
        # Debian / Ubuntu
        logger.debug("匹配到 apt 包管理器")
        cmd.append(["apt", "update"])
        cmd.append(["apt", "install", "libmagickwand-dev", "-y"])
    elif shutil.which("yum"):
        # CentOS / RHEL / Fedora
        logger.debug("匹配到 yum 包管理器")
        cmd.append(["yum", "update"])
        cmd.append(["yum", "install", "ImageMagick-devel", "-y"])
    elif shutil.which("apk"):
        # Alpine Linux
        logger.debug("匹配到 apk 包管理器")
        cmd.append(["apk", "update"])
        cmd.append(["apk", "add", "imagemagick"])
    elif shutil.which("pacman"):
        # Arch Linux
        logger.debug("匹配到 pacman 包管理器")
        cmd.append(["pacman", "-Syyu", "imagemagick", "--noconfirm"])
    elif shutil.which("zypper"):
        # openSUSE
        logger.debug("匹配到 zypper 包管理器")
        cmd.append(["zypper", "refresh"])
        cmd.append(["zypper", "install", "ImageMagick", "-y"])
    elif shutil.which("nix-env"):
        # NixOS / Nix
        logger.debug("匹配到 nix 包管理器")
        cmd.append(["nix-channel", "--update"])
        cmd.append(["nix-env", "-iA", "nixos.imagemagick"])
    else:
        raise RuntimeError("不支持的 Linux 系统, 无法自动安装 ImageMagick, 请尝试手动安装 ImageMagick")

    for c in cmd:
        run_cmd(c)

    logger.info("安装 ImageMagick 到 Linux 系统中成功")


def uninstall_image_magick_linux() -> None:
    """在 Linux 系统中卸载 ImageMagick

    Raises:
        RuntimeError: 当 Linux 不支持自动卸载 ImageMagick 时
    """
    if not check_image_magick_is_installed():
        logger.info("ImageMagick 未安装在 Linux 系统中")
        return

    if not is_root_on_linux():
        raise PermissionError("当前未使用管理员权限运行 Ani2xcur, 卸载安装 ImageMagick, 请使用管理员权限进行重试")

    logger.info("从 Linux 系统中卸载 ImageMagick 中")
    cmd: list[list[str]] = []

    if shutil.which("apt"):
        # Debian / Ubuntu
        logger.debug("匹配到 apt 包管理器")
        # 使用 purge 可以同时删除配置文件，如果只需删除程序可用 remove
        cmd.append(["apt", "purge", "libmagickwand-dev", "-y"])
        cmd.append(["apt", "autoremove", "-y"])
    elif shutil.which("yum"):
        # CentOS / RHEL / Fedora
        logger.debug("匹配到 yum 包管理器")
        cmd.append(["yum", "remove", "ImageMagick-devel", "-y"])
    elif shutil.which("apk"):
        # Alpine Linux
        logger.debug("匹配到 apk 包管理器")
        cmd.append(["apk", "del", "imagemagick"])
    elif shutil.which("pacman"):
        # Arch Linux
        logger.debug("匹配到 pacman 包管理器")
        # -Rs 会同时删除该软件及其不再被需要的依赖
        cmd.append(["pacman", "-Rs", "imagemagick", "--noconfirm"])
    elif shutil.which("zypper"):
        # openSUSE
        logger.debug("匹配到 zypper 包管理器")
        cmd.append(["zypper", "remove", "ImageMagick", "-y"])
    elif shutil.which("nix-env"):
        # NixOS / Nix
        logger.debug("匹配到 nix 包管理器")
        # 注意: nix-env 卸载时使用的是安装时的包名 (非属性路径 A)
        cmd.append(["nix-env", "-e", "imagemagick"])
    else:
        raise RuntimeError("不支持的 Linux 系统, 无法自动卸载 ImageMagick, 请尝试手动卸载")

    for c in cmd:
        run_cmd(c)

    logger.info("将 ImageMagick 从 Linux 系统中卸载成功")


def find_wand_library_paths() -> Generator[tuple[str | None, str | None], None, None]:
    """迭代尝试加载的库路径对 (Wand 库路径, Core 库路径).

    结果路径是基于启发式搜索生成的, 不一定在磁盘上真实存在.

    调用者通常需要遍历此生成器并尝试用 ctypes.CDLL 加载, 直到成功为止.

    Returns:
        (Generator[tuple[str | None, str | None], None, None]): 一个生成器, 每次迭代返回 (libwand_path, libmagick_path)
    """
    # 初始化库路径变量
    libwand = None
    libmagick = None

    # 定义可能的版本后缀, 用于匹配不同版本的 ImageMagick 库
    versions = "", "-7", "-7.Q8", "-7.Q16", "-6", "-Q16", "-Q8", "-6.Q16"

    # 定义可能的选项后缀, 如高动态范围 (HDRI) 支持
    options = "", "HDRI", "HDRI-2"

    # 获取当前操作系统类型 (Windows、Darwin/MacOS、Linux 等)
    system = platform.system()

    # 获取 MAGICK_HOME 环境变量的值, 这是 ImageMagick 的安装根目录
    magick_home = os.environ.get("MAGICK_HOME")

    # 获取自定义的库文件后缀
    magick_suffix = os.environ.get("WAND_MAGICK_LIBRARY_SUFFIX")

    if system == "Windows":
        # Windows 版的 ImageMagick 安装程序通常将编解码器和滤镜 DLL 安装在子文件夹中,
        # 我们需要将这些文件夹添加到 PATH 环境变量中, 否则稍后加载 DLL 时会失败.
        try:
            # 打开 Windows 注册表中 ImageMagick 的配置项
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ImageMagick\Current") as reg_key:
                # 从注册表中查询库路径、编解码器模块路径和滤镜模块路径
                libPath = winreg.QueryValueEx(reg_key, "LibPath")  # pylint: disable=invalid-name
                coderPath = winreg.QueryValueEx(reg_key, "CoderModulesPath")  # pylint: disable=invalid-name
                filterPath = winreg.QueryValueEx(reg_key, "FilterModulesPath")  # pylint: disable=invalid-name

                # 设置 magick_home 为库路径
                magick_home = libPath[0]

                # 将库路径、编解码器路径和滤镜路径添加到系统 PATH 环境变量中
                os.environ["PATH"] += str((";" + libPath[0] + ";" + coderPath[0] + ";" + filterPath[0]))
        except OSError:
            # 如果无法从注册表读取, 则使用 MAGICK_HOME 环境变量,
            # 并假设编解码器和滤镜 DLL 在相同的目录中
            pass

    # 辅助函数: 构建 ImageMagick 路径
    def magick_path(path):
        return os.path.join(magick_home, *path)

    # 生成版本和选项的所有组合
    combinations = itertools.product(versions, options)
    suffixes = []

    # 如果存在自定义后缀, 将其分割为列表
    if magick_suffix:
        suffixes = str(magick_suffix).split(";")

    # 我们需要将 combinations 生成器转换为列表, 以便可以遍历两次
    suffixes.extend(list(version + option for version, option in combinations))

    if magick_home:
        # 在调用 find_library 之前, 在 magick_home 中彻底搜索库文件
        for suffix in suffixes:
            # 在 Windows 上, API 被分成两个库. 在其他平台上, 它们全部包含在一个库中.
            if system == "Windows":
                # 尝试第一种 DLL 命名约定
                libwand = ("CORE_RL_wand_{0}.dll".format(suffix),)  # pylint: disable=consider-using-f-string
                libmagick = ("CORE_RL_magick_{0}.dll".format(suffix),)  # pylint: disable=consider-using-f-string
                yield magick_path(libwand), magick_path(libmagick)

                # 尝试第二种 DLL 命名约定
                libwand = ("CORE_RL_MagickWand_{0}.dll".format(suffix),)  # pylint: disable=consider-using-f-string
                libmagick = ("CORE_RL_MagickCore_{0}.dll".format(suffix),)  # pylint: disable=consider-using-f-string
                yield magick_path(libwand), magick_path(libmagick)

                # 尝试第三种 DLL 命名约定
                libwand = ("libMagickWand{0}.dll".format(suffix),)  # pylint: disable=consider-using-f-string
                libmagick = ("libMagickCore{0}.dll".format(suffix),)  # pylint: disable=consider-using-f-string
                yield magick_path(libwand), magick_path(libmagick)

            elif system == "Darwin":  # MacOS
                # 在 MacOS上, MagickWand 库通常也是 MagickCore 库
                libwand = (
                    "lib",
                    "libMagickWand{0}.dylib".format(suffix),  # pylint: disable=consider-using-f-string
                )
                yield magick_path(libwand), magick_path(libwand)
            else:  # Linux 和其他 Unix-like 系统
                # 尝试标准的 .so 库文件命名
                libwand = (
                    "lib",
                    "libMagickWand{0}.so".format(suffix),  # pylint: disable=consider-using-f-string
                )
                libmagick = (
                    "lib",
                    "libMagickCore{0}.so".format(suffix),  # pylint: disable=consider-using-f-string
                )
                yield magick_path(libwand), magick_path(libmagick)

                # 尝试带版本号的 .so 库文件命名 (版本 9)
                libwand = (
                    "lib",
                    "libMagickWand{0}.so.9".format(suffix),  # pylint: disable=consider-using-f-string
                )
                libmagick = (
                    "lib",
                    "libMagickCore{0}.so.9".format(suffix),  # pylint: disable=consider-using-f-string
                )
                yield magick_path(libwand), magick_path(libmagick)

                # 尝试带版本号的 .so 库文件命名 (版本6)
                libwand = (
                    "lib",
                    "libMagickWand{0}.so.6".format(suffix),  # pylint: disable=consider-using-f-string
                )
                libmagick = (
                    "lib",
                    "libMagickCore{0}.so.6".format(suffix),  # pylint: disable=consider-using-f-string
                )
                yield magick_path(libwand), magick_path(libmagick)

    # 如果在 magick_home 中未找到库文件, 使用系统默认路径搜索
    for suffix in suffixes:
        if system == "Windows":
            # 在 Windows 上分别查找 wand 和 magick 库
            libwand = ctypes.util.find_library("CORE_RL_wand_" + suffix)
            libmagick = ctypes.util.find_library("CORE_RL_magick_" + suffix)
            yield libwand, libmagick

            libwand = ctypes.util.find_library("CORE_RL_MagickWand_" + suffix)
            libmagick = ctypes.util.find_library("CORE_RL_MagickCore_" + suffix)
            yield libwand, libmagick

            libwand = ctypes.util.find_library("libMagickWand" + suffix)
            libmagick = ctypes.util.find_library("libMagickCore" + suffix)
            yield libwand, libmagick
        else:
            # 在非 Windows 系统上查找 MagickCore 和 MagickWand 库
            libmagick = ctypes.util.find_library("MagickCore" + suffix)
            libwand = ctypes.util.find_library("MagickWand" + suffix)

            # 如果 MagickCore 库存在, 则返回 wand 和 magick 路径对
            if libmagick is not None:
                yield libwand, libmagick

            # 也返回 wand 库路径, 它可能与 magick 库相同
            yield libwand, libwand


def check_image_magick_is_installed() -> bool:
    """检测 ImageMagick 是否已经安装

    Returns:
        bool: 当已经安装时则返回 True
    """
    # wand.api 在初始化时会调用 load_library() 加载 ImageMagick 的链接库
    # 当加载失败时将引发 ImportError
    # Windows 查找 ImageMagick 主要根据 MAGICK_HOME 环境变量
    # 或者注册表中`计算机\HKEY_LOCAL_MACHINE\SOFTWARE\ImageMagick\Current`的 LibPath, CoderModulesPath, FilterModulesPath
    # Linux 中是通过 ctypes.util.find_library() 查找
    for libwand_path, libmagick_path in find_wand_library_paths():
        if libwand_path is not None or libmagick_path is not None:
            logger.debug("找到 ImageMagick 库路径: ('%s', '%s')", libwand_path, libmagick_path)
            return True
        logger.debug("未找到 ImageMagick 库路径")
    return False
