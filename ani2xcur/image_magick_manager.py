

import os
from tempfile import TemporaryDirectory
from pathlib import Path
import getpass
from datetime import datetime


from ani2xcur.downloader import download_file_from_url
from ani2xcur.file_operations.archive_manager import extract_archive
from ani2xcur.cmd import run_cmd
from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_COLOR,
    LOGGER_LEVEL,
    LOGGER_NAME,
    IMAGE_MAGICK_WINDOWS_DOWNLOAD_URL,
    IMAGE_MAGICK_WINDOWS_INSTALL_PATH
)
from ani2xcur.manager.win_env_val_manager import add_path_to_env_path
from ani2xcur.manager.win_env_val_manager import add_val_to_env
from ani2xcur.utils import is_admin_on_windows
from ani2xcur.manager.regedit import (
    RegistryAccess,
    RegistryRootKey,
    RegistryValueType,
    registry_set_value,
    registry_create_path,
    registry_delete_tree,
    registry_query_value
)
from ani2xcur.file_operations.file_manager import remove_files



logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


IMAGE_MAGICK_WINDOWS_REGISTRY_CONFIG_PATH = r"SOFTWARE\ImageMagick\Current"
"""ImageMagick 注册表配置信息"""

IMAGE_MAGICK_WINDOWS_REGISTRY_UNINSTALL_CONFIG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ImageMagick 7.1.2 Q16-HDRI (64-bit)_is1"
"""ImageMagick 注册表卸载面板信息"""





def install_image_magick_windows(
    install_path: Path | None = None,
) -> None:
    """在 Windows 系统中安装 ImageMagick

    Args:
        install_path (Path | None): 安装 ImageMagick 的目录
    Raises:
        PermissionError: 当未使用管理员权限运行时
    """
    if check_image_magick_windows_is_installed():
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
        ("FilterModulesPath", str(install_path / "modules" / "filters"), RegistryValueType.SZ),
        ("ConfigurePath", str(install_path), RegistryValueType.SZ),
        ("CoderModulesPath", str(install_path / "modules" / "coders"), RegistryValueType.SZ),
        ("BinPath", str(install_path), RegistryValueType.SZ),
    ]
    uninstall_exe = str(install_path / "unins000.exe")
    uninstall_config: list[tuple[str, str | int, RegistryValueType]] = [
        ("DisplayIcon", str(install_path / "ImageMagick.ico"), RegistryValueType.SZ),
        ("DisplayName", "ImageMagick 7.1.2-12 Q16-HDRI (64-bit) (2025-12-28)",RegistryValueType.SZ),
        ("DisplayVersion", "7.1.2.12", RegistryValueType.SZ),
        ("EstimatedSize", int("eb6f", 16), RegistryValueType.DWORD),
        ("HelpLink", "http://www.imagemagick.org/", RegistryValueType.SZ),
        ("Inno Setup: App Path", str(install_path), RegistryValueType.SZ),
        ("Inno Setup: Deselected Tasks", "legacy_support,install_devel,install_perlmagick", RegistryValueType.SZ),
        ("Inno Setup: Icon Group", "ImageMagick 7.1.2 Q16-HDRI (64-bit)", RegistryValueType.SZ),
        ("Inno Setup: Language", "default", RegistryValueType.SZ),
        ("Inno Setup: Selected Tasks", "modifypath", RegistryValueType.SZ),
        ("Inno Setup: Setup Version", "6.2.0", RegistryValueType.SZ),
        ("Inno Setup: User", getpass.getuser(),RegistryValueType.SZ ),
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
        ("URLUpdateInfo", "http://www.imagemagick.org/script/download.php", RegistryValueType.SZ),
        ("VersionMajor", 7, RegistryValueType.DWORD),
        ("VersionMinor", 1, RegistryValueType.DWORD),
    ]

    # 下载并解压 ImageMagick
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        image_magick_archive_path = download_file_from_url(
            url=IMAGE_MAGICK_WINDOWS_DOWNLOAD_URL,
            save_path=tmp_dir,
        )
        extract_archive(
            archive_path=image_magick_archive_path,
            extract_to=install_path,
        )
    
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
    add_image_magick_to_path(install_path)


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
    add_val_to_env(
        name="MAGICK_HOME",
        value=str(install_path),
        dtype="system"
    )
    add_val_to_env(
        name="MAGICK_HOME",
        value=str(install_path),
        dtype="user",
    )


def uninstall_image_magick_windows() -> None:
    """将 ImageMagick 从 Windows 系统上卸载

    Raises:
        PermissionError: 未使用管理员权限运行时
        FileNotFoundError: 当 ImageMagick 存在于系统但未找到 ImageMagick 安装路径时
        RuntimeError: 删除 ImageMagick 文件发生失败时
    """
    
    if not check_image_magick_windows_is_installed():
        return

    if not is_admin_on_windows():
        raise PermissionError("当前未使用管理员权限运行 Ani2xcur, 卸载安装 ImageMagick, 请使用管理员权限进行重试")
    
    # 查找 ImageMagick 安装路径
    install_path = find_image_magick_install_path_windows()

    if install_path is None:
        raise FileNotFoundError("未找到 ImageMagick 安装路径, 无法卸载 ImageMagick")
    
    # 删除 ImageMagick 文件
    try:
        remove_files(install_path)
    except OSError as e:
        logger.error("尝试删除 ImageMagick 时发生错误: %s\n可尝试手动卸载 ImageMagick", e)
        raise RuntimeError(f"尝试删除 ImageMagick 时发生错误: {e}\n可尝试手动卸载 ImageMagick") from e
    
    # 删除 ImageMagick 启动图标
    icon_path = Path(os.getenv("ProgramData", "C:/ProgramData/Microsoft/Windows/Start Menu/Programs"))
    # TODO
    # try:
    #     remove_files(icon_path / "")

    # 删除注册表中的 ImageMagick 信息
    registry_delete_tree(
        sub_key=IMAGE_MAGICK_WINDOWS_REGISTRY_CONFIG_PATH,
        key=RegistryRootKey.LOCAL_MACHINE,
    )
    # 删除注册表中在卸载列表的 ImageMagick 信息
    registry_delete_tree(
        sub_key=IMAGE_MAGICK_WINDOWS_REGISTRY_UNINSTALL_CONFIG_PATH,
        key=RegistryRootKey.LOCAL_MACHINE,
    )


def find_image_magick_install_path_windows() -> Path | None:
    """在 Windows 系统中查找 ImageMagick 安装路径

    Returns:
        (Path | None): ImageMagick 安装路径, 当未找到 ImageMagick 安装路径时则返回 None
    """
    install_path = None
    for name in ["BinPath", "ConfigurePath", "LibPath"]:
        try:
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


def install_image_magick_linux() -> None: ...


def uninstall_image_magick_linux() -> None: ...


def check_image_magick_windows_is_installed() -> bool:
    """检测 ImageMagick 是否已经安装

    Returns:
        bool: 当已经安装时则返回 True
    """
    try:
        # wand.api 在初始化时会调用 load_library() 加载 ImageMagick 的链接库
        # 当加载失败时将引发 ImportError
        # Windows 查找 ImageMagick 主要根据 MAGICK_HOME 环境变量
        # 或者注册表中`计算机\HKEY_LOCAL_MACHINE\SOFTWARE\ImageMagick\Current`的 LibPath, CoderModulesPath, FilterModulesPath
        # Linux 中是通过 ctypes.util.find_library() 查找
        import wand.api # pylint: disable=import-outside-toplevel
        _ = wand.api
        return True
    except (ImportError, IOError):
        return False

