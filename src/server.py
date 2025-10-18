from mcp.server import FastMCP

from visual import AnimationType, visual

mcp = FastMCP()


@mcp.tool()
def set_solid(color: tuple[int, int, int]):
    """
    Установить светодиодной ленте один постоянный цвет

    Args:
        color: желаемый цвет
    """
    visual.send_command(AnimationType.SOLID, [color])
    return "OK"


@mcp.tool()
def set_rainbow():
    """
    Установить радужное переливание по кругу
    """
    visual.send_command(AnimationType.RAINBOW, [])
    return "OK"


@mcp.tool()
def set_breath(color: tuple[int, int, int]):
    """
    Установить эффект дыхания - плавное пульсирование цвета

    Args:
        color: желаемый цвет
    """
    visual.send_command(AnimationType.BREATH, [color])
    return "OK"


@mcp.tool()
def set_loop(colors: list[tuple[int, int, int]]):
    """
    Установить последовательное переливание несколькими цветами

    Args:
        colors: цвета, которыми лента должна переливаться
    """
    visual.send_command(AnimationType.LOOP, colors)
    return "OK"


def run_mcp():
    mcp.run("streamable-http")
