from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolResult, ToolArgsDescription, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class OpenUrl(BaseTool):
    name = "open_url"
    description = "打开网站地址"
    args = [
        ToolArgsDescription(name="url", type=ToolArgsType.STR,description="要打开的url", required=True),
        ToolArgsDescription(name="wait_for_load", type=ToolArgsType.INT,description="等待所有请求加载完毕的等待时间，单位秒", required=False)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self, url: str,wait_for_load:int = 5) -> ToolResult:
        try:
            await self.browser_oper.dom.goto(url,wait_for_load=wait_for_load)
            return ToolResult.ok(None,f"成功打开：{url}")
        except Exception as e:
            return ToolResult.error(f"打开失败：{url}",error_msg=str(e))