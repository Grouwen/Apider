from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolArgsDescription, ToolArgsType, ToolResult
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class GetHookData(BaseTool):
    name = "get_hook_data"
    description = "根据hook_uuid获取捕获的数据"
    args = [
        ToolArgsDescription("hook_uuid", ToolArgsType.STR, "add_hook 返回的 hook_uuid", required=True),
        ToolArgsDescription("mode", ToolArgsType.STR, "summary 或 raw，默认 summary", required=False),
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self, hook_uuid: str, mode="summary") -> ToolResult:
        records = await self.browser_oper.runtime.get_hook_data_by_id(hook_uuid)

        if not records:
            return ToolResult.ok(None, summary=f"hook_uuid:{hook_uuid} 暂无捕获记录")

        if mode == "summary":
            last = records[-1]
            return ToolResult.ok(
                
                data=[{
                    "hook_id": hook_uuid,
                    "call_count": len(records),
                    "last_call_time": last.get("timestamp"),
                    "last_args_preview": str(last.get("args", ""))[:200],
                }],
                summary=f"获取hook数据成功，hook_id:{hook_uuid} 共捕获 {len(records)} 次调用"
            )
        else:
            return ToolResult.ok( data=records, summary=f"返回 {len(records)} 条原始记录")