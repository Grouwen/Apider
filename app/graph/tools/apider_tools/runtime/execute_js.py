from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolArgsDescription, ToolResult, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry

@ToolRegistry.register
class ExecuteJs(BaseTool):
    name = "execute_js"
    description = '''
    Execute browser JavaScript. Best practice: wrap in IIFE (function(){...})() with try-catch
for safety. Use ONLY browser APIs (document, window, DOM). NO Node.js APIs (fs, require,
process). Example: (function(){try{const el=document.querySelector('#id');return el?
el.value:'not found'}catch(e){return 'Error: '+e.message}})()
Avoid comments. Use for hover, drag, zoom, custom selectors, extract/filter links, or
analysing page structure. IMPORTANT: Shadow DOM elements with [index] markers can be
clicked directly with click(index) — do NOT use evaluate() to click them... Limit output size.'''
    args = [
        ToolArgsDescription("js_code",ToolArgsType.STR,"要执行的js代码",True),
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self, js_code: str) -> ToolResult:
        js_result = await self.browser_oper.runtime.execute_js(js_code)
        return ToolResult.ok([js_result],"执行js成功")