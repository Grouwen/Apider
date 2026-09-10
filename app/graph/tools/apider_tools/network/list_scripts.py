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
        js_with_url_list = []
        dynamic_js_list = []
        for script in scripts_list:
            id = script.script_id
            if script.url.startswith("动态"):
                dynamic_js_list.append(id)
                continue
            js_with_url_list.append({
                id: script.url
            })

        return ToolResult.ok(data=[{
            "normal_js_list": js_with_url_list,
            "dynamic_js_list": dynamic_js_list,
        }],summary="获取js列表成功，格式为{'scriptId':'url'}")