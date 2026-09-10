from typing import List

from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolArgsDescription, ToolResult, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class AddFacts(BaseTool):
    name = "add_facts"
    description = (
        "当取得重大突破或确认关键事实时调用：如定位到加密入口函数、确认某参数来源、"
        "还原出算法某一步、完成一次独立验证。只记录有证据支持的事实，推测不要调用本工具。"
        "每条事实一句话概括，并注明证据位置（工具名+request_id/script_id/行列号）。"
    )
    args = [
        ToolArgsDescription("facts",ToolArgsType.LIST,"要保存的事实",True)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,facts:List[str])->ToolResult:
        return ToolResult.ok(None, "已提交记录")