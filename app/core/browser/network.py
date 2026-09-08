import re
from typing import List

from app.common.constants import GENERIC_NOISE_PATTERNS
from app.domain.network_request import NetworkRequest
from app.domain.network_response import NetworkResponse, ResponseResult
from app.domain.browser_data import BrowserData
from playwright.async_api import CDPSession

COMPILED_NOISE_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in GENERIC_NOISE_PATTERNS]

class Network:
    def __init__(self, cdp: CDPSession, data: BrowserData):
        self.cdp = cdp
        self.data = data

        # 注册监听
        self.cdp.on("Network.requestWillBeSent", self._handle_requests)
        self.cdp.on("Network.responseReceived", self._handle_response)

    async def _handle_requests(self, params: dict):
        if params["type"] in ["XHR", "Fetch"] and not self.is_noise(params):
            req = NetworkRequest.from_full_dict(params)
            self.data.request_list.append(req)

    async def _handle_response(self, params: dict):
        if params["type"] in ["XHR", "Fetch"] and not self.is_noise(params):
            response = NetworkResponse.from_dict(params)
            self.data.response_list.append(response)

    def is_noise(self,params:dict)->bool:
        url = params.get("request", {}).get("url", "")
        is_noise = any(pattern.search(url) for pattern in COMPILED_NOISE_PATTERNS)
        return is_noise

    # method
    async def get_request_list(self) -> List[NetworkRequest]:
        """
        获取fetch/xhr请求列表
        """
        return self.data.request_list

    async def get_response_by_request_id(self,request_id:str) -> NetworkResponse |None:
        """
        获取fetch/xhr请求的响应
        """
        for response in self.data.response_list:
            if response.requestId == request_id:
                response_result = await self.cdp.send("Network.getResponseBody",{
                    "requestId": request_id
                })
                response.response_result = ResponseResult.from_dict(response_result)
                return response
        return None