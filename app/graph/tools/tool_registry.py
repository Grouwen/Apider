from typing import Dict, List, Any

from app.graph.tools.base import BaseTool


class ToolRegistry:
    tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool_class: BaseTool):
        cls.tools[tool_class.name] = tool_class
        return tool_class

    @classmethod
    def get(cls, name: str) -> BaseTool|None:
        return cls.tools.get(name)

    @classmethod
    def all_schemas(cls) -> List[Dict[str, Any]]:
        return [t.to_schemas() for t in cls.tools.values()]