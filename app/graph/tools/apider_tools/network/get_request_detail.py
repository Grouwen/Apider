import os
from dataclasses import asdict
from typing import Dict, Any
from urllib.parse import urlparse

from app.core.browser.browser_oper import BrowserOper
from app.domain.network_request import NetworkRequest
from app.graph.tools.base import ToolArgsDescription, ToolResult, BaseTool, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class GetRequestDetail(BaseTool):
    name = "get_request_detail"
    description = "根据request_id获取fetch/xhr请求的详细信息，返回调用栈（可以用于锁定js）"
    args = [
        ToolArgsDescription(name="request_id",type=ToolArgsType.STR, description="要获取fetch/xhr请求详情的request_id", required=True)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self, request_id: str) -> ToolResult:
        try:
            request_list = await self.browser_oper.network.get_request_list()
            for request in request_list:
                if request.request_id == request_id:
                    result = self._handle_request(request)
                    return ToolResult.ok( [result], f"调用栈：{result["initiator"]}，下一步优先分析initiator中的代码。initiator返回格式：script_id:line:column")

            return ToolResult.error( f"获取request_id:{request_id} 请求详细信息失败", error_msg="请求详细信息为空")
        except Exception as e:
            return ToolResult.error(f"获取request_id:{request_id} 请求详细信息失败：{request_id}",error_msg=str(e))

    def _handle_request(self, request:NetworkRequest)->Dict[str,Any]:
        request_dict = asdict(request)

        # 修改调用栈格式
        final_initiator = ""
        for stack in request_dict["initiator"]["stack"]:
            url = stack.get("script_id", "")
            if url:
                filename = os.path.splitext(os.path.basename(urlparse(url).path))[0]
            else:
                filename = "<unknown>"
            line_number = str(stack["line_number"]+1)
            column_number = str(stack["column_number"])
            final_initiator += f" {filename}:{line_number}:{column_number} <"

        # 赋值
        request_dict["initiator"] = final_initiator[1:-2]

        return request_dict
