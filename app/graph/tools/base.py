from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, ClassVar


@dataclass
class ToolResult:
    success: bool
    data: List[dict] | None
    summary: str
    error_msg: str

    @classmethod
    def ok(cls,data: List[dict] | None,summary:str) -> "ToolResult":
        return cls(success=True, data=data, summary=summary,error_msg="")

    @classmethod
    def error(cls,summary: str,error_msg:str) -> "ToolResult":
        return cls(success=False, data=None, summary=summary, error_msg=error_msg)

class ToolArgsType(Enum):
    STR = "string"
    INT = "number"
    FLOAT = "number"
    BOOL = "boolean"
    LIST = "array"
    DICT = "object"

@dataclass
class ToolArgsDescription:
    name: str
    type: ToolArgsType
    description: str
    required: bool

class BaseTool(ABC):
    """
    工具信息作为类属性
    """
    name: ClassVar[str]
    description: ClassVar[str]
    args: ClassVar[List[ToolArgsDescription]]

    @abstractmethod
    async def run(self, **kwargs) -> ToolResult:
        raise NotImplementedError

    @classmethod
    def to_schemas(cls) -> Dict[str, Any]:
        """
        自动生成 OpenAI / 千问 function calling 格式的 json
        """
        properties = {}
        required = []
        for arg in cls.args:
            properties[arg.name] = {
                "type": arg.type.value,
                "description": arg.description,
            }
            if arg.required:
                required.append(arg.name)

        return {
            "type": "function",
            "function": {
                "name": cls.name,
                "description": cls.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }