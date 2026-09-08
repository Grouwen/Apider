import os
from typing import Dict, Any
from urllib.parse import urlparse

from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolResult, ToolArgsDescription, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class ListRequests(BaseTool):
    name = "list_requests"
    description = "获取所有fetch/xhr请求列表"
    args = [
        ToolArgsDescription("post_data_limit",ToolArgsType.INT,"post_data数据最大显示字符数，默认400",False)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,post_data_limit:int=400) -> ToolResult:
        request_list = await self.browser_oper.network.get_request_list()
        # 处理request_list
        results = {}
        for request in request_list:
            domain_and_filename = self.extract_url_info(request.request.url)
            domain = domain_and_filename["target_domain"]
            filename = domain_and_filename["filename"]

            if domain not in results:
                results[domain] = {
                    "total_count": 0,
                    "requests": []
                }
            results[domain]["total_count"] += 1
            results[domain]["requests"].append({
                "request_id": request.request_id,
                "filename": filename,
                "timestamp": request.timestamp,
                "method": request.request.method,
                "post_data":request.request.post_data[:post_data_limit] if request.request.post_data else None,
            })

        return ToolResult.ok(data=[results], summary=f"获取fetch/xhr请求列表成功,post_data最多显示400字符，需要详情，使用get_request_detail")

    def extract_url_info(self, url: str) -> Dict[str, Any]:
        """
        提取 URL 中的 target_domain 和 filename
        """
        parsed = urlparse(url)

        # 提取域名
        target_domain = parsed.netloc

        # 提取文件名
        filename = os.path.basename(parsed.path)

        # 如果 URL 没有指向具体文件（例如只有目录），提取最后一个目录名并保留斜杠
        if not filename:
            path_parts = [p for p in parsed.path.split('/') if p]

            if path_parts:
                filename = path_parts[-1] + '/'
            else:
                filename = None

        return {
            "target_domain": target_domain,
            "filename": filename
        }
