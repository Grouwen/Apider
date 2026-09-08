from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolResult, ToolArgsDescription, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class InputDom(BaseTool):
    name = "input_dom"
    description = "根据ref进行输入"
    args = [
        ToolArgsDescription("ref", ToolArgsType.STR, "要输入的元素ref", True),
        ToolArgsDescription("input", ToolArgsType.STR, "输入内容", True),
        ToolArgsDescription("submit", ToolArgsType.BOOL, "是否输入后按回车提交，默认False", False)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,ref:str,input:str,submit:bool=False) -> ToolResult:
        try:
            await self.browser_oper.dom.input(ref,input)
            if submit:
                await self.browser_oper.dom.press(ref,"Enter")
            return ToolResult.ok(None,f"向元素中输入成功")
        except Exception as e:
            return ToolResult.error(f"向元素中输入失败，ref={ref}",str(e))
