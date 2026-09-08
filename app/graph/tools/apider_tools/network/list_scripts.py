from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolResult
from app.graph.tools.tool_registry import ToolRegistry



@ToolRegistry.register
class ListScripts(BaseTool):
    name = "list_scripts"
    description = "获取所有js"
    args = []

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self) -> ToolResult:
        scripts_list = await self.browser_oper.debug.get_scripts_list()
        # 处理list_scripts只返回scriptId和url
        result_list = [{script.script_id: script.url} for script in scripts_list]
        return ToolResult.ok(data=result_list,summary="获取js列表成功，格式为{'scriptId':'url'}")