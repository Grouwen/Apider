from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CallFrame:
    """调用栈帧"""
    function_name: str
    url: str
    line_number: int
    column_number: int = 0
    script_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "CallFrame":
        return cls(
            function_name=data.get("functionName", ""),
            url=data.get("url", ""),
            line_number=data.get("lineNumber", 0),
            column_number=data.get("columnNumber", 0),
            script_id=data.get("scriptId"),
        )


@dataclass
class Initiator:
    """请求发起者"""
    type: str                    # script / parser / other / preload
    url: str                     # 发起脚本URL
    line_number: int = 0
    column_number: int = 0
    stack: List[CallFrame] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Initiator":
        frames = []
        if "stack" in data and "callFrames" in data["stack"]:
            frames = [CallFrame.from_dict(f) for f in data["stack"]["callFrames"]]
        return cls(
            type=data.get("type", ""),
            url=data.get("url", ""),
            line_number=data.get("lineNumber", 0),
            column_number=data.get("columnNumber", 0),
            stack=frames,
        )


@dataclass
class Request:
    """请求详情"""
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    post_data: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Request":
        return cls(
            url=data.get("url", ""),
            method=data.get("method", "GET"),
            headers=data.get("headers", {}),
            post_data=data.get("postData") or data.get("post_data"),
        )


@dataclass
class NetworkRequest:
    """
    CDP Network.request 精简版对象
    """
    request_id: str
    request: Request
    initiator: Initiator
    type: str = "XHR"
    document_url: Optional[str] = None
    timestamp: Optional[float] = None

    # ========== 从精简版 dict 构造 ==========

    @classmethod
    def from_dict(cls, data: dict) -> "NetworkRequest":
        """
        从精简版 dict 构造对象
        期望结构：
        {
            "requestId": "...",
            "request": {"url": "...", "method": "...", "headers": {...}, "postData": "..."},
            "initiator": {"type": "script", "url": "...", "stack": {"callFrames": [...]}},
            "type": "XHR",
            "documentURL": "...",   # 可选
            "timestamp": ...,       # 可选
        }
        """
        return cls(
            request_id=data.get("requestId", ""),
            request=Request.from_dict(data.get("request", {})),
            initiator=Initiator.from_dict(data.get("initiator", {})),
            type=data.get("type", "XHR"),
            document_url=data.get("documentURL"),
            timestamp=data.get("timestamp"),
        )

    # ========== 从完整版 dict 构造 ==========

    @classmethod
    def from_full_dict(cls, data: dict) -> "NetworkRequest":
        """
        从 CDP 完整返回数据中自动提取关键字段构造对象
        自动忽略无关字段（loaderId, wallTime, redirectResponse 等）
        """
        return cls.from_dict({
            "requestId": data.get("requestId", ""),
            "request": data.get("request", {}),
            "initiator": data.get("initiator", {}),
            "type": data.get("type", "XHR"),
            "documentURL": data.get("documentURL"),
            "timestamp": data.get("timestamp"),
        })