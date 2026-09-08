from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Script:
    """Debugger.scriptParsed 核心字段"""
    script_id: str  # 核心：用于后续获取源码
    url: str  # 核心：脚本的完整 URL
    execution_context_id: int  # 核心：脚本所属的执行上下文 ID
    source_map_url: Optional[str] = None  # 核心：用于还原源码
    stack_trace: Optional[Dict[str, Any]] = None  # 核心：动态脚本的调用栈
    is_module: Optional[bool] = None  # 判断是否为 ES Module

    @classmethod
    def from_dict(cls, params: dict) -> "Script":
        return cls(
            script_id=params["scriptId"],
            url=params.get("url", ""),
            execution_context_id=params.get("executionContextId", 0),
            source_map_url=params.get("sourceMapURL"),
            stack_trace=params.get("stackTrace"),
            is_module=params.get("isModule")
        )