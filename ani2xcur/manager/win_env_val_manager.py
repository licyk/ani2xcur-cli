"""Windows 环境变量管理工具"""

from typing import Literal

from ani2xcur.manager.desktop_config.windows import broadcast_settings_change
from ani2xcur.manager.regedit import (
    RegistryAccess,
    RegistryRootKey,
    RegistryValueType,
    registry_query_value,
    registry_set_value,
    registry_delete_value,
)

WINDOWS_ENV_VALUE_REGESTRY_PATH_SYSTEM = [RegistryRootKey.LOCAL_MACHINE, r"SYSTEM\ControlSet001\Control\Session Manager\Environment"]
"""Windows 的环境变量的注册表路径 (系统变量)"""

WINDOWS_ENV_VALUE_REGESTRY_PATH_USER = [RegistryRootKey.CURRENT_USER, "Environment"]
"""Windows 的环境变量的注册表路径 (用户变量)"""


def add_path_to_env_path(
    new_path: str,
    dtype: Literal["user", "system"] | None = "user",
) -> bool:
    """将路径添加到 PATH 环境变量

    Args:
        new_path (str): 要添加到 PATH 环境变量的路径
        dtype (Literal["user", "system"] | None): 要添加路径的环境变量类型
    Returns:
        bool: 当添加成功时返回 True, 已经存在时则返回 False
    Raises:
        ValueError: 使用未知的环境变量类型时
    """
    if dtype == "user":
        key, sub_key = WINDOWS_ENV_VALUE_REGESTRY_PATH_USER
    elif dtype == "system":
        key, sub_key = WINDOWS_ENV_VALUE_REGESTRY_PATH_SYSTEM
    else:
        raise ValueError(f"未知的环境变量类型: {dtype}")

    raw_path = registry_query_value(
        name="Path",
        sub_key=sub_key,
        key=key,
        access=RegistryAccess.READ,
    )
    paths = [p for p in raw_path.split(";") if p.strip()]
    if new_path in paths:
        return False

    paths.append(new_path)
    registry_set_value(
        name="Path",
        value=";".join(paths),
        reg_type=RegistryValueType.EXPAND_SZ,
        sub_key=sub_key,
        key=key,
        access=RegistryAccess.WRITE,
    )
    broadcast_settings_change()
    return True


def add_val_to_env(
    name: str,
    value: str,
    dtype: Literal["user", "system"] | None = "user",
) -> None:
    """将变量添加到环境变量

    Args:
        name (str): 环境变量的名称
        value (str): 环境变量的值
        dtype (Literal["user", "system"] | None): 要添加路径的环境变量类型
    Raises:
        ValueError: 使用未知的环境变量类型时
    """
    if dtype == "user":
        key, sub_key = WINDOWS_ENV_VALUE_REGESTRY_PATH_USER
    elif dtype == "system":
        key, sub_key = WINDOWS_ENV_VALUE_REGESTRY_PATH_SYSTEM
    else:
        raise ValueError(f"未知的环境变量类型: {dtype}")

    registry_set_value(
        name=name,
        value=value,
        reg_type=RegistryValueType.EXPAND_SZ,
        sub_key=sub_key,
        key=key,
        access=RegistryAccess.WRITE,
    )
    broadcast_settings_change()


def delete_path_from_env_path(
    key_path: str,
    dtype: Literal["user", "system"] | None = "user",
) -> bool:
    """将指定路径从 PATH 环境变量中删除

    Args:
        key_path (str): 要从 PATH 环境变量删除的路径
        dtype (Literal["user", "system"] | None): 要删除路径的环境变量类型
    Raises:
        ValueError: 使用未知的环境变量类型时
    """
    if dtype == "user":
        key, sub_key = WINDOWS_ENV_VALUE_REGESTRY_PATH_USER
    elif dtype == "system":
        key, sub_key = WINDOWS_ENV_VALUE_REGESTRY_PATH_SYSTEM
    else:
        raise ValueError(f"未知的环境变量类型: {dtype}")

    raw_path = registry_query_value(
        name="Path",
        sub_key=sub_key,
        key=key,
        access=RegistryAccess.READ,
    )
    paths = [p for p in raw_path.split(";") if p.strip() and key_path not in p]
    registry_set_value(
        name="Path",
        value=";".join(paths),
        reg_type=RegistryValueType.EXPAND_SZ,
        sub_key=sub_key,
        key=key,
        access=RegistryAccess.WRITE,
    )
    broadcast_settings_change()


def delete_val_from_env(
    name: str,
    dtype: Literal["user", "system"] | None = "user",
) -> None:
    """将变量从环境变量中删除

    Args:
        name (str): 环境变量的名称
        dtype (Literal["user", "system"] | None): 要删除变量的环境变量类型
    Raises:
        ValueError: 使用未知的环境变量类型时
    """
    if dtype == "user":
        key, sub_key = WINDOWS_ENV_VALUE_REGESTRY_PATH_USER
    elif dtype == "system":
        key, sub_key = WINDOWS_ENV_VALUE_REGESTRY_PATH_SYSTEM
    else:
        raise ValueError(f"未知的环境变量类型: {dtype}")

    registry_delete_value(name=name, sub_key=sub_key, key=key, access=RegistryAccess.WRITE)
    broadcast_settings_change()
