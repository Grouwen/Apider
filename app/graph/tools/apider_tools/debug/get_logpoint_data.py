from dataclasses import asdict

from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolArgsDescription, ToolArgsType, ToolResult
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class GetLogpointData(BaseTool):
    name = "get_logpoint_data"
    description = "根据logpoint_uuid获取断点数据"
    args = [
        ToolArgsDescription("logpoint_uuid",ToolArgsType.STR,"logpoint的uuid",True)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self, logpoint_uuid: str) -> ToolResult:
        logpoint_data = await self.browser_oper.debug.get_logpoint_data_by_uuid(logpoint_uuid)
        result = []
        for data in logpoint_data:
            if data.object_id:
                object_value = await self.browser_oper.debug.get_object_by_object_id(data.object_id)
                result.append({
                    data.var_name:object_value
                })
            else:
                result.append({
                    data.var_name:data.value
                })

        return ToolResult.ok(result,summary=f"获取logpoint_uuid:{logpoint_uuid} 的数据成功")