from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import ToolArgsDescription, ToolResult, BaseTool, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class GetCookie(BaseTool):
    name = "get_cookie"
    description = "获取cookie"
    args = [
        ToolArgsDescription("domain",ToolArgsType.STR,"要过滤的网站domain，不填则返回全部",False)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,domain:str="") -> ToolResult:
        cookies = await self.browser_oper.network.get_cookie()

        if not cookies:
            return ToolResult.error("获取cookie失败", "cookie为空")

        if not domain:
            return ToolResult.ok(cookies,"获取cookie成功")

        filterd_cookie = []
        for item in cookies:
            if domain in item.get("domain",""):
                filterd_cookie.append(item)

        return ToolResult.ok(filterd_cookie,"获取cookie成功")
