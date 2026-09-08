from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolResult, ToolArgsDescription, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class Scroll(BaseTool):
    name = "scroll"
    description = "滚动页面"
    args = [
        ToolArgsDescription("scroll_x", ToolArgsType.INT, "滚动位置x轴，垂直向下滚动设为0即可", True),
        ToolArgsDescription("scroll_y", ToolArgsType.INT, "滚动位置y轴", True),
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,scroll_x:int,scroll_y:int) -> ToolResult:
        try:
            await self.browser_oper.dom.scroll(scroll_x, scroll_y)
            return ToolResult.ok(None, f"滚动成功")
        except Exception as e:
            return ToolResult.error(f"滚动失败",str(e))