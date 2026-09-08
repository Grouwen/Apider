from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolResult, ToolArgsDescription, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class ClickDom(BaseTool):
    name = "click_dom"
    description = "根据ref点击对应元素"
    args = [
        ToolArgsDescription("ref",ToolArgsType.STR,"要输入的元素ref",True)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,ref:str) -> ToolResult:
        try:
            await self.browser_oper.dom.click(ref)
            return ToolResult.ok(None,f"点击ref={ref}的元素成功")
        except Exception as e:
            return ToolResult.error(f"点击ref={ref}的元素失败",str(e))
