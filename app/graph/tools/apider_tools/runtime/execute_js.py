from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolArgsDescription, ToolResult, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry

@ToolRegistry.register
class ExecuteJs(BaseTool):
    name = "execute_js"
    description = "传入js在浏览器的环境中执行（全局）仅在进行加密校验时能使用，其他时候一律禁用！！！"
    args = [
        ToolArgsDescription("js_code",ToolArgsType.STR,"要执行的js代码",True),
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self, js_code: str) -> ToolResult:
        js_result = await self.browser_oper.runtime.execute_js(js_code)
        return ToolResult.ok([js_result],"执行js成功")