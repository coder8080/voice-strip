from mcp.server import FastMCP

mcp = FastMCP()


@mcp.tool()
def set_solid(color: tuple[int, int, int]):
    """
    Установить светодиодной ленте один цвет

    Args:
        color: желаемый цвет
    """
