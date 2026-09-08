from dataclasses import asdict
from typing import Dict, Any

from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import ToolArgsDescription, ToolResult, BaseTool, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class GetRequestResponse(BaseTool):
    name = "get_request_response"
    description = "根据request_id获取fetch/xhr请求的响应信息"
    args = [
        ToolArgsDescription("request_id",ToolArgsType.STR,"要获取fetch/xhr请求响应的request_id",True),
        ToolArgsDescription("max_response_result_chars",ToolArgsType.INT,
                            "请求响应内容的最大字符数，默认1000", required=False)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self, request_id: str,max_response_result_chars:int=1000) -> ToolResult:
        try:
            response = await self.browser_oper.network.get_response_by_request_id(request_id)
            if response:
                response.response_result.body = response.response_result.body[:max_response_result_chars]
                return ToolResult.ok( [asdict(response)], f"获取request_id:{request_id} 请求的响应信息成功")

            return ToolResult.error( f"获取request_id:{request_id} 请求的响应信息失败", f"响应信息为空")

        except Exception as e:
            return ToolResult.error(f"获取request_id:{request_id} 请求的响应信息失败：{request_id}",error_msg=str(e))