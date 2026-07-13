"""入口文件"""

import sys
import traceback

import typer
from typer import Abort, Exit
from typer._click.exceptions import ClickException

from ani2xcur.cli.cli import typer_factory
from ani2xcur.config import (
    LOGGER_NAME,
    LOGGER_LEVEL,
    LOGGER_COLOR,
)
from ani2xcur.logger import get_logger
from ani2xcur.cli.system import (
    version,
    update,
    env,
)
from ani2xcur.cli.convert import (
    win2xcur,
    x2wincur,
)
from ani2xcur.cli.cursor import (
    install_cursor,
    uninstall_cursor,
    export_cursor,
    set_cursor_theme,
    set_cursor_size,
    list_cursor,
    get_current_cursor,
)


logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)


def get_app() -> typer.Typer:
    """获取 Ani2xcur 命令行应用

    Returns:
        typer.Typer: Ani2xcur 命令行应用
    """
    app = typer_factory("鼠标指针转换和管理命令行工具")

    app.command(help="显示 Ani2xcur 和其他组件的当前版本", name="version")(version)
    app.command(help="更新 Ani2xcur", name="update")(update)
    app.command(help="列出 Ani2xcur 所使用的环境变量", name="env")(env)

    convert_cli = typer_factory(help="鼠标指针转换工具")
    convert_cli.command(help="将 Windows 鼠标指针文件包转换为 Linux 鼠标指针文件包", name="win2x")(win2xcur)
    convert_cli.command(help="将 Linux 鼠标指针文件包转换为 Windows 鼠标指针文件包", name="x2win")(x2wincur)

    cursor_cli = typer_factory(help="系统鼠标指针管理工具")
    cursor_cli.command(help="将鼠标指针安装到系统中", name="install")(install_cursor)
    cursor_cli.command(help="删除系统中指定的鼠标指针", name="uninstall")(uninstall_cursor)
    cursor_cli.command(help="将鼠标指针从系统中导出", name="export")(export_cursor)
    cursor_cli.command(help="列出当前系统中已安装的鼠标指针", name="list")(list_cursor)
    cursor_cli.command(help="显示当前系统中设置的鼠标指针名称和大小", name="status")(get_current_cursor)

    cursor_set_cli = typer_factory(help="设置鼠标指针的工具")
    cursor_set_cli.command(help="设置系统要使用的鼠标指针主题", name="theme")(set_cursor_theme)
    cursor_set_cli.command(help="设置系统要使用的鼠标指针大小", name="size")(set_cursor_size)
    cursor_cli.add_typer(cursor_set_cli, name="set")

    app.add_typer(convert_cli, name="convert")
    app.add_typer(cursor_cli, name="cursor")

    return app


def main() -> None:
    """主函数"""
    try:
        get_app()()
    except Exit as e:
        sys.exit(e.exit_code)
    except Abort:
        logger.error("操作已取消")
        sys.exit(1)
    except ClickException as e:
        e.show()
        sys.exit(e.exit_code)
    except Exception as e:  # pylint: disable=broad-exception-caught
        traceback.print_exc()
        logger.error("命令执行失败: %s", e)
        sys.exit(1)
