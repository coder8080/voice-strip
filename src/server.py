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


@mcp.tool()
def set_rainbow():
    """
    Установить радужное переливание
    """
    visual.send_command(AnimationType.RAINBOW)


def run_mcp():
    mcp.run("streamable-http")
