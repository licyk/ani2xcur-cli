"""入口文件"""

import typer

from ani2xcur.cli.cli import typer_factory
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
from ani2xcur.cli.image_magick import (
    install_image_magick,
    uninstall_image_magick,
)
from ani2xcur.updater import auto_check_update


def get_app() -> typer.Typer:
    """获取 Ani2xcur 命令行应用

    Returns:
        typer.Typer: Ani2xcur 命令行应用
    """
    app = typer_factory("鼠标指针转换、管理、和管理 ImageMagick 的命令行工具")
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

    image_magick_cli = typer_factory(help="ImageMagick 管理工具")
    image_magick_cli.command(help="安装 ImageMagick 到系统中", name="install")(install_image_magick)
    image_magick_cli.command(help="将 ImageMagick 从系统中卸载", name="uninstall")(uninstall_image_magick)

    app.add_typer(convert_cli, name="convert")
    app.add_typer(cursor_cli, name="cursor")
    app.add_typer(image_magick_cli, name="imagemagick")

    return app


def main() -> None:
    """主函数"""
    get_app()()
    auto_check_update()


if __name__ == "__main__":
    main()
