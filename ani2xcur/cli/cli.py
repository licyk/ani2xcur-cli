"""CLI 构建工具"""

import typer
import click


class AlphabeticalMixedGroup(typer.core.TyperGroup):
    """
    自定义的命令组
    """

    def list_commands(
        self,
        ctx: click.Context,
    ) -> list[str]:  # type: ignore[name-defined]
        """将命令按键名进行字母排序

        Args:
            ctx (click.Context): click 组件上下文
        """
        return sorted(self.commands.keys())


def typer_factory(
    help: str,  # pylint: disable=redefined-builtin
) -> typer.Typer:
    """生成 typer 装饰器

    Args:
        help (str): 命令的帮助信息
    Returns:
        typer.Typer: typer 装饰器
    """
    return typer.Typer(
        help=help,
        add_completion=True,  # 启用自动补全功能
        no_args_is_help=True,  # 不带参数运行时显示帮助信息
        cls=AlphabeticalMixedGroup,  # 使用自定义的分组类
        rich_markup_mode=None,  # 禁用 rich 标记模式
        rich_help_panel=None,  # 禁用 rich 帮助面板
        pretty_exceptions_enable=False,  # 禁用美化异常显示
    )
