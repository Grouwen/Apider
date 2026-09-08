from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Response:
    """
    Network.responseReceived 事件回调参数结构
    """
    url: str
    status: int
    statusText: str
    headers: Dict[str, str]
    mimeType: str
    charset: str

    @classmethod
    def from_dict(cls, d: dict) -> "Response":
        return cls(
            url=d["url"],
            status=d["status"],
            statusText=d["statusText"],
            headers=d.get("headers", {}),
            mimeType=d["mimeType"],
            charset=d["charset"],
        )

@dataclass
class ResponseResult:
    body:str
    base64Encoded:bool
    @classmethod
    def from_dict(cls, d: dict) -> "ResponseResult":
        return cls(
            body=d["body"],
            base64Encoded=bool(d["base64Encoded"]),
        )

@dataclass
class NetworkResponse:
    requestId: str
    response: Response
    type: str
    response_result:ResponseResult|None = None

    @classmethod
    def from_dict(cls, d: dict) -> "NetworkResponse":
        return cls(
            requestId=d["requestId"],
            response=Response.from_dict(d["response"]),
            type=d["type"],
            response_result=None
        )